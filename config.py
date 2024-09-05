from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path

from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

BASE_DIR = Path(__file__).parent
GUARDIAN_PATH = BASE_DIR / "guardian" / "ruBERT_1.0acc"

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_CONFIG = {
    "model": "llama3:8b-instruct-q4_0",
    "stream": False,
    "keep_alive": "5m",
}

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
CREATE TABLE Addresses (
    address_id INTEGER NOT NULL, -- ID адреса
    line_1 VARCHAR(80), -- Основная информация об адресе (улица, дом, номер квартиры)
    line_2 VARCHAR(80), -- Дополнительная информация об адресе
    city VARCHAR(50), -- Название города
    zip_postcode CHAR(20), -- Почтовый индекс
    state_province_county VARCHAR(50), -- Название штата или области
    country VARCHAR(50), -- Название страны
    PRIMARY KEY (address_id)
);

CREATE TABLE Courses (
    course_id VARCHAR(100) NOT NULL, -- ID курса
    course_name VARCHAR(120), -- Название курса
    course_description VARCHAR(255), -- Описание курса
    other_details VARCHAR(255), -- Дополнительная информация о курсе
    PRIMARY KEY (course_id)
);

CREATE TABLE People (
    person_id INTEGER NOT NULL, -- ID человека
    first_name VARCHAR(255), -- Имя
    middle_name VARCHAR(255), -- Второе имя
    last_name VARCHAR(255), -- Фамилия
    cell_mobile_number VARCHAR(40), -- Номер телефона
    email_address VARCHAR(40), -- Адрес электронной почты
    login_name VARCHAR(40), -- Логин
    password VARCHAR(40), -- Пароль
    PRIMARY KEY (person_id)
);

CREATE TABLE Candidates (
    candidate_id INTEGER NOT NULL , -- ID кандидата 
    candidate_details VARCHAR(255), -- Дополнительная информация о кандидате
    PRIMARY KEY (candidate_id),
    FOREIGN KEY (candidate_id) REFERENCES People (person_id)
);

CREATE TABLE People_Addresses (
    person_address_id INTEGER, -- ID связывающей записи
    person_id INTEGER, --  ID человека
    address_id INTEGER, --  ID адреса
    PRIMARY KEY (person_address_id),
    FOREIGN KEY (address_id) REFERENCES Addresses(address_id),
    FOREIGN KEY (person_id) REFERENCES People(person_id)
);

CREATE TABLE Students (
    student_id INTEGER NOT NULL, -- ID студента
    student_details VARCHAR(255), -- Дополнительная информация о студенте
    PRIMARY KEY (student_id),
    FOREIGN KEY (student_id) REFERENCES People (person_id)
);

CREATE TABLE Candidate_Assessments (
    candidate_id INTEGER NOT NULL, -- ID кандидата
    qualification CHAR(15) NOT NULL, -- Оценка за вступительный экзамен
    assessment_date DATETIME NOT NULL, -- Дата вступительного экзамена
    assessment_outcome_code CHAR(15) NOT NULL, -- Результат вступительного экзамена (Pass или Fail)
    PRIMARY KEY (candidate_id, qualification),
    FOREIGN KEY (candidate_id) REFERENCES Candidates (candidate_id)
);

CREATE TABLE Student_Course_Registrations (
    student_id INTEGER NOT NULL, -- ID студента
    course_id VARCHAR(100) NOT NULL, -- ID курса
    registration_date DATETIME NOT NULL, -- Дата регистрации на курс
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES Students (student_id),
    FOREIGN KEY (course_id) REFERENCES Courses (course_id)
);

CREATE TABLE Student_Course_Attendance (
    student_id INTEGER NOT NULL, -- ID студента
    course_id VARCHAR(100) NOT NULL, -- ID курса
    date_of_attendance DATETIME NOT NULL, -- Дата прохождения курса
    other_details VARCHAR(255), -- Дополнительная информация о прохождении курса
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id, course_id) REFERENCES Student_Course_Registrations (student_id,course_id)
);

**Ensure that the output contains only the SQL query and no additional text, symbols or comments.**

### Response:
Based on your instructions, here is the SQL query (with no additional text, symbols or comments) I have generated to meet the prompt `{0}`:
"""


class DbSettings(BaseModel):
    url_api: str = "[ДАННЫЕ УДАЛЕНЫ]"
    url_admin: str = "[ДАННЫЕ УДАЛЕНЫ]"
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
    auth_url_prefix: str = "/auth"


class GuardianSettings(BaseModel):
    path: str = str(GUARDIAN_PATH)


class CoreLLMSettings(BaseModel):
    url: str = OLLAMA_ENDPOINT
    config: dict = OLLAMA_CONFIG
    prompt: str = PROMPT_TEMPLATE


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
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWTSettings = AuthJWTSettings()
    security: SecuritySettings = SecuritySettings()
    guardian: GuardianSettings = GuardianSettings()
    core_llm: CoreLLMSettings = CoreLLMSettings()
    frontend: FrontendSettings = FrontendSettings()
    run: RunConfig = RunConfig()
    api: ApiSettings = ApiSettings()


settings = Settings()
