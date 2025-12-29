"""Prompt engineering templates for financial analysis using Perplexity Sonar API."""

from typing import Dict, List, Optional

# Domain filters for high-quality financial sources
FINANCE_DOMAINS = [
    "sec.gov",
    "bloomberg.com",
    "reuters.com",
    "wsj.com",
    "seekingalpha.com",
    "ft.com",
    "cnbc.com",
    "marketwatch.com",
    "investor.*.com",
]

# Pre-built prompt templates for common financial queries
FINANCE_PROMPTS: Dict[str, str] = {
    "earnings_summary": """Analyze the latest earnings report for {ticker}.
Focus on:
- Revenue growth (YoY and QoQ)
- Profit margins (gross, operating, net)
- Forward guidance and management commentary
- Key risks and challenges mentioned
- Comparison to analyst expectations

Include specific numbers and citations from SEC filings and earnings calls.""",

    "geopolitical_impact": """Assess how recent geopolitical events in {region}
affect {company}'s operations, supply chain, and revenue.

Analyze:
- Geographic revenue exposure to {region}
- Supply chain dependencies and vulnerabilities
- Regulatory and sanctions risks
- Currency exposure and hedging
- Management statements on geopolitical risk

Provide specific examples, percentages, and citations from recent filings and news.""",

    "peer_comparison": """Compare {ticker1} vs {ticker2} across:
- Revenue growth (1Y, 3Y, 5Y CAGR)
- Profitability metrics (gross margin, operating margin, net margin)
- Valuation (P/E, P/S, EV/EBITDA, P/FCF)
- Market positioning and competitive advantages
- Balance sheet strength (debt levels, cash position)

Use latest financial data with specific numbers and citations.""",

    "risk_assessment": """Evaluate major risks facing {company}:

1. Regulatory Risk: Government regulations, compliance requirements
2. Competitive Risk: Market share threats, new entrants
3. Geopolitical Risk: International operations exposure
4. Operational Risk: Supply chain, key person dependencies
5. Financial Risk: Debt levels, liquidity, currency exposure
6. Technology Risk: Disruption threats, cybersecurity

Reference recent news, SEC filings, and analyst reports with citations.""",

    "sector_analysis": """Analyze the current state of the {sector} sector:
- Key trends and drivers
- Major players and market share
- Regulatory environment
- Growth outlook
- Headwinds and tailwinds
- Impact of macroeconomic factors

Include specific data points, recent developments, and citations.""",

    "stock_overview": """Provide a comprehensive overview of {ticker} stock:
- Current price action and recent movement
- Key valuation metrics (P/E, P/S, EV/EBITDA)
- Recent news and catalysts
- Analyst sentiment and price targets
- Technical levels (support/resistance)
- Risk factors

Include specific numbers and multiple source citations.""",

    "market_impact": """Analyze the market impact of {event}:
- Affected sectors and industries
- Specific companies with exposure
- Expected duration of impact
- Historical precedents
- Potential mitigation strategies

Include market data, analyst commentary, and news citations.""",

    "dividend_analysis": """Analyze the dividend profile of {ticker}:
- Current yield and payout ratio
- Dividend growth history (1Y, 5Y, 10Y)
- Dividend coverage (FCF, earnings)
- Comparison to sector peers
- Sustainability assessment
- Ex-dividend dates and payment schedule

Include historical data and citations.""",

    "technical_analysis": """Provide technical analysis for {ticker}:
- Current trend direction
- Key support and resistance levels
- Moving averages (50-day, 200-day)
- RSI and momentum indicators
- Volume patterns
- Chart patterns (if any)

Include recent price data and technical indicator values.""",

    "earnings_preview": """Preview upcoming earnings for {ticker}:
- Expected earnings date
- Analyst EPS estimates (consensus, range)
- Revenue expectations
- Key metrics to watch
- Recent guidance from management
- Historical earnings surprise pattern

Include analyst estimates and recent company statements.""",

    "supply_chain_analysis": """Analyze {company}'s supply chain:
- Key suppliers and their locations
- Geographic concentration risks
- Recent supply chain disruptions
- Inventory management approach
- Supplier diversification efforts
- Geopolitical vulnerabilities

Include company disclosures and industry data with citations.""",

    "esg_analysis": """Analyze {company}'s ESG profile:
- Environmental initiatives and metrics
- Social responsibility programs
- Governance structure and practices
- ESG ratings from major agencies
- Regulatory compliance
- Sustainability goals and progress

Include ESG data, ratings, and company disclosures.""",
}


def get_prompt_template(template_name: str) -> Optional[str]:
    """
    Get a prompt template by name.

    Args:
        template_name: Name of the template

    Returns:
        Template string or None if not found
    """
    return FINANCE_PROMPTS.get(template_name)


def format_prompt(template_name: str, **kwargs) -> Optional[str]:
    """
    Format a prompt template with provided variables.

    Args:
        template_name: Name of the template
        **kwargs: Variables to substitute in the template

    Returns:
        Formatted prompt or None if template not found
    """
    template = FINANCE_PROMPTS.get(template_name)
    if template:
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"Missing required parameter: {e}"
    return None


def list_templates() -> List[str]:
    """
    List all available prompt templates.

    Returns:
        List of template names
    """
    return list(FINANCE_PROMPTS.keys())


def get_template_info() -> Dict[str, Dict[str, str]]:
    """
    Get information about all templates including required parameters.

    Returns:
        Dictionary mapping template names to their info
    """
    info = {}
    for name, template in FINANCE_PROMPTS.items():
        # Extract parameters from template
        import re
        params = re.findall(r"\{(\w+)\}", template)
        info[name] = {
            "description": template.split("\n")[0].strip(),
            "parameters": list(set(params)),
        }
    return info


# System prompts for different analysis contexts
SYSTEM_PROMPTS: Dict[str, str] = {
    "financial_analyst": """You are a senior financial analyst specializing in equity research.
Provide accurate, data-driven analysis with specific numbers and citations.
Focus on actionable insights for investment decisions.
Always cite your sources and acknowledge uncertainty when relevant.""",

    "risk_analyst": """You are a risk analyst specializing in geopolitical risk assessment.
Analyze how political, economic, and social factors affect financial markets.
Quantify risks where possible and provide scenario analysis.
Always cite your sources from reputable publications.""",

    "market_strategist": """You are a market strategist analyzing market trends and dynamics.
Provide insights on market positioning, sector rotation, and macro factors.
Use data to support your analysis and provide actionable recommendations.
Cite current market data and expert opinions.""",

    "earnings_analyst": """You are an earnings analyst focused on corporate financial results.
Analyze earnings reports in detail, comparing to expectations and historical trends.
Highlight key takeaways, surprises, and forward guidance implications.
Reference specific numbers from SEC filings and earnings transcripts.""",

    "esg_analyst": """You are an ESG analyst evaluating environmental, social, and governance factors.
Assess company sustainability practices, governance quality, and social impact.
Use ESG ratings, disclosures, and industry benchmarks for analysis.
Provide balanced assessment of strengths and areas for improvement.""",
}


def get_system_prompt(context: str = "financial_analyst") -> str:
    """
    Get system prompt for a specific analysis context.

    Args:
        context: Analysis context type

    Returns:
        System prompt string
    """
    return SYSTEM_PROMPTS.get(context, SYSTEM_PROMPTS["financial_analyst"])


# Follow-up question suggestions based on analysis type
FOLLOWUP_SUGGESTIONS: Dict[str, List[str]] = {
    "earnings_summary": [
        "How does this compare to the previous quarter?",
        "What are analysts saying about the guidance?",
        "How did competitors perform this quarter?",
        "What are the key risks mentioned by management?",
    ],
    "geopolitical_impact": [
        "How are competitors handling similar exposure?",
        "What hedging strategies could mitigate this risk?",
        "Are there historical precedents for this situation?",
        "How might this affect the company's valuation?",
    ],
    "peer_comparison": [
        "Which company has better growth prospects?",
        "How do their balance sheets compare?",
        "What are the key competitive advantages of each?",
        "Which is better positioned for market conditions?",
    ],
    "risk_assessment": [
        "What are the most critical risks?",
        "How is management addressing these risks?",
        "How do these risks compare to industry peers?",
        "What would trigger these risk scenarios?",
    ],
    "stock_overview": [
        "What are the key catalysts ahead?",
        "Is the current valuation justified?",
        "What do analysts recommend?",
        "What are the main bear case arguments?",
    ],
}


def get_followup_suggestions(analysis_type: str) -> List[str]:
    """
    Get suggested follow-up questions for an analysis type.

    Args:
        analysis_type: Type of analysis performed

    Returns:
        List of suggested follow-up questions
    """
    return FOLLOWUP_SUGGESTIONS.get(analysis_type, [
        "Can you provide more details?",
        "What are the key risks?",
        "How does this compare to competitors?",
        "What is the outlook going forward?",
    ])
