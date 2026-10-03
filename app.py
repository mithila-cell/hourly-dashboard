import streamlit as st
import pandas as pd
import plotly.express as px

# Mobile Responsive Page Config
st.set_page_config(page_title="Hourly Production Dashboard", layout="wide")

st.title("🏭 Hourly Production Live Dashboard")
st.caption("Google Sheets හා සම්බන්ධිත සජීවී Production Tracker එක")

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
    st.dataframe(df, use_container_width=True)

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
