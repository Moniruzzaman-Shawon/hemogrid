# Hemogrid - Blood Bank Management API

Hemogrid is a RESTful backend service built with Django and Django REST Framework to facilitate smooth connections between blood donors and recipients. It provides user registration with email verification, donor profile management, blood request creation, donation history tracking, and JWT authentication.

---

## Features

- User registration, login, logout with email verification  
- JWT-based authentication and session support  
- Donor profile management (name, age, address, last donation date, availability)  
- Create, view, and accept blood donation requests  
- Dashboard APIs for requests and donation history  
- Search and filter donors and requests by blood group and location  
- Email notifications for account activation and request acceptance  
- Pagination for API lists  
- Debug toolbar enabled for development

---

## Tech Stack

- Python 3.13  
- Django 5.2  
- Django REST Framework  
- Simple JWT for token authentication  
- PostgreSQL / SQLite (default)  
- SMTP (Gmail) for email verification  
- django-filter for filtering APIs  
- django-debug-toolbar for development debugging

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/hemogrid.git
cd hemogrid
```

2. Create and activate a virtual environment:

````bash
python -m venv .hemo_env
source .hemo_env/bin/activate  # Linux/Mac
.hemo_env\Scripts\activate     # Windows
````

3. Install dependencies:
````bash
pip install -r requirements.txt
````
4. Create a .env file in the project root with the following content:
```
env
    DJANGO_SECRET_KEY=your-secret-key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    EMAIL_HOST_USER=your_email@gmail.com
    EMAIL_HOST_PASSWORD=your_email_password_or_app_password
```


5. Apply migrations:
````bash
python manage.py migrate
````

6. Create a superuser (admin):
````bash
python manage.py createsuperuser
````

7. Run the development server:
````bash
python manage.py runserver
````


| Endpoint                          | Method       | Description                          | Auth Required |
|----------------------------------|--------------|------------------------------------|---------------|
| /api/auth/register/               | POST         | Register new user (with email verification) | No            |
| /api/auth/login/                  | POST         | Login and get JWT token             | No            |
| /api/auth/logout/                 | POST         | Logout user                        | Yes           |
| /api/donor-profile/              | GET, PUT     | Get or update donor profile details | Yes           |
| /api/blood-requests/              | GET          | List active blood requests          | Yes           |
| /api/blood-requests/create/       | POST         | Create new blood request            | Yes           |
| /api/blood-requests/<id>/accept/  | POST         | Accept a blood request              | Yes           |
| /api/donation-history/            | GET          | View donor's donation history       | Yes           |


## Notes
+ Use JWT tokens for authenticated requests in the Authorization header with prefix JWT.

+ Email verification link is sent on registration; clicking it activates the account.

+ Donors can create and accept requests; donation history tracks accepted donations.

+ Search and filtering features available on donor and request lists.

+ Debug toolbar enabled in development (DEBUG=True).

## Deployment
+ Set DEBUG=False in .env for production.

+ Add your domain to ALLOWED_HOSTS.

+ Use a production-ready server like Gunicorn or uWSGI.

+ Configure HTTPS and static file hosting (e.g., via Nginx).

+ Secure your email credentials and secret key.


## Contact

Created by **Moniruzzaman Shawon**  
Email: [m.zaman.djp@gmail.com](mailto:m.zaman.djp@gmail.com)
