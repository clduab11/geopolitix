# AI & Advanced Search Integrations

## Overview

GEOPOLITIX integrates multiple AI-powered and advanced search services to provide comprehensive geopolitical intelligence. This document describes all integrations, their capabilities, and how to use them.

## Integrated Services

### 1. Perplexity Finance

**Purpose:** Real-time financial market intelligence related to geopolitical events

**Module:** `src/data_sources/perplexity_finance.py`

**Key Features:**
- Stock market impact analysis by country/sector
- Currency fluctuation tracking
- Commodity price movements (oil, gas, metals, agricultural)
- Bond yields and sovereign debt indicators
- Cryptocurrency market sentiment
- Financial risk correlation with geopolitical scores

**Configuration:**
```bash
PERPLEXITY_API_KEY=your_key_here
PERPLEXITY_FINANCE_ENABLED=true
PERPLEXITY_SONAR_MODEL=sonar-pro
```

**Usage Example:**
```python
from src.data_sources.perplexity_finance import PerplexityFinanceClient

client = PerplexityFinanceClient()

# Get market impact for a country
market_data = client.get_market_impact(
    country="China",
    event_description="Trade policy changes"
)

# Get stock market reaction
stock_impact = client.get_stock_market_impact(
    country="United States",
    sector="defense"
)

# Get currency impact
currency_data = client.get_currency_impact(
    country="Russia",
    currency_code="RUB"
)

# Calculate financial correlation with risk score
correlation = client.calculate_financial_risk_correlation(
    country="Iran",
    risk_score=75.5
)
```

**Cache TTL:** 5-15 minutes (varies by method)

---

### 2. Perplexity Sonar Reasoning Pro

**Purpose:** Advanced AI reasoning for deep geopolitical analysis

**Module:** `src/ai_analysis/sonar_reasoning.py`

**Key Features:**
- Comprehensive deep dive country analysis
- Multi-source news synthesis
- Emerging trend identification
- Scenario validation against historical data
- Comparative country analysis
- Alert prioritization by impact
- Causal inference analysis
- Executive briefing generation

**Configuration:**
```bash
PERPLEXITY_API_KEY=your_key_here
PERPLEXITY_SONAR_MODEL=sonar-reasoning-pro
```

**Usage Example:**
```python
from src.ai_analysis.sonar_reasoning import SonarReasoningClient

client = SonarReasoningClient()

# Deep dive analysis
analysis = client.deep_dive_analysis(
    country="Ukraine",
    focus_areas=["political", "security"]
)

# Synthesize news articles
summary = client.synthesize_news(
    articles=news_articles,
    country="Taiwan"
)

# Validate a scenario
validation = client.validate_scenario(
    scenario_description="China invades Taiwan in 2025",
    historical_context="Historical Taiwan Strait crises"
)

# Compare countries
comparison = client.compare_countries(
    countries=["Iran", "Saudi Arabia", "UAE"],
    comparison_factors=["political_stability", "economic_risk"]
)

# Generate executive brief
brief = client.generate_executive_brief(
    timeframe="24h",
    focus_regions=["Middle East", "East Asia"]
)
```

**Cache TTL:** 30-120 minutes (varies by method)

---

### 3. Tavily Search

**Purpose:** Real-time web search and news aggregation optimized for AI

**Module:** `src/data_sources/tavily_search.py`

**Key Features:**
- Real-time news search by country/keywords
- Breaking news detection (last 24 hours)
- Advanced search depth options
- Domain filtering (include/exclude)
- Multi-language search support
- Source credibility assessment
- Event validation with multiple sources
- Research mode for deep queries

**Configuration:**
```bash
TAVILY_API_KEY=your_key_here
TAVILY_SEARCH_DEPTH=advanced  # or basic
TAVILY_MAX_RESULTS=10
TAVILY_INCLUDE_DOMAINS=reuters.com,apnews.com
TAVILY_EXCLUDE_DOMAINS=example.com
```

**Usage Example:**
```python
from src.data_sources.tavily_search import TavilySearchClient

client = TavilySearchClient()

# Search country events
events = client.search_country_events(
    country="North Korea",
    event_type="military",
    days=7
)

# Breaking news search
breaking_news = client.breaking_news_search(
    keywords=["coup", "military", "crisis"],
    hours=24
)

# Research query
research = client.research_query(
    topic="Iran nuclear program developments",
    source_types=["news", "government", "academic"]
)

# Validate event
validation = client.validate_event(
    event_description="India-Pakistan border conflict",
    source_count=3
)

# Multi-language search
multilang = client.multi_language_search(
    query="China Taiwan relations",
    languages=["en", "zh", "fr"]
)
```

**Cache TTL:** 3-15 minutes (varies by method)

---

### 4. Exa AI

**Purpose:** Neural/semantic search for high-quality content discovery

**Module:** `src/data_sources/exa_search.py`

**Key Features:**
- Neural search for semantic matching
- Find similar historical events
- Discover expert analysis from think tanks
- Identify emerging narratives
- Content recommendation engine
- Academic research discovery
- Policy document search
- Event similarity clustering

**Configuration:**
```bash
EXA_API_KEY=your_key_here
EXA_NUM_RESULTS=10
EXA_USE_AUTOPROMPT=true
```

**Usage Example:**
```python
from src.data_sources.exa_search import ExaSearchClient

client = ExaSearchClient()

# Neural search
results = client.neural_search(
    query="Middle East peace process challenges",
    num_results=10,
    use_autoprompt=True
)

# Find similar historical events
similar = client.find_similar_events(
    event_description="Military coup in Myanmar 2021",
    num_results=10
)

# Discover expert analysis
expert_content = client.discover_expert_analysis(
    topic="Russia-Ukraine conflict"
)

# Identify emerging narratives
narratives = client.identify_emerging_narratives(
    region="South China Sea",
    days=30
)

# Search academic research
research = client.search_academic_research(
    topic="Geopolitical impacts of climate change",
    num_results=10
)

# Policy document search
policies = client.policy_document_search(
    query="US foreign policy Middle East",
    governments=["state.gov", "whitehouse.gov"]
)
```

**Cache TTL:** 30-240 minutes (varies by method)

---

### 5. Firecrawl

**Purpose:** Deep web scraping and official source monitoring

**Module:** `src/data_sources/firecrawl.py`

**Key Features:**
- Single URL scraping with JavaScript support
- Multi-page website crawling
- Government website monitoring
- International organization tracking
- Think tank publication scraping
- Defense ministry monitoring
- Sanctions tracking from official sources
- Change detection for monitored sites

**Configuration:**
```bash
FIRECRAWL_API_KEY=your_key_here
FIRECRAWL_CRAWL_DEPTH=2
FIRECRAWL_ENABLE_JAVASCRIPT=true
FIRECRAWL_WAIT_FOR_SELECTOR=.content
```

**Usage Example:**
```python
from src.data_sources.firecrawl import FirecrawlClient

client = FirecrawlClient()

# Scrape single URL
content = client.scrape_url(
    url="https://www.state.gov/briefing-room/",
    include_raw_html=False
)

# Monitor government sites
gov_updates = client.monitor_government_site(
    country_code="US"
)

# Track international organizations
un_updates = client.track_international_orgs(
    organization="UN"
)

# Scrape think tanks
think_tank_content = client.scrape_think_tanks(
    topic="China",
    think_tanks=["https://www.cfr.org/", "https://www.csis.org/"]
)

# Monitor defense ministries
defense_updates = client.monitor_defense_ministries(
    countries=["US", "UK", "FR"]
)

# Track sanctions
sanctions = client.track_sanctions(
    target_country="Russia"
)

# Detect content changes
changes = client.detect_changes(
    url="https://www.kremlin.ru/",
    previous_content=old_content
)
```

**Cache TTL:** 60-360 minutes (varies by method)

---

## Unified Intelligence Aggregator

**Purpose:** Orchestrate all AI and search services for comprehensive analysis

**Module:** `src/intelligence/aggregator.py`

The Intelligence Aggregator is the central hub that combines all services for unified intelligence gathering.

**Key Methods:**

### `comprehensive_country_analysis(country, include_financial, include_historical)`

Performs multi-source intelligence gathering combining:
1. Real-time news (Tavily)
2. Historical precedents (Exa)
3. Government sources (Firecrawl)
4. Financial market impact (Perplexity Finance)
5. Traditional news (NewsAPI)
6. AI synthesis and deep analysis (Sonar)

**Example:**
```python
from src.intelligence.aggregator import IntelligenceAggregator

aggregator = IntelligenceAggregator()

# Comprehensive country analysis
analysis = aggregator.comprehensive_country_analysis(
    country="China",
    include_financial=True,
    include_historical=True
)

# Access different data sources
tavily_news = analysis["data_sources"]["tavily_news"]
financial_data = analysis["data_sources"]["financial_impact"]
ai_analysis = analysis["data_sources"]["deep_analysis"]
```

### `breaking_news_monitor(keywords, hours)`

Real-time monitoring across all news sources with AI prioritization.

**Example:**
```python
# Monitor breaking news
breaking = aggregator.breaking_news_monitor(
    keywords=["military", "conflict", "sanctions"],
    hours=24
)

# Get prioritized alerts
alerts = breaking["prioritized_alerts"]
```

### `generate_executive_brief(timeframe, focus_regions)`

AI-generated executive summary using all sources.

**Example:**
```python
# Generate executive brief
brief = aggregator.generate_executive_brief(
    timeframe="24h",
    focus_regions=["Middle East", "East Asia"]
)

print(brief["brief"])
```

### `multi_source_search(query, include_financial)`

Search across all available sources simultaneously.

**Example:**
```python
# Multi-source search
results = aggregator.multi_source_search(
    query="Iran nuclear program",
    include_financial=True
)

# Access different source results
tavily = results["sources"]["tavily"]
exa = results["sources"]["exa"]
finance = results["sources"]["finance"]
```

### `validate_event_multi_source(event_description, min_sources)`

Validate events using multiple sources and AI analysis.

**Example:**
```python
# Validate event
validation = aggregator.validate_event_multi_source(
    event_description="Military buildup on Taiwan Strait",
    min_sources=3
)

is_valid = validation["validated"]
ai_assessment = validation["ai_analysis"]
```

### `financial_geopolitical_correlation(country, risk_score)`

Analyze correlation between geopolitical risk and financial markets.

**Example:**
```python
# Analyze financial correlation
correlation = aggregator.financial_geopolitical_correlation(
    country="Russia",
    risk_score=85.3
)

stock_impact = correlation["stock_impact"]
currency_impact = correlation["currency_impact"]
```

### `track_official_sources(countries, include_international_orgs)`

Monitor official government and international organization sources.

**Example:**
```python
# Track official sources
official = aggregator.track_official_sources(
    countries=["US", "CN", "RU"],
    include_international_orgs=True
)

us_gov = official["official_sources"]["United States"]
intl_orgs = official["official_sources"]["international_orgs"]
```

---

## Best Practices

### 1. API Key Management
- Store all API keys in `.env` file (never commit)
- Rotate keys regularly for security
- Monitor API usage and quotas
- Implement rate limiting per service

### 2. Caching Strategy
- Use appropriate TTL for each data type:
  - Real-time news: 3-5 minutes
  - Financial data: 5-10 minutes
  - Analysis results: 30-60 minutes
  - Historical data: 120-240 minutes
- Clear cache when needed using `cache.clear_cache()`

### 3. Error Handling
- All clients include automatic retry logic
- Handle rate limiting gracefully
- Log all errors for debugging
- Implement fallback mechanisms

### 4. Performance Optimization
- Use parallel API calls when possible (ThreadPoolExecutor)
- Batch requests where APIs support it
- Implement request deduplication
- Monitor and optimize slow queries

### 5. Cost Management
- Monitor API usage across all services
- Set budget alerts
- Use caching aggressively
- Optimize query frequency

---

## Troubleshooting

### Common Issues

**1. API Key Not Found**
```
Error: PERPLEXITY_API_KEY not configured
```
Solution: Add API key to `.env` file

**2. Rate Limiting**
```
Error: Rate limit exceeded for Tavily API
```
Solution: Implement exponential backoff, adjust request frequency

**3. Timeout Errors**
```
Error: Request timeout for Exa API
```
Solution: Increase timeout in settings, check network connectivity

**4. Cache Issues**
```
Warning: Cache size exceeding limit
```
Solution: Increase `CACHE_MAX_SIZE` or clear cache more frequently

**5. Integration Failures**
```
Error: Multiple services unavailable
```
Solution: Check API service status, implement circuit breakers

---

## API Rate Limits

| Service | Free Tier | Paid Tier | Recommended |
|---------|-----------|-----------|-------------|
| Perplexity | 5 req/min | 50 req/min | Cache aggressively |
| Tavily | 1000 req/month | Custom | Use for breaking news |
| Exa | 1000 searches/month | Custom | Long TTL cache |
| Firecrawl | 500 pages/month | Custom | Schedule crawls |

---

## Testing

All integrations include comprehensive test suites:

```bash
# Test all AI integrations
pytest tests/data_sources/test_perplexity_finance.py
pytest tests/ai_analysis/test_sonar_reasoning.py
pytest tests/data_sources/test_tavily_search.py
pytest tests/data_sources/test_exa_search.py
pytest tests/data_sources/test_firecrawl.py

# Test intelligence aggregator
pytest tests/intelligence/test_aggregator.py

# Run with coverage
pytest tests/ --cov=src/data_sources --cov=src/ai_analysis --cov=src/intelligence
```

---

## Support

For issues or questions:
1. Check this documentation
2. Review API provider documentation
3. Check logs in `logs/app.log`
4. Open issue on GitHub

---

## Future Enhancements

Planned improvements:
- [ ] Real-time streaming for breaking news
- [ ] Custom alert rules per service
- [ ] Advanced correlation algorithms
- [ ] Machine learning for trend prediction
- [ ] Multi-modal analysis (images, videos)
- [ ] GraphQL API for intelligence data
- [ ] WebSocket support for live updates

---

## Changelog

**v1.0.0** (2024-01-XX)
- Initial implementation of all AI integrations
- Perplexity Finance and Sonar Reasoning
- Tavily, Exa, and Firecrawl integrations
- Unified Intelligence Aggregator
- Comprehensive documentation
