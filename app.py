import streamlit as st
import pandas as pd
import os

# Page Configuration
st.set_page_config(page_title="GIZA Hourly Production Dashboard", layout="wide")

# Logo Display Logic
logo_col1, logo_col2, title_col = st.columns([1, 1, 4])

with logo_col1:
    for filename in ["GizaCo-Logo.jpg", "GizaCo-Logo.png", "GizaCo-Logo.jpeg", "giza.png", "giza.jpg"]:
        if os.path.exists(filename):
            st.image(filename, width=120)
            break

with logo_col2:
    for filename in ["HIJ LOGO.png", "HIJ LOGO.jpg", "HIJ LOGO.jpeg", "hij.png", "hij.jpg"]:
        if os.path.exists(filename):
            st.image(filename, width=120)
            break

with title_col:
    st.title("GIZA Hourly Production Dashboard")

st.divider()

# Google Sheet CSV Link
SHEET_URL = "https://docs.google.com/spreadsheets/d/18YQkUYI-GQz24ImIIdm4vmB_JYBmNKIxDsgdWyJ0ehQ/export?format=csv"

@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_URL)
    return df

try:
    raw_df = load_data()

    # Active hours සොයා ගැනීම
    active_hours = []
    for h in range(1, 10):
        col = str(h)
        if col in raw_df.columns:
            has_data = pd.to_numeric(raw_df[col], errors='coerce').notna().any()
            if has_data:
                active_hours.append(h)

    current_hour = max(active_hours) if active_hours else 0

    # Up to Now Target & Actual Calculations
    if current_hour > 0 and 'Hourly Forecast' in raw_df.columns:
        hourly_target_sum = pd.to_numeric(raw_df['Hourly Forecast'], errors='coerce').fillna(0).sum()
        upto_now_target = hourly_target_sum * current_hour
    else:
        upto_now_target = 0

    upto_now_actual = 0
    for h in range(1, current_hour + 1):
        col = str(h)
        if col in raw_df.columns:
            upto_now_actual += pd.to_numeric(raw_df[col], errors='coerce').fillna(0).sum()

    p2p_pct = (upto_now_actual / upto_now_target * 100) if upto_now_target > 0 else 0.0

    # Top KPI Metrics Display
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Target Output (Up to Hr {current_hour})", f"{int(upto_now_target):,} Pcs")
    col2.metric(f"Actual Output (Up to Hr {current_hour})", f"{int(upto_now_actual):,} Pcs")
    col3.metric("Up to now P2P", f"{p2p_pct:.1f}%")

    st.divider()
    st.subheader("📋 Module Wise Hourly Production Table")

    # Display clean-up (Decimal ඉවත් කිරීම)
    display_df = raw_df.copy()
    
    for col in display_df.columns:
        if col not in ['MODULE', 'Line No']:
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
                                styles[i] = 'background-color: #c8e6c9; color: #1b5e20; font-weight: bold;'
                            else:
                                styles[i] = 'background-color: #ffcdd2; color: #b71c1c; font-weight: bold;'
                    except (ValueError, TypeError):
                        pass
        return styles

    # මාතෘකා උඩ-යට පේළි 2කට කඩා Column Width එක අඩු කිරීම
    col_config = {
        "Line No": st.column_config.Column("Line\nNo", width="small"),
        "MODULE": st.column_config.Column("Module", width="small"),
        "Day Forecast": st.column_config.Column("Day\nForecast", width="small"),
        "Hourly Forecast": st.column_config.Column("Hourly\nForecast", width="small"),
        "TOTAL": st.column_config.Column("TOTAL", width="small")
    }
    
    for i in range(1, 10):
        col_config[str(i)] = st.column_config.Column(str(i), width="small")

    # Table Display
    st.dataframe(
        display_df.style.apply(highlight_hourly, axis=1), 
        use_container_width=True, 
        hide_index=True,
        column_config=col_config
    )

except Exception as e:
    st.error(f"Data Load කිරීමේදී දෝෂයක් සිදු විය: {e}")
