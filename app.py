import streamlit as st
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(page_title="Hourly Production Dashboard", layout="wide")

st.title("🏭 Hourly Production Live Dashboard")
st.caption("Google Sheets හා සම්බන්ධිත සජීවී Production Tracker එක")

# Google Sheet CSV Link
SHEET_URL = "https://docs.google.com/spreadsheets/d/18YQkUYI-GQz24ImIIdm4vmB_JYBmNKIxDsgdWyJ0ehQ/export?format=csv"

@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_URL)
    # None / NaN වෙනුවට හිස් අගයන් හෝ 0 යෙදීම
    df = df.fillna("")
    return df

try:
    df = load_data()

    # Total Target & Actual සෙවීම (Day Forecast සහ 1-9 පැයවල එකතුවෙන්)
    if 'Day Forecast' in df.columns:
        total_target = pd.to_numeric(df['Day Forecast'], errors='coerce').sum()
    else:
        total_target = 0

    # පැය 1 සිට 9 දක්වා එකතුව (Actual Output)
    hourly_cols = [str(i) for i in range(1, 10) if str(i) in df.columns]
    actual_sum = 0
    for col in hourly_cols:
        actual_sum += pd.to_numeric(df[col], errors='coerce').fillna(0).sum()
    
    total_actual = actual_sum
    overall_eff = (total_actual / total_target * 100) if total_target > 0 else 0.0

    # Top KPI Metrics Display
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Target Output", f"{int(total_target):,} Pcs")
    col2.metric("Total Actual Output", f"{int(total_actual):,} Pcs")
    col3.metric("Plant Efficiency", f"{overall_eff:.1f}%")

    st.divider()
    st.subheader("📋 Module Wise Hourly Production Table")

    # Conditional Formatting Function
    def highlight_hourly(row):
        styles = [''] * len(row)
        # Target එක ලෙස 'Hourly Forecast' ලබා ගැනීම
        target = row.get('Hourly Forecast', 0)
        
        try:
            target_val = float(target)
        except (ValueError, TypeError):
            target_val = 0

        for i, col in enumerate(row.index):
            # 1 සිට 9 දක්වා පැය තීරූ සසඳා පාට කිරීම
            if str(col) in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                val_str = str(row[col]).strip()
                if val_str != "" and val_str != "None":
                    try:
                        actual_val = float(val_str)
                        if target_val > 0:
                            if actual_val >= target_val:
                                styles[i] = 'background-color: #c8e6c9; color: #1b5e20; font-weight: bold;' # කොළ පාට
                            else:
                                styles[i] = 'background-color: #ffcdd2; color: #b71c1c; font-weight: bold;' # රතු පාට
                    except (ValueError, TypeError):
                        pass
        return styles

    # Table Display
    st.dataframe(df.style.apply(highlight_hourly, axis=1), use_container_width=True)

except Exception as e:
    st.error(f"Data Load කිරීමේදී දෝෂයක් සිදු විය: {e}")
