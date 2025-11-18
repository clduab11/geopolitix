# GEOPOLITIX User Guide

Welcome to GEOPOLITIX, your comprehensive geopolitical risk analysis dashboard. This guide will help you navigate and utilize all features of the platform.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Global Overview](#global-overview)
3. [Risk Analytics](#risk-analytics)
4. [Scenario Modeling](#scenario-modeling)
5. [Company Exposure](#company-exposure)
6. [Understanding Risk Scores](#understanding-risk-scores)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### Accessing the Dashboard

1. Open your web browser
2. Navigate to `http://your-server:8050`
3. The dashboard loads with the Global Overview tab

### Dashboard Layout

The dashboard consists of:
- **Header**: Application title, refresh button, last updated time
- **Tab Navigation**: Switch between main views
- **Content Area**: Active tab content

### Refreshing Data

Data automatically refreshes every 15 minutes. To manually refresh:
- Click the **Refresh Data** button in the header
- New data is fetched from all sources

## Global Overview

The default view provides a high-level picture of global geopolitical risk.

### World Risk Map

**Interactive Features:**
- **Hover**: View country name and risk score
- **Click**: (Future) Drill down to country details
- **Zoom**: Use scroll or controls to zoom
- **Pan**: Click and drag to move

**Color Legend:**
- Green: Low risk (0-25)
- Yellow/Orange: Moderate risk (26-50)
- Red: High risk (51-75)
- Purple: Critical risk (76-100)

### Risk Summary Cards

Three key metrics:
- **Average Risk**: Mean score across all monitored countries
- **High Risk**: Count of countries with score ≥70
- **Critical**: Count of countries with score ≥85

### Recent Alerts

Real-time feed of significant risk events:
- Red badge: Critical alerts
- Orange badge: High-risk alerts
- Each alert shows country, score, and timestamp

### Highest Risk Countries

Top 5 countries by composite risk score:
- Country name
- Current risk score (color-coded badge)

## Risk Analytics

Deep-dive analysis tools for comparing and tracking risk.

### Analysis Controls

**Select Countries:**
- Click dropdown to see available countries
- Select multiple countries for comparison
- Remove selections by clicking ×

**Time Range:**
- 7 Days: Short-term trends
- 30 Days: Monthly patterns
- 90 Days: Quarterly analysis
- 1 Year: Long-term trends

**Chart Type:**
- Bar Chart: Side-by-side comparison
- Radar Chart: Multi-factor profile view

### Trends Tab

Line chart showing risk score evolution:
- Each country as separate line
- Threshold lines at 25, 50, 75
- Hover for exact values

**Interpreting Trends:**
- Rising line: Increasing risk
- Falling line: Decreasing risk
- Volatile line: Unstable situation

### Comparison Tab

Compare risk factors across countries:

**Bar Chart View:**
- Groups of 4 bars per country (Political, Economic, Security, Trade)
- Easy to spot which factor drives risk

**Radar Chart View:**
- Pentagon shape per country
- Larger area = higher overall risk
- Useful for profile comparison

### Correlations Tab

Heat map showing relationships between factors:
- Dark red: Strong positive correlation
- Dark blue: Strong negative correlation
- White: No correlation

**Example Insights:**
- High security risk often correlates with high political risk
- Trade risk may be independent of other factors

## Scenario Modeling

Test hypothetical geopolitical events and their impact.

### Creating a Scenario

1. **Select Template:**
   - Trade Embargo: Economic isolation between countries
   - Military Conflict: Armed confrontation
   - Economic Sanctions: International penalties
   - Political Crisis: Government instability
   - Natural Disaster: Major catastrophic event
   - Custom: Define your own parameters

2. **Select Affected Countries:**
   - Choose one or more countries
   - These will receive the scenario impact

3. **Set Severity (1-10):**
   - 1-3: Minor event, limited impact
   - 4-6: Moderate event, significant impact
   - 7-10: Major event, severe impact

4. **Set Duration:**
   - Enter expected duration in months
   - Longer duration = sustained impact

5. **Run Scenario:**
   - Click "Run Scenario" button
   - Results appear in right panel

### Understanding Results

**Impact Cards:**
- Current score → Projected score
- Change amount (positive = increased risk)
- Color indicates severity of change

**Comparison Chart:**
- Blue bars: Current factor scores
- Coral bars: Projected scores
- Visual representation of impact

### Exporting Scenarios

**Export as JSON:**
- Click "Export as JSON"
- Save file for later reference
- Can be shared with team

**Generate Report:**
- Click "Generate Report"
- Creates PDF summary (future feature)

## Company Exposure

Assess your organization's risk based on geographic presence.

### Adding Exposure Data

**Upload CSV File:**
1. Prepare CSV with columns:
   - `country`: Country name
   - `type`: Location type
   - `value`: Value in millions ($)
2. Drag and drop or click to select
3. Data appears in Exposure Locations list

**Manual Entry:**
1. Enter Country name
2. Select Type:
   - Manufacturing: Production facilities
   - Supply Chain: Suppliers, logistics
   - Market: Sales territories
   - Headquarters: Corporate offices
3. Enter Value (in millions)
4. Click "Add Location"

### Exposure Analysis

**Risk Exposure Analysis:**
- Total Exposure: Sum of all location values
- Weighted Risk: Value-weighted average risk
- Risk Level: Overall classification

**Exposure by Region (Pie Chart):**
- Distribution of value by location type
- Helps identify concentration risks

**Risk by Location (Bar Chart):**
- Risk score for each location
- Colored by location type
- Higher bars = higher risk

### Priority Actions

Automatically generated recommendations:
- **Immediate review**: Risk score >70
- **Monitor closely**: Risk score 50-70
- **Maintain status**: Risk score <50

## Understanding Risk Scores

### Score Components

The composite score (0-100) combines four factors:

**Political (25%):**
- Government stability
- Democratic institutions
- Corruption levels
- Rule of law

**Economic (25%):**
- Economic growth
- Inflation
- Currency stability
- Debt levels

**Security (30%):**
- Armed conflicts
- Terrorism risk
- Civil unrest
- Border security

**Trade (20%):**
- Tariff barriers
- Sanctions
- Trade disputes
- Supply chain risk

### Score Interpretation

| Score | Level | Action |
|-------|-------|--------|
| 0-25 | Low | Monitor quarterly |
| 26-50 | Moderate | Monitor monthly |
| 51-75 | High | Active management |
| 76-100 | Critical | Immediate action |

### Data Sources

Scores are derived from:
- **GDELT**: News sentiment and volume
- **NewsAPI**: Current events sentiment
- **World Bank**: Governance indicators
- **ACLED**: Conflict events and fatalities

## Best Practices

### Regular Monitoring

1. Check dashboard daily for alerts
2. Review trends weekly
3. Update company exposure quarterly
4. Run scenarios for major events

### Scenario Planning

1. Model potential events before they occur
2. Test multiple severity levels
3. Share scenarios with stakeholders
4. Update as situations evolve

### Exposure Management

1. Keep location data current
2. Include all significant operations
3. Review priority actions monthly
4. Document risk mitigation steps

### Custom Analysis

1. Use presets for common views
2. Save frequent country selections
3. Export data for external analysis
4. Cross-reference with internal data

## Troubleshooting

### Dashboard Not Loading

1. Check internet connection
2. Verify server is running
3. Clear browser cache
4. Try different browser

### Data Not Updating

1. Click Refresh button manually
2. Check API key configuration
3. Verify API rate limits
4. Check logs for errors

### Missing Countries

Not all countries have complete data:
1. Small nations may lack indicators
2. Some APIs have limited coverage
3. Contact support to add sources

### Slow Performance

1. Reduce selected countries
2. Use shorter time ranges
3. Close unused tabs
4. Check network speed

### Export Issues

1. Ensure popup blockers disabled
2. Check download folder
3. Try different browser
4. Verify file permissions

## Getting Help

### Documentation
- README.md: Quick start
- API_REFERENCE.md: Technical details
- ARCHITECTURE.md: System design

### Support
- GitHub Issues: Bug reports
- Email: support@geopolitix.com
- Slack: #geopolitix-help

### Training
- Video tutorials (coming soon)
- Webinar sessions
- On-site training available

---

Thank you for using GEOPOLITIX. Stay informed, stay prepared.
