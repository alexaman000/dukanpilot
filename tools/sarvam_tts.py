"""Sarvam AI Text-to-Speech Integration for DukaanPilot AI.

Provides high-quality Indian English and natural Hindi voice synthesis for
small shopkeeper business briefings. Supports text chunking, local audio
caching, section-by-section generation, and robust fallback error handling.
"""

import base64
import hashlib
import os
import re
from typing import Any, Dict, List, Optional, Tuple
import requests

from workflow.config import (
    DEFAULT_SARVAM_MODEL,
    DEFAULT_SARVAM_SPEAKER_EN,
    DEFAULT_SARVAM_SPEAKER_HI,
    SARVAM_TTS_URL,
    get_sarvam_api_key,
)

# Local cache directory for synthesized audio
AUDIO_CACHE_DIR = os.path.join(".cache", "audio")


def ensure_cache_dir() -> str:
    """Ensure that the local audio cache directory exists."""
    os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
    return AUDIO_CACHE_DIR


def compute_audio_cache_key(
    text: str, language_code: str, speaker: str, model: str
) -> str:
    """Compute a deterministic SHA-256 hash for audio caching."""
    hasher = hashlib.sha256()
    payload_str = f"{text.strip()}::{language_code}::{speaker}::{model}"
    hasher.update(payload_str.encode("utf-8"))
    return hasher.hexdigest()


def chunk_text_for_tts(text: str, max_chars: int = 1500) -> List[str]:
    """Split long reports into sentence/paragraph aligned chunks under Sarvam's limit.
    
    Supports both English (periods) and Hindi (Purna Viram '।').
    """
    clean_text = text.strip()
    if len(clean_text) <= max_chars:
        return [clean_text] if clean_text else []

    # First attempt splitting by double newlines (paragraphs)
    paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= max_chars:
            current_chunk = f"{current_chunk}\n\n{para}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            
            # If paragraph itself exceeds max_chars, split by sentence endings (. or ।)
            if len(para) > max_chars:
                sentences = re.split(r"([।\.\?\!\n])", para)
                temp = ""
                for i in range(0, len(sentences), 2):
                    s = sentences[i]
                    delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""
                    sentence_full = (s + delimiter).strip()
                    if not sentence_full:
                        continue
                    if len(temp) + len(sentence_full) + 1 <= max_chars:
                        temp = f"{temp} {sentence_full}".strip()
                    else:
                        if temp:
                            chunks.append(temp)
                        temp = sentence_full
                if temp:
                    current_chunk = temp
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def synthesize_speech(
    text: str,
    language_code: str = "hi-IN",
    speaker: Optional[str] = None,
    pace: float = 1.0,
    api_key: Optional[str] = None,
    use_cache: bool = True,
    timeout_sec: float = 20.0,
) -> Tuple[Optional[bytes], Optional[str]]:
    """Synthesize speech using Sarvam AI Text-to-Speech API.
    
    Returns:
        (audio_bytes, error_message): If successful, audio_bytes is not None and error is None.
    """
    if not text or not text.strip():
        return None, "Empty text provided for synthesis."

    key = api_key or get_sarvam_api_key()
    if not key:
        return (
            None,
            "SARVAM_API_KEY is not configured. Please set SARVAM_API_KEY in your .env file or Streamlit secrets.",
        )

    # Determine default speaker based on language
    if not speaker:
        speaker = (
            DEFAULT_SARVAM_SPEAKER_HI
            if language_code.startswith("hi")
            else DEFAULT_SARVAM_SPEAKER_EN
        )

    model = DEFAULT_SARVAM_MODEL
    cache_dir = ensure_cache_dir()
    cache_key = compute_audio_cache_key(text, language_code, speaker, model)
    cache_path = os.path.join(cache_dir, f"{cache_key}.mp3")

    # Return cached audio if available
    if use_cache and os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
        try:
            with open(cache_path, "rb") as f:
                return f.read(), None
        except Exception:
            pass

    # If text is longer than 1500 characters, handle chunking
    chunks = chunk_text_for_tts(text, max_chars=1500)
    if len(chunks) > 1:
        combined_audio = bytearray()
        for idx, chunk in enumerate(chunks):
            chunk_audio, err = synthesize_speech(
                text=chunk,
                language_code=language_code,
                speaker=speaker,
                pace=pace,
                api_key=key,
                use_cache=use_cache,
                timeout_sec=timeout_sec,
            )
            if err or not chunk_audio:
                return None, f"Chunk {idx + 1} synthesis failed: {err}"
            combined_audio.extend(chunk_audio)
        
        result_bytes = bytes(combined_audio)
        if use_cache:
            try:
                with open(cache_path, "wb") as f:
                    f.write(result_bytes)
            except Exception:
                pass
        return result_bytes, None

    # Single chunk request to Sarvam AI TTS API
    headers = {
        "Content-Type": "application/json",
        "api-subscription-key": key,
    }

    # BCP-47 normalized language code
    lang_normalized = "hi-IN" if language_code.startswith("hi") else "en-IN"

    payload = {
        "text": text.strip(),
        "language_code": lang_normalized,
        "model": model,
        "speaker": speaker,
        "pace": pace,
        "speech_sample_rate": 24000,
        "output_audio_codec": "mp3",
    }

    try:
        response = requests.post(
            SARVAM_TTS_URL,
            json=payload,
            headers=headers,
            timeout=timeout_sec,
        )

        if response.status_code == 200:
            res_json = response.json()
            audios = res_json.get("audios", [])
            if not audios or not audios[0]:
                return None, "Sarvam AI API responded with empty audio data."

            audio_bytes = base64.b64decode(audios[0])
            if use_cache:
                try:
                    with open(cache_path, "wb") as f:
                        f.write(audio_bytes)
                except Exception:
                    pass
            return audio_bytes, None

        elif response.status_code in (401, 403):
            return (
                None,
                f"Sarvam AI Authentication Failed (HTTP {response.status_code}). Please verify your SARVAM_API_KEY.",
            )
        elif response.status_code == 429:
            return (
                None,
                "Sarvam AI Rate Limit Exceeded (HTTP 429). Please wait a few seconds and try again.",
            )
        else:
            err_msg = response.text[:200] if response.text else f"HTTP {response.status_code}"
            return None, f"Sarvam AI TTS Error ({response.status_code}): {err_msg}"

    except requests.exceptions.Timeout:
        return (
            None,
            "Sarvam AI request timed out. Please check your internet connection.",
        )
    except requests.exceptions.RequestException as e:
        return None, f"Network error connecting to Sarvam AI: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error during speech synthesis: {str(e)}"
