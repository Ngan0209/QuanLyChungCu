# QuanLyChungCu

## Technologies
- Backend: Python, Django, Django REST Framework
- Database: MySQL
- Deployment: PythonAnywhere
- Tools: Git, Postman

## Features
- Resident management (create, update, delete, search)
- Apartment and service management
- Billing & payment tracking
- Role-based access (Admin, Resident)
- REST API for integration

## Installation
1. Clone the repository
2. Create virtual environment & install dependencies: pip install -r requirements.txt
3. In file setting.py fill in the information of the MySQL account
   DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '<NameDatabase>',
        'USER': '<UserName>',
        'PASSWORD': '<Passworld>',
        'HOST': ''
    }
  }
4. Create a database with the same name as the one entered above
5. Run migrations: python manage.py migrate
6. Create an admin account: python manage.py createsuperuser
7. Start server: python manage.py runserver

## Demo Api
- Python Anywhere: https://chulengan0209.pythonanywhere.com/
