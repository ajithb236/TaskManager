# Frontend

Vanilla HTML/JS frontend for task management. Login, register, and manage tasks.

Files:
- index.html - Login/register page
- dashboard.html - Task dashboard
- js/ - JavaScript logic
- css/ - Styles

Run with Docker or local HTTP server.
Access at http://localhost:3000

## Authentication

Token is stored in localStorage after successful login and included in all subsequent API requests via the `Authorization: Bearer <token>` header.
