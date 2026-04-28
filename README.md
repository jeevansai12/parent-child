# Parent-Child Communication Quality Analyzer

A full-stack Django web application that uses Machine Learning (Gradient Boosting) to analyze and classify parent-child communication quality as **Strong**, **Moderate**, or **Weak**, with actionable recommendations.

---

## 🚀 Quick Start Guide

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| MySQL | 8.0+ (or XAMPP) |
| pip | Latest |

---

### Step 1 — Clone / Navigate to the project

```bash
cd krupa
```

### Step 2 — Create and activate the virtual environment

```bash
# Windows
py -m venv venv
venv\Scripts\activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
pip install mysqlclient
```

### Step 4 — Set up MySQL

Start your MySQL server (via XAMPP, MySQL Workbench, or the MySQL service).

Then create the database:

```sql
CREATE DATABASE communication_analyzer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Step 5 — Configure environment

Edit `.env` in the project root:

```env
SECRET_KEY=django-insecure-change-me-in-production-abc123xyz
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=communication_analyzer
DB_USER=root
DB_PASSWORD=          # your MySQL root password (leave blank if none)
DB_HOST=localhost
DB_PORT=3306
```

### Step 6 — Train the ML model

```bash
python ml_engine/train_model.py
```

Expected output:
```
Test Accuracy: 0.8933
Model saved to: ml_engine/model.pkl
```

### Step 7 — Run database migrations

```bash
python manage.py makemigrations accounts questionnaire
python manage.py migrate
```

### Step 8 — Create admin superuser (optional)

```bash
python manage.py createsuperuser
```

### Step 9 — Start the development server

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## 📁 Project Structure

```
krupa/
├── manage.py
├── requirements.txt
├── .env                         ← DB & secret key config
├── communication_analyzer/      ← Django project settings
│   ├── settings.py
│   └── urls.py
├── accounts/                    ← Auth (register, login, logout)
│   ├── models.py               (CustomUser with role)
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── questionnaire/               ← Core feature app
│   ├── models.py               (QuestionnaireResponse, PredictionResult, Recommendation)
│   ├── views.py                (submit, predict, history, recommendations)
│   ├── serializers.py
│   └── urls.py
├── ml_engine/                   ← Machine Learning
│   ├── train_model.py          (GradientBoostingClassifier training)
│   ├── predict.py              (inference function)
│   └── model.pkl               (trained model artifact)
└── templates/                   ← HTML templates
    ├── base.html
    ├── accounts/
    │   ├── login.html
    │   └── register.html
    └── questionnaire/
        ├── questionnaire.html
        ├── results.html
        └── history.html
```

---

## 🌐 Pages & API Endpoints

### Web Pages

| URL | Description |
|-----|-------------|
| `/login/` | Login page |
| `/register/` | Registration with role (Parent/Child) |
| `/questionnaire/` | 10-question Likert questionnaire |
| `/results/<id>/` | Results dashboard with score & recommendations |
| `/history/` | History with trend chart |

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register/` | Register a new user |
| POST | `/api/login/` | Login (session auth) |
| POST | `/api/logout/` | Logout |
| POST | `/api/submit-questionnaire/` | Submit answers → returns prediction |
| GET | `/api/predict/` | Latest prediction result |
| GET | `/api/results-history/` | All past results |
| GET | `/api/recommendations/` | Latest recommendations |

---

## 🤖 ML Model Details

- **Algorithm**: Gradient Boosting Classifier (`sklearn.ensemble.GradientBoostingClassifier`)
- **Features**: 10 Likert-scale responses (1–5)
- **Classes**: Weak (0), Moderate (1), Strong (2)
- **Score range**: 1.0–3.0 (probability-weighted)
- **Test Accuracy**: ~89%
- **Training data**: 1500 synthetic samples

### Classification

| Score Range | Category |
|-------------|----------|
| 1.0 – 1.67 | Weak |
| 1.67 – 2.33 | Moderate |
| 2.33 – 3.0 | Strong |

---

## 🔐 Security Features

- CSRF protection on all forms
- Password hashing (Django PBKDF2)
- Session-based authentication
- Input validation via DRF serializers
- ORM-only queries (no raw SQL)
- `SESSION_COOKIE_HTTPONLY = True`

---

## 🗄️ Database Schema

```
CustomUser          → id, username, email, password_hash, role, date_joined
QuestionnaireResponse → id, user_id, pq1..pq10, submitted_at
PredictionResult    → id, response_id, score, category, predicted_at
Recommendation      → id, result_id, text
```

---

## ☁️ Deployment (Render/Railway)

1. Set environment variables from `.env` in the platform dashboard
2. Add `gunicorn` to requirements: `pip install gunicorn`
3. Start command: `gunicorn communication_analyzer.wsgi:application`
4. Use an external MySQL database (PlanetScale, Railway MySQL, etc.)
5. Run `python manage.py collectstatic` for static files

---

## 🧪 Running Tests

```bash
# Check Django setup
python manage.py check

# Quick prediction test
python -c "from ml_engine.predict import run_prediction; print(run_prediction([4,5,4,3,5,4,5,4,3,4]))"
```
