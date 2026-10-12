import os
from typing import List, Optional

class Settings:
    PROJECT_NAME: str = "Simplifier 2.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    API_V1_STR: str = "/api/v1"
    
    # Upload constraints
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "15"))
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "jpg", "jpeg", "png", "webp"]
    
    # Production Auth / Supabase placeholders
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL", None)
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY", None)

    def validate_production(self):
        """Production must fail closed if required credentials are absent."""
        if self.ENVIRONMENT == "production":
            if not self.SUPABASE_URL or not self.SUPABASE_KEY:
                raise RuntimeError("PRODUCTION CONFIG ERROR: SUPABASE_URL and SUPABASE_KEY are required in production mode.")

settings = Settings()
