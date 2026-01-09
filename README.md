# BJJ Training Journal

A personal Brazilian Jiu-Jitsu training journal application for tracking your training sessions, techniques, and progress.

## Features

- User authentication (register/login)
- Create detailed training entries
- Answer predefined questions about each session
- View all your training history
- Mobile-responsive design
- Local hosting for privacy

## Quick Start

### Option 1: Python Development Server

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the backend:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs

### Option 2: Docker (Recommended)

1. **Build and run:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000

## API Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /questions/` - Get all questions
- `POST /entries/` - Create new entry
- `GET /entries/` - Get user's entries
- `GET /entries/{id}` - Get specific entry
- `DELETE /entries/{id}` - Delete entry

## Default Questions

The app comes with 10 predefined questions:
1. What type of training was this?
2. How long was your training session (minutes)?
3. Rate your energy level (1-10)
4. What techniques did you work on?
5. Who did you roll/spar with?
6. What went well today?
7. What do you need to work on?
8. Any injuries or physical notes?
9. Rate your confidence level (1-10)
10. Additional notes

## Testing

Run the test script to verify all endpoints:
```bash
# Start the server first, then:
python test_api.py
```

## Database

- Uses SQLite for simplicity
- Database file: `data/bjj_journal.db`
- Automatic table creation on startup

## Development

### Project Structure
```
bjj_journal/
├── app/
│   ├── models/          # Database models
│   ├── routers/         # API endpoints
│   ├── database.py      # Database config
│   ├── dependencies.py  # Auth utilities
│   └── schemas.py       # Pydantic models
├── frontend/            # React app
├── data/               # SQLite database
├── main.py             # FastAPI app
└── requirements.txt    # Python dependencies
```

### Adding New Questions

Questions are automatically created on startup. To modify:
1. Edit the `default_questions` list in `main.py`
2. Restart the application

## Security Notes

- Change the SECRET_KEY in `dependencies.py` for production
- Uses JWT tokens for authentication
- Passwords are hashed with bcrypt

## Next Steps (Phase 2)

- Photo/video uploads
- Advanced analytics
- Export functionality
- Mobile app (PWA)
- Backup/restore features