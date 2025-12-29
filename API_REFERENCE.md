# API Reference

This document describes the data sources and API integrations used by GEOPOLITIX.

## Data Sources Overview

| Source | Type | Authentication | Rate Limit |
|--------|------|----------------|------------|
| GDELT | News/Events | None/Free | Reasonable use |
| NewsAPI | News | API Key | 100/day (free) |
| World Bank | Indicators | None | 500/day |
| ACLED | Conflicts | API Key + Email | 10,000/month |
| Perplexity | AI Analysis | API Key | 5 req/min (free) |
| FMP | Financial Data | API Key | 250/day (free) |

## GDELT Project API

**Base URL**: `https://api.gdeltproject.org/api/v2`

### Endpoints Used

#### Document API
```
GET /doc/doc?query={query}&mode={mode}&format=json
```

Parameters:
- `query`: Search query (e.g., `"United States" sourcelang:eng`)
- `mode`: Response mode (`artlist`, `tonechart`, `wordcloud`)
- `maxrecords`: Maximum results (default: 250)
- `format`: `json` or `csv`

Example:
```python
from src.data_sources.gdelt import GDELTClient

client = GDELTClient()
data = client.get_country_mentions("Russia", days=7)
```

Response:
```json
{
  "country": "Russia",
  "article_count": 150,
  "articles": [...],
  "query_time": "2024-01-15T10:30:00"
}
```

## NewsAPI

**Base URL**: `https://newsapi.org/v2`

### Authentication

Add API key to headers:
```
X-Api-Key: your_api_key
```

### Endpoints Used

#### Everything
```
GET /everything?q={query}&from={date}&language=en
```

Parameters:
- `q`: Search query
- `from`: Start date (YYYY-MM-DD)
- `language`: Language code
- `sortBy`: `relevancy`, `popularity`, `publishedAt`
- `pageSize`: Results per page (max 100)

Example:
```python
from src.data_sources.newsapi import NewsAPIClient

client = NewsAPIClient()
data = client.get_country_news("China", days=7)
sentiment = client.calculate_news_sentiment_score("China")
```

Response:
```json
{
  "country": "China",
  "average_polarity": -0.15,
  "average_subjectivity": 0.45,
  "article_count": 85,
  "risk_score": 57.5
}
```

## World Bank API

**Base URL**: `https://api.worldbank.org/v2`

### Endpoints Used

#### Country Indicators
```
GET /country/{country}/indicator/{indicator}?format=json&date={range}
```

Parameters:
- `country`: ISO 3166-1 alpha-3 code or `all`
- `indicator`: Indicator code (see below)
- `date`: Date range (e.g., `2015:2023`)
- `per_page`: Results per page

### World Governance Indicators

| Code | Name |
|------|------|
| VA.EST | Voice and Accountability |
| PV.EST | Political Stability |
| GE.EST | Government Effectiveness |
| RQ.EST | Regulatory Quality |
| RL.EST | Rule of Law |
| CC.EST | Control of Corruption |

Example:
```python
from src.data_sources.worldbank import WorldBankClient

client = WorldBankClient()
indicators = client.get_governance_indicators("DEU")
score = client.calculate_governance_risk_score("DEU")
```

Response:
```json
{
  "country_code": "DEU",
  "country": "Germany",
  "indicators": {
    "Political Stability": {"value": 0.85, "year": "2022"},
    "Rule of Law": {"value": 1.65, "year": "2022"}
  },
  "query_time": "2024-01-15T10:30:00"
}
```

## ACLED API

**Base URL**: `https://api.acleddata.com/acled/read`

### Authentication

Parameters:
- `key`: API key
- `email`: Registered email

### Endpoints Used

#### Read Events
```
GET /?key={key}&email={email}&country={country}&event_date={range}
```

Parameters:
- `country`: Country name
- `event_date`: Date or range
- `event_date_where`: `BETWEEN`, `=`, `>`, `<`
- `limit`: Maximum events

### Event Types

- Battles
- Explosions/Remote violence
- Violence against civilians
- Protests
- Riots
- Strategic developments

Example:
```python
from src.data_sources.acled import ACLEDClient

client = ACLEDClient()
events = client.get_country_events("Syria", days=30)
score = client.calculate_conflict_risk_score("Syria")
```

Response:
```json
{
  "country": "Syria",
  "event_count": 125,
  "events": [
    {
      "event_id": "12345",
      "event_date": "2024-01-10",
      "event_type": "Battles",
      "fatalities": 5,
      "location": "Idlib"
    }
  ],
  "date_range": "2023-12-15 to 2024-01-15"
}
```

## Internal APIs

### RiskScorer

```python
from src.risk_engine.scoring import RiskScorer

scorer = RiskScorer()

# Get composite score
result = scorer.calculate_composite_score("United States")
# Returns: {composite_score, risk_level, factors, ...}

# Batch scoring
df = scorer.get_batch_scores(["USA", "China", "Russia"])
# Returns: DataFrame with all scores

# Generate alerts
alerts = scorer.generate_alerts(df, threshold=70)
# Returns: List of alert dictionaries
```

### ScenarioModeler

```python
from src.risk_engine.scenarios import ScenarioModeler

modeler = ScenarioModeler()

# Create from template
scenario = modeler.create_from_template("trade_embargo", {
    "country_a": "USA",
    "country_b": "China",
    "severity": 1.5,
})

# Calculate impact
impact = modeler.calculate_impact(scenario, current_scores)
# Returns: {country: {current, projected, changes}, ...}

# Compare scenarios
comparison = modeler.compare_scenarios([s1, s2], scores)
```

### WeightManager

```python
from src.risk_engine.weights import WeightManager

manager = WeightManager()

# Get presets
presets = manager.get_weight_presets()
# Returns: {balanced, security_focused, economic_focused, ...}

# Apply preset
manager.apply_preset("security_focused")

# Custom weights
manager.set_weights({
    "political": 0.4,
    "economic": 0.3,
    "security": 0.2,
    "trade": 0.1,
})

# Calculate score
score = manager.calculate_weighted_score(factor_scores)
```

## Error Handling

All API clients include retry logic and error handling:

```python
from src.data_sources.base import BaseAPIClient

# Automatic retries with exponential backoff
# Retries on: 429, 500, 502, 503, 504
# Max retries: 3
# Backoff factor: 1.0

# Timeout handling
# Default timeout: 10 seconds
# Returns None on timeout with warning log

# HTTP error handling
# Logs error and returns None
# Check logs/api_errors.log for details
```

## Caching

API responses are cached to reduce calls:

```python
from src.utils.cache import cache_response, clear_cache

# Default TTL: 15 minutes
# Max cache size: 1000 entries

# Clear all cache
clear_cache()

# Custom TTL
@cache_response(ttl_minutes=30)
def my_function():
    pass
```

## Perplexity Sonar API

**Base URL**: `https://api.perplexity.ai`

### Authentication

Use Bearer token authentication:
```
Authorization: Bearer your_api_key
```

### Chat Completions

```
POST /chat/completions
```

Request Body:
```json
{
  "model": "sonar-pro",
  "messages": [
    {"role": "system", "content": "You are a financial analyst."},
    {"role": "user", "content": "Analyze AAPL stock performance."}
  ],
  "temperature": 0.2,
  "search_domain_filter": ["sec.gov", "bloomberg.com"]
}
```

Response:
```json
{
  "choices": [
    {
      "message": {
        "content": "Apple (AAPL) is currently trading at..."
      }
    }
  ],
  "citations": ["https://sec.gov/...", "https://bloomberg.com/..."],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350
  }
}
```

### Available Models

| Model | Use Case |
|-------|----------|
| `sonar` | Quick factual queries |
| `sonar-pro` | Complex financial analysis |
| `sonar-deep-research` | Comprehensive reports (30+ min) |

Example:
```python
from src.data_sources.perplexity_api import PerplexityClient

client = PerplexityClient()
result = client.analyze_stock("AAPL", analysis_type="overview")
print(result["content"])
print(result["citations"])
```

## Financial Modeling Prep API

**Base URL**: `https://financialmodelingprep.com/api/v3`

### Authentication

Add API key as query parameter:
```
?apikey=your_api_key
```

### Endpoints Used

#### Stock Quote
```
GET /quote/{symbol}?apikey={key}
```

Response:
```json
[{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "price": 150.50,
  "change": 2.50,
  "changesPercentage": 1.69,
  "marketCap": 2500000000000,
  "pe": 28.5,
  "volume": 50000000
}]
```

#### Company Profile
```
GET /profile/{symbol}?apikey={key}
```

#### Historical Prices
```
GET /historical-price-full/{symbol}?apikey={key}
```

#### Financial Statements
```
GET /income-statement/{symbol}?period={annual|quarter}&limit=5&apikey={key}
GET /balance-sheet-statement/{symbol}?period={annual|quarter}&limit=5&apikey={key}
GET /cash-flow-statement/{symbol}?period={annual|quarter}&limit=5&apikey={key}
```

#### Ticker Search
```
GET /search?query={query}&limit=10&apikey={key}
```

Example:
```python
from src.data_sources.fmp_api import FMPClient

client = FMPClient()
quote = client.get_stock_quote("AAPL")
profile = client.get_company_profile("AAPL")
income = client.get_income_statement("AAPL", period="annual")
```

## Rate Limiting

Respect API rate limits:
- NewsAPI: 100 requests/day (free tier)
- World Bank: 500 requests/day
- ACLED: ~10,000 requests/month
- Perplexity: 5 requests/minute (free tier)
- FMP: 250 requests/day (free tier)

Configure in `.env`:
```
API_RATE_LIMIT_PER_MINUTE=60
```
