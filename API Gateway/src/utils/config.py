import os
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # путь до корня проекта
CONFIG_PATH = BASE_DIR / 'config.yaml'

load_dotenv()


def resolve_env_vars(obj):
    if isinstance(obj, dict):
        return {k: resolve_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_env_vars(i) for i in obj]
    elif isinstance(obj, str):
        return re.sub(r"\$\{(\w+)\}", lambda m: os.getenv(m.group(1), m.group(0)), obj)
    else:
        return obj


def load_yaml_config(path: str = CONFIG_PATH):
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    return resolve_env_vars(raw)


class AnalysisConfig(BaseModel):
    host: str
    port: int


class StoreConfig(BaseModel):
    host: str
    port: int


class Config(BaseModel):
    analysis_service: AnalysisConfig
    store_service: StoreConfig

    @property
    def ANALYSIS_API_URL(self):
        return f"http://{self.analysis_service.host}:{self.analysis_service.port}"

    @property
    def FILES_API_URL(self):
        return f"http://{self.store_service.host}:{self.store_service.port}"


def load_config() -> Config:
    data = load_yaml_config()
    return Config(**data)
