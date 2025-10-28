# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **generic FastAPI backend template** with Firebase integration. It provides reusable API endpoints for common features like authentication, messaging, friend management, and push notifications.

### Core Features
- **User Authentication**: Firebase Auth + JWT tokens
- **Messaging System**: Real-time messaging with read receipts
- **Friend Management**: Friend requests, acceptance, relationships
- **Push Notifications**: Firebase Cloud Messaging integration
- **Security**: Password hashing, encryption utilities, JWT validation

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   ├── core/                # Core utilities (Firebase initialization)
│   ├── api/v1/              # API endpoint routers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── users.py         # User management
│   │   ├── messages.py      # Message handling
│   │   ├── friends.py       # Friend relationships
│   │   └── notifications.py # Push notifications
│   ├── models/              # Data models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic layer
│   └── utils/               # Helper functions
└── tests/                   # Unit and integration tests
```

**Key architectural decisions:**
- All API routes are versioned under `/api/v1/`
- Firebase is used for authentication, Firestore for database, and FCM for notifications
- JWT tokens are used for session management
- Encryption utilities are available for sensitive data

## Development Commands

### Backend (FastAPI)
```bash
cd backend

# Install dependencies with uv
uv sync

# Run development server (auto-reload enabled)
uv run uvicorn app.main:app --reload

# Run on specific host/port
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Key Configuration Files

### Backend (.env required)
```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=/path/to/serviceAccountKey.json
SECRET_KEY=your-jwt-secret
ENCRYPTION_KEY=your-encryption-key
DEBUG=False
```

### Important Settings (app/config.py)
- `SECRET_KEY` - JWT token signing key
- `ACCESS_TOKEN_EXPIRE_MINUTES=30` - JWT token expiration
- `ENCRYPTION_KEY` - For encrypting sensitive data

## Development Environment

### Local Development Setup
This project is designed for local development with the following prerequisites:

**Required Tools:**
- **Python 3.11+**: Backend runtime
- **uv**: Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

**Environment Setup:**
1. Clone or use this repository as a template
2. Set up Firebase credentials (see backend/.env.example)
3. Install dependencies:
   ```bash
   cd backend && uv sync
   ```

**Running the Development Server:**
```bash
cd backend && uv run uvicorn app.main:app --reload
```

### Formatters & Linters
- **Python**: Ruff (configured in `pyproject.toml` - 100 char line length)
- **VS Code**: Configure editor settings for auto-formatting on save

## Firebase Integration

The app relies on Firebase services:
- **Authentication**: User sign-up, login, token verification
- **Firestore**: All data storage (users, messages, friends)
- **Cloud Messaging**: Push notifications
- **Storage**: Profile images and media files (optional)

Firebase is initialized in `app/core/firebase.py` and must be configured with a service account JSON file.

## Testing

### Backend Tests
```bash
cd backend
uv run pytest                    # Run all tests
uv run pytest tests/test_auth.py # Run specific test file
uv run pytest -v                 # Verbose output
```

## Common Development Workflows

### Git Branching Strategy
When working on new features or fixes:
1. Always create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Work on your feature branch
3. When ready, create a PR to merge back into main

**Branch naming conventions:**
- `feature/` - New features (e.g., `feature/oauth-integration`)
- `fix/` - Bug fixes (e.g., `fix/jwt-expiration`)
- `refactor/` - Code refactoring (e.g., `refactor/auth-service`)
- `docs/` - Documentation updates (e.g., `docs/api-readme`)

### Adding a New API Endpoint
1. Create router in `backend/app/api/v1/new_feature.py`
2. Define Pydantic schemas in `backend/app/schemas/new_feature.py`
3. Implement business logic in `backend/app/services/new_feature.py`
4. Register router in `backend/app/main.py`:
   ```python
   from app.api.v1 import new_feature
   app.include_router(new_feature.router, prefix="/api/v1/new_feature", tags=["New Feature"])
   ```
5. Add tests in `backend/tests/test_new_feature.py`

### Using This Template for a New Project

When someone wants to use this template for a new project:

1. **Clone the template:**
   ```bash
   git clone <this-repo-url> my-new-project
   cd my-new-project
   ```

2. **Remove git history:**
   ```bash
   rm -rf .git
   git init
   ```

3. **Set up Firebase for the new project:**
   - Create new Firebase project
   - Update `.env` with new credentials

4. **Add project-specific features:**
   - Keep existing auth, messaging, friends, notifications
   - Add new endpoints for project-specific features
   - Example: For a location-based app, add `locations.py`, `map.py`

5. **Update documentation:**
   - Modify README.md with project-specific info
   - Update this CLAUDE.md with new features

## Security Considerations

- All passwords must be hashed before storage
- JWT tokens expire after 30 minutes (configurable in `config.py`)
- Sensitive data should be encrypted using `ENCRYPTION_KEY`
- CORS is currently set to `*` for development - **must restrict in production**
- Never log user credentials or tokens
- Firebase security rules should be configured properly

## API Endpoints Reference

### Authentication (`/api/v1/auth`)
- `POST /signup` - Register new user
- `POST /login` - Login with email/password
- `POST /refresh` - Refresh JWT token
- `POST /logout` - Logout user

### Users (`/api/v1/users`)
- `GET /me` - Get current user profile
- `PUT /me` - Update user profile
- `GET /{user_id}` - Get user by ID
- `DELETE /me` - Delete account

### Messages (`/api/v1/messages`)
- `POST /` - Send message
- `GET /conversations` - List conversations
- `GET /conversations/{user_id}` - Get messages with specific user
- `PUT /{message_id}/read` - Mark message as read

### Friends (`/api/v1/friends`)
- `POST /request` - Send friend request
- `POST /accept` - Accept friend request
- `POST /reject` - Reject friend request
- `GET /list` - List all friends
- `DELETE /{friend_id}` - Remove friend

### Notifications (`/api/v1/notifications`)
- `POST /register` - Register FCM token
- `POST /send` - Send push notification
- `GET /` - Get notification history

## Port Reference
- **8000**: FastAPI backend API

## Notes for Claude Code

When helping developers use this template:

1. **Emphasize reusability**: This is a template meant to be copied and extended
2. **Firebase setup**: Always guide users through Firebase configuration first
3. **Environment variables**: Ensure `.env` is properly configured before running
4. **Adding features**: Show how to add new endpoints while keeping existing ones
5. **Testing**: Encourage writing tests for new features

**Example usage scenario:**
```
User: "I want to build a location-sharing app using this template"

Claude: "Great! This template provides authentication, messaging, and friends functionality.
You can keep all of those and add new location-specific endpoints:

1. Create backend/app/api/v1/locations.py for location tracking
2. Create backend/app/schemas/location.py for location data models
3. Create backend/app/services/locations.py for location business logic
4. Register the router in main.py

The existing auth system will handle user authentication, and you can use the friends
API to manage who can see each user's location."
```
