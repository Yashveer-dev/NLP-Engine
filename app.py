import json
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from risk_engine import RiskEngineNLP, DataIngestionPipe
from stress_tester import get_wholesale_portfolio, run_portfolio_stress_test

# Page configuration
st.set_page_config(page_title="CRISIL S&P Risk Engine & Stress Tester", layout="wide", page_icon="🛡️")

# Custom Dark Institutional Styling
st.markdown("""
<style>
    .stApp {
        background-color: #080a0f;
        color: #f1f5f9;
    }
    div[data-testid="stMetricValue"] {
        font-family: monospace;
        font-size: 1.8rem;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
    }
    .stAlert {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_nlp_engine():
    # Set use_hf=False for instant local runtime, or True if finbert weights are cached
    return RiskEngineNLP(use_hf=False)

engine = load_nlp_engine()

# Main Header
st.title("🛡️ AI/NLP Financial Risk Engine & Stress Testing Platform")
st.caption("Institutional-grade unstructured intelligence pipeline & Basel III wholesale portfolio stress tester (CRISIL / S&P Challenge).")

# Sidebar - Live Data Ingestion Controls
st.sidebar.header("📥 Ingestion Data Control")
input_option = st.sidebar.radio("Select Ingestion Mode", [
    "Preset High-Risk Feed (Benchmark)",
    "Live NewsAPI Feed",
    "Live Finnhub Feed",
    "Custom Text Input"
])

source_name = "Custom Source"
input_text = ""

if input_option == "Preset High-Risk Feed (Benchmark)":
    mock_feed = DataIngestionPipe.fetch_mock_data_feed()
    feed_options = {f"[{item['source']}] {item['text'][:60]}...": item for item in mock_feed}
    selected_label = st.sidebar.selectbox("Select Ingestion Item", list(feed_options.keys()))
    selected_item = feed_options[selected_label]
    source_name = selected_item["source"]
    input_text = selected_item["text"]

elif input_option == "Live NewsAPI Feed":
    api_key = st.sidebar.text_input("NewsAPI Key (optional if NEWSAPI_KEY env set)", type="password")
    news_query = st.sidebar.text_input("Query", "default OR inflation OR banking")
    live_items = DataIngestionPipe.fetch_news_api(api_key=api_key or None, query=news_query)
    if live_items:
        live_options = {f"[{i['source']}] {i['text'][:60]}...": i for i in live_items}
        sel_label = st.sidebar.selectbox("Select Live Article", list(live_options.keys()))
        source_name = live_options[sel_label]["source"]
        input_text = live_options[sel_label]["text"]
    else:
        st.sidebar.info("Provide a NewsAPI key to fetch live stream, or fall back to preset.")
        source_name = "NewsAPI (Live Fallback)"
        input_text = "Federal Reserve signals aggressive rate tightening as inflationary pressure accelerates."

elif input_option == "Live Finnhub Feed":
    finnhub_key = st.sidebar.text_input("Finnhub Key (optional if FINNHUB_KEY env set)", type="password")
    live_items = DataIngestionPipe.fetch_finnhub_news(api_key=finnhub_key or None)
    if live_items:
        live_options = {f"[{i['source']}] {i['text'][:60]}...": i for i in live_items}
        sel_label = st.sidebar.selectbox("Select Finnhub Headline", list(live_options.keys()))
        source_name = live_options[sel_label]["source"]
        input_text = live_options[sel_label]["text"]
    else:
        st.sidebar.info("Provide Finnhub token to stream real-time financial market wires.")
        source_name = "Finnhub (Live Fallback)"
        input_text = "$XYZ Bank credit default swaps widen sharply amid asset quality review."

else:
    source_name = st.sidebar.text_input("Source Identifier", "Custom Feed / Social Wire")
    input_text = st.sidebar.text_area(
        "Enter Unstructured Financial Text",
        "$XYZ Bank faces severe liquidity shortfall as default spreads reach decade peak."
    )

# Process Text through Engine
signal = engine.process_text(source=source_name, text=input_text)

# Section 1: NLP Risk Engine Signal Output
st.subheader("1. Core NLP Risk Engine Signal Payload")
st.info(f"**Ingested Data:** \"{signal.headline_or_text}\" | **Source:** `{signal.source}`")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Entity Detected", signal.entity_mentioned)
col2.metric("Sentiment Score", f"{signal.sentiment_score:+.2f}")
col3.metric("Event Classification", signal.event_classification)
col4.metric("Impact Severity Score", f"{signal.impact_score} / 10")

st.divider()

# Section 2: Downstream Portfolio Stress Testing (Module B)
st.subheader("2. Strategic Portfolio Stress Testing (Module B - Wholesale Banking)")

portfolio_df = get_wholesale_portfolio()
initial_val = portfolio_df["Current_Value_USD"].sum()
initial_el = portfolio_df["Baseline_EL_USD"].sum()

if signal.trigger_stress_test:
    st.error(f"🚨 **HIGH-IMPACT SIGNAL DETECTED** (Impact Score: {signal.impact_score}/10). Automated Stress Simulation Executed.")
    
    # Run Stress Simulation
    stressed_df = run_portfolio_stress_test(portfolio_df, signal.event_classification, signal.impact_score)
    final_val = stressed_df["Stressed_Value_USD"].sum()
    total_val_loss = stressed_df["Valuation_Loss_USD"].sum()
    loss_pct = (total_val_loss / initial_val) * 100
    
    stressed_el = stressed_df["Stressed_EL_USD"].sum()
    el_surge = stressed_df["EL_Delta_USD"].sum()
    el_pct_surge = (el_surge / initial_el) * 100

    # Summary Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pre-Event Exposure (EAD)", f"${initial_val:,.2f}")
    m2.metric("Post-Stress Valuation", f"${final_val:,.2f}", delta=f"-${total_val_loss:,.2f} (-{loss_pct:.2f}%)", delta_color="inverse")
    m3.metric("Baseline Expected Loss (EL)", f"${initial_el:,.2f}")
    m4.metric("Stressed Expected Loss", f"${stressed_el:,.2f}", delta=f"+${el_surge:,.2f} (+{el_pct_surge:.1f}%)", delta_color="inverse")

    # Visualizations
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        fig_bar = go.Figure(data=[
            go.Bar(name='Pre-Stress Value ($)', x=stressed_df['Asset_ID'], y=stressed_df['Current_Value_USD'], marker_color='#2ca02c'),
            go.Bar(name='Post-Stress Value ($)', x=stressed_df['Asset_ID'], y=stressed_df['Stressed_Value_USD'], marker_color='#d62728')
        ])
        fig_bar.update_layout(barmode='group', title="Asset-Level Valuation Shock (Pre vs. Post Stress)", height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

    with chart_col2:
        fig_el = px.bar(
            stressed_df,
            x='Asset_Class',
            y='EL_Delta_USD',
            color='Asset_Class',
            title="Expected Loss (Credit Risk Surge by Asset Class)",
            labels={'EL_Delta_USD': 'Surge in Expected Loss ($)'},
            height=400
        )
        st.plotly_chart(fig_el, use_container_width=True)

    st.markdown("### Asset-Level Impairment & Credit Migration Matrix")
    display_cols = ["Asset_ID", "Asset_Name", "Asset_Class", "Credit_Rating", "Current_Value_USD", "Valuation_Shock_%", "Stressed_Value_USD", "Baseline_PD", "Stressed_PD", "EL_Delta_USD"]
    st.dataframe(stressed_df[display_cols], use_container_width=True)

else:
    st.success("🟢 **NORMAL OPERATING STATUS**: Signal impact score is below threshold (< 7). No portfolio stress triggered.")
    st.markdown("### Baseline Wholesale Portfolio Structure")
    st.dataframe(portfolio_df[["Asset_ID", "Asset_Name", "Asset_Class", "Credit_Rating", "Current_Value_USD", "Baseline_PD", "Baseline_LGD", "Baseline_EL_USD"]], use_container_width=True)