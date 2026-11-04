"""Unit and integration tests for Sarvam AI Text-to-Speech integration."""

import os
from unittest.mock import MagicMock, patch
import pytest

from tools.sarvam_tts import (
    chunk_text_for_tts,
    compute_audio_cache_key,
    synthesize_speech,
)
from workflow.config import get_sarvam_api_key, is_sarvam_available


def test_chunk_text_short_text():
    """Verify that short text remains a single chunk."""
    short_text = "Namaste, welcome to Sneha Bhandar."
    chunks = chunk_text_for_tts(short_text, max_chars=500)
    assert len(chunks) == 1
    assert chunks[0] == short_text


def test_chunk_text_long_hindi_and_english():
    """Verify that long reports split cleanly along sentence and paragraph boundaries."""
    # Long text with Hindi Purna Viram and English periods
    long_text = (
        "नमस्ते स्नेहा भंडार में आपका स्वागत है। आपकी कुल बिक्री ₹24,000 दर्ज की गई है। "
        "यह एक परीक्षण रिपोर्ट है जो लंबी है।\n\n"
        "अगला खंड व्यापार लक्ष्य का है। मासिक लक्ष्य ₹10,000 है और अंतर ₹841 है। "
        "हम इसे कई छोटे वाक्यों में विभाजित कर रहे हैं। " * 10
    )
    chunks = chunk_text_for_tts(long_text, max_chars=300)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 300
        assert len(c.strip()) > 0


def test_compute_audio_cache_key_deterministic():
    """Verify that cache key is deterministic for identical inputs and varies for different inputs."""
    k1 = compute_audio_cache_key("Hello World", "en-IN", "priya", "bulbul:v3")
    k2 = compute_audio_cache_key("Hello World", "en-IN", "priya", "bulbul:v3")
    k3 = compute_audio_cache_key("Hello World", "hi-IN", "ritu", "bulbul:v3")
    assert k1 == k2
    assert k1 != k3


def test_synthesize_speech_missing_key_behavior(monkeypatch):
    """Verify that synthesize_speech returns descriptive error without crashing when key is absent."""
    monkeypatch.delenv("SARVAM_API_KEY", raising=False)
    audio, err = synthesize_speech("Hello", api_key=None, use_cache=False)
    assert audio is None
    assert err is not None
    assert "SARVAM_API_KEY is not configured" in err


def test_synthesize_speech_mocked_success(monkeypatch, tmp_path):
    """Verify that valid Sarvam API responses are correctly decoded from base64."""
    import base64

    # Fake audio bytes (e.g. 100 bytes)
    sample_bytes = b"ID3\x03\x00\x00\x00\x00\x00#TSSE\x00\x00\x00\x0f\x00\x00\x03Lavf58.76.100" + b"\x00" * 80
    fake_b64 = base64.b64encode(sample_bytes).decode("utf-8")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"audios": [fake_b64]}

    with patch("requests.post", return_value=mock_resp):
        audio, err = synthesize_speech(
            "नमस्ते स्नेहा भंडार",
            language_code="hi-IN",
            api_key="mock_sarvam_key",
            use_cache=False,
        )

    assert err is None
    assert audio == sample_bytes


def test_synthesize_speech_mocked_401_error():
    """Verify that 401 unauthorized errors are clearly reported."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized: Invalid subscription key"

    with patch("requests.post", return_value=mock_resp):
        audio, err = synthesize_speech(
            "Hello",
            language_code="en-IN",
            api_key="invalid_key",
            use_cache=False,
        )

    assert audio is None
    assert "Authentication Failed" in err
    assert "401" in err


def test_synthesize_speech_timeout_handling():
    """Verify that network timeouts return a clear, user-friendly error message."""
    import requests

    with patch("requests.post", side_effect=requests.exceptions.Timeout("Connection timed out")):
        audio, err = synthesize_speech(
            "Test text",
            api_key="mock_key",
            use_cache=False,
            timeout_sec=0.1,
        )

    assert audio is None
    assert "timed out" in err
