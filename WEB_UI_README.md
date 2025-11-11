# ConversationIQ Web UI

Full-stack web application for ConversationIQ with React frontend and FastAPI backend.

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (Database ORM)
- WebSocket support for real-time updates
- CORS enabled for local development

**Frontend:**
- React 18 with Hooks
- Vite (build tool)
- TailwindCSS (styling)
- React Query (data fetching)
- React Router v6 (navigation)
- Recharts (data visualization)
- Axios (HTTP client)

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Git

### Installation & Running

#### Option 1: Using Startup Scripts (Recommended)

**On Linux/Mac:**
```bash
# Terminal 1 - Start Backend
chmod +x start-backend.sh
./start-backend.sh

# Terminal 2 - Start Frontend
chmod +x start-frontend.sh
./start-frontend.sh
```

**On Windows:**
```cmd
REM Terminal 1 - Start Backend
start-backend.bat

REM Terminal 2 - Start Frontend
start-frontend.bat
```

#### Option 2: Manual Setup

**Backend:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-web.txt

# Initialize database
python -c "from src.storage.database import init_database; init_database()"

# Start backend server
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access the Application

- **Frontend UI:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/api/docs
- **Alternative API Docs:** http://localhost:8000/api/redoc

## Features

### 🏠 Dashboard
- Overview statistics (agents, tests, evaluations)
- Tests by status breakdown
- Recent tests list
- Quick action cards

### 👥 Agent Management
- List all virtual agents
- Create custom agents with demographics and personality traits
- AI-powered agent generation based on task description
- Delete agents
- View agent details (expertise, occupation, traits)

### ⚙️ API Configuration
- Add chat API endpoints
- Configure API keys securely
- Test API connections
- Manage multiple API configurations
- Delete configurations

### 📝 Test Management
- Create comprehensive tests (multi-step wizard)
- Select API configuration
- Choose multiple agents for evaluation
- Upload questions (JSON, CSV, TXT)
- View test details
- Run tests
- Monitor test status

### 📊 Results & Analytics
- View detailed test results
- Rating statistics with charts
- Common positive feedback
- Common concerns/dislikes
- Top improvement suggestions
- Export results (JSON, CSV, Full Report)
- Visualizations with Recharts

## API Endpoints

### Agents
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create agent
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent
- `POST /api/agents/generate` - Generate agents

### API Configs
- `GET /api/api-configs` - List all configurations
- `POST /api/api-configs` - Create configuration
- `GET /api/api-configs/{id}` - Get configuration
- `PUT /api/api-configs/{id}` - Update configuration
- `DELETE /api/api-configs/{id}` - Delete configuration
- `POST /api/api-configs/{id}/test` - Test connection

### Tests
- `GET /api/tests` - List all tests
- `POST /api/tests` - Create test
- `GET /api/tests/{id}` - Get test details
- `PUT /api/tests/{id}` - Update test
- `DELETE /api/tests/{id}` - Delete test
- `POST /api/tests/{id}/run` - Run test
- `GET /api/tests/{id}/status` - Get test status
- `GET /api/tests/{id}/questions` - Get test questions
- `POST /api/tests/{id}/questions` - Add questions

### Questions
- `POST /api/questions/upload` - Upload questions file
- `POST /api/questions/parse` - Parse questions from text

### Results
- `GET /api/results/{test_id}` - Get complete results
- `GET /api/results/{test_id}/summary` - Get summary
- `GET /api/results/{test_id}/evaluations` - Get all evaluations
- `GET /api/results/{test_id}/by-question` - Results by question
- `GET /api/results/{test_id}/by-agent` - Results by agent
- `GET /api/results/{test_id}/export` - Export results

### Dashboard
- `GET /api/dashboard` - Get dashboard statistics

### WebSocket
- `WS /ws/test/{test_id}` - Real-time test updates

## Project Structure

```
ConversationIQ/
├── backend/                    # FastAPI Backend
│   ├── api/
│   │   ├── routes/            # API route handlers
│   │   │   ├── agents.py
│   │   │   ├── apis.py
│   │   │   ├── dashboard.py
│   │   │   ├── questions.py
│   │   │   ├── results.py
│   │   │   ├── tests.py
│   │   │   └── websocket.py
│   │   └── main.py            # FastAPI app
│   └── models/                # Additional models
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── api/               # API client (Axios)
│   │   ├── components/        # React components
│   │   │   └── Layout.jsx
│   │   ├── pages/             # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Agents.jsx
│   │   │   ├── AgentCreate.jsx
│   │   │   ├── APIConfigs.jsx
│   │   │   ├── Tests.jsx
│   │   │   ├── TestCreate.jsx
│   │   │   ├── TestDetail.jsx
│   │   │   └── TestResults.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── src/                        # Existing backend logic
│   ├── agents/
│   ├── api/
│   ├── evaluation/
│   ├── storage/
│   ├── tests/
│   └── ui/                    # CLI (still available)
│
├── start-backend.sh           # Backend startup script (Linux/Mac)
├── start-frontend.sh          # Frontend startup script (Linux/Mac)
├── start-backend.bat          # Backend startup script (Windows)
├── start-frontend.bat         # Frontend startup script (Windows)
└── requirements-web.txt       # Additional web dependencies
```

## Development

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Backend Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run with auto-reload
uvicorn backend.api.main:app --reload

# Run tests
pytest

# Format code
black backend/
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Database
DATABASE_URL=sqlite:///./data/conversationiq.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration (in frontend/.env)
VITE_API_URL=http://localhost:8000
```

### CORS Configuration

CORS is configured in `backend/api/main.py` to allow:
- http://localhost:5173 (Vite default)
- http://localhost:3000 (Create React App default)

To add more origins, edit the `allow_origins` list in `main.py`.

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :8000   # Windows
```

**Database errors:**
```bash
# Reset database
rm data/conversationiq.db
python -c "from src.storage.database import init_database; init_database()"
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt -r requirements-web.txt
```

### Frontend Issues

**Port already in use:**
```bash
# Vite will automatically try the next available port
# Or specify a different port in vite.config.js
```

**Module not found:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**API connection refused:**
- Ensure backend is running on port 8000
- Check CORS configuration
- Verify API_BASE_URL in `frontend/src/api/client.js`

## Building for Production

### Backend

```bash
# Install production dependencies
pip install gunicorn

# Run with gunicorn
gunicorn backend.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend

```bash
cd frontend
npm run build

# Files will be in frontend/dist/
# Serve with any static file server
```

## CLI Still Available

The original CLI is still fully functional:

```bash
python conversationiq.py --help
```

You can use both the web UI and CLI interchangeably!

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - See LICENSE file

## Support

For issues or questions:
- Open an issue on GitHub
- Check API docs at http://localhost:8000/api/docs
- Review this README

---

**Enjoy using ConversationIQ! 🚀**
