# Real-Time AI/NLP Financial Risk Engine & Stress Tester

An end-to-end financial risk intelligence platform designed to ingest unstructured market news and social feeds in real time, extract structured risk signals using financial NLP, and execute automated portfolio stress testing on wholesale banking assets.

---

## 1. Executive Summary

Traditional financial risk management systems rely on lagging numerical reporting cycles. Early indicators of liquidity crises, central bank rate shifts, or geopolitical disruptions often emerge first across unstructured channels like breaking news headlines and social media.

This platform bridges unstructured text processing and quantitative risk modeling through two core modules:
* **AI/NLP Risk Engine**: Ingests unstructured feeds (live REST APIs or mock streams), runs sentiment analysis using **FinBERT**, categorizes market events, and calculates impact severity scores ($1-10$).
* **Module B: Strategic Portfolio Stress Tester**: Monitors emitted risk signals and automatically triggers multi-asset shock models against a wholesale banking portfolio valued at **$278.5M USD** whenever high-severity events ($\text{Impact Score} \ge 7/10$) are detected.

---

## 2. System Architecture

```text
+-----------------------------------------------------------------+
|                      DATA INGESTION PIPELINE                    |
|  - Live NewsAPI Feed (REST API)                                 |
|  - Live Finnhub Market Feed (REST API)                          |
|  - Real-Time Mock / Social Streaming Feed (Twitter/X)           |
+--------------------------------+--------------------------------+
                                 |
                                 | Raw Unstructured Text
                                 v
+-----------------------------------------------------------------+
|                      AI/NLP RISK ENGINE                         |
|  - Sentiment Model: ProsusAI/finbert (HuggingFace Transformers) |
|  - Event Classification: Keyword & Semantic Rule Engine        |
|  - Severity Scoring Matrix: Calibrated Scale (1 to 10)          |
+--------------------------------+--------------------------------+
                                 |
                                 | JSON Risk Signal Payload
                                 v
+-----------------------------------------------------------------+
|              STRUCTURED RISK SIGNAL (JSON Schema)               |
|  { "entity": "XYZ", "sentiment": -0.85, "impact": 10, ... }     |
+--------------------------------+--------------------------------+
                                 |
                                 | Trigger: Impact Score >= 7
                                 v
+-----------------------------------------------------------------+
|             MODULE B: PORTFOLIO STRESS TEST ENGINE              |
|  - Portfolio: Corporate Loans, CRE, Bonds, Derivatives          |
|  - Event-Driven Multi-Asset Shock Matrix                        |
|  - Impairment Delta & Value-at-Risk (VaR) Calculation           |
+--------------------------------+--------------------------------+
                                 |
                                 | Analytics & Data Streams
                                 v
+-----------------------------------------------------------------+
|                   STREAMLIT INTERACTIVE DASHBOARD               |
|  - Real-time News Feed Control Panel                            |
|  - Pre- vs. Post-Stress Plotly Visualizations & Data Tables     |
+-----------------------------------------------------------------+

```
3. Key Capabilities
   Dual Ingestion Pipeline: Toggles between live REST APIs (NewsAPI, Finnhub) and structured fallback feeds for reliable presentation demos.
   Financial NLP Processing: Employs FinBERT (ProsusAI/finbert), a Transformer model fine-tuned on corporate financial filings and financial news, producing normalized sentiment scores ($[-1.0, +1.0]$).
   Event Classification: Categorizes input headlines into five discrete financial categories:
   Credit Event
   Geopolitical
   Macroeconomic
   Merger/Acquisition
   Product Launch

   Schema Validation: Guarantees typed data exchange between the NLP engine and downstream applications using Pydantic V2 schemas.
   Dynamic Asset Impairment: Automatically triggers asset-class shocks when impact_score >= 7, providing loss delta analytics across corporate loans, real estate, sovereign debt, and derivatives.

   4. Repository StructurePlaintextNLP-Risk-Engine/
```      
├── app.py                     # Streamlit Unified Web Dashboard
├── risk_engine.py             # Data Ingestion Engine & FinBERT Model Pipeline
├── stress_tester.py           # Module B Portfolio Stress Test Engine
├── risk_signals_output.json   # Machine-readable signal exchange payload
├── requirements.txt           # Project dependencies
└── README.md                  # Project Documentation
```

5. Quick Start & InstallationPrerequisitesPython 3.9+pip package managerSetup StepsClone the repository and navigate to the root directory:Bashgit clone [https://github.com/YOUR_GITHUB_USERNAME/NLP-Risk-Engine.git](https://github.com/YOUR_GITHUB_USERNAME/NLP-Risk-Engine.git)
cd NLP-Risk-Engine
Create and activate a virtual environment:Bash# Windows PowerShell
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
Install required dependencies:Bashpip install -r requirements.txt
Configure API Keys (Optional for live news ingestion):Bash# Windows PowerShell
$env:NEWSAPI_KEY="your_newsapi_key_here"
$env:FINNHUB_KEY="your_finnhub_key_here"

# macOS / Linux
export NEWSAPI_KEY="your_newsapi_key_here"
export FINNHUB_KEY="your_finnhub_key_here"
(If no keys are provided, the pipeline seamlessly falls back to pre-configured high-impact feeds).6. Execution ModesCommand-Line Execution (CLI)Run the NLP engine to generate structured risk output:Bashpython risk_engine.py
Run the downstream stress tester module:Bashpython stress_tester.py
Interactive Web DashboardLaunch the unified Streamlit application:Bashstreamlit run app.py
7. Operational OutputsSample Signal Payload (risk_signals_output.json)JSON[
  {
    "source": "Twitter/X (@MarketWatch)",
    "headline_or_text": "$XYZ Bank credit default swaps surge to 10-year highs following rumors of liquidity shortfall.",
    "entity_mentioned": "XYZ",
    "sentiment_score": -0.85,
    "event_classification": "Credit Event",
    "impact_score": 10,
    "trigger_stress_test": true
  },
  {
    "source": "Reuters News",
    "headline_or_text": "Federal Reserve unexpected rate hike of 75 bps causes sharp downturn across global bond yields.",
    "entity_mentioned": "Federal",
    "sentiment_score": -0.96,
    "event_classification": "Macroeconomic",
    "impact_score": 8,
    "trigger_stress_test": true
  }
]
Stress Test Console OutputPlaintext=======================================================
INITIAL PORTFOLIO VALUE: $278,500,000.00 USD
=======================================================

TRIGGERING STRESS TEST for Event: [Credit Event] (Impact Score: 10/10)
   Source Text: "$XYZ Bank credit default swaps surge to 10-year highs following rumors of liquidity shortfall."
   --> Post-Stress Portfolio Value: $253,520,000.00 USD
   --> Total Portfolio Loss: -$24,980,000.00 USD (-8.97%)

Asset_ID             Asset_Class  Current_Value_USD   Shock_%      Loss_USD
 AST-101          Corporate Loan           50000000     -0.15     7500000.0
 AST-102          Sovereign Bond           98500000      0.00           0.0
 AST-103             Derivatives           27200000      0.00           0.0
 AST-104 Commercial Real Estate           74000000     -0.10     7400000.0
 AST-105         High Yield Bond           28800000     -0.35    10080000.0

8. Stress Shock Mapping Matrix
The shock intensity scales proportionally based on event type and computed severity score:
Event Classification  Primary Asset Classes Impacted  Shock Mechanics
Credit Event  High Yield Bonds, Corporate Loans, CRE  Widening credit spreads and default rate adjustments.
Macroeconomic  Sovereign Bonds, CRE, Derivatives  Benchmark yield curve shifts and derivative repricing.
Geopolitical  Derivatives, High Yield Bonds  Market volatility spikes; flight-to-safety reallocation toward Sovereign Bonds.

9. Future Enhancement Roadmap
Module B Integration: Incorporate real-time stock index rebalancing using live market feeds.
Streaming Architecture: Scale ingestion using Apache Kafka message queues for high-throughput processing.
LLM Integration: Implement fine-tuned open-source LLMs (e.g., Llama-3) for entity extraction and complex event reasoning.
