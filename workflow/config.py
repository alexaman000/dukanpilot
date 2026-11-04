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


def get_gemini_api_key() -> Optional[str]:
    """Retrieve the Gemini API key from environment variables."""
    key = os.getenv("GEMINI_API_KEY")
    if key and key.strip() and key != "your_gemini_api_key_here":
        return key.strip()
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
