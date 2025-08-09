# 🍳 Foodgram — React + Django + Docker
A full-stack platform to publish, discover, and manage recipes.
Backend (Django REST), frontend (React SPA), PostgreSQL, Nginx reverse proxy, Dockerized multi-service setup, and CI/CD via GitHub Actions.









## 📌 Description
Foodgram lets users publish recipes, browse by tags/ingredients, manage favorites, and build a shopping list.
The stack is production-oriented: containerized services, static/media separation, and a reverse proxy in front.

Key features

🟢 Django REST backend (clean apps: ingredients, tags, recipes, users)

🎨 React SPA frontend (modern, responsive UX)

🗄️ PostgreSQL persistence

🛡️ Authentication & permissions (token-based; see API docs in your build)

🖼️ Image uploads (media volume)

🏷️ Tags & ingredients, search and filtering

🛒 Favorites & shopping cart generation

🔀 Nginx reverse proxy in front of services

🐳 Dockerized multi-service deployment (compose)

🔁 CI/CD pipeline (build, test, push images, optional deploy)

## 🧰 Tech Stack

[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?logo=django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-API-ff1709?logo=django)](https://www.django-rest-framework.org/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB?logo=react)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-336791?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker)](https://www.docker.com/)
[![Nginx](https://img.shields.io/badge/Nginx-reverse--proxy-009639?logo=nginx)](https://nginx.org/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-2088FF?logo=githubactions)](https://github.com/features/actions)








### 🚀 Quick Start (Docker, production-like)
Clone the repo
```
git clone https://github.com/Riadnov-dev/foodgram-project-react.git
```

Enter the project directory
```
cd foodgram-project-react
```

Create a .env in the project root (see below)

Build and run all services
```
docker-compose up -d --build
```

Open the app (served by Nginx gateway)
```
Frontend → http://localhost:7000
API base → http://localhost:7000/api/
```

Stop the stack
```
docker-compose down
```

### 🔐 Environment (.env example)
```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_pass
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET_KEY=your_secret_key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

(Adjust/add CORS/CSRF variables if your setup requires them.)

### 🌱 Initial Data (ingredients import)
The backend includes a management command to import ingredients from JSON.
In this compose setup ingredients.json is mounted into the backend at /app/ingredients.json.

Run migrations
```
docker-compose exec backend python manage.py migrate
```

Import ingredients
```
docker-compose exec backend python manage.py import_ingredients /app/ingredients.json
```

Collect static (if needed)
```
docker-compose exec backend python manage.py collectstatic --noinput
```

Create superuser (optional)
```
docker-compose exec backend python manage.py createsuperuser
```

### 📚 API
Authentication is token-based (implementation depends on your build; see API docs).
Common endpoints include:
```

GET /api/recipes/ — list recipes

POST /api/recipes/ — create recipe

GET /api/ingredients/ — list/search ingredients

GET /api/tags/ — list tags

POST /api/recipes/{id}/favorite — add to favorites

GET /api/recipes/download_shopping_cart — generate shopping list
```

Auth endpoints — see your configured auth (e.g., token/JWT)

If Swagger/Redoc is enabled in your build, the docs are typically served under /api/docs/ or /redoc/.

### 🧪 Tests

From the backend directory (local)
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

—or via Docker (if you configured a test target in compose workflow).

### 🐳 Images & CI/CD
Docker images (as configured in compose):
```

Backend: nriadnov29/foodgram_backend:latest

Frontend: nriadnov29/foodgram_frontend:latest

Gateway (Nginx): nriadnov29/foodgram_gateway:latest

GitHub Actions (on push) typically:

run backend/frontend tests
```

build images and push to Docker Hub

optionally deploy to a remote host if secrets are present

Workflow config: .github/workflows/main.yml (or your workflow file)

### 📂 Project Structure
```
backend/
├─ foodgram/ (project: settings, urls, utils, wsgi, asgi)
├─ ingredients/ (management, filters, models, serializers, views, urls, migrations)
├─ recipes/ (filters, models, permissions, pagination, serializers, views, urls, migrations, exception_handler)
├─ tags/ (forms, validators, models, serializers, views, urls, migrations)
├─ users/
├─ requirements.txt, Dockerfile, manage.py

frontend/ — React SPA (public, src, Dockerfile)
infra/ — infra configs (if used)
postman-collection/ — API collection (optional)
docker-compose.yml, docker-compose.production.yml
.nginx/ or nginx/ — proxy config (Dockerfile, nginx.conf)
.gitignore, pytest.ini, setup.cfg, etc.

```

### 👤 Author

Nikita Riadnov

GitHub: https://github.com/Riadnov-dev
