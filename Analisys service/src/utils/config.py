import os
import re
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy import URL

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


class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    name: str
    driver: str
    database_system: str

    def url(self):
        return URL.create(
            drivername=f"{self.database_system}+{self.driver}",
            username=self.user,
            database=self.name,
            password=self.password,
            port=self.port,
            host=self.host,
        ).render_as_string(hide_password=False)


class MinioConfig(BaseModel):
    host: str
    port: int
    secure: bool
    access_key: str
    secret_key: str
    bucket_name: str

    @property
    def endpoint(self):
        return f"{self.host}:{self.port}"


class StoreServiceConfig(BaseModel):
    host: str
    port: int
    secure: bool
    path: str


class WordCloudConfig(BaseModel):
    host: str
    path: str
    pic_format: str
    width: int
    height: int
    font_family: str
    font_scale: int
    scale: str


class Config(BaseModel):
    database: DatabaseConfig
    minio: MinioConfig
    file_store_service: StoreServiceConfig
    word_cloud: WordCloudConfig


def load_config() -> Config:
    data = load_yaml_config()
    return Config(**data)
