# Geopolitix User Guide

## Introduction

Welcome to Geopolitix, a comprehensive platform for analyzing geopolitical risks and their potential impact on your business. This guide will help you understand and use all features of the dashboard effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Viewing Conflict Data](#viewing-conflict-data)
4. [Analyzing Sentiment](#analyzing-sentiment)
5. [Understanding Risk Scores](#understanding-risk-scores)
6. [Customizing Risk Weights](#customizing-risk-weights)
7. [Scenario Modeling](#scenario-modeling)
8. [Company Exposure Analysis](#company-exposure-analysis)
9. [Alerts and Notifications](#alerts-and-notifications)
10. [Generating Reports](#generating-reports)
11. [API Integration](#api-integration)
12. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Creating an Account

1. Navigate to the Geopolitix login page
2. Click "Create Account"
3. Enter your email address and create a password
4. Verify your email address
5. Complete your profile setup

### Initial Configuration

After logging in for the first time:

1. **Select your focus regions** - Choose the geographic areas most relevant to your operations
2. **Set your industry** - This helps customize risk factors
3. **Configure notification preferences** - Choose how you want to receive alerts

### Navigation

The main navigation menu includes:

- **Dashboard** - Overview of global risks
- **Conflicts** - ACLED conflict event data
- **Sentiment** - GDELT media sentiment analysis
- **Risk Scores** - Composite risk calculations
- **Scenarios** - Scenario modeling tools
- **Companies** - Company exposure analysis
- **Reports** - Generated reports
- **Settings** - Account and configuration

---

## Dashboard Overview

The main dashboard provides a comprehensive view of global geopolitical risks.

### Components

#### Global Risk Map
- Interactive world map showing risk levels by region
- Color-coded by risk severity (green to red)
- Click any region for detailed information
- Zoom and pan for closer inspection

#### Risk Summary Panel
- Top 10 highest-risk regions
- 24-hour risk changes
- Active alerts count
- Data freshness indicator

#### Trend Charts
- Risk score trends over time
- Conflict event frequency
- Sentiment analysis trends

#### Recent Events Feed
- Latest significant events
- Source and time stamps
- Quick-view details

### Customizing the Dashboard

1. Click the "Customize" button in the top-right corner
2. Drag and drop widgets to rearrange
3. Add or remove widgets from the panel
4. Save your layout

---

## Viewing Conflict Data

The Conflicts section displays ACLED (Armed Conflict Location & Event Data) information.

### Event Map

The event map shows conflict locations:

- **Markers**: Individual conflict events
- **Clusters**: Grouped events (click to expand)
- **Heatmap**: Toggle for density visualization

#### Marker Colors
- Red: Battles and armed clashes
- Orange: Violence against civilians
- Yellow: Protests
- Blue: Riots
- Purple: Strategic developments

### Filtering Events

Use the filter panel to narrow results:

1. **Date Range**: Select start and end dates
2. **Country/Region**: Choose specific locations
3. **Event Type**: Select one or more event types
4. **Actors**: Filter by involved parties
5. **Fatalities**: Set minimum/maximum thresholds

### Event Details

Click any event to view:

- Full event description
- Actor information
- Casualty numbers
- Source attribution
- Related events

### Exporting Data

1. Apply your desired filters
2. Click "Export" button
3. Choose format (CSV, JSON, Excel)
4. Download the file

---

## Analyzing Sentiment

The Sentiment section provides media tone analysis from GDELT data.

### Sentiment Overview

The overview shows:

- **Average Tone**: Overall media sentiment (-10 to +10)
- **Coverage Intensity**: Volume of media coverage
- **Volatility**: How much sentiment fluctuates
- **Trend Direction**: Improving or deteriorating

### Regional Sentiment

View sentiment by region:

1. Select a region from the dropdown or map
2. View sentiment timeline
3. Compare with historical averages
4. See top contributing themes

### Theme Analysis

Explore sentiment by topic:

- Military/Security
- Diplomacy
- Economic
- Social/Humanitarian
- Political

### Source Breakdown

Understand where information comes from:

- Source credibility ratings
- Geographic distribution
- Language breakdown
- Publication types

---

## Understanding Risk Scores

Risk scores provide a unified measure of geopolitical risk.

### Composite Score

The composite score (0-100) combines multiple factors:

| Score Range | Level | Meaning |
|-------------|-------|---------|
| 0-20 | Low | Minimal risk, stable environment |
| 21-40 | Moderate | Some concerns, monitor situation |
| 41-60 | Elevated | Significant risks, heightened vigilance |
| 61-80 | High | Serious risks, consider mitigation |
| 81-100 | Critical | Extreme risk, immediate action needed |

### Risk Factors

Four main factors contribute to the score:

#### 1. Conflict Risk
Based on ACLED data:
- Event frequency
- Casualty rates
- Actor involvement
- Trend direction

#### 2. Sentiment Risk
Based on GDELT data:
- Media tone
- Coverage intensity
- Source consensus
- Volatility

#### 3. Political Stability
Based on governance indicators:
- Government effectiveness
- Regime stability
- Election/transition risks

#### 4. Economic Risk
Based on economic indicators:
- Currency stability
- Trade disruption
- Sanctions impact

### Viewing Breakdowns

To see how a score is calculated:

1. Click on any region's risk score
2. View the "Factor Breakdown" panel
3. Expand each factor for component details
4. See historical factor trends

---

## Customizing Risk Weights

Adjust how factors contribute to the composite score.

### Why Customize Weights?

Different use cases require different emphasis:

- **Security teams**: Prioritize conflict data
- **PR/Communications**: Prioritize sentiment
- **Investors**: Prioritize economic factors
- **General**: Balanced approach

### Adjusting Weights

1. Navigate to **Risk Scores > Settings**
2. Use sliders to adjust each factor weight (0% to 100%)
3. Weights automatically normalize to total 100%
4. Preview the impact on scores
5. Click "Apply" to save

### Using Presets

Pre-configured weight sets are available:

- **Balanced**: Equal weights (25% each)
- **Security-Focused**: Conflict 50%, Political 30%, Sentiment 10%, Economic 10%
- **Reputation-Focused**: Sentiment 50%, Conflict 20%, Political 20%, Economic 10%
- **Investment-Focused**: Economic 40%, Political 30%, Conflict 20%, Sentiment 10%

To use a preset:
1. Click "Load Preset"
2. Select from the dropdown
3. Optionally fine-tune
4. Apply the weights

### Creating Custom Presets

1. Configure weights as desired
2. Click "Save as Preset"
3. Name your preset
4. Add optional description
5. Save

---

## Scenario Modeling

Model hypothetical situations and assess potential impacts.

### Creating a Scenario

1. Navigate to **Scenarios > Create New**
2. Choose a template or start from scratch
3. Define scenario parameters:
   - **Name**: Descriptive title
   - **Trigger Event**: What initiates the scenario
   - **Regions**: Affected geographic areas
   - **Duration**: Expected timeframe
   - **Intensity**: Severity level (0-1)
   - **Probability**: Likelihood assessment

### Available Templates

- **Armed Conflict Escalation**: Regional military conflict
- **Political Transition**: Government change or instability
- **Economic Sanctions**: Trade restrictions
- **Natural Disaster**: Environmental crisis
- **Civil Unrest**: Protests and social upheaval
- **Cyber Attack**: Digital infrastructure threat

### Running Simulations

1. Open your scenario
2. Click "Run Simulation"
3. Configure iterations (recommended: 1000+)
4. Set time horizon
5. Start simulation

Simulations use Monte Carlo methods to generate probability distributions.

### Interpreting Results

Results include:

- **Mean Impact**: Average risk score change
- **Confidence Interval**: Range of likely outcomes (5th-95th percentile)
- **Timeline**: How impacts evolve over time
- **Regional Breakdown**: Impact by affected region
- **Spillover Effects**: Secondary regional impacts

### Comparing Scenarios

1. Select multiple scenarios (checkbox)
2. Click "Compare"
3. View side-by-side analysis
4. Identify best/worst case scenarios

---

## Company Exposure Analysis

Analyze how your organization's geographic footprint intersects with geopolitical risks.

### Adding Your Company

1. Navigate to **Companies > Add Company**
2. Enter basic information:
   - Company name
   - Industry
   - Size
   - Headquarters location

### Mapping Locations

Add all relevant locations:

1. Click "Add Location"
2. Select location type:
   - Headquarters
   - Office
   - Factory/Plant
   - Warehouse
   - Data Center
   - Supplier
   - Customer
3. Enter address or coordinates
4. Set importance level (Low/Medium/High/Critical)
5. Add optional notes

### Bulk Import

For many locations:

1. Download the CSV template
2. Fill in location data
3. Upload the completed file
4. Review and confirm

### Exposure Dashboard

View your company's risk profile:

- **Overall Exposure Score**: Weighted average of all locations
- **Location Risk Table**: Risk score per location
- **Factor Breakdown**: Which risk factors affect you most
- **Geographic Heatmap**: Visual risk distribution
- **Trend Analysis**: How exposure changes over time

### Recommendations

The system provides actionable insights:

- High-priority risks to address
- Diversification opportunities
- Monitoring suggestions
- Mitigation strategies

---

## Alerts and Notifications

Stay informed of significant risk changes.

### Alert Types

- **Score Change**: Composite score changes significantly
- **Threshold Breach**: Score exceeds your defined level
- **New Event**: Significant event in your regions
- **Trend Alert**: Sustained increase/decrease in risk
- **Company Alert**: Risk change at your locations

### Configuring Alerts

1. Navigate to **Settings > Alerts**
2. For each alert type:
   - Enable/disable
   - Set thresholds
   - Choose severity triggers
   - Select regions/companies

### Notification Channels

Choose how to receive alerts:

- **Email**: Detailed notifications to your inbox
- **Dashboard**: In-app notification center
- **Webhook**: POST to your URL for integration
- **SMS**: Critical alerts (Premium plan)

### Managing Alert History

View and manage past alerts:

1. Go to **Alerts > History**
2. Filter by type, date, severity
3. Mark as read/unread
4. Export for records

---

## Generating Reports

Create professional reports for stakeholders.

### Report Types

#### Executive Summary
- High-level overview
- Key risk indicators
- Major changes
- Recommendations

#### Regional Analysis
- Deep dive into specific regions
- Historical trends
- Event analysis
- Forecast

#### Company Exposure
- Your organization's risk profile
- Location analysis
- Peer comparison
- Action items

#### Scenario Report
- Simulation results
- Impact analysis
- Probability assessments
- Decision support

### Creating a Report

1. Navigate to **Reports > Generate**
2. Select report type
3. Configure parameters:
   - Time period
   - Regions/Companies
   - Sections to include
4. Choose format (PDF, Word, Excel)
5. Generate report

### Scheduling Reports

Automate regular reports:

1. Create a report configuration
2. Click "Schedule"
3. Set frequency (daily, weekly, monthly)
4. Add recipients
5. Activate schedule

---

## API Integration

Integrate Geopolitix data into your systems.

### Getting API Keys

1. Navigate to **Settings > API**
2. Click "Generate New Key"
3. Name your key
4. Set permissions
5. Copy and secure your key

### Basic Usage

```bash
# Get risk scores
curl https://api.geopolitix.io/v1/risk/scores \
  -H "Authorization: Bearer YOUR_API_KEY"

# Get events
curl "https://api.geopolitix.io/v1/acled/events?country=Ukraine" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Rate Limits

- Standard: 1,000 requests/minute
- Premium: 10,000 requests/minute

### SDKs

Official SDKs are available:

- Python: `pip install geopolitix-python`
- JavaScript: `npm install geopolitix-js`

### Documentation

Full API documentation is available at:
- Interactive: https://api.geopolitix.io/docs
- Reference: [API Reference](../api/README.md)

---

## Troubleshooting

### Common Issues

#### Data Not Loading
1. Check your internet connection
2. Clear browser cache
3. Try a different browser
4. Contact support if persistent

#### Scores Not Updating
- Risk scores update hourly
- Check the "Last Updated" timestamp
- Manual refresh: click the refresh icon
- If stale, report to support

#### Map Not Displaying
1. Enable WebGL in browser settings
2. Update your browser
3. Disable browser extensions
4. Try incognito mode

#### Export Failing
1. Reduce date range or filters
2. Try a different format
3. Check download permissions
4. Contact support for large exports

### Getting Help

- **In-app Help**: Click the "?" icon on any page
- **Documentation**: https://docs.geopolitix.io
- **Support Email**: support@geopolitix.io
- **Status Page**: https://status.geopolitix.io

### Providing Feedback

We value your input:

1. Click "Feedback" in the footer
2. Describe your issue or suggestion
3. Attach screenshots if helpful
4. Submit

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open search | Ctrl/Cmd + K |
| Toggle sidebar | Ctrl/Cmd + B |
| Refresh data | Ctrl/Cmd + R |
| New scenario | Ctrl/Cmd + N |
| Export view | Ctrl/Cmd + E |
| Help | Ctrl/Cmd + ? |

---

## Glossary

**ACLED**: Armed Conflict Location & Event Data - Source for conflict event information

**CAMEO**: Conflict and Mediation Event Observations - Coding system for political events

**Composite Score**: Weighted combination of all risk factors

**GDELT**: Global Database of Events, Language, and Tone - Source for media sentiment

**Goldstein Scale**: Measure of event impact (-10 to +10)

**Monte Carlo Simulation**: Statistical method using random sampling

**Spillover**: Secondary effects in neighboring regions

**Tone**: GDELT measure of media sentiment (-10 to +10)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-19 | Initial release |

---

## Appendix: Data Sources

### ACLED
- Coverage: Global
- Update Frequency: Daily
- Event Types: 6 main categories
- Website: https://acleddata.com

### GDELT
- Coverage: Global
- Update Frequency: 15 minutes
- Languages: 100+
- Website: https://gdeltproject.org
