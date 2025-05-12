import os

from pydantic import BaseModel, NonNegativeInt
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).parent
GUARDIAN_PATH = BASE_DIR / "guardian" / "ruBERT_1.0acc"

OLLAMA_ENDPOINT = "http://localhost:11434/v1"

USER_GROUP_RIGHTS = {
    "developer": ("select", "insert", "update", "delete"),
    "manager": ("select",),
}

PROMPT_TEMPLATE = """
### Instructions:
Your task is convert a prompt into a SQL query, given a database schema.
Adhere to these rules:
- **Deliberately go through the question and database schema word by word** to answer the question correctly.
- **Use table aliases** to avoid ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
- **Ensure that the output contains only the SQL query** and **no additional text or comments**.
- **Use MySQL SQL dialect**

### Input:
Generate a SQL query that meet the prompt `{0}`.
This query will run on a database whose schema is represented below:
`{1}`

**Ensure that the output contains only the SQL query and no additional text, symbols or comments.**
**Do not generate markdown code block like ```sql```**

### Response:
Based on your instructions, here is the SQL query (with no additional text, symbols or comments, no markdown code syntax) I have generated to meet the prompt `{0}`:
"""

with open(
    str(BASE_DIR / "sql_generator" / "creation_commented.sql"), "r", encoding="utf-8"
) as file:
    DB_CONTEXT = file.read()


class DBSettings(BaseModel):
    url_api: str = os.getenv("DB_URL_API")
    url_admin: str = os.getenv("DB_URL_ADMIN")
    echo: bool = False


class AuthJWTSettings(BaseModel):
    private_key_path: Path = BASE_DIR / "security" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "security" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 10
    refresh_token_expire_days: int = 1
    bcrypt_work_factor: int = 12


class SecuritySettings(BaseModel):
    user_group_rights: dict[str, tuple] = USER_GROUP_RIGHTS
    user_group_default: str = "developer"
    auth_url_prefix: str = "/auth"
    enabled: bool = True


class GuardianSettings(BaseModel):
    path: str = str(GUARDIAN_PATH)
    enabled: bool = True


class CoreLLMSettings(BaseModel):
    url: str = OLLAMA_ENDPOINT
    # model_name: str = "gemini-2.5-flash-preview-04-17"
    # provider: str = "gemini"
    model_name: str = "llama3.1:8b-instruct-q4_K_M"
    provider: str = "ollama"
    retry_count: NonNegativeInt = 5
    api_key: str = os.getenv("GEMINI_API_KEY")
    prompt: str = PROMPT_TEMPLATE
    db_context: str = DB_CONTEXT


class FrontendSettings(BaseModel):
    frontend_path: Path = BASE_DIR / "frontend"
    templates_path: Path = BASE_DIR / "frontend" / "templates"
    static_path: Path = frontend_path / "static"
    static_path_relative: str = (
        str(static_path).replace(str(BASE_DIR), "").replace("\\", "/")
    )


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 1337


class ApiV1Settings(BaseModel):
    prefix: str = "/v1"


class ApiSettings(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Settings = ApiV1Settings()
    current_root_url: str = prefix + v1.prefix


class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    auth_jwt: AuthJWTSettings = AuthJWTSettings()
    security: SecuritySettings = SecuritySettings()
    guardian: GuardianSettings = GuardianSettings()
    core_llm: CoreLLMSettings = CoreLLMSettings()
    frontend: FrontendSettings = FrontendSettings()
    run: RunConfig = RunConfig()
    api: ApiSettings = ApiSettings()


settings = Settings()
