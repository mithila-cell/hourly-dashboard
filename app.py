import streamlit as st
import pandas as pd
import plotly.express as px

# Mobile Responsive Page Config
st.set_page_config(page_title="Hourly Production Dashboard", layout="wide")

st.title("🏭 Hourly Production Live Dashboard")
st.caption

# ඔබේ Google Sheet Published CSV Link එක මෙතැනට ඇතුළත් කර ඇත:
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT5HBlp2thoIYR7zPuWLoQ0_FtowtlmTen0_IbrNAKwB5lz9I20JngpWaGClLHE_HU_HIGoqraocXUk/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=10)  # තත්පර 10කට වරක් Data Auto-Refresh වේ
def load_data():
    data = pd.read_csv(GOOGLE_SHEET_CSV_URL)
    return data

try:
    df = load_data()

    # Columns සහ Data සකස් කිරීම
    hour_cols = [str(i) for i in range(1, 10)]
    
    # Text numeric columns බවට පත් කිරීම
    for col in hour_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    if 'HOURLY_PCS' in df.columns:
        df['HOURLY_PCS'] = pd.to_numeric(df['HOURLY_PCS'], errors='coerce').fillna(0)
        df['TOTAL_TARGET'] = df['HOURLY_PCS'] * 9
    else:
        df['TOTAL_TARGET'] = 0

    df['TOTAL_ACTUAL'] = df[hour_cols].sum(axis=1)
    df['ACHIEVEMENT_%'] = (df['TOTAL_ACTUAL'] / df['TOTAL_TARGET']) * 100
    df['ACHIEVEMENT_%'] = df['ACHIEVEMENT_%'].fillna(0)

    # Top KPI Summary Cards (Mobile එකට ලස්සනට පෙනෙන ලෙස)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Target Output", f"{int(df['TOTAL_TARGET'].sum()):,} Pcs")
    col2.metric("Total Actual Output", f"{int(df['TOTAL_ACTUAL'].sum()):,} Pcs")
    col3.metric("Plant Efficiency", f"{df['ACHIEVEMENT_%'].mean():.1f}%")

    st.markdown("---")

    # Board Layout එකට සමාන Data Table එක
    st.subheader("📋 Module Wise Hourly Production Table")
    st.dataframe# Hourly Columns 1 සිට 9 දක්වා Compare කර පාට කරන Function එක
def highlight_hourly(row):
    styles = [''] * len(row)
    # Target / Hourly Forecast අගය ලබා ගැනීම (HOURLY PCS හෝ TARGET තීරුවෙන්)
    target = row.get('HOURLY PCS', 0)
    
    try:
        target_val = float(target)
    except (ValueError, TypeError):
        target_val = 0

    # 1 සිට 9 දක්වා පැය 9 තීරූ සසඳා පාට යෙදීම
    for i, col in enumerate(row.index):
        if str(col) in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            try:
                actual_val = float(row[col])
                if target_val > 0:
                    if actual_val >= target_val:
                        # Target එකට සමාන හෝ වැඩි නම් - කොළ පාට
                        styles[i] = 'background-color: #c8e6c9; color: #1b5e20; font-weight: bold;'
                    else:
                        # Target එකට වඩා අඩු නම් - රතු පාට
                        styles[i] = 'background-color: #ffcdd2; color: #b71c1c; font-weight: bold;'
            except (ValueError, TypeError):
                pass
    return styles

# Table එක Display කිරීමේදී Function එක apply කිරීම
st.dataframe(df.style.apply(highlight_hourly, axis=1), use_container_width=True)

    # Output Heatmap Visual Chart
    st.subheader("📊 Hourly Production Heatmap Chart")
    fig = px.imshow(
        df[hour_cols],
        labels=dict(x="Hours", y="Modules", color="Pcs Output"),
        color_continuous_scale="Viridis",
        aspect="auto"
    )
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error("Google Sheet එක සම්බන්ධ කිරීමේ දෝෂයක් ඇත. Google Sheet එකේ Column Headers (MODULE, HOURLY_PCS, 1, 2, 3...) නිවැරදිදැයි පරීක්ෂා කරන්න.")
