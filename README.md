# 🍳 Foodgram — Recipe Sharing Platform

A **full-stack web application** to publish, discover, and manage recipes — built with **Django REST API**, **React SPA frontend**, **PostgreSQL**, **Docker**, **Nginx**, and **CI/CD**.

---

## 📌 About the Project

**Foodgram** is a production-ready recipe sharing platform where users can:  

- Publish and edit **recipes**  
- Browse recipes by **tags** or **ingredients**  
- Add recipes to **favorites**  
- Generate a **shopping cart** with ingredients  
- Upload and store **images**  
- Manage authentication and permissions via tokens  

The stack follows best practices with **Dockerized services**, **media/static separation**, and an **Nginx reverse proxy**. A CI/CD pipeline ensures automated build, testing, and deployment.  

---

## 🧰 Tech Stack

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white"/> <img src="https://img.shields.io/badge/DRF-ff1709?style=for-the-badge&logo=django&logoColor=white"/> <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black"/> <img src="https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white"/> <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/> <img src="https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white"/> <img src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white"/>

---

## ✨ Features

- 🟢 **Django REST backend** with modular apps (ingredients, tags, recipes, users)  
- 🎨 **React SPA frontend** with responsive UI  
- 🗄️ **PostgreSQL** for persistent storage  
- 🛡️ **Authentication & permissions** with token-based access  
- 🖼️ **Image upload & media storage**  
- 🏷️ **Tags & ingredient search/filtering**  
- 🛒 **Favorites & shopping cart generation**  
- 🔀 **Nginx reverse proxy** for serving services  
- 🐳 **Dockerized multi-service deployment** with Compose  
- 🔁 **CI/CD pipeline** for automated testing & deployment  

---








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

— or via Docker (if you configured a test target in compose workflow).

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
