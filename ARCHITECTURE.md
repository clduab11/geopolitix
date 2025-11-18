# Architecture Documentation

This document describes the technical architecture and design decisions for GEOPOLITIX.

## System Overview

GEOPOLITIX is a Python-based web application built with Dash that provides real-time geopolitical risk analysis. It integrates multiple external data sources, applies risk scoring algorithms, and presents results through interactive visualizations.

```
┌─────────────────────────────────────────────────────────────┐
│                    GEOPOLITIX Dashboard                      │
├─────────────────────────────────────────────────────────────┤
│  Visualization Layer (Dash/Plotly)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Maps    │ │  Charts  │ │ Layouts  │ │Callbacks │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
├───────┼────────────┼────────────┼────────────┼──────────────┤
│  Risk Engine                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│  │ Scoring  │ │ Weights  │ │Scenarios │                     │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘                     │
├───────┼────────────┼────────────┼───────────────────────────┤
│  Data Sources Layer                                          │
│  ┌──────┐ ┌────────┐ ┌──────────┐ ┌───────┐                 │
│  │GDELT │ │NewsAPI │ │WorldBank │ │ ACLED │                 │
│  └──┬───┘ └───┬────┘ └────┬─────┘ └───┬───┘                 │
│     └─────────┼───────────┼───────────┘                      │
│            ┌──┴───────────┴──┐                               │
│            │  Base API Client │                              │
│            └─────────────────┘                               │
├─────────────────────────────────────────────────────────────┤
│  Utilities                                                   │
│  ┌───────┐ ┌────────────┐ ┌────────┐                        │
│  │ Cache │ │Transformers│ │ Logger │                        │
│  └───────┘ └────────────┘ └────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Data Sources Layer

All API clients inherit from `BaseAPIClient`, which provides:
- Connection pooling
- Automatic retry with exponential backoff
- Timeout handling
- Error logging

```python
class BaseAPIClient:
    """Base class with resilient HTTP handling."""

    def _create_session(self):
        """Create session with retry strategy."""
        retry_strategy = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
```

Each data source client (GDELT, NewsAPI, WorldBank, ACLED) implements:
- Source-specific API calls
- Data transformation to common format
- Individual risk score calculation
- Caching of responses

### Risk Engine

#### Scoring Module

The `RiskScorer` class aggregates data from all sources to calculate composite risk scores:

```python
def calculate_composite_score(self, country):
    political = self._calculate_political_score(iso_code)  # WorldBank
    economic = self._calculate_economic_score(iso_code)    # WorldBank
    security = self._calculate_security_score(country)     # ACLED
    trade = self._calculate_trade_score(country)           # GDELT

    composite = sum(score * weight for score, weight in factors)
    return {composite_score, risk_level, factors, ...}
```

#### Weighting System

The `WeightManager` allows customizable factor weights:

Default weights:
- Political: 25%
- Economic: 25%
- Security: 30%
- Trade: 20%

Presets available:
- Balanced
- Security-focused
- Economic-focused
- Trade-focused
- Political-focused

#### Scenario Modeling

The `ScenarioModeler` simulates hypothetical events:

1. Select template or create custom scenario
2. Define affected countries and parameters
3. Apply severity multiplier to factor impacts
4. Calculate projected scores
5. Compare before/after states

### Visualization Layer

#### Layout Structure

The dashboard uses a tab-based layout:

1. **Global Overview**: World map, summary cards, alerts
2. **Risk Analytics**: Trends, comparisons, correlations
3. **Scenario Modeling**: Builder and results
4. **Company Exposure**: Input and analysis

#### Callback Architecture

Callbacks follow a reactive pattern:

```python
@app.callback(
    Output("world-map", "figure"),
    Input("btn-refresh", "n_clicks"),
    Input("interval-refresh", "n_intervals")
)
def update_map(n_clicks, n_intervals):
    # Fetch data
    # Process
    # Return figure
```

Key callbacks:
- `update_main_data`: Refreshes all data sources
- `update_overview_panels`: Updates summary and alerts
- `update_analytics`: Generates analysis charts
- `run_scenario`: Executes scenario simulation
- `calculate_exposure`: Computes company risk

### Caching Strategy

Caching reduces API calls and improves response time:

```python
@cache_response(ttl_minutes=15)
def get_country_data(country):
    # API call
    pass
```

Cache configuration:
- TTL: 15 minutes (configurable)
- Max size: 1000 entries
- Key: hash of function + arguments
- Storage: In-memory (cachetools.TTLCache)

### Data Flow

1. **User Action** → Callback triggered
2. **Data Fetch** → Check cache → API call if needed
3. **Processing** → Risk scoring, aggregation
4. **Visualization** → Generate Plotly figures
5. **Update UI** → Return outputs to components

## Risk Scoring Methodology

### Composite Score Calculation

```
Composite = Σ(Factor_Score × Factor_Weight)
```

Where:
- `Factor_Score` ∈ [0, 100]
- `Σ(Factor_Weight) = 1.0`

### Individual Factor Calculations

#### Political Score (WorldBank WGI)
```python
# WGI values range from -2.5 to 2.5
# Convert to 0-100 risk (lower WGI = higher risk)
risk_score = ((2.5 - avg_wgi) / 5) × 100
```

#### Economic Score (WorldBank)
Combines:
- Government Effectiveness
- Regulatory Quality

#### Security Score (ACLED)
Factors:
- Event count (weighted by type)
- Total fatalities
- Event severity

```python
risk = event_score + fatality_score + severity_score
```

Event type weights:
- Battles: 10
- Explosions: 8
- Violence: 9
- Protests: 3
- Riots: 5
- Strategic: 2

#### Trade Score (GDELT)
Based on news sentiment around trade topics:
```python
risk = (1 / sentiment_ratio) × 20
```

### Risk Levels

| Level | Score Range | Color |
|-------|-------------|-------|
| Low | 0-25 | Green (#2ecc71) |
| Moderate | 26-50 | Orange (#f39c12) |
| High | 51-75 | Red (#e74c3c) |
| Critical | 76-100 | Purple (#8e44ad) |

## Performance Optimization

### Caching
- API responses cached for 15 minutes
- Reduces redundant API calls
- Improves response time

### Lazy Loading
- Data fetched on demand
- Pagination for large datasets
- Progressive rendering

### Parallel Fetching
- Multiple API calls can run concurrently
- Uses connection pooling

### Client-side Processing
- Plotly figures rendered client-side
- Reduces server load

## Security Considerations

### API Key Management
- Keys stored in `.env` (never committed)
- Loaded via `python-decouple`
- Keys not logged

### Input Validation
- User inputs sanitized
- File uploads validated
- SQL injection prevented (no raw SQL)

### Error Handling
- Errors logged, not displayed to user
- Graceful degradation on API failure
- Default values for missing data

## Deployment Architecture

### Development
```
python app.py
# Runs on localhost:8050
# Debug mode enabled
```

### Production
```python
app.run_server(
    host="0.0.0.0",
    port=8050,
    debug=False,
)
```

Recommendations:
- Use gunicorn with multiple workers
- Add Redis for distributed caching
- Use HTTPS via reverse proxy (nginx)
- Set up monitoring (Prometheus/Grafana)

## Extensibility

### Adding New Data Sources

1. Create client in `src/data_sources/`
2. Inherit from `BaseAPIClient`
3. Implement required methods
4. Add to `RiskScorer` calculation
5. Update factor weights if needed

### Adding New Visualizations

1. Add figure function to `charts.py` or `maps.py`
2. Create callback in `callbacks.py`
3. Add component to layout
4. Wire up inputs/outputs

### Custom Risk Factors

1. Define in `risk_thresholds.py`
2. Add weight to `FACTOR_WEIGHTS`
3. Implement calculation in `scoring.py`
4. Update UI to display

## Testing Strategy

### Unit Tests
- Test individual functions
- Mock API calls
- Cover edge cases

### Integration Tests
- Test callback chains
- Verify data flow
- Test error handling

### Coverage Target
- Minimum 80% coverage
- All critical paths tested
- Error conditions covered

## Future Enhancements

1. **Real-time streaming**: WebSocket updates
2. **Machine learning**: Predictive risk modeling
3. **Multi-language**: International news sources
4. **Custom alerts**: User-defined thresholds
5. **API endpoints**: REST API for integration
6. **Historical database**: PostgreSQL storage
7. **Report generation**: PDF export
8. **Role-based access**: User authentication
