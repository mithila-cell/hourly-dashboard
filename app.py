import streamlit as st
import pandas as pd
import os

# Page config
st.set_page_config(
    page_title="GIZA Plant 2 - Hourly Production Monitoring Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    /* Top padding adjustment */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    .dashboard-title {
        font-size: 20px;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 10px;
        line-height: 1.2;
    }
    
    .table-container {
        width: 100%;
        overflow-x: auto;
    }
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        font-size: 11px;
        table-layout: auto;
    }
    .styled-table th {
        background-color: #1E293B;
        color: white;
        padding: 6px 4px;
        text-align: center;
        border: 1px solid #334155;
        font-weight: bold;
        white-space: nowrap;
    }
    .styled-table td {
        padding: 5px 3px;
        text-align: center;
        border: 1px solid #CBD5E1;
        font-weight: bold;
        white-space: nowrap;
    }
    
    /* Cell Status Colors */
    .pass-cell {
        background-color: #22C55E !important;
        color: white !important;
    }
    .fail-cell {
        background-color: #EF4444 !important;
        color: white !important;
    }
    .yellow-cell {
        background-color: #EAB308 !important;
        color: white !important;
    }
    .neutral-cell {
        background-color: #F8FAFC;
        color: #0F172A;
    }
    .pm-cell {
        background-color: #E2E8F0;
        color: #0F172A;
        vertical-align: middle;
        font-weight: bold;
        font-size: 10px;
    }

    @media (max-width: 600px) {
        .dashboard-title {
            font-size: 14px;
        }
        .styled-table {
            font-size: 9px;
        }
        .styled-table th, .styled-table td {
            padding: 3px 1px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Layout Header with Logos and Title
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    if os.path.exists("GizaCo-Logo.jpg"):
        st.image("GizaCo-Logo.jpg", width=110)

with col2:
    st.markdown('<div class="dashboard-title">GIZA Plant 2 - Hourly Production Monitoring Dashboard</div>', unsafe_allow_html=True)

with col3:
    if os.path.exists("HIJ LOGO.png"):
        st.image("HIJ LOGO.png", width=90)

SHEET_URL = "https://docs.google.com/spreadsheets/d/18YQkUYI-GQz24ImIIdm4vmB_JYBmNKIxDsgdWyJ0ehQ/export?format=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        return df
    except Exception as e:
        st.error(f"Error loading Google Sheet: {e}")
        return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    df_raw.columns = [str(col).strip() for col in df_raw.columns]
    df = df_raw.copy()
    
    if 'PM' in df.columns:
        df['PM'] = df['PM'].ffill()

    if 'Line No' in df.columns:
        df['Line No Clean'] = df['Line No'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        df['Line No Clean'] = df['Line No Clean'].replace('nan', '')
    else:
        df['Line No Clean'] = ''

    df = df[df['PM'].notna() & (df['PM'] != '')]

    hours = [str(h) for h in range(1, 9)]
    
    html = '<div class="table-container"><table class="styled-table"><thead><tr>'
    html += '<th>PM</th>'
    html += '<th>Line</th>'
    html += '<th>Day FC</th>'
    html += '<th>Hr FC</th>'
    
    for h in hours:
        html += f'<th>H{h}</th>'
    html += '</tr></thead><tbody>'

    pm_counts = df['PM'].value_counts(sort=False)
    seen_pms = set()

    for _, row in df.iterrows():
        pm_val = str(row.get('PM', ''))
        line_val = row.get('Line No Clean', '')
        day_fc = str(row.get('Day Forecast', '0'))
        if pd.isna(day_fc) or day_fc == 'nan':
            day_fc = '-'
            
        hr_fc_val = row.get('Hourly Forecast', 0)
        
        try:
            hr_fc = float(hr_fc_val)
        except (ValueError, TypeError):
            hr_fc = 0.0

        html += f'<tr>'
        
        if pm_val not in seen_pms:
            rowspan = pm_counts.get(pm_val, 1)
            html += f'<td class="pm-cell" rowspan="{rowspan}">{pm_val}</td>'
            seen_pms.add(pm_val)

        html += f'<td class="neutral-cell">{line_val}</td>'
        html += f'<td class="neutral-cell">{day_fc}</td>'
        html += f'<td class="neutral-cell">{hr_fc_val if not pd.isna(hr_fc_val) else "-"}</td>'

        for h in hours:
            actual_val = row.get(h, None)
            
            if pd.isna(actual_val) or str(actual_val).strip() == "" or str(actual_val) == "nan":
                cell_text = "-"
            else:
                try:
                    act_num = float(actual_val)
                    cell_text = f"{int(act_num)}" if act_num.is_integer() else f"{act_num}"
                except (ValueError, TypeError):
                    cell_text = str(actual_val)

            # Color Logic
            if cell_text == "-":
                cell_class = "neutral-cell"
            elif hr_fc == 0:
                cell_class = "yellow-cell"
            else:
                try:
                    act_num = float(actual_val)
                    if act_num >= hr_fc:
                        cell_class = "pass-cell"
                    else:
                        cell_class = "fail-cell"
                except (ValueError, TypeError):
                    cell_class = "neutral-cell"

            html += f'<td class="{cell_class}">{cell_text}</td>'

        html += '</tr>'

    html += '</tbody></table></div>'
    
    st.markdown(html, unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
else:
    st.warning("No data found in Google Sheet.")
