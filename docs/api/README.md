# Geopolitix API Reference

## Overview

The Geopolitix API provides RESTful endpoints for accessing geopolitical risk data, managing risk calculations, running scenario simulations, and analyzing company exposure. All endpoints require authentication unless otherwise noted.

**Base URL**: `http://localhost:8000/api/v1`

**API Version**: 1.0

## Authentication

### Obtain Access Token

```http
POST /auth/token
```

**Request Body** (form-urlencoded):
| Field | Type | Description |
|-------|------|-------------|
| `username` | string | User email address |
| `password` | string | User password |

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using the Token

Include the token in the Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## ACLED Endpoints

### List Conflict Events

```http
GET /acled/events
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `country` | string | Filter by country name |
| `region` | string | Filter by region code |
| `event_type` | string | Filter by event type |
| `start_date` | date | Start date (YYYY-MM-DD) |
| `end_date` | date | End date (YYYY-MM-DD) |
| `limit` | integer | Number of results (default: 100, max: 1000) |
| `offset` | integer | Pagination offset |

**Response**:
```json
{
  "total": 1250,
  "limit": 100,
  "offset": 0,
  "data": [
    {
      "id": "ACL-12345",
      "event_date": "2024-01-15",
      "event_type": "Battles",
      "sub_event_type": "Armed clash",
      "actor1": "Military Forces",
      "actor2": "Rebel Group",
      "country": "Ethiopia",
      "region": "Tigray",
      "location": "Mekelle",
      "latitude": 13.4967,
      "longitude": 39.4753,
      "fatalities": 12,
      "notes": "Clashes reported between...",
      "source": "Local News Agency"
    }
  ]
}
```

### Get Event Details

```http
GET /acled/events/{event_id}
```

**Response**:
```json
{
  "id": "ACL-12345",
  "event_date": "2024-01-15",
  "event_type": "Battles",
  "sub_event_type": "Armed clash",
  "actor1": "Military Forces",
  "actor1_type": "State Forces",
  "actor2": "Rebel Group",
  "actor2_type": "Rebel Groups",
  "interaction": 12,
  "country": "Ethiopia",
  "admin1": "Tigray",
  "admin2": "Central Zone",
  "admin3": "Mekelle",
  "location": "Mekelle",
  "latitude": 13.4967,
  "longitude": 39.4753,
  "geo_precision": 1,
  "fatalities": 12,
  "notes": "Clashes reported between military forces and rebel groups...",
  "source": "Local News Agency",
  "source_scale": "National",
  "timestamp": "2024-01-15T08:30:00Z"
}
```

### Get Conflict Statistics

```http
GET /acled/statistics
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `region` | string | Filter by region code |
| `start_date` | date | Start date |
| `end_date` | date | End date |
| `group_by` | string | Group by: `country`, `event_type`, `month` |

**Response**:
```json
{
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "summary": {
    "total_events": 3456,
    "total_fatalities": 1234,
    "countries_affected": 45,
    "avg_events_per_day": 111.5
  },
  "by_event_type": {
    "Battles": 1200,
    "Violence against civilians": 890,
    "Protests": 756,
    "Riots": 410,
    "Explosions/Remote violence": 200
  }
}
```

### Get Conflict Trends

```http
GET /acled/trends
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `region` | string | Region code |
| `interval` | string | `daily`, `weekly`, `monthly` |
| `periods` | integer | Number of periods (default: 12) |

**Response**:
```json
{
  "region": "MENA",
  "interval": "monthly",
  "data": [
    {
      "period": "2024-01",
      "events": 456,
      "fatalities": 234,
      "change_pct": 5.2
    },
    {
      "period": "2024-02",
      "events": 423,
      "fatalities": 198,
      "change_pct": -7.2
    }
  ]
}
```

### Get Regional Summary

```http
GET /acled/regions/{region_code}
```

**Response**:
```json
{
  "region_code": "MENA",
  "region_name": "Middle East and North Africa",
  "countries": ["Syria", "Yemen", "Iraq", "Libya"],
  "summary": {
    "total_events_30d": 1234,
    "total_fatalities_30d": 567,
    "trend": "increasing",
    "change_pct": 12.5
  },
  "top_event_types": [
    {"type": "Battles", "count": 456},
    {"type": "Explosions/Remote violence", "count": 234}
  ],
  "hotspots": [
    {"location": "Idlib", "country": "Syria", "events": 89},
    {"location": "Marib", "country": "Yemen", "events": 67}
  ]
}
```

---

## GDELT Endpoints

### List GDELT Events

```http
GET /gdelt/events
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Keyword search |
| `theme` | string | GDELT theme filter |
| `country` | string | Country code |
| `start_date` | datetime | Start datetime |
| `end_date` | datetime | End datetime |
| `tone_min` | float | Minimum tone score |
| `tone_max` | float | Maximum tone score |
| `limit` | integer | Results limit |

**Response**:
```json
{
  "total": 5678,
  "data": [
    {
      "id": "GDL-987654",
      "date": "2024-01-15T14:30:00Z",
      "source_url": "https://example.com/article",
      "source_name": "Example News",
      "title": "Trade negotiations...",
      "event_code": "036",
      "event_description": "Express intent to meet or negotiate",
      "actor1": "USA",
      "actor2": "CHN",
      "goldstein_scale": 4.0,
      "tone": -2.5,
      "location": "Washington DC",
      "latitude": 38.9072,
      "longitude": -77.0369
    }
  ]
}
```

### Get Sentiment Analysis

```http
GET /gdelt/sentiment
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `region` | string | Region code |
| `topic` | string | Topic/theme |
| `start_date` | date | Start date |
| `end_date` | date | End date |

**Response**:
```json
{
  "region": "UKR",
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "sentiment": {
    "average_tone": -3.2,
    "tone_range": [-8.5, 2.1],
    "volatility": 2.8,
    "trend": "deteriorating"
  },
  "coverage": {
    "total_articles": 45678,
    "sources": 234,
    "languages": 15
  },
  "top_themes": [
    {"theme": "MILITARY", "count": 12345, "avg_tone": -4.5},
    {"theme": "DIPLOMACY", "count": 8765, "avg_tone": -1.2}
  ]
}
```

### Get Event Trends

```http
GET /gdelt/trends
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `region` | string | Region code |
| `theme` | string | Theme filter |
| `interval` | string | `hourly`, `daily`, `weekly` |

**Response**:
```json
{
  "region": "UKR",
  "interval": "daily",
  "data": [
    {
      "date": "2024-01-15",
      "event_count": 1234,
      "avg_tone": -3.5,
      "coverage_intensity": 8.7
    }
  ]
}
```

### Get Source Analysis

```http
GET /gdelt/sources
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `region` | string | Region code |
| `limit` | integer | Number of sources |

**Response**:
```json
{
  "sources": [
    {
      "name": "Reuters",
      "domain": "reuters.com",
      "articles": 5678,
      "avg_tone": -1.2,
      "credibility_score": 0.95
    }
  ]
}
```

### Get Event Correlations

```http
GET /gdelt/correlations
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `region` | string | Region code |
| `start_date` | date | Start date |
| `end_date` | date | End date |

**Response**:
```json
{
  "correlations": [
    {
      "gdelt_event_id": "GDL-987654",
      "acled_event_id": "ACL-12345",
      "correlation_score": 0.85,
      "time_delta_hours": 12,
      "location_match": true
    }
  ]
}
```

---

## Risk Engine Endpoints

### Get Risk Scores

```http
GET /risk/scores
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `region` | string | Filter by region code |
| `threshold` | integer | Minimum score to return |

**Response**:
```json
{
  "timestamp": "2024-01-15T12:00:00Z",
  "scores": [
    {
      "region": "UKR",
      "region_name": "Ukraine",
      "composite_score": 78.5,
      "level": "High",
      "factors": {
        "conflict": 92.0,
        "sentiment": 75.0,
        "political": 68.0,
        "economic": 65.0
      },
      "change_24h": 2.5,
      "trend": "increasing"
    }
  ]
}
```

### Calculate Risk with Custom Weights

```http
POST /risk/scores/calculate
```

**Request Body**:
```json
{
  "region": "UKR",
  "weights": {
    "conflict": 0.4,
    "sentiment": 0.3,
    "political": 0.2,
    "economic": 0.1
  }
}
```

**Response**:
```json
{
  "region": "UKR",
  "composite_score": 81.2,
  "level": "High",
  "weights_applied": {
    "conflict": 0.4,
    "sentiment": 0.3,
    "political": 0.2,
    "economic": 0.1
  },
  "factor_contributions": {
    "conflict": 36.8,
    "sentiment": 22.5,
    "political": 13.6,
    "economic": 8.3
  },
  "confidence": 0.92
}
```

### Get Regional Risk Breakdown

```http
GET /risk/scores/{region}
```

**Response**:
```json
{
  "region": "UKR",
  "region_name": "Ukraine",
  "composite_score": 78.5,
  "level": "High",
  "factors": {
    "conflict": {
      "score": 92.0,
      "weight": 0.25,
      "contribution": 23.0,
      "components": {
        "event_frequency": 95,
        "fatality_rate": 88,
        "trend": 93
      }
    },
    "sentiment": {
      "score": 75.0,
      "weight": 0.25,
      "contribution": 18.75,
      "components": {
        "media_tone": 78,
        "coverage_intensity": 72,
        "volatility": 75
      }
    },
    "political": {
      "score": 68.0,
      "weight": 0.25,
      "contribution": 17.0,
      "components": {
        "stability": 65,
        "governance": 70,
        "transition_risk": 69
      }
    },
    "economic": {
      "score": 65.0,
      "weight": 0.25,
      "contribution": 16.25,
      "components": {
        "currency": 60,
        "trade": 68,
        "sanctions": 67
      }
    }
  },
  "historical": [
    {"date": "2024-01-14", "score": 76.0},
    {"date": "2024-01-13", "score": 74.5}
  ]
}
```

### Get Risk Factors

```http
GET /risk/factors
```

**Response**:
```json
{
  "factors": [
    {
      "id": "conflict",
      "name": "Conflict Risk",
      "description": "Based on ACLED event frequency and severity",
      "source": "ACLED",
      "components": ["event_frequency", "fatality_rate", "trend"],
      "default_weight": 0.25
    }
  ]
}
```

### Get Weight Configuration

```http
GET /risk/weights
```

**Response**:
```json
{
  "current": {
    "conflict": 0.25,
    "sentiment": 0.25,
    "political": 0.25,
    "economic": 0.25
  },
  "presets": [
    {
      "id": "security",
      "name": "Security-Focused",
      "weights": {"conflict": 0.5, "sentiment": 0.2, "political": 0.2, "economic": 0.1}
    }
  ]
}
```

### Update Weight Configuration

```http
PUT /risk/weights
```

**Request Body**:
```json
{
  "conflict": 0.4,
  "sentiment": 0.3,
  "political": 0.2,
  "economic": 0.1
}
```

**Response**:
```json
{
  "updated": true,
  "weights": {
    "conflict": 0.4,
    "sentiment": 0.3,
    "political": 0.2,
    "economic": 0.1
  }
}
```

### List Weight Presets

```http
GET /risk/presets
```

**Response**:
```json
{
  "presets": [
    {
      "id": "balanced",
      "name": "Balanced",
      "description": "Equal weights across all factors",
      "weights": {"conflict": 0.25, "sentiment": 0.25, "political": 0.25, "economic": 0.25},
      "is_default": true
    },
    {
      "id": "security",
      "name": "Security-Focused",
      "description": "Emphasizes conflict and political stability",
      "weights": {"conflict": 0.5, "sentiment": 0.1, "political": 0.3, "economic": 0.1}
    }
  ]
}
```

### Create Weight Preset

```http
POST /risk/presets
```

**Request Body**:
```json
{
  "name": "Custom Security",
  "description": "Custom weights for security analysis",
  "weights": {
    "conflict": 0.45,
    "sentiment": 0.15,
    "political": 0.25,
    "economic": 0.15
  }
}
```

### Get Historical Risk Scores

```http
GET /risk/history
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `region` | string | Region code |
| `start_date` | date | Start date |
| `end_date` | date | End date |
| `interval` | string | `hourly`, `daily`, `weekly` |

**Response**:
```json
{
  "region": "UKR",
  "interval": "daily",
  "history": [
    {
      "date": "2024-01-15",
      "composite_score": 78.5,
      "factors": {
        "conflict": 92.0,
        "sentiment": 75.0,
        "political": 68.0,
        "economic": 65.0
      }
    }
  ]
}
```

### Get Risk Alerts

```http
GET /risk/alerts
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `region` | string | Filter by region |
| `severity` | string | `low`, `medium`, `high`, `critical` |
| `unread` | boolean | Only unread alerts |

**Response**:
```json
{
  "alerts": [
    {
      "id": "alert-123",
      "timestamp": "2024-01-15T08:30:00Z",
      "region": "UKR",
      "type": "score_increase",
      "severity": "high",
      "title": "Significant risk increase in Ukraine",
      "message": "Composite risk score increased by 15% in the last 24 hours",
      "score_before": 68.0,
      "score_after": 78.5,
      "read": false
    }
  ]
}
```

---

## Scenario Endpoints

### List Scenarios

```http
GET /scenarios
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | `draft`, `active`, `archived` |
| `limit` | integer | Results limit |

**Response**:
```json
{
  "scenarios": [
    {
      "id": "scn-123",
      "name": "Regional Conflict Escalation",
      "description": "Scenario modeling increased conflict in MENA region",
      "status": "active",
      "created_at": "2024-01-10T10:00:00Z",
      "updated_at": "2024-01-15T08:00:00Z",
      "regions_affected": ["SYR", "IRQ", "LBN"],
      "probability": 0.35
    }
  ]
}
```

### Create Scenario

```http
POST /scenarios
```

**Request Body**:
```json
{
  "name": "Trade War Escalation",
  "description": "Modeling impact of increased tariffs",
  "trigger_event": "Major tariff announcement",
  "regions": ["USA", "CHN"],
  "parameters": {
    "duration_days": 180,
    "intensity": 0.7,
    "probability": 0.4
  },
  "impacts": {
    "economic": 25,
    "sentiment": 15,
    "political": 10
  }
}
```

**Response**:
```json
{
  "id": "scn-456",
  "name": "Trade War Escalation",
  "status": "draft",
  "created_at": "2024-01-15T12:00:00Z"
}
```

### Get Scenario Details

```http
GET /scenarios/{id}
```

**Response**:
```json
{
  "id": "scn-456",
  "name": "Trade War Escalation",
  "description": "Modeling impact of increased tariffs",
  "status": "active",
  "trigger_event": "Major tariff announcement",
  "regions": ["USA", "CHN"],
  "parameters": {
    "duration_days": 180,
    "intensity": 0.7,
    "probability": 0.4,
    "spillover_regions": ["JPN", "KOR", "TWN"]
  },
  "impacts": {
    "economic": 25,
    "sentiment": 15,
    "political": 10
  },
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

### Update Scenario

```http
PUT /scenarios/{id}
```

**Request Body**:
```json
{
  "name": "Trade War Escalation - Updated",
  "parameters": {
    "probability": 0.5
  }
}
```

### Delete Scenario

```http
DELETE /scenarios/{id}
```

### Run Simulation

```http
POST /scenarios/{id}/simulate
```

**Request Body**:
```json
{
  "iterations": 1000,
  "time_horizon_days": 90
}
```

**Response**:
```json
{
  "simulation_id": "sim-789",
  "status": "running",
  "started_at": "2024-01-15T14:00:00Z",
  "estimated_completion": "2024-01-15T14:05:00Z"
}
```

### Get Simulation Results

```http
GET /scenarios/{id}/results
```

**Response**:
```json
{
  "scenario_id": "scn-456",
  "simulation_id": "sim-789",
  "completed_at": "2024-01-15T14:05:00Z",
  "iterations": 1000,
  "results": {
    "risk_impact": {
      "mean": 18.5,
      "median": 17.2,
      "std_dev": 4.3,
      "percentile_5": 11.2,
      "percentile_95": 26.8
    },
    "by_region": [
      {
        "region": "USA",
        "current_score": 35.0,
        "projected_score": 48.5,
        "change": 13.5,
        "confidence_interval": [41.2, 55.8]
      }
    ],
    "timeline": [
      {
        "day": 30,
        "avg_impact": 8.5
      },
      {
        "day": 60,
        "avg_impact": 15.2
      }
    ]
  }
}
```

### List Scenario Templates

```http
GET /scenarios/templates
```

**Response**:
```json
{
  "templates": [
    {
      "id": "tpl-conflict",
      "name": "Armed Conflict Escalation",
      "description": "Template for modeling regional conflict intensification",
      "default_parameters": {
        "duration_days": 90,
        "intensity": 0.6
      }
    }
  ]
}
```

### Compare Scenarios

```http
POST /scenarios/compare
```

**Request Body**:
```json
{
  "scenario_ids": ["scn-123", "scn-456"],
  "regions": ["USA", "CHN"],
  "metrics": ["risk_impact", "economic_impact"]
}
```

### Export Scenario Report

```http
GET /scenarios/{id}/export
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | `pdf`, `xlsx`, `json` |

**Response**: File download or JSON data

---

## Company Endpoints

### List Companies

```http
GET /companies
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `industry` | string | Filter by industry |
| `risk_level` | string | Filter by risk level |
| `limit` | integer | Results limit |

**Response**:
```json
{
  "companies": [
    {
      "id": "comp-123",
      "name": "Acme Corporation",
      "industry": "Manufacturing",
      "headquarters": "New York, USA",
      "overall_risk_score": 45.2,
      "risk_level": "Moderate",
      "locations_count": 15
    }
  ]
}
```

### Create Company Profile

```http
POST /companies
```

**Request Body**:
```json
{
  "name": "Acme Corporation",
  "industry": "Manufacturing",
  "size": "large",
  "headquarters": {
    "country": "USA",
    "city": "New York",
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "locations": [
    {
      "type": "factory",
      "country": "CHN",
      "city": "Shanghai",
      "latitude": 31.2304,
      "longitude": 121.4737,
      "importance": "high"
    }
  ]
}
```

### Get Company Details

```http
GET /companies/{id}
```

**Response**:
```json
{
  "id": "comp-123",
  "name": "Acme Corporation",
  "industry": "Manufacturing",
  "size": "large",
  "headquarters": {
    "country": "USA",
    "city": "New York"
  },
  "locations": [
    {
      "id": "loc-456",
      "type": "factory",
      "country": "CHN",
      "city": "Shanghai",
      "importance": "high",
      "risk_score": 42.0
    }
  ],
  "overall_risk_score": 45.2,
  "risk_breakdown": {
    "by_location": [
      {"location_id": "loc-456", "contribution": 15.5}
    ]
  }
}
```

### Update Company

```http
PUT /companies/{id}
```

### Delete Company

```http
DELETE /companies/{id}
```

### Get Company Exposure Analysis

```http
GET /companies/{id}/exposure
```

**Response**:
```json
{
  "company_id": "comp-123",
  "overall_exposure_score": 45.2,
  "exposure_by_factor": {
    "conflict": 35.0,
    "sentiment": 42.0,
    "political": 48.0,
    "economic": 55.0
  },
  "geographic_exposure": {
    "high_risk_locations": 3,
    "total_locations": 15,
    "most_exposed_region": "MENA"
  },
  "recommendations": [
    {
      "priority": "high",
      "type": "diversification",
      "message": "Consider diversifying supply chain away from high-risk regions"
    }
  ]
}
```

### Get Company Locations

```http
GET /companies/{id}/locations
```

### Add Company Location

```http
POST /companies/{id}/locations
```

### Get Company Alerts

```http
GET /companies/{id}/alerts
```

### Configure Company Alerts

```http
PUT /companies/{id}/alerts
```

**Request Body**:
```json
{
  "thresholds": {
    "overall_risk": 60,
    "location_risk": 70,
    "risk_change": 10
  },
  "notifications": {
    "email": true,
    "webhook_url": "https://example.com/webhooks/geopolitix"
  }
}
```

### Get Company Reports

```http
GET /companies/{id}/reports
```

### Generate Company Report

```http
POST /companies/{id}/reports
```

**Request Body**:
```json
{
  "type": "executive_summary",
  "period": "monthly",
  "format": "pdf"
}
```

### Compare Companies

```http
GET /companies/compare
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `ids` | string | Comma-separated company IDs |

### Bulk Import Companies

```http
POST /companies/import
```

**Request Body**: Multipart form with CSV file

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid region code",
    "details": {
      "field": "region",
      "value": "INVALID"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_REQUIRED` | 401 | No valid token provided |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

- **Default**: 100 requests per minute
- **Authenticated**: 1000 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1705320000
```

---

## Webhooks

Configure webhooks to receive real-time notifications:

### Webhook Events

- `risk.score_changed` - Risk score changed significantly
- `risk.alert_triggered` - Alert threshold exceeded
- `company.location_risk_changed` - Company location risk changed
- `scenario.simulation_completed` - Simulation finished

### Webhook Payload

```json
{
  "event": "risk.alert_triggered",
  "timestamp": "2024-01-15T08:30:00Z",
  "data": {
    "alert_id": "alert-123",
    "region": "UKR",
    "severity": "high",
    "score_change": 15.0
  }
}
```

---

## SDKs and Libraries

- **Python**: `pip install geopolitix-python`
- **JavaScript/Node.js**: `npm install geopolitix-js`
- **Go**: `go get github.com/geopolitix/geopolitix-go`

---

## Changelog

### v1.0 (2025-11-19)
- Initial API release
- ACLED and GDELT integration
- Composite risk engine
- Scenario modeling
- Company exposure analysis
