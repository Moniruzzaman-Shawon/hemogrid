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
