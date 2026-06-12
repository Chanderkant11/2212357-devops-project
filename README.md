# 2212357 — DevOps Fundamentals Final Project

**Student:** Chanderkant
**Registration Number:** 2212357
**Course:** DevOps Fundamentals
**Live URL:** `http://<YOUR_EC2_IP>:8000`

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        GitHub                                │
│  push → main  ──► CI (lint + test) ──► CD (SSH to EC2)      │
└──────────────────────────────┬──────────────────────────────┘
                               │ SSH
                               ▼
┌──────────────────── AWS EC2 t2.micro ───────────────────────┐
│                                                              │
│   ┌─────────────────────┐     ┌──────────────────────────┐  │
│   │   FastAPI + Uvicorn  │────►│  PostgreSQL 15 container │  │
│   │   (port 8000)        │     │  (port 5432, named vol.) │  │
│   └─────────────────────┘     └──────────────────────────┘  │
│           Docker Compose (prod)                              │
└──────────────────────────────────────────────────────────────┘
```

| Component | Technology |
|-----------|-----------|
| Web Service | FastAPI + Uvicorn on port 8000 |
| Database | PostgreSQL 15 with named Docker volume |
| CI Pipeline | GitHub Actions → flake8 + pytest |
| CD Pipeline | GitHub Actions → SSH → docker compose up |
| Cloud Server | AWS EC2 t2.micro (Ubuntu 22.04) |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Returns status, DB connection, and registration number |
| POST | `/students` | Create a new student record |
| GET | `/students` | List all student records |
| GET | `/students/{id}` | Get a single student by ID (404 if not found) |

### Example Requests

```bash
# Health check
curl http://localhost:8000/health

# Create a student
curl -X POST http://localhost:8000/students \
  -H "Content-Type: application/json" \
  -d '{"name": "Ali Hassan", "email": "ali@example.com", "course": "DevOps"}'

# List all students
curl http://localhost:8000/students

# Get student by ID
curl http://localhost:8000/students/1
```

---

## Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/Chanderkant11/2212357-devops-project.git
cd 2212357-devops-project

# 2. Create your .env file
cp .env.example .env

# 3. Build and start containers
docker compose up --build

# 4. Test it
curl http://localhost:8000/health
```

---

## GitHub Secrets Required

Go to your GitHub repo → **Settings → Secrets → Actions** and add:

| Secret Name | Value |
|-------------|-------|
| `EC2_HOST` | Your EC2 public IP address |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | Full contents of your `.pem` private key file |
| `REPO_URL` | `https://github.com/Chanderkant11/2212357-devops-project.git` |
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_PASSWORD` | Any strong password |
| `POSTGRES_DB` | `studentsdb` |

---

## EC2 First-Time Setup

```bash
# SSH into your EC2
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Install Docker
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Allow ubuntu user to run Docker without sudo
sudo usermod -aG docker ubuntu
newgrp docker
```

---

## Running Tests Locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest app/tests/ -v
flake8 app/ --max-line-length=100
```

---

## Project Structure

```
2212357-devops-project/
├── app/
│   ├── __init__.py
│   ├── main.py               ← FastAPI routes & endpoints
│   ├── database.py           ← SQLAlchemy engine & session
│   ├── models.py             ← Student ORM model
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py       ← pytest fixtures, SQLite test DB
│       ├── test_health.py    ← /health endpoint tests
│       └── test_students.py  ← POST & GET /students tests
├── Dockerfile
├── docker-compose.yml        ← Local development
├── docker-compose.prod.yml   ← Production (EC2)
├── requirements.txt
├── .env.example
├── .gitignore
├── .dockerignore
├── .github/
│   └── workflows/
│       ├── ci.yml            ← Lint + test on every push/PR
│       └── cd.yml            ← Auto-deploy to EC2 on main push
└── README.md
```
