# Insurance Claims Processing API

A FastAPI-based application for processing insurance claims with AI-powered suggestions and video analysis capabilities.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- SQLite (for development) or PostgreSQL (for production)
- OpenAI API key (for AI suggestions and video analysis)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd claims-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create a .env file in the project root
cp .env.example .env

# Edit .env with your configuration
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./app.db  # For development
# DATABASE_URL=postgresql://user:password@localhost/dbname  # For production
```

## Running the Application

1. Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

2. Access the API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running Tests

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Run the test suite:
```bash
pytest tests/ -v
```

## API Endpoints

### Claims API
- `POST /api/claims/` - Create a new claim
- `GET /api/claims/{claim_id}` - Get claim details
- `PATCH /api/claims/{claim_id}` - Update a claim
- `DELETE /api/claims/{claim_id}` - Delete a claim
- `POST /api/claims/{claim_id}/video` - Upload video for a claim

### Suggestions API
- `GET /api/suggestions/claim/{claim_id}` - Get suggestions for a claim
- `PATCH /api/suggestions/{suggestion_id}` - Update a suggestion
- `GET /api/suggestions/metrics` - Get suggestion metrics
- `GET /api/suggestions/high-confidence` - Get high confidence suggestions
- `GET /api/suggestions/pending` - Get pending suggestions

## Development

### Project Structure
```
claims-api/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   └── main.py
├── tests/
├── requirements.txt
└── requirements-test.txt
```

### Database Migrations
The application uses SQLAlchemy for database operations. For production, consider using Alembic for database migrations:

```bash
# Initialize migrations
alembic init migrations

# Create a migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Production Deployment

For production deployment:

1. Use a production-grade ASGI server like Gunicorn:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. Set up a reverse proxy (e.g., Nginx) for SSL termination and load balancing

3. Use environment variables for sensitive configuration:
```bash
export OPENAI_API_KEY=your_key
export DATABASE_URL=your_production_db_url
export SECRET_KEY=your_secret_key
```

4. Enable CORS and rate limiting in production

## Monitoring and Logging

The application includes logging configuration. In production, consider:
- Setting up application monitoring (e.g., Prometheus, Grafana)
- Configuring log aggregation (e.g., ELK Stack)
- Setting up error tracking (e.g., Sentry)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 