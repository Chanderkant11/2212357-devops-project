# YOUR_REG_NO — DevOps Fundamentals Final Project

**Student:** Your Full Name
**Registration Number:** YOUR_REG_NO
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

### Prerequisites
- Docker Desktop (or Docker Engine + Docker Compose plugin)
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REGNUM-devops-project.git
cd YOUR_REGNUM-devops-project

# 2. Create your .env file from the template
cp .env.example .env
# Edit .env with your preferred credentials (or leave defaults)

# 3. Build and start both containers
docker compose up --build

# 4. Verify the app is running
curl http://localhost:8000/health
# Expected: {"status":"ok","db":"connected","student":"YOUR_REG_NO"}
```

The API is now live at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

---

## Running Tests Locally

```bash
# Install dependencies (in a virtual environment recommended)
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run all tests
pytest app/tests/ -v

# Run linter
flake8 app/ --max-line-length=100
```

---

## AWS EC2 Deployment (Manual First-Time Setup)

### 1. Launch EC2 Instance
- AMI: Ubuntu Server 22.04 LTS
- Instance type: t2.micro (free tier)
- Security Group inbound rules:
  - Port 22 (SSH) — your IP
  - Port 8000 (HTTP) — 0.0.0.0/0

### 2. Install Docker on EC2

```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

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

### 3. Clone the Repo on EC2

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REGNUM-devops-project.git ~/app
cd ~/app
cp .env.example .env
# Fill in strong production values in .env
```

### 4. Set GitHub Secrets

In your GitHub repo → Settings → Secrets → Actions, add:

| Secret | Value |
|--------|-------|
| `EC2_HOST` | Your EC2 public IP |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | Contents of your `.pem` private key |
| `REPO_URL` | `https://github.com/YOUR_USERNAME/YOUR_REGNUM-devops-project.git` |
| `POSTGRES_USER` | e.g. `postgres` |
| `POSTGRES_PASSWORD` | Strong password |
| `POSTGRES_DB` | e.g. `studentsdb` |

### 5. Trigger First Deploy

```bash
git commit --allow-empty -m "chore: trigger initial CD deploy"
git push origin main
```

Watch the Actions tab — the CD job will SSH into EC2 and start the containers automatically.

---

## CI/CD Pipeline

### CI (`.github/workflows/ci.yml`)
Triggers on every push and pull request to any branch.
1. Checks out code
2. Installs Python dependencies
3. Runs `flake8` linter (max line length 100)
4. Runs `pytest` with SQLite in-memory test database

### CD (`.github/workflows/cd.yml`)
Triggers only on push to `main`.
1. SSHs into EC2 using stored secrets
2. Pulls latest code via `git pull`
3. Writes `.env` from GitHub Secrets
4. Runs `docker compose -f docker-compose.prod.yml up --build -d`
5. Confirms health endpoint returns 200

---

## Git Workflow

This project follows a feature-branch workflow:

```
main          ← protected, auto-deploys to EC2
  └── feat/docker-setup
  └── feat/api-endpoints
  └── feat/ci-pipeline
  └── feat/cd-pipeline
  └── docs/readme
```

Each feature branch is merged into `main` via a Pull Request after CI passes.

---

## Project Structure

```
YOUR_REGNUM-devops-project/
├── app/
│   ├── main.py               ← FastAPI routes & endpoints
│   ├── database.py           ← SQLAlchemy engine & session
│   ├── models.py             ← Student ORM model
│   └── tests/
│       ├── conftest.py       ← pytest fixtures, SQLite test DB
│       ├── test_health.py    ← /health endpoint tests
│       └── test_students.py  ← POST & GET /students tests
├── Dockerfile                ← Multi-stage, non-root user
├── docker-compose.yml        ← Local development
├── docker-compose.prod.yml   ← Production (EC2)
├── requirements.txt
├── .env.example              ← Template — never commit real .env
├── .gitignore
├── .dockerignore
├── .github/
│   └── workflows/
│       ├── ci.yml            ← Lint + test on every push/PR
│       └── cd.yml            ← Auto-deploy to EC2 on main push
└── README.md
```
