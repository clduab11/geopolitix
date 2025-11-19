# Geopolitix Architecture

## Overview

Geopolitix is built as a modern, scalable microservices-inspired architecture with clear separation of concerns between data ingestion, processing, storage, and presentation layers.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  React Dashboard  │  REST API Clients  │  Webhook Consumers     │
└────────┬──────────┴─────────┬──────────┴─────────┬───────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                              │
├─────────────────────────────────────────────────────────────────┤
│  Authentication  │  Rate Limiting  │  Request Routing  │ CORS   │
└────────┬──────────┴─────────┬───────┴─────────┬──────────────────┘
         │                    │                 │
         ▼                    ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  ACLED       │  GDELT       │  Risk        │  Scenario          │
│  Service     │  Service     │  Engine      │  Service           │
├──────────────┼──────────────┼──────────────┼────────────────────┤
│  Company     │  Alert       │  Report      │  User              │
│  Service     │  Service     │  Service     │  Service           │
└──────┬───────┴───────┬──────┴──────┬───────┴────────┬───────────┘
       │               │             │                │
       ▼               ▼             ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
├──────────────────┬──────────────────┬───────────────────────────┤
│   PostgreSQL     │     Redis        │    Celery Workers         │
│   (Primary DB)   │  (Cache/Queue)   │  (Background Tasks)       │
└──────────────────┴──────────────────┴───────────────────────────┘
         ▲                    ▲
         │                    │
┌────────┴────────────────────┴───────────────────────────────────┐
│                    DATA INGESTION LAYER                          │
├──────────────────┬──────────────────┬───────────────────────────┤
│   ACLED API      │   GDELT API      │   Other Sources           │
│   Connector      │   Connector      │   (Future)                │
└──────────────────┴──────────────────┴───────────────────────────┘
```

## Component Details

### 1. Client Layer

#### React Dashboard
- **Technology**: React 18 with TypeScript
- **State Management**: Redux Toolkit with RTK Query
- **UI Framework**: Material-UI or Chakra UI
- **Mapping**: Mapbox GL JS
- **Charts**: Recharts / D3.js

Key Features:
- Real-time data updates via WebSocket
- Responsive design for desktop and tablet
- Accessibility compliance (WCAG 2.1)
- Dark mode support

#### REST API Clients
- External systems integration
- Mobile applications
- Third-party dashboards

### 2. API Gateway

#### FastAPI Application
- **Framework**: FastAPI 0.100+
- **Authentication**: JWT with OAuth2
- **Validation**: Pydantic v2
- **Documentation**: OpenAPI/Swagger auto-generation

Features:
- Request/response validation
- Rate limiting (per user, per endpoint)
- CORS configuration
- Request logging and tracing
- Health checks

### 3. Application Layer

#### ACLED Service
Responsibilities:
- Fetch and parse ACLED API data
- Normalize event data
- Calculate conflict metrics
- Provide query interface

Components:
```
acled_service/
├── client.py          # ACLED API client
├── parser.py          # Data parsing and normalization
├── metrics.py         # Conflict metric calculations
├── repository.py      # Database operations
└── schemas.py         # Pydantic models
```

#### GDELT Service
Responsibilities:
- Query GDELT 2.0 API
- Process event and sentiment data
- Aggregate media tone metrics
- Cross-reference with ACLED

Components:
```
gdelt_service/
├── client.py          # GDELT API client
├── sentiment.py       # Sentiment analysis
├── correlation.py     # Event correlation engine
├── repository.py      # Database operations
└── schemas.py         # Pydantic models
```

#### Risk Engine
Core calculation service for composite risk scores.

Components:
```
risk_engine/
├── calculator.py      # Main risk calculation logic
├── factors/
│   ├── conflict.py    # Conflict risk factor
│   ├── sentiment.py   # Sentiment risk factor
│   ├── political.py   # Political stability factor
│   └── economic.py    # Economic risk factor
├── weights.py         # Weight management
├── alerts.py          # Alert generation
└── schemas.py         # Pydantic models
```

Risk Calculation Algorithm:
```python
def calculate_composite_score(region, weights):
    factors = {
        'conflict': calculate_conflict_score(region),
        'sentiment': calculate_sentiment_score(region),
        'political': calculate_political_score(region),
        'economic': calculate_economic_score(region)
    }

    weighted_sum = sum(
        factors[f] * weights[f] * get_confidence(f, region)
        for f in factors
    )

    total_weight = sum(weights.values())

    return weighted_sum / total_weight
```

#### Scenario Service
Handles scenario creation and simulation.

Components:
```
scenario_service/
├── builder.py         # Scenario creation
├── simulator.py       # Monte Carlo simulation
├── impact.py          # Impact calculation
├── templates.py       # Scenario templates
└── schemas.py         # Pydantic models
```

Simulation Process:
1. Load scenario parameters
2. Generate random variations (Monte Carlo)
3. Apply impact functions
4. Calculate regional spillover
5. Aggregate results with confidence intervals

#### Company Service
Manages company profiles and exposure analysis.

Components:
```
company_service/
├── profiles.py        # Company CRUD operations
├── locations.py       # Location management
├── exposure.py        # Exposure calculation
├── alerts.py          # Company-specific alerts
└── schemas.py         # Pydantic models
```

### 4. Data Layer

#### PostgreSQL Database
- **Version**: 15+ with PostGIS extension
- **Purpose**: Primary data storage

Schema Design:
```sql
-- Core tables
regions
events (partitioned by date)
risk_scores (time-series)
companies
company_locations

-- Supporting tables
users
api_keys
scenarios
simulations
alerts
weight_presets
```

Key Design Decisions:
- Time-series partitioning for events
- PostGIS for geospatial queries
- JSONB for flexible metadata
- Materialized views for aggregations

#### Redis
- **Version**: 7+
- **Purpose**: Caching, sessions, task queue

Use Cases:
- API response caching (TTL: 5-60 minutes)
- Session storage
- Rate limiting counters
- Celery message broker
- Real-time score caching

Cache Strategy:
```python
# Cache key patterns
f"risk:score:{region}:{timestamp}"
f"acled:events:{query_hash}"
f"gdelt:sentiment:{region}:{date}"
f"company:exposure:{company_id}"
```

#### Celery Workers
- **Broker**: Redis
- **Backend**: Redis
- **Purpose**: Background task processing

Task Types:
- Data ingestion (scheduled)
- Score calculations (on-demand)
- Report generation (async)
- Alert processing (event-driven)
- Simulation execution (compute-intensive)

### 5. Data Ingestion Layer

#### ACLED Connector
- Schedule: Daily at 02:00 UTC
- Rate limit handling: Exponential backoff
- Incremental updates: Last sync timestamp
- Historical backfill: Configurable date range

Process:
```
1. Check last sync timestamp
2. Fetch new/updated events
3. Validate and normalize data
4. Deduplicate against existing
5. Bulk insert to database
6. Update sync metadata
7. Trigger score recalculation
```

#### GDELT Connector
- Schedule: Every 15 minutes
- Data volume: High (millions of events)
- Selective ingestion: Region/theme filters

Process:
```
1. Query GDELT for time window
2. Filter by relevance criteria
3. Extract tone and metadata
4. Aggregate by region/theme
5. Store aggregations
6. Correlate with ACLED events
```

## Data Flow

### Real-Time Risk Score Update

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  ACLED  │────▶│ Ingest  │────▶│  Store  │────▶│ Notify  │
│   API   │     │ Worker  │     │   DB    │     │  Cache  │
└─────────┘     └─────────┘     └────┬────┘     └─────────┘
                                     │
                                     ▼
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │◀────│   API   │◀────│  Risk   │◀────│ Trigger │
│Dashboard│     │ Gateway │     │ Engine  │     │  Calc   │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
```

### Scenario Simulation Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────▶│ Create  │────▶│  Queue  │────▶│  Monte  │
│  Input  │     │Scenario │     │  Task   │     │  Carlo  │
└─────────┘     └─────────┘     └─────────┘     └────┬────┘
                                                     │
                                                     ▼
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Display │◀────│  Fetch  │◀────│  Store  │◀────│Aggregate│
│ Results │     │ Results │     │ Results │     │ Results │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
```

## Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────────────┐
│              Security Layer                  │
├─────────────────────────────────────────────┤
│  JWT Tokens    │  Role-Based Access Control │
│  API Keys      │  Resource-Level Permissions│
│  OAuth2 Flow   │  Audit Logging            │
└─────────────────────────────────────────────┘
```

Roles:
- **Admin**: Full system access
- **Analyst**: Read/write on risk and scenarios
- **Viewer**: Read-only access
- **API User**: Programmatic access only

### Data Security

- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Database connection pooling with SSL
- Secrets management (environment variables / Vault)
- PII handling compliance

### API Security

- Input validation on all endpoints
- SQL injection prevention (parameterized queries)
- XSS protection (content security policy)
- Rate limiting per user/IP
- Request size limits

## Scalability Considerations

### Horizontal Scaling

```
                    ┌─────────────┐
                    │   Load      │
                    │  Balancer   │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  API Pod 1  │ │  API Pod 2  │ │  API Pod N  │
    └─────────────┘ └─────────────┘ └─────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           ▼
    ┌─────────────────────────────────────────────┐
    │              Shared Services                │
    ├─────────────┬─────────────┬────────────────┤
    │  PostgreSQL │    Redis    │     Celery     │
    │  (Primary/  │  (Cluster)  │   (Workers)    │
    │   Replica)  │             │                │
    └─────────────┴─────────────┴────────────────┘
```

### Performance Optimizations

1. **Database**
   - Read replicas for query distribution
   - Connection pooling (PgBouncer)
   - Query optimization and indexing
   - Partitioning for large tables

2. **Caching**
   - Multi-tier caching (Redis + application)
   - Cache invalidation strategies
   - Pre-computation of common queries

3. **API**
   - Response compression
   - Pagination for large datasets
   - Async endpoints where appropriate

4. **Frontend**
   - Code splitting and lazy loading
   - CDN for static assets
   - Service worker caching

## Deployment Architecture

### Development Environment

```yaml
# docker-compose.yml
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [db, redis]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]

  db:
    image: postgis/postgis:15

  redis:
    image: redis:7

  celery:
    build: ./backend
    command: celery worker
```

### Production Environment (Kubernetes)

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Ingress    │  │  ConfigMaps  │  │   Secrets    │       │
│  │  Controller  │  │              │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │              Application Namespace                │       │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐          │       │
│  │  │ API     │  │Frontend │  │ Celery  │          │       │
│  │  │Deployment│ │Deployment│ │Deployment│          │       │
│  │  │ (3 pods)│  │ (2 pods)│  │ (5 pods)│          │       │
│  │  └─────────┘  └─────────┘  └─────────┘          │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │              Data Namespace                       │       │
│  │  ┌─────────┐  ┌─────────┐                        │       │
│  │  │PostgreSQL│ │  Redis  │                        │       │
│  │  │ (HA)    │  │(Cluster)│                        │       │
│  │  └─────────┘  └─────────┘                        │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Monitoring & Observability

### Metrics Stack

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Application │────▶│ Prometheus  │────▶│   Grafana   │
│   Metrics   │     │             │     │  Dashboard  │
└─────────────┘     └─────────────┘     └─────────────┘
```

Key Metrics:
- API response times (p50, p95, p99)
- Request rates and error rates
- Database query performance
- Cache hit ratios
- Background task completion rates
- Data freshness indicators

### Logging Stack

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Application │────▶│   Fluentd   │────▶│Elasticsearch│
│    Logs     │     │             │     │   Kibana    │
└─────────────┘     └─────────────┘     └─────────────┘
```

Log Levels:
- ERROR: System failures
- WARN: Potential issues
- INFO: Business events
- DEBUG: Detailed diagnostics

### Alerting

Alert Categories:
- **Critical**: System down, data pipeline failure
- **Warning**: High latency, approaching limits
- **Info**: Deployments, scheduled maintenance

## Future Considerations

### Planned Enhancements

1. **Machine Learning Pipeline**
   - Predictive risk scoring
   - Anomaly detection
   - Natural language processing for news

2. **Real-Time Streaming**
   - Apache Kafka for event streaming
   - Real-time dashboard updates
   - Complex event processing

3. **Additional Data Sources**
   - Economic indicators (IMF, World Bank)
   - Social media sentiment
   - Satellite imagery analysis

4. **Multi-Tenancy**
   - Isolated data per organization
   - Custom configurations
   - White-labeling support

### Technical Debt Tracking

- Regular dependency updates
- Security vulnerability scanning
- Performance regression testing
- Documentation maintenance

## Appendix

### Technology Stack Summary

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | React | 18.x |
| UI Components | Material-UI | 5.x |
| State Management | Redux Toolkit | 2.x |
| Backend | FastAPI | 0.100+ |
| ORM | SQLAlchemy | 2.x |
| Database | PostgreSQL + PostGIS | 15+ |
| Cache | Redis | 7+ |
| Task Queue | Celery | 5.x |
| Containerization | Docker | 24+ |
| Orchestration | Kubernetes | 1.28+ |

### Related Documentation

- [API Reference](../api/README.md)
- [User Guide](../guides/user-guide.md)
- [Development Roadmap](../../ROADMAP.md)
