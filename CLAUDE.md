# GEOPOLITIX Development Guide

## Project Overview
GEOPOLITIX is a real-time geopolitical risk analysis dashboard designed for Chief Geopolitical Officers (CGOs) and strategic decision-makers. It integrates multiple external data sources, performs advanced analytics, and presents actionable intelligence through interactive visualizations.

## Common Commands
- `python app.py`: Launch the Dash development server (port 8050)
- `pytest tests/ --cov=src --cov-report=term-missing`: Run full test suite with coverage
- `python scripts/update_data.py`: Manual data refresh from all API sources
- `black . && flake8 --max-line-length=88`: Format and lint the codebase
- `mypy src/`: Run type checking on source code

## Code Style Guidelines
- Follow PEP 8 conventions strictly
- Use type hints for all function signatures (enforced by MyPy)
- Maximum line length: 88 characters (Black default)
- Prefer explicit over implicit: avoid magic numbers, use named constants
- All API calls must include timeout parameters (default: 10 seconds)
- Use connection pooling for repeated API requests to the same endpoint
- Docstrings required for all public functions and classes (Google style)

## Testing Requirements
- Minimum 80% code coverage for production code
- Mock all external API calls in unit tests using `responses` library
- Include integration tests for Dash callbacks using `dash.testing`
- Test error handling: network failures, malformed API responses, rate limiting
- Run tests with: `pytest tests/ -v --cov=src`

## Security & API Key Management
- Store all API keys in `.env` file (never commit to repo)
- Use `python-decouple` for environment variable management
- Implement rate limiting respect: track API call frequency per endpoint
- Log all API errors to `logs/api_errors.log` for debugging
- Never log sensitive data (API keys, user credentials)

## Performance Optimization
- Cache API responses using in-memory cache (TTL: 15 minutes for real-time data)
- Implement lazy loading for large datasets: paginate results in UI
- Use Dash's clientside callbacks for UI updates that don't need server processing
- Profile dashboard rendering time: target <2 seconds for initial load
- Use connection pooling for all HTTP requests

## Project Structure
```
geopolitix/
├── app.py                    # Main Dash application entry point
├── CLAUDE.md                 # This file
├── README.md                 # Project overview and setup
├── requirements.txt          # Python dependencies
├── .env.example              # Template for environment variables
├── .gitignore               # Git ignore patterns
├── config/
│   ├── settings.py          # Application configuration
│   ├── api_endpoints.py     # API URL definitions
│   └── risk_thresholds.py   # Risk scoring parameters
├── src/
│   ├── data_sources/        # API integration modules
│   │   ├── gdelt.py         # GDELT Project API
│   │   ├── newsapi.py       # NewsAPI integration
│   │   ├── worldbank.py     # World Bank data
│   │   ├── acled.py         # Armed Conflict data
│   │   └── base.py          # Base API client class
│   ├── risk_engine/         # Risk calculation logic
│   │   ├── scoring.py       # Risk scoring algorithms
│   │   ├── weights.py       # Factor weighting models
│   │   └── scenarios.py     # Scenario simulation
│   ├── visualization/       # Dash components
│   │   ├── layouts.py       # Page layouts
│   │   ├── maps.py          # Choropleth map components
│   │   ├── charts.py        # Chart components
│   │   └── callbacks.py     # Dash callbacks
│   └── utils/               # Helper utilities
│       ├── cache.py         # Caching logic
│       ├── transformers.py  # Data transformation
│       └── logger.py        # Logging configuration
├── tests/                   # Test files mirroring src/
├── scripts/                 # Utility scripts
├── logs/                    # Application logs
└── assets/                  # Static assets (CSS, images)
```

## API Integration Guidelines
- All API modules must inherit from `BaseAPIClient` in `src/data_sources/base.py`
- Implement retry logic with exponential backoff for all external calls
- Cache responses appropriately based on data freshness requirements
- Handle rate limiting gracefully with informative error messages
- Log all API errors with full context for debugging

## Risk Scoring Methodology
The composite risk score (0-100) is calculated from:
- Political Stability (25%): Governance indicators, regime stability
- Economic Risk (25%): Trade policy, sanctions, currency volatility
- Security Risk (30%): Conflict events, terrorism, civil unrest
- Trade Relations (20%): Tariff changes, trade disputes, embargoes

## Git Workflow
- Feature branches: `feature/<description>`
- Bug fixes: `fix/<description>`
- Commit messages: Use conventional commits format
- Pull requests require passing tests and code review

## Environment Setup
1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add API keys
6. Run application: `python app.py`
