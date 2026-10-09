import json
import pandas as pd

# ==========================================================
# 1. INSTITUTIONAL WHOLESALE BANKING SYNTHETIC PORTFOLIO
# ==========================================================

def get_wholesale_portfolio() -> pd.DataFrame:
    """
    Constructs a synthetic wholesale banking portfolio conforming to 
    Basel III / S&P credit risk reporting standards:
    - EAD: Exposure at Default (USD)
    - Rating: External S&P / CRISIL equivalent rating
    - PD: Baseline annual Probability of Default
    - LGD: Loss Given Default
    - Baseline_EL: Baseline Expected Loss (PD * LGD * EAD)
    """
    portfolio_data = [
        {
            "Asset_ID": "AST-101",
            "Asset_Name": "Global Energy Transition Term Loan",
            "Asset_Class": "Corporate Loan",
            "Credit_Rating": "BBB-",
            "Notional_USD": 50000000,
            "Current_Value_USD": 50000000,
            "EAD_USD": 50000000,
            "Baseline_PD": 0.0180,  # 1.80%
            "Baseline_LGD": 0.45,   # 45%
        },
        {
            "Asset_ID": "AST-102",
            "Asset_Name": "US Sovereign 10Y Benchmark Bond",
            "Asset_Class": "Sovereign Bond",
            "Credit_Rating": "AA+",
            "Notional_USD": 100000000,
            "Current_Value_USD": 98500000,
            "EAD_USD": 98500000,
            "Baseline_PD": 0.0005,  # 0.05%
            "Baseline_LGD": 0.15,   # 15%
        },
        {
            "Asset_ID": "AST-103",
            "Asset_Name": "Semiconductor Swaption Collar",
            "Asset_Class": "Derivatives",
            "Credit_Rating": "A",
            "Notional_USD": 25000000,
            "Current_Value_USD": 27200000,
            "EAD_USD": 27200000,
            "Baseline_PD": 0.0075,  # 0.75%
            "Baseline_LGD": 0.60,   # 60%
        },
        {
            "Asset_ID": "AST-104",
            "Asset_Name": "Tier-1 Metro Office Syndicated CRE Loan",
            "Asset_Class": "Commercial Real Estate",
            "Credit_Rating": "BB+",
            "Notional_USD": 75000000,
            "Current_Value_USD": 74000000,
            "EAD_USD": 74000000,
            "Baseline_PD": 0.0320,  # 3.20%
            "Baseline_LGD": 0.40,   # 40%
        },
        {
            "Asset_ID": "AST-105",
            "Asset_Name": "Telecom Infrastructure High-Yield Note",
            "Asset_Class": "High Yield Bond",
            "Credit_Rating": "B",
            "Notional_USD": 30000000,
            "Current_Value_USD": 28800000,
            "EAD_USD": 28800000,
            "Baseline_PD": 0.0650,  # 6.50%
            "Baseline_LGD": 0.55,   # 55%
        },
    ]
    df = pd.DataFrame(portfolio_data)
    df["Baseline_EL_USD"] = df["EAD_USD"] * df["Baseline_PD"] * df["Baseline_LGD"]
    return df

# ==========================================================
# 2. EVENT-DRIVEN STRESS TEST SIMULATION ENGINE
# ==========================================================

def run_portfolio_stress_test(df: pd.DataFrame, event_category: str, impact_score: int) -> pd.DataFrame:
    """
    Applies calibrated multi-asset financial shocks:
    1. Valuation Shock (% MTM impact on Current Value)
    2. PD Multiplier Shock (Rating degradation / default probability spike)
    3. Stressed Expected Loss = EAD * Stressed_PD * Stressed_LGD
    """
    severity = max(0.1, impact_score / 10.0)
    
    valuation_shocks = {
        "Corporate Loan": 0.0,
        "Sovereign Bond": 0.0,
        "Derivatives": 0.0,
        "Commercial Real Estate": 0.0,
        "High Yield Bond": 0.0
    }
    
    pd_multipliers = {
        "Corporate Loan": 1.0,
        "Sovereign Bond": 1.0,
        "Derivatives": 1.0,
        "Commercial Real Estate": 1.0,
        "High Yield Bond": 1.0
    }

    if event_category == "Credit Event":
        valuation_shocks["High Yield Bond"] = -0.35 * severity
        valuation_shocks["Corporate Loan"] = -0.15 * severity
        valuation_shocks["Commercial Real Estate"] = -0.10 * severity
        
        pd_multipliers["High Yield Bond"] = 1.0 + (3.5 * severity)
        pd_multipliers["Corporate Loan"] = 1.0 + (2.0 * severity)
        pd_multipliers["Commercial Real Estate"] = 1.0 + (1.5 * severity)

    elif event_category == "Geopolitical":
        valuation_shocks["Derivatives"] = -0.30 * severity
        valuation_shocks["High Yield Bond"] = -0.20 * severity
        valuation_shocks["Sovereign Bond"] = +0.03 * severity  # Safe-haven flight
        
        pd_multipliers["Derivatives"] = 1.0 + (2.2 * severity)
        pd_multipliers["High Yield Bond"] = 1.0 + (1.8 * severity)

    elif event_category == "Macroeconomic":
        valuation_shocks["Sovereign Bond"] = -0.12 * severity
        valuation_shocks["Commercial Real Estate"] = -0.15 * severity
        valuation_shocks["Derivatives"] = -0.18 * severity
        
        pd_multipliers["Commercial Real Estate"] = 1.0 + (2.4 * severity)
        pd_multipliers["Corporate Loan"] = 1.0 + (1.6 * severity)
        pd_multipliers["Sovereign Bond"] = 1.0 + (0.2 * severity)

    df_stressed = df.copy()
    df_stressed["Valuation_Shock_%"] = df_stressed["Asset_Class"].map(valuation_shocks)
    df_stressed["Stressed_Value_USD"] = df_stressed["Current_Value_USD"] * (1 + df_stressed["Valuation_Shock_%"])
    df_stressed["Valuation_Loss_USD"] = df_stressed["Current_Value_USD"] - df_stressed["Stressed_Value_USD"]
    
    # Calculate Stressed PD and Expected Loss (EL)
    df_stressed["PD_Multiplier"] = df_stressed["Asset_Class"].map(pd_multipliers)
    df_stressed["Stressed_PD"] = (df_stressed["Baseline_PD"] * df_stressed["PD_Multiplier"]).clip(upper=1.0)
    df_stressed["Stressed_EL_USD"] = df_stressed["EAD_USD"] * df_stressed["Stressed_PD"] * df_stressed["Baseline_LGD"]
    df_stressed["EL_Delta_USD"] = df_stressed["Stressed_EL_USD"] - df_stressed["Baseline_EL_USD"]
    
    return df_stressed

# ==========================================================
# 3. CLI EXECUTION & VALIDATION
# ==========================================================

if __name__ == "__main__":
    try:
        with open("risk_signals_output.json", "r", encoding="utf-8") as f:
            signals = json.load(f)
    except FileNotFoundError:
        print("[ERROR] 'risk_signals_output.json' not found. Run risk_engine.py first!")
        exit(1)

    portfolio = get_wholesale_portfolio()
    initial_total_val = portfolio["Current_Value_USD"].sum()
    initial_total_el = portfolio["Baseline_EL_USD"].sum()

    print("\n" + "=" * 70)
    print(" [CRISIL / S&P] WHOLESALE BANKING PORTFOLIO STRESS TESTING ENGINE")
    print("=" * 70)
    print(f"BASELINE PORTFOLIO EXPOSURE (EAD): ${initial_total_val:,.2f} USD")
    print(f"BASELINE EXPECTED LOSS (EL):       ${initial_total_el:,.2f} USD ({(initial_total_el / initial_total_val)*100:.3f}%)\n")

    for signal in signals:
        if signal["trigger_stress_test"]:
            print(f"[TRIGGER] Stress Testing Event: [{signal['event_classification']}] (Impact: {signal['impact_score']}/10)")
            print(f"  Signal Source: \"{signal['headline_or_text']}\"")
            
            stressed = run_portfolio_stress_test(portfolio, signal["event_classification"], signal["impact_score"])
            
            final_val = stressed["Stressed_Value_USD"].sum()
            total_loss = stressed["Valuation_Loss_USD"].sum()
            total_stressed_el = stressed["Stressed_EL_USD"].sum()
            el_delta = stressed["EL_Delta_USD"].sum()
            loss_pct = (total_loss / initial_total_val) * 100
            
            print(f"  --> Post-Stress Valuation:     ${final_val:,.2f} USD (M2M Loss: -${total_loss:,.2f} / -{loss_pct:.2f}%)")
            print(f"  --> Stressed Expected Loss:    ${total_stressed_el:,.2f} USD (EL Surge: +${el_delta:,.2f})\n")
            
            summary_cols = ["Asset_ID", "Asset_Class", "Credit_Rating", "Current_Value_USD", "Valuation_Shock_%", "Stressed_PD", "EL_Delta_USD"]
            print(stressed[summary_cols].to_string(index=False))
            print("-" * 70)