import streamlit as st
import pandas as pd

# Page config - Title එක නිවැරදි කර ඇත
st.set_page_config(
    page_title="GIZA Plant 2 - Hourly Production Monitoring Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-title {
        font-size: 26px;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 18px;
        font-weight: 600;
        color: #2563EB;
        text-align: center;
        margin-bottom: 25px;
    }
    
    /* Table Styling */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        font-size: 14px;
        margin-top: 10px;
    }
    .styled-table th {
        background-color: #1E293B;
        color: white;
        padding: 10px 6px;
        text-align: center;
        border: 1px solid #334155;
        font-weight: bold;
    }
    .styled-table td {
        padding: 8px 6px;
        text-align: center;
        border: 1px solid #CBD5E1;
        font-weight: bold;
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
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">GIZA Plant 2 - Hourly Production Monitoring Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Line Wise Hourly Production Output</div>', unsafe_allow_html=True)

# Public Google Sheet CSV Link
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
    
    # Fill missing PM values vertically
    if 'PM' in df.columns:
        df['PM'] = df['PM'].ffill()

    # Clean Line No
    df['Line No Clean'] = df['Line No'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    df = df[df['Line No Clean'].str.contains(r'^\d+$', na=False)]

    hours = [str(h) for h in range(1, 9)]
    
    html = '<table class="styled-table"><thead><tr>'
    html += '<th>PM</th>'
    html += '<th>Line No</th>'
    html += '<th>Day Forecast</th>'
    html += '<th>Hourly Forecast</th>'
    
    for h in hours:
        html += f'<th>Hour {h}</th>'
    html += '</tr></thead><tbody>'

    # PM එකට අදාළ Lines ගණන ගණනය කිරීම (Merge කිරීම සඳහා)
    pm_counts = df['PM'].value_counts(sort=False)
    seen_pms = set()

    for _, row in df.iterrows():
        pm_val = str(row.get('PM', ''))
        line_val = row.get('Line No Clean', '')
        day_fc = str(row.get('Day Forecast', '0'))
        hr_fc_val = row.get('Hourly Forecast', 0)
        
        try:
            hr_fc = float(hr_fc_val)
        except (ValueError, TypeError):
            hr_fc = 0.0

        html += f'<tr>'
        
        # PM කෙනෙකුගේ නම පටන් ගන්නා විට පමණක් Rowspan එකක් දමා Merge කිරීම
        if pm_val not in seen_pms:
            rowspan = pm_counts.get(pm_val, 1)
            html += f'<td class="pm-cell" rowspan="{rowspan}">{pm_val}</td>'
            seen_pms.add(pm_val)

        html += f'<td class="neutral-cell">{line_val}</td>'
        html += f'<td class="neutral-cell">{day_fc}</td>'
        html += f'<td class="neutral-cell">{hr_fc_val}</td>'

        for h in hours:
            actual_val = row.get(h, None)
            
            if pd.isna(actual_val) or str(actual_val).strip() == "":
                cell_text = "-"
            else:
                try:
                    act_num = float(actual_val)
                    cell_text = f"{int(act_num)}" if act_num.is_integer() else f"{act_num}"
                except (ValueError, TypeError):
                    cell_text = str(actual_val)

            # Color logic
            if hr_fc == 0:
                cell_class = "yellow-cell"
            elif cell_text == "-":
                cell_class = "neutral-cell"
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

    html += 'tbody></table>'
    
    st.markdown(html, unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
else:
    st.warning("No data found in Google Sheet.")
