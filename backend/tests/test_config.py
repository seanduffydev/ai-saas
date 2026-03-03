"""Tests for app config."""

def test_settings_has_required_attributes():
    """Settings object has all required config attributes."""
    from app.config import settings
    assert hasattr(settings, "supabase_url")
    assert hasattr(settings, "supabase_key")
    assert hasattr(settings, "openai_api_key")
    assert hasattr(settings, "news_api_key")
    assert hasattr(settings, "alpha_vantage_api_key")
    assert isinstance(settings.supabase_url, str)
    assert isinstance(settings.supabase_key, str)
