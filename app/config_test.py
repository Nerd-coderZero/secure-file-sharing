# app/config_test.py
from app.config import Settings
import os
from pydantic import Field

class TestSettings(Settings):
    # Override database URL for tests
    DATABASE_URL: str = Field(
        "sqlite:///./test.db", 
        description="Database URL for testing"
    )
    # Test-specific settings
    TESTING: bool = True

def get_test_settings():
    return TestSettings()
