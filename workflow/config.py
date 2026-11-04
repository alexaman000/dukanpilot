"""Configuration settings and environment variable management for DukaanPilot AI."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load local environment configuration
load_dotenv()

# Shop Profile Constants
SHOP_NAME = "Sneha Bhandar"
SHOP_ADDRESS = "Shiv Shakti Nagar, Booty More, Ranchi, Jharkhand - 834009"
SHOP_TYPE = "Neighborhood grocery and daily-needs shop"
SHOP_CURRENCY = "INR"

# Business Targets
BASELINE_MONTHLY_REVENUE = 8000.0
TARGET_MONTHLY_REVENUE = 10000.0
MONTHLY_REVENUE_GROWTH_TARGET = TARGET_MONTHLY_REVENUE - BASELINE_MONTHLY_REVENUE

# Database & Storage
DEFAULT_DB_PATH = os.getenv("DATABASE_PATH", "database/dukaanpilot.db")

# Model Configuration
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Sarvam AI Text-to-Speech Configuration
SARVAM_TTS_URL = os.getenv("SARVAM_TTS_URL", "https://api.sarvam.ai/text-to-speech")
DEFAULT_SARVAM_MODEL = os.getenv("SARVAM_MODEL", "bulbul:v3")
DEFAULT_SARVAM_SPEAKER_HI = os.getenv("SARVAM_SPEAKER_HI", "ritu")
DEFAULT_SARVAM_SPEAKER_EN = os.getenv("SARVAM_SPEAKER_EN", "priya")


def get_gemini_api_key() -> Optional[str]:
    """Retrieve the Gemini API key from environment variables or Streamlit secrets."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass

    if key and str(key).strip() and str(key).strip() != "your_gemini_api_key_here":
        return str(key).strip()
    return None


def is_gemini_available() -> bool:
    """Check whether a valid Gemini API key is configured."""
    return get_gemini_api_key() is not None


def require_gemini_api_key() -> str:
    """Retrieve the Gemini API key or raise an explicit, descriptive error."""
    key = get_gemini_api_key()
    if not key:
        raise ValueError(
            "Missing Gemini API credentials: GEMINI_API_KEY environment variable is not configured. "
            "Please copy .env.example to .env and supply a valid Gemini API key."
        )
    return key


def get_sarvam_api_key() -> Optional[str]:
    """Retrieve the Sarvam AI API key from environment variables or Streamlit secrets."""
    key = os.getenv("SARVAM_API_KEY")
    if not key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "SARVAM_API_KEY" in st.secrets:
                key = st.secrets["SARVAM_API_KEY"]
        except Exception:
            pass

    if key and str(key).strip() and str(key).strip() != "your_sarvam_api_key_here":
        return str(key).strip()
    return None


def is_sarvam_available() -> bool:
    """Check whether a valid Sarvam AI API key is configured."""
    return get_sarvam_api_key() is not None


def require_sarvam_api_key() -> str:
    """Retrieve the Sarvam AI API key or raise an explicit, descriptive error."""
    key = get_sarvam_api_key()
    if not key:
        raise ValueError(
            "Missing Sarvam AI credentials: SARVAM_API_KEY environment variable is not configured. "
            "Please set SARVAM_API_KEY in your .env file or Streamlit deployment secrets."
        )
    return key
