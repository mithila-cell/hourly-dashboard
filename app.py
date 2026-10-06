import streamlit as st
import pandas as pd
import os

# Page config
st.set_page_config(
    page_title="GIZA Plant 2 - Hourly Production Monitoring Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom Styling (Desktop & Mobile Optimized)
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
        margin-top: 5px;
        margin-bottom: 10px;
        line-height: 1.2;
    }
    
    /* Center align logos inside columns */
    [data-testid="stColumn"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .table-container {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        font-size: 11px;
        table-layout: auto;
    }
    .styled-table th {
        background-color: #1E293B !important;
        color: white !important;
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

    /* Global Keyframes for Blinking Red Alert (< 40% Target) */
    @keyframes blink-red {
        0% { background-color: #EF4444; color: #FFFFFF; }
        50% { background-color: #7F1D1D; color: #FFFFFF; }
        100% { background-color: #EF4444; color: #FFFFFF; }
    }

    /* Strict Colors */
    td.pass-cell {
        background-color: #22C55E !important;
        color: #FFFFFF !important;
    }
    td.fail-cell {
        background-color: #EF4444 !important;
        color: #FFFFFF !important;
    }
    td.yellow-cell {
        background-color: #EAB308 !important;
        color: #000000 !important;
    }
    td.neutral-cell {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    td.pm-cell {
        background-color: #E2E8F0 !important;
        color: #0F172A !important;
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
col1, col2, col3 = st.columns([1.5, 5, 1.5])

with col1:
    if os.path.exists("GizaCo-Logo.jpg"):
        st.image("GizaCo-Logo.jpg", width=100)

with col2:
    st.markdown('<div class="dashboard-title">GIZA Plant 2 - Hourly Production Monitoring Dashboard</div>', unsafe_allow_html=True)

with col3:
    if os.path.exists("HIJ LOGO.png"):
        st.image("HIJ LOGO.png", width=80)

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
    html += '<th>TOTAL</th>'
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

        entered_hours_count = 0
        total_actual_so_far = 0.0

        for h in hours:
            val = row.get(h, None)
            if not (pd.isna(val) or str(val).strip() == "" or str(val) == "nan"):
                try:
                    act_val = float(val)
                    total_actual_so_far += act_val
                    entered_hours_count += 1
                except (ValueError, TypeError):
                    pass

        target_so_far = hr_fc * entered_hours_count
        
        # Line Number Cell Style Logic (Direct Blinking Inline Style)
        line_extra_style = ""
        if hr_fc > 0 and entered_hours_count > 0 and target_so_far > 0:
            if total_actual_so_far < (0.40 * target_so_far):
                line_extra_style = 'style="animation: blink-red 1s infinite !important;"'

        html += f'<tr>'
        
        if pm_val not in seen_pms:
            rowspan = pm_counts.get(pm_val, 1)
            html += f'<td class="pm-cell" rowspan="{rowspan}">{pm_val}</td>'
            seen_pms.add(pm_val)

        html += f'<td class="neutral-cell" {line_extra_style}>{line_val}</td>'
        html += f'<td class="neutral-cell">{day_fc}</td>'
        html += f'<td class="neutral-cell">{hr_fc_val if not pd.isna(hr_fc_val) else "-"}</td>'

        for h in hours:
            actual_val = row.get(h, None)
            
            # Forecast = 0 නම් පැය 8ම Yellow වෙනවා
            if hr_fc == 0:
                cell_class = "yellow-cell"
                if pd.isna(actual_val) or str(actual_val).strip() == "" or str(actual_val) == "nan":
                    cell_text = "-"
                else:
                    try:
                        act_num = float(actual_val)
                        cell_text = f"{int(act_num)}" if act_num.is_integer() else f"{act_num}"
                    except (ValueError, TypeError):
                        cell_text = str(actual_val)
            else:
                if pd.isna(actual_val) or str(actual_val).strip() == "" or str(actual_val) == "nan":
                    cell_text = "-"
                    cell_class = "neutral-cell"
                else:
                    try:
                        act_num = float(actual_val)
                        cell_text = f"{int(act_num)}" if act_num.is_integer() else f"{act_num}"
                        if act_num >= hr_fc:
                            cell_class = "pass-cell"
                        else:
                            cell_class = "fail-cell"
                    except (ValueError, TypeError):
                        cell_text = str(actual_val)
                        cell_class = "neutral-cell"

            html += f'<td class="{cell_class}">{cell_text}</td>'

        total_text = f"{int(total_actual_so_far)}" if total_actual_so_far.is_integer() else f"{total_actual_so_far}"
        if entered_hours_count == 0:
            total_text = "-"
            
        html += f'<td class="neutral-cell">{total_text}</td>'

        html += '</tr>'

    html += '</tbody></table></div>'
    
    st.markdown(html, unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
else:
    st.warning("No data found in Google Sheet.")
