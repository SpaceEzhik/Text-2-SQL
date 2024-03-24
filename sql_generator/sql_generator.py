import httpx

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_CONFIG = {
    "model": "mistral",
    "stream": False,
}
HEADERS = {
    "Content-Type": "application/json",
}


async def generate_sql(question: str):
    prompt = f"""
    ### Instructions:
    Ваша задача - преобразовать вопрос в SQL-запрос, зная схему базы данных.
    Придерживайтесь следующих правил:
    - **Преднамеренно просматривайте вопрос и схему базы данных слово за словом**, чтобы правильно ответить на вопрос.
    - **Используйте псевдонимы таблиц**, чтобы избежать двусмысленности. Например, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.

    ### Input:    
    Создайте SQL-запрос, отвечающий на вопрос `{question}`.
    Этот запрос будет выполняться на базе данных, схема которой представлена в этой строке:
    
    CREATE TABLE Addresses (
        address_id INTEGER NOT NULL, --Уникальные ID для адресов
        line_1 VARCHAR(80), -- Полный адрес
        city VARCHAR(50),-- Название города
        zip_postcode CHAR(20), --Почтовый индекс
        state_province_county VARCHAR(50), --Штат
        country VARCHAR(50) --Страна
    );
    CREATE TABLE People (
        person_id INTEGER NOT NULL,--Уникальные ID для человека
        first_name VARCHAR(255), --Первое имя
        middle_name VARCHAR(255), -- Второе ия
        last_name VARCHAR(255), -- Последнее имя
        cell_mobile_number VARCHAR(40), -- Номер телефона
        email_address VARCHAR(40), --Адрес электронной почты
        login_name VARCHAR(40),--Логин
        password VARCHAR(40)-Пароль
    );
    CREATE TABLE Students (
        student_id INTEGER NOT NULL, --Id студента
        student_details VARCHAR(255) --Имя студента
    );
    CREATE TABLE Courses (
        course_id VARCHAR(100) NOT NULL,--Уникальные ID для курса
        course_name VARCHAR(120), --Название курса
        course_description VARCHAR(255), --Описание курса
    );
    CREATE TABLE People_Addresses (
        person_address_id INTEGER NOT NULL, --Уникальные ID для человека
        person_id INTEGER NOT NULL, --Уникальные ID для человека
        address_id INTEGER NOT NULL, --Уникальные ID для адреса
        date_from DATETIME, -- Дата с которой человек проживает по адресу
        date_to DATETIME -- Дата в котороую человек съезал с адреса
    );
    CREATE TABLE Student_Course_Registrations (
        student_id INTEGER NOT NULL,--Уникальные ID для студента
        course_id INTEGER NOT NULL,--Уникальные ID для курса
        registration_date DATETIME NOT NULL --Дата регистрации
    );
    CREATE TABLE Student_Course_Attendance (
        student_id INTEGER NOT NULL, --Уникальные ID для студента
        course_id INTEGER NOT NULL,--Уникальные ID для курса
        date_of_attendance DATETIME NOT NULL --Дата прохождения
    );
    CREATE TABLE Candidates (
        candidate_id INTEGER NOT NULL , --Уникальные ID для кандидата 
        candidate_details VARCHAR(255) --Имя кандидата
    );

    ### Response:
    Основываясь на ваших инструкциях, вот SQL-запрос, который я создал для ответа на вопрос `{question}`:
    ```sql
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(OLLAMA_ENDPOINT,
                                     json={"prompt": prompt, **OLLAMA_CONFIG},
                                     headers=HEADERS,
                                     timeout=100
                                     )
        query = response.json()["response"].strip()
    return query

# print(generate_sql("show me the whole suppliers table"))
