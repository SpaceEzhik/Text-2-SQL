# Text-2-SQL Web Application

## Overview

This project is a Text-2-SQL web application powered by large language models (LLMs), allowing users to query a specific
database using natural language input.

It features a custom BERT-based model trained to detect and filter potentially unrelated or malicious queries. The
backend is built using FastAPI for efficient API management, with SQLAlchemy utilized for seamless database
interactions, and MySQL serves as the database management system. A user-friendly interface has been implemented for
easy query input and result viewing.

## Navigation

1. [Installation](#installation)
2. [Usage](#usage)
3. [Project details](#project-details)
4. [Testing](#testing)
5. [Possible TODOs](#possible-todos)
6. [License](#license)

---

## Installation

### Prerequisites

- Make sure you have [Python 3.12](https://www.python.org/downloads/) installed on your machine.

### Database setup

Here is the setup process for MySQL, but you are free to use another relational database.

1. Set up your MySQL server: Follow
   the [MySQL getting started guide](https://dev.mysql.com/doc/mysql-getting-started/en/).
2. Create your database structure: Use the [DDL script](./sql_generator/creation_commented.sql) to describe your domain
   to the LLM.
3. Create a user for the API: Follow
   these [instructions to create a MySQL user](https://dev.mysql.com/doc/refman/8.4/en/create-user.html). This user will
   be used by the API to execute queries.
4. Assign necessary privileges: Use the [privileges script](./security/privileges.sql) to grant the user the required
   permissions.
5. Create a users table: If you're setting up authentication, use
   the [users table script](./security/users.sql). If not, simply
   comment `APIRouter` dependencies [here](./api/api_v1/views.py).

### Ollama setup

1. Install [Ollama](https://ollama.com/)

3. Download a model: Choose a model from the [Ollama library](https://ollama.com/library). During development, I
   used [llama3 8b-instruct](https://ollama.com/library/llama3:8b-instruct-q4_0), but feel
   free to experiment:
   ```bash
    ollama pull [model name]
    ```
3. Run Ollama: Once installed, get Ollama running.

### Guardian setup

If you're skipping the anti-fraud system, simply set `enabled` attribute to `False`
in `GuardianSettings` in the [config file](./config.py).

Otherwise, you should train it yourself:

1. Create your dataset: Prepare your own dataset (example provided [here](./guardian/dataset.csv)) and refer to [project
   details](#project-details).
2. Choose a BERT-based model: Select a suitable BERT variant to fine-tune.
3. Train your model: Follow the steps outlined in [this notebook](./guardian/bert_tuning.ipynb) to fine-tune your model.

### Application setup

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/fastapi-app.git
    cd fastapi-app
    ```

3. Create a virtual environment: Follow the official [venv guide](https://docs.python.org/3/library/venv.html).

3. Install [Poetry](https://python-poetry.org/):
    ```bash
    pip install poetry
    ```

4. Install the required dependencies:
    ```bash
    poetry install
    ```
5. Install PyTorch: Depending on your setup, you might need a specific version of PyTorch. Follow the
   instructions [here](https://pytorch.org/get-started/locally/).
6. Generate RSA keys: Issue RSA keys using [instructions](./security/certs/README.md).

7. Configure `DBSettings` (which involves creating `.env` file as in the [example](.env.example)) and `CoreLLMSettings`
   in the [config file](./config.py)
   to match
   your [database](#database-setup) setup and the LLM chosen during the [Ollama setup](#ollama-setup).

8. Run the application:
    ```bash
    python app.py
    ```

---

## Usage

Once the application is running **locally**, open your browser and navigate to:

- `http://localhost:8000/api/v1` for the application.
- `http://localhost:8000/docs` for the auto-generated API documentation (Swagger UI).
- `http://localhost:8000/redoc` for the ReDoc documentation.

---

## Project details

### Reasoning

In today's world, nearly every company has analysts or developers who frequently work with databases. Often, employees
without SQL knowledge approach these professionals to retrieve data, disrupting their primary tasks.

The goal of this project is to automate these requests, empowering users to access database information by interacting
with the system
in natural language without needing SQL expertise. Large language models (LLMs) will assist in making this
possible.

### Guardian

Creating a training dataset for fine-tuning the ruBERT model on a binary classification task is essential for improving
the model's accuracy in the specific context of the project.
Here, [ruBERT model](https://huggingface.co/DeepPavlov/rubert-base-cased) acts as a "guardian," filtering irrelevant
queries before they reach the main language model, which generates SQL queries from natural language input.

To achieve the goals of the project, a training [dataset](./guardian/dataset.csv) consisting of 1,200 samples was
created in accordance with database specifics. The dataset includes
600 examples of relevant queries and 600 examples of irrelevant queries. Each query was manually annotated for the
binary classification task, where each query is labeled as either relevant or irrelevant (classes 1 and 0,
respectively).

### Security

I implemented JWT authentication from scratch — not because it's the most efficient solution, but for the sake of
learning. It’s a bit of reinventing the wheel, but the process was valuable for educational purposes.

Additionally, there's a basic role-based access control system in place. You can easily adjust the roles and permissions
through the `SecuritySettings` in [config file](./config.py).


---

## Testing

Run the tests using:

```bash
poetry run pytest -v
```

---

## Possible TODOs

1. Implement automatic redirection: When the access token expires, the `/refresh` endpoint is
   triggered and returns a new pair of tokens in raw
   JSON format. This forces the user to manually navigate to another page instead of being automatically redirected back
   to the previous page. Since frontend is not my favorite, this minor inconvenience remains unresolved for now.
2. Fix response codes for redirection: The current redirection implementation results in slightly misleading status
   codes — successful responses appear when redirection responses should be shown. This needs to be cleaned up.
3. Create a polished frontend: The current frontend is a bit kludgy, so a more polished implementation would improve
   user experience.
4. Simplify auto-redirect logic: The current auto-redirect setup is somewhat chaotic, and a proper frontend will help
   streamline this process.
5. Enhance model output processing: Improving the parsing and processing of model outputs is a key step to enhancing the
   overall application performance.

---

## License

This project is licensed under the MIT License.

You can view the full license text in the [LICENSE](./LICENSE) file.


