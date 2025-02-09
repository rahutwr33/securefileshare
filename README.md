# Secure file share

system requirements:

- docker

## Description

This is a simple project that uses React for the frontend and FastAPI for the backend. It is containerized using Docker.

## Installation

1. Clone the repository

```bash
git clone https://github.com/rahutwr33/secure-file-share.git
```

To run the project, navigate to the root directory and run the following command:

```bash
cd react-fastapi-docker

Set admin credentials in server/.env file for admin user


# Admin Email: abc@yopmail.com
# Admin Password: Admin@123!


docker-compose up --build
```

to access the frontend, navigate to `http://localhost:3000`

Functionality covered:

# https added in server side

Authentication:

- Secure http only cookie
- User can signup and login with email and password and 2 factor authentication uisng email
- User can logout
- admin can login with email and password with 2 factor authentication using email

User Role:

- User can upload file securely
- User can download file file securely
- User can view list of files
- User can share file with other users with expiry date

Admin Role:

- Admin can view all users
- Admin can view all files
- Admin can delete any file
- Admin can delete any file

Share File:

- User can shared files with other users and that user will get link in the email. the link have expiry date
- User can download or view shared files if permission is granted

Security Practice

- MFA using email
- http only cookie authentication
- Rate limiting
- Https url backend
- 2 layer encryption when upload file
- block user for 15 minute attempt if login attempt too much ex 100 time

Test Case

- admin can login with email and password with 2 factor authentication using email
- admin can view all users
- admin can view all files
- admin can delete any file
- admin can delete any file

Coverage 73%

## Name ------------ Stmts ------------ Miss ------------ Cover ------------ Missing

app/config.py ------------ 28 ------------ 0 ------------100%
app/core/**init**.py ------------ 2 ------------ 2 ------------ 0% 1-3
app/database.py ------------ 15 ------------ 4 ------------ 73% 30-34
app/dependencies/**init**.py ------------ 1 ------------ 0 ------------ 100%
app/dependencies/auth.py ------------ 12 ------------ 0 ------------ 100%
app/main.py ------------ 90 ------------ 32 ------------ 64% 53-81, 128, 139-140, 151-161, 166, 171, 193-198, 204-205, 218-222
app/models/file.py ------------ 21 ------------ 0 ------------ 100%
app/models/share.py ------------ 16 ------------ 0 ------------ 100%
app/models/token_blacklist.py ------------ 8 ------------ 0 ------------ 100%
app/models/user.py ------------ 25 ------------ 1 ------------ 96% 34
app/models/verification.py ------------ 14 ------------ 0 ------------ 100%
app/routes/admin.py ------------ 34 ------------ 2 ------------ 94% 54, 88
app/routes/auth.py ------------ 133 ------------ 70 ------------ 47% 69-79, 83, 89, 95-110, 144, 147, 183-222, 252-337, 368
app/routes/user.py ------------ 134 ------------ 23 ------------ 83% 38, 42, 108-110, 125-137, 201-202, 216-221, 239, 244, 249, 291, 303, 327-329
app/schemas/auth.py ------------ 66 ------------ 0 ------------ 100%
app/schemas/file.py ------------ 45 ------------ 3 ------------ 93% 43-45
app/schemas/user.py ------------ 26 ------------ 0 ------------ 100%
app/services/auth_service.py ------------ 49 ------------ 23 ------------ 53% 31-60, 75, 84-95
app/utils/auth.py ------------ 63 ------------ 17 ------------ 73% 32, 61-63, 67, 74, 83, 90-104
app/utils/auth_utils.py ------------ 37 ------------ 16 ------------ 57% 16-26, 30, 36, 51, 53, 55
app/utils/email.py ------------ 25 ------------ 6 ------------ 76% 41-43, 63-65
app/utils/encryption.py ------------ 28 ------------ 16 ------------ 43% 11-13, 23-27, 34-47, 54-64
app/utils/init_admin.py ------------ 35 ------------ 26 ------------ 26% 14-58
app/utils/mfa.py ------------ 15 ------------ 5 ------------ 67% 9, 14-16, 21

---

TOTAL 922 ------------ 246 ------------ 73%
