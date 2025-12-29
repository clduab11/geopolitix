# Finance Module Documentation

## Overview

The GEOPOLITIX Finance Module integrates Perplexity's Sonar API and Financial Modeling Prep (FMP) API to provide real-time financial analysis capabilities with geopolitical risk overlay. This module enables users to assess how geopolitical events impact specific companies, markets, and financial instruments through AI-enhanced search and analysis.

## Features

- **AI-Powered Stock Analysis**: Natural language queries about companies with real-time citations
- **Real-Time Financial Data**: Live stock quotes, charts, and key metrics
- **Financial Statements**: Income statements, balance sheets, and cash flow data
- **Peer Comparison**: Compare companies across key metrics
- **Geopolitical Risk Overlay**: Map company geographic exposure to GEOPOLITIX risk scores
- **Model Selection**: Choose between quick, detailed, and deep research analysis modes

## Architecture

### Data Sources

#### Perplexity Sonar API (`src/data_sources/perplexity_api.py`)

The Perplexity client provides AI-powered financial analysis with real-time search and citations.

**Available Models:**

| Model | Use Case | Processing Time | Cost |
|-------|----------|-----------------|------|
| `sonar` | Quick factual queries, company lookups | Fast | Low |
| `sonar-pro` | Complex financial analysis, multi-step queries | Medium | Moderate |
| `sonar-deep-research` | Comprehensive reports, in-depth research | 30+ minutes | High |

**Example Usage:**

```python
from src.data_sources.perplexity_api import PerplexityClient

client = PerplexityClient()

# Basic stock analysis
result = client.analyze_stock("AAPL", analysis_type="overview")
print(result["content"])
print(result["citations"])

# Compare stocks
comparison = client.compare_stocks("AAPL", "MSFT")

# Geopolitical impact assessment
impact = client.get_geopolitical_impact("Apple", "China")

# Custom query with model selection
response = client.query(
    prompt="What are the key risks for Tesla in 2024?",
    model="sonar-pro",
    search_domain_filter=["sec.gov", "bloomberg.com", "reuters.com"]
)
```

#### Financial Modeling Prep API (`src/data_sources/fmp_api.py`)

The FMP client provides real-time financial data including quotes, historical prices, and financial statements.

**Example Usage:**

```python
from src.data_sources.fmp_api import FMPClient

client = FMPClient()

# Get stock quote
quote = client.get_stock_quote("AAPL")
print(f"Price: ${quote['price']}, Change: {quote['change_percent']}%")

# Get company profile
profile = client.get_company_profile("AAPL")
print(f"Sector: {profile['sector']}, Industry: {profile['industry']}")

# Get historical prices
historical = client.get_historical_prices("AAPL", period="1M")

# Get financial statements
income = client.get_income_statement("AAPL", period="annual")
balance = client.get_balance_sheet("AAPL", period="quarter")
cashflow = client.get_cash_flow("AAPL", period="annual")

# Search for tickers
results = client.search_ticker("Apple")

# Get key metrics
metrics = client.get_key_metrics("AAPL")

# Get peer comparison
peers = client.get_peer_comparison("AAPL")
```

### Prompt Templates (`src/data_sources/finance_prompts.py`)

Pre-built prompt templates for common financial analysis scenarios:

- `earnings_summary` - Analyze earnings reports
- `geopolitical_impact` - Assess geopolitical effects on companies
- `peer_comparison` - Compare companies across metrics
- `risk_assessment` - Evaluate company risks
- `sector_analysis` - Analyze sector trends
- `stock_overview` - General stock overview
- `market_impact` - Analyze event market impact
- `dividend_analysis` - Analyze dividend profiles
- `technical_analysis` - Technical chart analysis
- `earnings_preview` - Preview upcoming earnings

**Example Usage:**

```python
from src.data_sources.finance_prompts import format_prompt, get_system_prompt

# Format a prompt template
prompt = format_prompt(
    "geopolitical_impact",
    region="China",
    company="Apple"
)

# Get appropriate system prompt
system_prompt = get_system_prompt("risk_analyst")
```

## Dashboard Components

### Finance Tab Layout (`src/visualization/finance_layouts.py`)

The Finance tab is a two-column layout:

**Left Column (8/12 width):**
- AI Analysis output with citations
- Follow-up question interface
- Suggested follow-up questions

**Right Column (4/12 width):**
- Stock price and chart
- Key metrics grid
- Financial statements tabs

### Charts (`src/visualization/finance_charts.py`)

Chart generation functions:

- `create_stock_chart()` - Line, area, or candlestick stock charts
- `create_metrics_chart()` - Bar chart for key metrics
- `create_peer_comparison_chart()` - Compare company vs peers
- `create_geographic_exposure_chart()` - Pie chart with risk overlay
- `create_financial_statement_chart()` - Bar chart for statement data
- `create_sector_performance_chart()` - Horizontal bar for sectors

### Callbacks (`src/visualization/finance_callbacks.py`)

Dash callbacks for interactivity:

- Ticker autocomplete search
- Stock analysis on search
- Chart period selection (1D, 5D, 1M, 3M, 6M, 1Y, 5Y)
- Financial statement tab switching
- Follow-up question handling
- CSV export

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Perplexity AI
PERPLEXITY_API_KEY=your_perplexity_api_key_here
PERPLEXITY_FINANCE_ENABLED=true
PERPLEXITY_FINANCE_MODEL=sonar-pro

# Financial Modeling Prep
FMP_API_KEY=your_fmp_api_key_here
FMP_BASE_URL=https://financialmodelingprep.com/api/v3
```

### API Keys

**Perplexity AI:**
- Sign up at [perplexity.ai](https://www.perplexity.ai/)
- Generate API key in settings
- Free tier: Limited requests per day
- Pro tier: Higher limits, access to all models

**Financial Modeling Prep:**
- Sign up at [financialmodelingprep.com](https://site.financialmodelingprep.com/)
- Free tier: 250 requests/day
- Starter tier: 300 requests/day + historical data

## Best Practices

### Model Selection

| Scenario | Recommended Model |
|----------|-------------------|
| Quick stock lookup | `sonar` |
| Earnings analysis | `sonar-pro` |
| Geopolitical impact | `sonar-pro` |
| Comprehensive research | `sonar-deep-research` |
| Real-time price check | FMP API only |

### Domain Filtering

For higher quality financial sources, use domain filters:

```python
FINANCE_DOMAINS = [
    "sec.gov",           # SEC filings
    "bloomberg.com",     # Market news
    "reuters.com",       # Financial news
    "wsj.com",           # Wall Street Journal
    "seekingalpha.com",  # Analysis
    "ft.com",            # Financial Times
]
```

### Caching Strategy

| Data Type | Cache TTL |
|-----------|-----------|
| Stock quotes | 5 minutes |
| Historical prices | 15 minutes |
| Financial statements | 30 minutes |
| Company profiles | 10 minutes |
| AI analysis | 10 minutes |
| Sector performance | 60 minutes |

### Error Handling

All API calls include:
- Automatic retry with exponential backoff
- Rate limit handling
- Graceful degradation when APIs unavailable
- Detailed logging to `logs/api_errors.log`

## Geopolitical Risk Integration

### Company Exposure Calculator

Map FMP geographic revenue data to GEOPOLITIX risk scores:

```python
from src.data_sources.fmp_api import FMPClient

fmp = FMPClient()

# Get geographic revenue breakdown
segments = fmp.get_geographic_revenue("AAPL")

# Map to risk scores (from main GEOPOLITIX risk engine)
for segment in segments["segments"]:
    region = segment["region"]
    revenue = segment["revenue"]
    risk_score = get_risk_score_for_region(region)  # From risk engine
    weighted_risk = revenue * risk_score
```

### Scenario Impact Analysis

Link Perplexity queries to GEOPOLITIX scenario modeling:

```python
from src.data_sources.perplexity_api import PerplexityClient

client = PerplexityClient()

# Get AI assessment of scenario impact
impact = client.query(
    prompt=f"How would {scenario_description} affect {company}?",
    model="sonar-pro"
)

# Combine with risk engine projections
scenario_results = scenario_modeler.calculate_impact(scenario, current_scores)
```

## Testing

Run finance module tests:

```bash
# All finance tests
pytest tests/data_sources/test_perplexity_api.py -v
pytest tests/data_sources/test_fmp_api.py -v
pytest tests/visualization/test_finance_charts.py -v

# With coverage
pytest tests/ --cov=src/data_sources --cov=src/visualization
```

## Troubleshooting

### Common Issues

**1. "API not configured" error**
```
Error: Perplexity API not available
```
Solution: Add `PERPLEXITY_API_KEY` to your `.env` file

**2. No stock data returned**
```
Error: Data not available for TICKER
```
Solution: Verify `FMP_API_KEY` is set and ticker symbol is valid

**3. Rate limit exceeded**
```
Error: 429 Too Many Requests
```
Solution: Wait for rate limit reset or upgrade API plan

**4. Citations not appearing**
```
Warning: No citations available
```
Solution: Some queries may not return citations; this is expected behavior

### Logs

Check `logs/app.log` for detailed error information:
```bash
tail -f logs/app.log | grep -i "finance\|perplexity\|fmp"
```

## API Rate Limits

| Service | Free Tier | Recommended Usage |
|---------|-----------|-------------------|
| Perplexity | 5 req/min | Cache aggressively |
| FMP | 250 req/day | Cache financial data |

## Future Enhancements

- [ ] Real-time WebSocket updates for stock prices
- [ ] Custom watchlists with alerts
- [ ] Portfolio risk assessment
- [ ] Historical backtesting
- [ ] PDF report generation
- [ ] Cryptocurrency tracking
- [ ] Options and derivatives data

## References

- [Perplexity API Docs](https://docs.perplexity.ai/)
- [Perplexity Sonar Models](https://docs.perplexity.ai/getting-started/models/models/sonar)
- [FMP API Docs](https://site.financialmodelingprep.com/developer/docs/)
- [GEOPOLITIX AI Integrations](docs/AI_INTEGRATIONS.md)
