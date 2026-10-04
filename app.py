import streamlit as st
import pandas as pd
import os

# Page Configuration
st.set_page_config(page_title="GIZA Hourly Production Dashboard", layout="wide")

# Custom CSS for Mobile Responsive Single-Cell Table
st.markdown("""
    <style>
        .mobile-table-container {
            width: 100%;
            max-width: 850px;
            margin: 10px auto;
            overflow-x: auto;
        }
        .mobile-table {
            width: 100%;
            border-collapse: collapse;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 11px;
            text-align: center;
        }
        .mobile-table th {
            background-color: #333;
            color: #fff;
            padding: 6px 3px !important;
            border: 1px solid #444;
            white-space: nowrap;
            font-size: 10px;
            line-height: 1.1;
        }
        .mobile-table td {
            padding: 6px 3px !important;
            border: 1px solid #ccc;
            font-weight: bold;
            font-size: 11px;
            vertical-align: middle;
        }
        .pass-cell {
            background-color: #00a65a !important; /* Bold Green */
            color: #ffffff !important;
        }
        .fail-cell {
            background-color: #ff0000 !important; /* Bold Red */
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# Logo Display Logic
logo_col1, logo_col2, title_col = st.columns([1, 1, 4])

with logo_col1:
    for filename in ["GizaCo-Logo.jpg", "GizaCo-Logo.png", "GizaCo-Logo.jpeg", "giza.png", "giza.jpg"]:
        if os.path.exists(filename):
            st.image(filename, width=100)
            break

with logo_col2:
    for filename in ["HIJ LOGO.png", "HIJ LOGO.jpg", "HIJ LOGO.jpeg", "hij.png", "hij.jpg"]:
        if os.path.exists(filename):
            st.image(filename, width=100)
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

    # Active hours calculation (1 to 8 only)
    active_hours = []
    for h in range(1, 9):
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

    # Clean Mobile HTML Table Generation (Hours 1 to 8)
    html_table = """
    <div class="mobile-table-container">
    <table class="mobile-table">
        <thead>
            <tr>
                <th>Line<br>No</th>
                <th>Day<br>Fcst</th>
                <th>Hr<br>Fcst</th>
                <th>1</th><th>2</th><th>3</th><th>4</th><th>5</th>
                <th>6</th><th>7</th><th>8</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
    """

    for idx, row in raw_df.iterrows():
        html_table += "<tr>"
        
        # Line No cleaning
        line_val = row.get('Line No', row.get('MODULE', ''))
        try:
            line_str = str(int(float(line_val))) if pd.notna(line_val) and str(line_val).strip() != '' else ''
        except:
            line_str = str(line_val) if pd.notna(line_val) else ''
            
        html_table += f"<td>{line_str}</td>"
        
        # Day Forecast
        df_val = row.get('Day Forecast', '')
        try:
            df_str = str(int(float(df_val))) if pd.notna(df_val) and str(df_val).strip() != '' else ''
        except:
            df_str = ''
        html_table += f"<td>{df_str}</td>"
        
        # Hourly Forecast (Target)
        hf_val = row.get('Hourly Forecast', '')
        try:
            target_val = float(hf_val) if pd.notna(hf_val) and str(hf_val).strip() != '' else 0
            hf_str = str(int(target_val)) if target_val > 0 else ''
        except:
            target_val = 0
            hf_str = ''
        html_table += f"<td>{hf_str}</td>"

        # Hours 1 to 8 (Single Cell with Target Comparison Color)
        for h in range(1, 9):
            val = row.get(str(h), '')
            cell_class = ""
            val_str = ""
            
            if pd.notna(val) and str(val).strip() != '' and str(val).lower() != 'nan':
                try:
                    act_val = float(val)
                    val_str = str(int(act_val))
                    
                    if target_val > 0:
                        if act_val >= target_val:
                            cell_class = "pass-cell"
                        else:
                            cell_class = "fail-cell"
                except:
                    val_str = str(val)
            
            html_table += f"<td class='{cell_class}'>{val_str}</td>"

        # TOTAL
        tot_val = row.get('TOTAL', '')
        try:
            tot_str = str(int(float(tot_val))) if pd.notna(tot_val) and str(tot_val).strip() != '' and str(tot_val).lower() != 'nan' else ''
        except:
            tot_str = ''
        html_table += f"<td>{tot_str}</td>"
        html_table += "</tr>"

    html_table += "</tbody></table></div>"

    st.markdown(html_table, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Data Load කිරීමේදී දෝෂයක් සිදු විය: {e}")
