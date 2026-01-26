# CodeSage 🧠

**AI-Assisted Debugger and Learning Platform**

Empowering the next generation of smart developers. Turn bugs into breakthroughs.

## Features

- 🤖 **AI-Powered Debugging Assistant** - Fix code instantly with intelligent explanations
- 📝 **Step-by-Step Solutions** - Understand why bugs happen, not just what they are
- 🌐 **Full-Stack Support** - JavaScript, Python, Java, C#, and more
- 📚 **Learn While You Debug** - Every error becomes a lesson

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **JWT** - Authentication

### Frontend
- **React** - UI library
- **React Router** - Navigation
- **Axios** - HTTP client
- **Vite** - Build tool

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL

### Backend Setup

1. Create and activate virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_PASSWORD=your_password
DATABASE_NAME=postgres
DATABASE_USERNAME=postgres
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Run the backend:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` with docs at `/docs`.

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## Project Structure

```
codesage/
├── app/                    # Backend (FastAPI)
│   ├── api/               # API routes
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── router.py
│   ├── db/                # Database
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── utils/             # Utilities
│   ├── config.py          # Settings
│   └── main.py            # App entry point
├── frontend/              # Frontend (React)
│   └── src/
│       ├── components/    # React components
│       ├── pages/         # Page components
│       └── services/      # API services
├── .env                   # Environment variables
└── requirements.txt       # Python dependencies
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login and get token

### Users
- `GET /api/v1/users/me` - Get current user info

## License

MIT License - feel free to use for learning and personal projects.