# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BUBBLE (Be Unseen, Be Loved, Everywhere) is a privacy-focused messaging and location-sharing application. It enables healthy communication boundaries while maintaining trust between close contacts through status-based location sharing instead of precise GPS tracking.

### Core Principles
- **User-controlled messaging**: Messages only appear when users choose to view them
- **Privacy-first location sharing**: Location status (home/work/moving/unknown) instead of exact coordinates
- **Trust enforcement**: 90-day restriction on changing registered addresses to prevent deception
- **Delayed near-miss notifications**: Past location proximity detected through encrypted daily batch processing

## Monorepo Structure

```
BUBBLE/
├── backend/              # FastAPI REST API (Python 3.11+)
├── mobile/               # React Native mobile app (Expo)
├── web/                  # Next.js 14 web admin interface
├── shared/               # Shared TypeScript types and constants
└── firebase/             # Firebase security rules and config
```

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

### Mobile (React Native + Expo)
```bash
cd mobile

# Install dependencies
npm install

# Start Expo development server
npm start

# Run on specific platforms
npm run android
npm run ios
npm run web

# Type checking
npm run type-check

# Lint and format
npm run lint
npm run format
```

### Web (Next.js)
```bash
cd web

# Install dependencies
npm install

# Run development server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type checking
npm run type-check

# Lint
npm run lint
```

## Architecture

### Backend Architecture (app/main.py)

The FastAPI backend follows a modular structure:

```
app/
├── main.py              # Application entry point, router registration
├── config.py            # Environment configuration (Firebase, JWT, location settings)
├── core/                # Core utilities (Firebase initialization)
├── api/v1/              # API endpoint routers
│   ├── auth.py          # Authentication endpoints
│   ├── users.py         # User management
│   ├── messages.py      # Message handling with visibility control
│   ├── locations.py     # Location status tracking
│   ├── friends.py       # Friend relationships and trust levels
│   ├── notifications.py # Push notifications
│   └── near_miss.py     # Near-miss detection batch processing
├── models/              # Data models
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic layer
├── tasks/               # Background tasks (near-miss detection)
└── utils/               # Helper functions
```

**Key architectural decisions:**
- All API routes are versioned under `/api/v1/`
- Firebase is used for authentication, Firestore for database, and FCM for notifications
- Location data is encrypted before storage using the `ENCRYPTION_KEY` from config
- The 90-day address change lock is enforced at the service layer
- Near-miss detection runs as a scheduled batch job, not real-time

### Mobile App Architecture (Expo Router)

The mobile app uses Expo Router for file-based routing:

```
mobile/
├── app/                 # Expo Router pages (file-based routing)
│   ├── tabs/            # Tab navigation (home, messages, friends)
│   ├── auth/            # Login/signup screens
│   ├── chat/            # Chat conversation screens
│   ├── location/        # Location status management
│   └── profile/         # User profile and settings
├── src/
│   ├── components/      # Reusable UI components
│   ├── hooks/           # Custom React hooks (useAuth, useLocation)
│   ├── services/        # API clients (axios), Firebase SDK integration
│   ├── store/           # Zustand state management
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Helper functions (encryption, location)
│   └── constants/       # App constants (colors, config)
└── assets/              # Images, icons, fonts
```

**Key features:**
- Background location tracking using `expo-location` and `expo-task-manager`
- Local authentication with `expo-local-authentication` (biometric auth for "surveillance mode")
- Location status calculation based on registered addresses from backend
- Message visibility controlled client-side until user explicitly reveals
- Encrypted location history stored locally for 7 days

### Web App Architecture (Next.js App Router)

```
web/src/
├── app/                 # Next.js 14 App Router pages
├── components/          # React components
├── lib/                 # Utilities (Firebase, API clients)
└── types/               # TypeScript types
```

The web app is primarily for administrative dashboards and special address change approval workflows.

### Shared Code

```
shared/
├── types/               # TypeScript interfaces shared across mobile/web
└── constants/           # Shared constants (status types, trust levels)
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
- `HOME_RADIUS_METERS=200` - Radius for home status detection
- `WORK_RADIUS_METERS=500` - Radius for work status detection
- `LOCATION_CHANGE_LOCK_DAYS=90` - Address change restriction period
- `NEAR_MISS_RADIUS_METERS=50` - Proximity threshold for near-miss
- `NEAR_MISS_TIME_DIFF_MINUTES=30` - Time window for near-miss
- `LOCATION_HISTORY_RETENTION_DAYS=7` - How long to keep location history

## Development Environment

### Local Development Setup
This project is designed for local development with the following prerequisites:

**Required Tools:**
- **Python 3.11+**: Backend runtime
- **Node.js 18+**: Frontend/mobile runtime
- **uv**: Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **npm**: Node.js package manager (comes with Node.js)

**Environment Setup:**
1. Clone the repository
2. Set up Firebase credentials (see backend/.env.example)
3. Install dependencies:
   ```bash
   # Backend
   cd backend && uv sync

   # Mobile
   cd mobile && npm install

   # Web
   cd web && npm install
   ```

**Running the Development Servers:**
```bash
# Backend (port 8000)
cd backend && uv run uvicorn app.main:app --reload

# Mobile (Expo dev server)
cd mobile && npm start

# Web (port 3000)
cd web && npm run dev
```

### Formatters & Linters
- **Python**: Ruff (configured in `pyproject.toml` - 100 char line length)
- **TypeScript**: Prettier (format on save enabled)
- **VS Code**: Configure editor settings for auto-formatting on save

## Firebase Integration

The app relies heavily on Firebase services:
- **Authentication**: User sign-up, login, token verification
- **Firestore**: All data storage (users, messages, locations, friends)
- **Cloud Messaging**: Push notifications for messages and status changes
- **Storage**: Profile images and media files

Firebase is initialized in `app/core/firebase.py` and must be configured with a service account JSON file.

## Location & Privacy Features

### Location Status Types
- **🏠 Home (green)**: Within HOME_RADIUS_METERS of registered home address
- **🏢 Work (blue)**: Within WORK_RADIUS_METERS of registered work address
- **🚶 Moving (yellow)**: Outside registered areas, speed > 5km/h
- **📍 Custom (purple)**: Optional user-defined locations (gym, café)
- **❓ Unknown (gray)**: Location services off or outside all registered areas

### Address Change Restriction
Registered home/work addresses cannot be changed for 90 days to maintain trust. Special exceptions require:
1. User initiates "Special Change Request" with reason (moving, job change, etc.)
2. Optional document upload for verification
3. Admin approval through web interface (24-48 hour review)
4. Change notification sent to close friends (trust level 5)

### Near-Miss Detection
- Runs as **scheduled batch job** (daily at midnight), not real-time
- Compares encrypted location history between friends
- Only detects proximity for users with "close friend" relationship
- Notifications delivered next morning to avoid real-time tracking
- Location history automatically deleted after 7 days

## Testing

### Backend Tests
```bash
cd backend
uv run pytest                    # Run all tests
uv run pytest tests/test_auth.py # Run specific test file
uv run pytest -v                 # Verbose output
```

### Mobile Tests
Test configuration not yet implemented. When added, use standard React Native testing with Jest.

## Common Development Workflows

### Adding a New API Endpoint
1. Create router in `backend/app/api/v1/new_feature.py`
2. Define Pydantic schemas in `backend/app/schemas/new_feature.py`
3. Implement business logic in `backend/app/services/new_feature.py`
4. Register router in `backend/app/main.py`
5. Update mobile API client in `mobile/src/services/api.ts`

### Adding a New Location Status Type
1. Update `LocationStatus` enum in `shared/types/`
2. Modify status calculation logic in `backend/app/services/locations.py`
3. Update mobile UI in `mobile/src/components/LocationStatusBadge.tsx`
4. Add new status detection logic in `mobile/src/utils/location.ts`

### Implementing a Background Task
1. Create task in `backend/app/tasks/`
2. Use Firebase Cloud Functions or cron job to trigger
3. Ensure proper error handling and logging
4. Consider impact on encrypted data (decryption in memory only)

## Security Considerations

- All location data must be encrypted before storage using `ENCRYPTION_KEY`
- JWT tokens expire after 30 minutes (configurable in `config.py`)
- Biometric authentication required for "surveillance mode" in mobile app
- CORS is currently set to `*` for development - **must restrict in production**
- Never log decrypted location data or user credentials
- Address change audit trail must be immutable (append-only logs)

## Port Reference
- **8000**: FastAPI backend API
- **3000**: Next.js web interface
- **19000**: Expo dev server (Metro bundler)
- **19001**: Expo dev server (iOS)
- **19002**: Expo dev server (web)
