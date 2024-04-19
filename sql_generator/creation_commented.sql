CREATE TABLE Addresses (
	address_id INTEGER NOT NULL AUTO_INCREMENT, -- ID адреса
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
	person_id INTEGER NOT NULL AUTO_INCREMENT, -- ID человека
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