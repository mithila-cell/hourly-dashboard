import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Hourly Production Dashboard", layout="wide")

st.title("🏭 Hourly Production Live Dashboard")
st.caption("Google Sheets හා සම්බන්ධිත සජීවී Production Tracker එක")

# Google Sheet CSV Link
SHEET_URL = "https://docs.google.com/spreadsheets/d/18YQkUYI-GQz24ImIIdm4vmB_JYBmNKIxDsgdWyJ0ehQ/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL)
    return df

try:
    df = load_data()

    # KPI Calculation (Column එක නැතිනම් Error නොවන ලෙස ආරක්ෂිතව ගණනය කිරීම)
    target_series = df['TOTAL_TARGET'] if 'TOTAL_TARGET' in df.columns else pd.Series([0])
    actual_series = df['TOTAL_ACTUAL'] if 'TOTAL_ACTUAL' in df.columns else pd.Series([0])

    total_target = pd.to_numeric(target_series, errors='coerce').sum()
    total_actual = pd.to_numeric(actual_series, errors='coerce').sum()
    overall_eff = (total_actual / total_target * 100) if total_target > 0 else 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Target Output", f"{int(total_target):,} Pcs")
    col2.metric("Total Actual Output", f"{int(total_actual):,} Pcs")
    col3.metric("Plant Efficiency", f"{overall_eff:.1f}%")

    st.divider()
    st.subheader("📋 Module Wise Hourly Production Table")

    # Target එකට වඩා වැඩි නම් කොළ / අඩු නම් රතු පාටින් පෙන්වන ශ්‍රිතය
    def highlight_hourly(row):
        styles = [''] * len(row)
        target = row.get('HOURLY PCS', 0)
        
        try:
            target_val = float(target)
        except (ValueError, TypeError):
            target_val = 0

        for i, col in enumerate(row.index):
            if str(col) in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                try:
                    actual_val = float(row[col])
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
