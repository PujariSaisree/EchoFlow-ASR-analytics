from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ECHOFLOW_", extra="ignore")

    app_name: str = "EchoFlow — AI-Powered Speech Analytics and Business Decision Support Platform"
    app_short_name: str = "EchoFlow"
    data_dir: Path = Path("data")
    upload_dir: Path = Path("storage/uploads")
    processed_dir: Path = Path("storage/processed")
    database_path: Path = Path("data/echoflow.db")
    max_upload_mb: int = 50
    default_model: str = "tiny"
    allowed_models: tuple[str, ...] = ("tiny", "base", "small", "medium")
    target_sample_rate: int = 16000
    compute_type: str = "int8"
    device: str = "cpu"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()


def ensure_directories() -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
