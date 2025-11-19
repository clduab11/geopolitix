# Geopolitix

Real-time geopolitical risk analysis dashboard with API integration for monitoring global events and their business impact.

## Overview

Geopolitix is a comprehensive platform for analyzing geopolitical risks by integrating multiple data sources including ACLED conflict data and GDELT event/sentiment data. It features a sophisticated composite risk engine with adjustable weighting, scenario modeling capabilities, and company exposure analysis.

### Key Features

- **Multi-Source Data Integration**: Combines ACLED conflict events and GDELT media sentiment for comprehensive analysis
- **Composite Risk Engine**: Calculate risk scores with customizable factor weights
- **Scenario Modeling**: Simulate hypothetical events and assess potential impacts
- **Company Exposure Analysis**: Map organizational footprints to geographic risks
- **Real-Time Dashboard**: Interactive visualizations with live data updates
- **Flexible API**: RESTful API for integration with existing systems

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with PostGIS
- Redis 7+
- Docker and Docker Compose (recommended)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/clduab11/geopolitix.git
cd geopolitix
```

2. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start with Docker Compose** (recommended)

```bash
docker-compose up -d
```

4. **Or install manually**

Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

5. **Access the application**

- Dashboard: http://localhost:3000
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Configuration

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://localhost/geopolitix` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `ACLED_API_KEY` | ACLED API key | - |
| `ACLED_EMAIL` | ACLED registered email | - |
| `SECRET_KEY` | JWT secret key | - |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

## Project Structure

```
geopolitix/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── tasks/          # Background tasks
│   ├── alembic/            # Database migrations
│   └── tests/              # Backend tests
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API clients
│   │   ├── store/          # Redux store
│   │   └── utils/          # Utilities
│   └── tests/              # Frontend tests
├── docs/                   # Documentation
│   ├── api/               # API reference
│   ├── architecture/      # Architecture docs
│   └── guides/            # User guides
├── docker/                 # Docker configurations
└── scripts/               # Utility scripts
```

## Documentation

- [Development Roadmap](ROADMAP.md) - Project timeline and milestones
- [API Reference](docs/api/README.md) - Complete API documentation
- [Architecture](docs/architecture/README.md) - System design and components
- [User Guide](docs/guides/user-guide.md) - How to use the dashboard

## Data Sources

### ACLED (Armed Conflict Location & Event Data)

Provides detailed information on conflict events worldwide including:
- Battles and armed clashes
- Violence against civilians
- Protests and riots
- Strategic developments

### GDELT (Global Database of Events, Language, and Tone)

Provides global event monitoring and media sentiment analysis including:
- Event tracking with CAMEO codes
- Media tone and sentiment
- Source analysis
- Global Knowledge Graph

## Risk Engine

The composite risk engine calculates risk scores based on multiple factors:

| Factor | Description | Weight Range |
|--------|-------------|--------------|
| Conflict Risk | Based on ACLED event frequency and severity | 0.0 - 1.0 |
| Sentiment Risk | Based on GDELT media tone analysis | 0.0 - 1.0 |
| Political Stability | Government effectiveness and transition risks | 0.0 - 1.0 |
| Economic Risk | Currency stability and trade indicators | 0.0 - 1.0 |

Weights are fully adjustable through the UI or API to customize risk assessment for your specific use case.

## API Usage

### Authentication

```bash
# Get access token
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"
```

### Get Risk Scores

```bash
# Get risk scores with default weights
curl http://localhost:8000/api/v1/risk/scores \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get risk scores with custom weights
curl -X POST http://localhost:8000/api/v1/risk/scores/calculate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "UKR",
    "weights": {
      "conflict": 0.4,
      "sentiment": 0.3,
      "political": 0.2,
      "economic": 0.1
    }
  }'
```

### Get ACLED Events

```bash
curl "http://localhost:8000/api/v1/acled/events?country=Ukraine&start_date=2024-01-01" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get GDELT Sentiment

```bash
curl "http://localhost:8000/api/v1/gdelt/sentiment?region=UKR" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

See the [API Reference](docs/api/README.md) for complete documentation.

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

### Code Style

```bash
# Backend linting
cd backend
ruff check .
black --check .

# Frontend linting
cd frontend
npm run lint
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment

### Docker Production Build

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes

Kubernetes manifests are available in the `k8s/` directory:

```bash
kubectl apply -f k8s/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [ACLED](https://acleddata.com/) for conflict event data
- [GDELT Project](https://www.gdeltproject.org/) for global event and sentiment data

## Support

- **Issues**: [GitHub Issues](https://github.com/clduab11/geopolitix/issues)
- **Discussions**: [GitHub Discussions](https://github.com/clduab11/geopolitix/discussions)
- **Email**: support@geopolitix.io
