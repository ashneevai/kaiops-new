from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "KaiOps API"
    environment: str = Field(default="development")
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(default="postgresql+psycopg://kaiops:kaiops@localhost:5432/kaiops")
    redis_url: str = Field(default="redis://localhost:6379/0")
    kafka_bootstrap_servers: str = Field(default="localhost:9092")
    kafka_required: bool = Field(default=False)
    prometheus_base_url: str = Field(default="http://localhost:9090")

    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=60)

    otel_enabled: bool = True
    otel_exporter_endpoint: str = Field(default="http://localhost:4317")

    embedding_provider: str = Field(default="openai")
    openai_api_key: str | None = None
    openai_embedding_model: str = Field(default="text-embedding-3-small")
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_embedding_deployment: str | None = None

    kubeconfig_path: str | None = None
    kubernetes_bearer_token: str | None = None
    terraform_token: str | None = None
    ansible_runner_endpoint: str | None = None
    ansible_runner_token: str | None = None
    jenkins_url: str | None = None
    jenkins_user: str | None = None
    jenkins_api_token: str | None = None
    argocd_url: str | None = None
    argocd_token: str | None = None


settings = Settings()
