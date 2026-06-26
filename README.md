# TaskLedger

A full-stack task management web app: create, update, and track tasks behind
user accounts, with a responsive board UI and a JSON API underneath it.

## Features

- **User authentication & authorization** — register/login with hashed
  passwords (Werkzeug), session-based auth (Flask-Login). Every task is
  scoped to its owner; the API never returns another user's tasks.
- **CRUD for tasks** — create, read, update, delete via a REST JSON API
  (`/api/tasks`), consumed by the frontend with `fetch`.
- **Dynamic, API-driven UI** — the board re-renders from API responses
  without full page reloads, and polls every 15s so changes from another
  tab/device show up automatically. A note in `app.js` shows where to plug
  in WebSockets/SSE for true real-time push if you want to extend it.
- **Responsive design** — single-column board on phones, three columns
  (To do / In progress / Done) from tablet width up.

## Project structure

```
taskmanager/
├── app.py              # app factory, page routes, auth
├── api.py               # /api/tasks REST endpoints (CRUD)
├── models.py             # User, Task SQLAlchemy models
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## Run it locally

```bash
cd taskmanager
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000**, create an account, and start adding tasks.
A SQLite database is created automatically at `instance/taskledger.db`.

## API reference

| Method | Endpoint            | Description                  |
|--------|---------------------|-------------------------------|
| GET    | `/api/tasks`         | List the current user's tasks (optional `?status=` filter) |
| POST   | `/api/tasks`         | Create a task                |
| GET    | `/api/tasks/<id>`    | Get one task                 |
| PUT    | `/api/tasks/<id>`    | Update a task                |
| DELETE | `/api/tasks/<id>`    | Delete a task                |

All endpoints require an active login session.

## Pushing to GitHub

```bash
cd taskmanager
git init
git add .
git commit -m "Initial commit: task management app"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

(Create the empty repo on GitHub first, then run the commands above from
inside this folder.)

## Ideas for extending it

- Swap the 15s poll in `app.js` for a WebSocket (Flask-SocketIO) connection
  for instant multi-client updates.
- Add drag-and-drop between columns to change status.
- Add due-date email/reminder notifications.
