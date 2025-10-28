# Generic API Template

A reusable FastAPI backend template with Firebase integration, providing authentication, messaging, friend management, and push notifications out of the box.

---

## 🎯 Overview

This is a production-ready FastAPI backend that can be used as a foundation for various applications. It includes common features like user authentication, real-time messaging, friend relationships, and push notifications.

### Key Features

- **Authentication**: Firebase Authentication integration with JWT tokens
- **User Management**: User profiles, settings, and account management
- **Messaging**: Real-time messaging system with read receipts
- **Friend System**: Friend requests, acceptance, and relationship management
- **Push Notifications**: Firebase Cloud Messaging integration
- **Security**: Password hashing, JWT validation, encryption utilities

---

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **Firebase** - Authentication, Firestore database, Cloud Messaging
- **uv** - Fast Python package manager
- **Pydantic** - Data validation and settings management
- **Python 3.11+** - Modern Python features

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Configuration settings
│   ├── api/
│   │   ├── dependencies.py      # Shared dependencies
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── users.py         # User management endpoints
│   │       ├── messages.py      # Messaging endpoints
│   │       ├── friends.py       # Friend management endpoints
│   │       └── notifications.py # Push notification endpoints
│   ├── core/
│   │   └── firebase.py          # Firebase initialization
│   ├── schemas/
│   │   ├── auth.py              # Authentication schemas
│   │   ├── user.py              # User schemas
│   │   ├── message.py           # Message schemas
│   │   ├── friend.py            # Friend schemas
│   │   └── notification.py      # Notification schemas
│   ├── services/
│   │   ├── auth.py              # Authentication business logic
│   │   ├── users.py             # User management logic
│   │   ├── messages.py          # Messaging logic
│   │   ├── friends.py           # Friend management logic
│   │   └── notifications.py     # Notification logic
│   └── utils/
│       ├── jwt.py               # JWT token utilities
│       ├── security.py          # Security helpers
│       └── encryption.py        # Encryption utilities
├── tests/                       # Unit and integration tests
├── pyproject.toml               # Python dependencies
├── uv.lock                      # Dependency lock file
└── .env.example                 # Environment variables template
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**: [Download](https://www.python.org/)
- **uv**: Python package manager
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Firebase Project**: Create at [Firebase Console](https://console.firebase.google.com/)

### 1. Clone or Use This Template

```bash
# If using as a template for a new project
git clone https://github.com/yourusername/backend-api-template.git my-new-project
cd my-new-project/backend
```

### 2. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project (or use existing)
3. Generate a service account key:
   - Project Settings → Service Accounts → Generate New Private Key
4. Save the JSON file as `serviceAccountKey.json` in the `backend/` directory
5. Note your Firebase Project ID

### 3. Install Dependencies

```bash
cd backend
uv sync
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Application
APP_NAME=Generic API
DEBUG=False

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json

# JWT
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Encryption
ENCRYPTION_KEY=your-encryption-key  # Generate with: openssl rand -hex 32
```

### 5. Run Development Server

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

---

## 📡 API Endpoints

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

---

## 🔧 Development

### Running Tests

```bash
cd backend
uv run pytest
```

### Code Formatting

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .
```

### Adding New Features

1. **Create new API endpoint** in `backend/app/api/v1/your_feature.py`
2. **Define schemas** in `backend/app/schemas/your_feature.py`
3. **Implement business logic** in `backend/app/services/your_feature.py`
4. **Register router** in `backend/app/main.py`:
   ```python
   from app.api.v1 import your_feature
   app.include_router(your_feature.router, prefix="/api/v1/your_feature", tags=["Your Feature"])
   ```

---

## 🔐 Security

### Best Practices

- All passwords are hashed using bcrypt
- JWT tokens expire after 30 minutes (configurable)
- Sensitive data can be encrypted using the encryption utility
- Firebase handles authentication securely
- CORS is set to `*` for development - **restrict in production**

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure CORS to specific origins
- [ ] Use HTTPS for all communications
- [ ] Rotate `SECRET_KEY` and `ENCRYPTION_KEY` regularly
- [ ] Enable Firebase security rules
- [ ] Set up monitoring and logging
- [ ] Review and restrict API rate limits

---

## 🌐 Deployment

### Using Docker (Recommended)

```bash
# Build image
docker build -t my-api .

# Run container
docker run -p 8000:8000 --env-file .env my-api
```

### Using Cloud Run (Google Cloud)

```bash
gcloud run deploy my-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Using Railway/Render

1. Connect your GitHub repository
2. Set environment variables from `.env`
3. Deploy automatically on push

---

## 📖 Usage Example

### Using This Template for Your Project

When starting a new project (e.g., "PopMatch"), you can use this template:

```bash
# Clone the template
git clone https://github.com/yourusername/backend-api-template.git popmatch
cd popmatch

# Remove git history and start fresh
rm -rf .git
git init

# Add your project-specific features
# Example: Add new endpoints for your app
# backend/app/api/v1/pops.py
# backend/app/api/v1/map.py

# Commit and push to your new repo
git add .
git commit -m "Initial commit from backend-api-template"
git remote add origin https://github.com/yourusername/popmatch.git
git push -u origin main
```

### Integrating with Claude Code

When working with Claude Code on a new project, provide the context:

```
I'm building a new app called PopMatch. Please use this backend API template as a foundation:
https://github.com/yourusername/backend-api-template

The template already includes authentication, messaging, friends, and notifications.
I need to add the following new features:
- Pop creation and management API
- Map-based search API
- ...
```

---

## 🤝 Contributing

This is a template repository. Feel free to:
- Fork and customize for your needs
- Submit PRs for general improvements
- Open issues for bugs or feature requests

---

## 📝 License

MIT License - Use freely for personal and commercial projects

---

## 🙏 Credits

Built with FastAPI, Firebase, and modern Python best practices.

---

**Last Updated**: 2025-10-28
**Version**: 1.0.0
