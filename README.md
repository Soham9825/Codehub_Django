# 🖥️ Django Programming Solver App

A Django-based programming problem-solving platform that integrates with **Judge0 API** for code execution.  
This project uses **MySQL** as the database and environment variables for configuration.

---

## 🚀 Features
- User can submit solutions to programming problems.
- Code execution powered by [Judge0 API](https://judge0.com/).
- Django backend with MySQL database.
- Environment-based configuration for secure secrets.

---

## 🛠️ Tech Stack
- **Backend:** Django (Python)
- **Database:** MySQL
- **Code Execution:** Judge0 API
- **Environment Config:** `python-decouple`

---

## 📦 Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Soham9825/Codehub_Django.git
cd Codehub_Django

2️⃣ Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Linux / Mac
venv\Scripts\activate      # On Windows


3️⃣ Install dependencies
pip install -r requirements.txt


4️⃣ Set up the database
Make sure MySQL is installed and running. Then create a database:

CREATE DATABASE your_db_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


5️⃣ Configure environment variables

Create a .env file in the project root:
include this 

DB_NAME=name
DB_USER=user
DB_PASS=pass
DB_HOST=127.0.0.1
DB_PORT=3306
SECRET_KEY = 'your_secret_key'
JUDGE0_API_URL="https://judge0-ce.p.rapidapi.com"
JUDGE0_API_HOST="judge0-ce.p.rapidapi.com"
JUDGE0_API_KEY = 'your_api_key'

In setting.py make changes there

# Django settings
SECRET_KEY=your_django_secret_key

# MySQL Database
DB_NAME=your_db_name
DB_USER=your_mysql_user
DB_PASS=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Judge0 API
JUDGE0_API_URL=https://your-judge0-instance-url
JUDGE0_API_HOST=your-judge0-api-host
JUDGE0_API_KEY=your-judge0-api-key

6️⃣ Run migrations
python manage.py migrate

7️⃣ Create a superuser (optional)
python manage.py createsuperuser

8️⃣ Start the server
python manage.py runserver

⚡ Useful Commands

Collect static files:

python manage.py collectstatic