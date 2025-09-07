# 🛒 AI-Driven Digital Product Store (Django + SQLite/MySQL)

A ready-to-run **digital products marketplace** built with Django.  
This project allows users to browse, purchase, and securely download digital files.  
Enhanced with **AI-powered product recommendations** and designed for **real payment gateway integration**.  

---

## 🚀 Features
- 📦 Digital products with downloadable files  
- 🏷️ Categories & search functionality  
- 🛒 Cart and checkout flow  
- 🔒 Secure downloads after purchase  
- 📑 Orders & order history  
- 🤖 AI-driven product recommendations (content-based filtering / collaborative filtering)  
- 💳 Stripe test payment integration  
- 🎨 Responsive Bootstrap UI  

---

## 🛠️ Tech Stack
- **Backend:** Django (Python)  
- **Database:** SQLite (default), MySQL optional  
- **Frontend:** HTML, CSS, Bootstrap  
- **AI/ML:** Recommendation Engine (scikit-learn, Pandas, NumPy)  
- **Payments:** Stripe (test mode)  

---

## ⚡ Quick Start

```bash
# 1) Create and activate a virtual environment
python -m venv env

# Windows
env\Scripts\activate

# macOS/Linux
source env/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Create Django project tables
python manage.py makemigrations
python manage.py migrate

# 4) Create superuser for admin
python manage.py createsuperuser

# 5) (Optional) Load sample categories & products (no files attached)
python manage.py loaddata initial_data.json

# 6) Run server
python manage.py runserver
