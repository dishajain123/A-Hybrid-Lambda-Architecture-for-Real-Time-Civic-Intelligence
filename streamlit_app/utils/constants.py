import os
from enum import Enum

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

# Colors
class SentimentColor(Enum):
    POSITIVE = "#10b981"  # Green
    NEUTRAL = "#6b7280"   # Gray
    NEGATIVE = "#ef4444"  # Red

class Severity(Enum):
    LOW = ("🟢", "Low", SentimentColor.POSITIVE.value)
    MEDIUM = ("🟡", "Medium", "#f59e0b")
    HIGH = ("🔴", "High", SentimentColor.NEGATIVE.value)

# UI color palette used by charts and badges
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "accent": "#10b981",
    "muted": "#6b7280",
}

# Sentiment labels used across pages
SENTIMENT_LABELS = {
    "positive": "Positive",
    "neutral": "Neutral",
    "negative": "Negative",
}

# Map sentiment to UI colors
SEVERITY_MAP = {
    "positive": {"label": "Positive", "color": SentimentColor.POSITIVE.value},
    "neutral": {"label": "Neutral", "color": SentimentColor.NEUTRAL.value},
    "negative": {"label": "Negative", "color": SentimentColor.NEGATIVE.value},
}

def get_color_from_sentiment(sentiment: float) -> str:
    """Map sentiment score to a color."""
    if sentiment > 0.2:
        return SentimentColor.POSITIVE.value
    if sentiment < -0.2:
        return SentimentColor.NEGATIVE.value
    return SentimentColor.NEUTRAL.value

def get_severity_from_sentiment(sentiment: float) -> Severity:
    """Convert sentiment score to severity"""
    if sentiment > 0.3:
        return Severity.LOW
    elif sentiment > -0.3:
        return Severity.MEDIUM
    else:
        return Severity.HIGH

# Categories
CATEGORIES = [
    "politics",
    "general",
    "sports",
    "business",
    "technology",
    "entertainment",
    "health"
]

# Default filters
DEFAULT_FILTERS = {
    "limit": 50,
    "category": None,
    "source": None,
    "sentiment_min": -1.0,
    "sentiment_max": 1.0
}

# UI Constants
CARD_BORDER_RADIUS = 12
CARD_PADDING = "1.5rem"
METRIC_DECIMALS = 2
CHART_HEIGHT = 400
SIDEBAR_WIDTH = 280

# Shared Plotly layout used across dashboard pages
PLOTLY_LAYOUT = {
    "template": "plotly_white",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Arial, sans-serif", "size": 12, "color": "#111827"}
}

# Refresh intervals
REFRESH_INTERVAL_SECONDS = 30
AUTO_REFRESH_ENABLED = True

# Map constants
DEFAULT_MAP_ZOOM = 4
DEFAULT_LATITUDE = 20.5937
DEFAULT_LONGITUDE = 78.9629
MAP_HEIGHT = 500
