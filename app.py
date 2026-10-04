import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Hourly Production Dashboard", layout="wide")

st.title("🏭 Hourly Production Live Dashboard")

# Google Sheet CSV Link
SHEET_URL = "https://docs.google.com/spreadsheets/d/18YQkUYI-GQz24ImIIdm4vmB_JYBmNKIxDsgdWyJ0ehQ/export?format=csv"

@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_URL)
    return df

try:
    raw_df = load_data()

    # KPI Calculations
    if 'Day Forecast' in raw_df.columns:
        total_target = pd.to_numeric(raw_df['Day Forecast'], errors='coerce').sum()
    else:
        total_target = 0

    hourly_cols = [str(i) for i in range(1, 10) if str(i) in raw_df.columns]
    actual_sum = 0
    for col in hourly_cols:
        actual_sum += pd.to_numeric(raw_df[col], errors='coerce').fillna(0).sum()
    
    total_actual = actual_sum
    overall_eff = (total_actual / total_target * 100) if total_target > 0 else 0.0

    # Top KPI Metrics Display
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Target Output", f"{int(total_target):,} Pcs")
    col2.metric("Total Actual Output", f"{int(total_actual):,} Pcs")
    col3.metric("Plant Efficiency", f"{overall_eff:.1f}%")

    st.divider()
    st.subheader("📋 Module Wise Hourly Production Table")

    # Display එක සඳහා දශම ස්ථාන ඉවත් කිරීම
    display_df = raw_df.copy()
    
    for col in display_df.columns:
        if col != 'MODULE':
            def clean_val(val):
                if pd.isna(val) or str(val).strip() in ['', 'None', 'nan']:
                    return ''
                try:
                    return str(int(float(val)))
                except (ValueError, TypeError):
                    return str(val)
            display_df[col] = display_df[col].apply(clean_val)

    # Conditional Formatting Function
    def highlight_hourly(row):
        styles = [''] * len(row)
        target = row.get('Hourly Forecast', '')
        
        try:
            target_val = float(target) if target != '' else 0
        except (ValueError, TypeError):
            target_val = 0

        for i, col in enumerate(row.index):
            if str(col) in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                val_str = str(row[col]).strip()
                if val_str != '':
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
    st.dataframe(display_df.style.apply(highlight_hourly, axis=1), use_container_width=True)

except Exception as e:
    st.error(f"Data Load කිරීමේදී දෝෂයක් සිදු විය: {e}")
