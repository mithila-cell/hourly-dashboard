import streamlit as st
import pandas as pd
import os

# Page Configuration
st.set_page_config(page_title="GIZA Hourly Production Dashboard", layout="wide")

# Custom CSS for Mobile Split Cell Standard Layout
st.markdown("""
    <style>
        .mobile-table-container {
            width: 100%;
            overflow-x: auto;
            margin-top: 10px;
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
            padding: 6px 2px !important;
            border: 1px solid #444;
            white-space: nowrap;
            font-size: 10px;
            line-height: 1.1;
        }
        .mobile-table td {
            padding: 0px !important;
            border: 1px solid #ccc;
            vertical-align: middle;
        }
        
        /* Split Cell Layout Style */
        .split-cell {
            display: flex;
            flex-direction: column;
            height: 100%;
            width: 100%;
            min-width: 28px;
        }
        .target-box {
            background-color: #00a65a; /* Green Target Top */
            color: #ffffff;
            font-weight: bold;
            font-size: 10px;
            padding: 2px 0;
            border-bottom: 1px solid rgba(255,255,255,0.3);
        }
        .actual-box-pass {
            background-color: #00a65a; /* Green Actual Bottom */
            color: #ffffff;
            font-weight: bold;
            font-size: 11px;
            padding: 2px 0;
        }
        .actual-box-fail {
            background-color: #ff0000; /* Red Actual Bottom */
            color: #ffffff;
            font-weight: bold;
            font-size: 11px;
            padding: 2px 0;
        }
        
        .plain-td {
            padding: 4px 2px !important;
            font-weight: bold;
            font-size: 11px;
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

    # Split-Cell HTML Table Generation
    html_table = """
    <div class="mobile-table-container">
    <table class="mobile-table">
        <thead>
            <tr>
                <th>Line<br>No</th>
                <th>Day<br>Fcst</th>
                <th>Hr<br>Fcst</th>
                <th>1</th><th>2</th><th>3</th><th>4</th><th>5</th>
                <th>6</th><th>7</th><th>8</th><th>9</th>
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
            
        html_table += f"<td class='plain-td'>{line_str}</td>"
        
        # Day Forecast
        df_val = row.get('Day Forecast', '')
        try:
            df_str = str(int(float(df_val))) if pd.notna(df_val) and str(df_val).strip() != '' else ''
        except:
            df_str = ''
        html_table += f"<td class='plain-td'>{df_str}</td>"
        
        # Hourly Forecast (Target)
        hf_val = row.get('Hourly Forecast', '')
        try:
            target_val = float(hf_val) if pd.notna(hf_val) and str(hf_val).strip() != '' else 0
            hf_str = str(int(target_val)) if target_val > 0 else ''
        except:
            target_val = 0
            hf_str = ''
        html_table += f"<td class='plain-td'>{hf_str}</td>"

        # Hours 1 to 9 (Split Cell Logic)
        for h in range(1, 10):
            val = row.get(str(h), '')
            if pd.notna(val) and str(val).strip() != '' and str(val).lower() != 'nan':
                try:
                    act_val = float(val)
                    act_str = str(int(act_val))
                    
                    # Actual >= Target -> Green else Red
                    actual_class = "actual-box-pass" if (target_val > 0 and act_val >= target_val) else "actual-box-fail"
                    target_str = str(int(target_val)) if target_val > 0 else "-"
                    
                    cell_html = f"""
                    <div class="split-cell">
                        <div class="target-box">{target_str}</div>
                        <div class="{actual_class}">{act_str}</div>
                    </div>
                    """
                except:
                    cell_html = str(val)
            else:
                cell_html = ""
            
            html_table += f"<td>{cell_html}</td>"

        # TOTAL
        tot_val = row.get('TOTAL', '')
        try:
            tot_str = str(int(float(tot_val))) if pd.notna(tot_val) and str(tot_val).strip() != '' and str(tot_val).lower() != 'nan' else ''
        except:
            tot_str = ''
        html_table += f"<td class='plain-td'>{tot_str}</td>"
        html_table += "</tr>"

    html_table += "</tbody></table></div>"

    st.markdown(html_table, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Data Load කිරීමේදී දෝෂයක් සිදු විය: {e}")
