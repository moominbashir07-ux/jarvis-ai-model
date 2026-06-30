import os
from pathlib import Path
from dotenv import load_dotenv

# Automatically locate and load the .env file from the root directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

class Settings:
    """Application settings class that handles loading, casting, and default fallbacks for env vars."""

    def __init__(self):
        # Environment Info
        self.env: str = os.getenv("JARVIS_ENV", "development").lower()
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

        # Directories
        self.root_dir: Path = ROOT_DIR
        self.logs_dir: Path = ROOT_DIR / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        # Brain / APIs
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

        # Voice Settings
        self.voice_enabled: bool = self._to_bool(os.getenv("VOICE_ENABLED", "true"))
        self.voice_provider: str = os.getenv("VOICE_PROVIDER", "system").lower()
        self.elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
        self.wake_word: str = os.getenv("WAKE_WORD", "jarvis").lower()
        self.energy_threshold: int = int(os.getenv("ENERGY_THRESHOLD", "300"))
        self.silence_duration: float = float(os.getenv("SILENCE_DURATION", "1.5"))
        self.stt_provider: str = os.getenv("STT_PROVIDER", "google").lower()
        self.voice_id: str = os.getenv("TTS_VOICE_ID", "")
        self.push_to_talk_key: str = os.getenv("PTT_KEY", "ctrl+space").lower()

        # Memory Settings
        self.memory_db_path: Path = ROOT_DIR / os.getenv("MEMORY_DB_PATH", "jarvis_memory.db")

        # Vision Settings
        self.vision_enabled: bool = self._to_bool(os.getenv("VISION_ENABLED", "false"))
        try:
            self.webcam_index: int = int(os.getenv("WEBCAM_INDEX", "0"))
        except ValueError:
            self.webcam_index = 0

        # Automation Settings
        self.allow_unsafe_commands: bool = self._to_bool(os.getenv("ALLOW_UNSAFE_COMMANDS", "false"))

    def _to_bool(self, val: str) -> bool:
        """Utility to convert environment string variables to actual boolean values."""
        if not val:
            return False
        return val.lower() in ("true", "1", "yes", "on", "t")

    def __repr__(self) -> str:
        return (
            f"Settings(env={self.env}, log_level={self.log_level}, "
            f"voice_enabled={self.voice_enabled}, vision_enabled={self.vision_enabled})"
        )

# Global settings instance
settings = Settings()
