# GEOPOLITIX

Real-time geopolitical risk analysis dashboard designed for Chief Geopolitical Officers (CGOs) and strategic decision-makers who need to assess and respond to global political instability, trade policy shifts, and regional conflicts that impact business operations.

## Features

### Core Analytics
- **Interactive World Risk Map**: Choropleth visualization of global geopolitical risk scores with drill-down capabilities
- **Multi-Dimensional Analytics**: Trend analysis, comparative charts, and correlation matrices
- **Scenario Modeling**: Simulate hypothetical geopolitical events and their cascading impacts
- **Company Exposure Assessment**: Calculate your organization's risk exposure based on geographic presence
- **Real-Time Alerts**: Automated notifications for significant risk changes

### AI & Advanced Search Integrations ⭐ NEW
- **Perplexity Finance**: Real-time financial market intelligence and geopolitical-financial correlation analysis
- **Sonar Reasoning Pro**: Advanced AI-powered deep analysis, trend identification, and executive briefings
- **Tavily Search**: Real-time web search optimized for breaking news and event validation
- **Exa AI**: Neural/semantic search for discovering expert analysis and historical precedents
- **Firecrawl**: Deep web scraping for monitoring official government and international organization sources
- **Intelligence Aggregator**: Unified orchestration of all AI services for comprehensive multi-source analysis

See [AI_INTEGRATIONS.md](docs/AI_INTEGRATIONS.md) for complete documentation.

## Quick Start

### Prerequisites

- Python 3.9+
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/geopolitix.git
cd geopolitix
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run the application:
```bash
python app.py
```

6. Open your browser to `http://localhost:8050`

### Troubleshooting

**Dashboard won't start:**
- Verify Python 3.9+ is installed: `python --version`
- Check all dependencies installed: `pip list | grep dash`
- Review logs in `logs/app.log`

**API errors:**
- Verify API keys in `.env` file are correct
- Check API rate limits haven't been exceeded
- Ensure internet connectivity for external API calls

**Data not loading:**
- Some data sources may be slow on first request
- Check browser console for JavaScript errors
- Manually refresh data: `python scripts/update_data.py`

**UI rendering issues:**
- Clear browser cache
- Try a different browser (Chrome/Firefox recommended)
- Check for ad-blockers interfering with CDN resources

## API Keys Required

### Core Data Sources

The dashboard integrates with multiple data sources. You'll need API keys for:

- **NewsAPI**: [https://newsapi.org/register](https://newsapi.org/register)
  - Free tier: 100 requests/day
  - Required for news sentiment analysis
- **ACLED**: [https://acleddata.com/register](https://acleddata.com/register)
  - Free tier: 2,500 requests/month
  - Required for conflict event data
  - Requires both API key and email address
- **GDELT** (optional): Most endpoints are free
  - No authentication required – used for global event tracking
- **World Bank**: No key required
  - Public API for governance indicators
  - No rate limits

### AI & Advanced Search APIs (Optional but Recommended)

For enhanced intelligence capabilities:

- **Perplexity AI**: [https://www.perplexity.ai/](https://www.perplexity.ai/)
  - Used for: Finance intelligence and AI reasoning
  - Required for: Financial market analysis, deep analysis, executive briefs
  - Free tier available with limits
- **Tavily**: [https://tavily.com/](https://tavily.com/)
  - Used for: Real-time news search and breaking news monitoring
  - Required for: Advanced news search, event validation
  - Free tier: 1,000 requests/month
- **Exa AI**: [https://exa.ai/](https://exa.ai/)
  - Used for: Neural/semantic search, expert content discovery
  - Required for: Similar event detection, think tank analysis
  - Free tier available
- **Firecrawl**: [https://firecrawl.dev/](https://firecrawl.dev/)
  - Used for: Web scraping, official source monitoring
  - Required for: Government site tracking, policy monitoring
  - Free tier: 500 pages/month

**Note**: The application will function with core data sources only. AI integrations are optional enhancements that provide additional intelligence capabilities.

**Important**: Set `HOST=0.0.0.0` in `.env` only if you need to expose the dashboard to your network. The default `127.0.0.1` restricts access to localhost for security.

## Project Structure

```text
geopolitix/
├── app.py                    # Main application entry point
├── CLAUDE.md                 # Development guidelines
├── config/                   # Configuration files
│   ├── settings.py          # Application settings
│   ├── api_endpoints.py     # API URL definitions
│   └── risk_thresholds.py   # Risk scoring parameters
├── src/
│   ├── data_sources/        # API integrations
│   ├── risk_engine/         # Scoring algorithms
│   ├── visualization/       # Dash components
│   └── utils/               # Helper utilities
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
└── assets/                  # Static assets
```

## Usage

### Global Overview

The main dashboard displays:
- Interactive world map with risk scores by country
- Summary statistics (average risk, high-risk count)
- Real-time alert feed
- Top risk countries list

### Risk Analytics

Analyze risk trends and compare countries:
1. Select countries from the dropdown
2. Choose time range (7-365 days)
3. View trends, comparisons, or correlation matrices

### Scenario Modeling

Simulate geopolitical events:
1. Choose a scenario template or create custom
2. Select affected countries
3. Adjust severity and duration
4. Run simulation to see projected impacts
5. Export results as JSON

### Company Exposure

Assess your organization's risk:
1. Upload CSV with location data or enter manually
2. View weighted risk score based on exposure
3. Review priority actions for high-risk locations

## Development

### Running Tests

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Code Quality

```bash
black .
flake8 --max-line-length=88
mypy src/
```

### Manual Data Update

```bash
python scripts/update_data.py
```

## Risk Scoring Methodology

The composite risk score (0-100) is calculated from four factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Political | 25% | Governance indicators, regime stability |
| Economic | 25% | Trade policy, sanctions, currency |
| Security | 30% | Conflict events, terrorism, unrest |
| Trade | 20% | Tariffs, disputes, embargoes |

Risk levels:
- **Low** (0-25): Green
- **Moderate** (26-50): Yellow/Orange
- **High** (51-75): Red
- **Critical** (76-100): Purple

## Performance

Target benchmarks:
- Dashboard initial load: <3 seconds
- Callback response: <500ms
- Full data refresh: <30 seconds
- Concurrent users: 50+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure tests pass and coverage is maintained
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and feature requests, please use the GitHub issue tracker.
