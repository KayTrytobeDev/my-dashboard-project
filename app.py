import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="แผนก & รายเดือน แดชบอร์ด", layout="wide", page_icon="📊")
st.title("📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน")
st.markdown("---")

# =========================================================
# ⚠️ แก้ไขข้อมูล Google Sheet ของคุณที่นี่
SHEET_ID = "14u71fDUsnE9uMl5G1PieIWaxWmeqAT1YRTOnzSbtr4o"
SHEET_NAME = "Sheet1"  
# =========================================================

url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=10)
def load_data():
    try:
        data = pd.read_csv(url)
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheet ได้: {e}")
        return None

df = load_data()

if df is not None:
    col_dept = 'ลำดับแต่ละแผนก'
    col_month = 'เดือน'
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) > 0:
        col_value = numeric_cols[0]
    else:
        df['จำนวน (แถว)'] = 1
        col_value = 'จำนวน (แถว)'

    st.sidebar.header("🛠️ ตัวกรองข้อมูล (Filters)")
    available_months = df[col_month].dropna().unique().tolist()
    filter_mode = st.sidebar.radio("รูปแบบการดูข้อมูล:", ["เปรียบเทียบทุกเดือน", "กรองดูเฉพาะเดือน"])
    
    if filter_mode == "กรองดูเฉพาะเดือน":
        selected_months = st.sidebar.multiselect("เลือกเดือนที่ต้องการดู:", options=available_months, default=available_months[:1])
        filtered_df = df[df[col_month].isin(selected_months)]
    else:
        filtered_df = df.copy()

    st.subheader(f"📈 กราฟแสดงผลในโหมด: {filter_mode}")
    if filter_mode == "เปรียบเทียบทุกเดือน":
        fig = px.bar(filtered_df, x=col_dept, y=col_value, color=col_month, barmode="group", text_auto=True)
    else:
        fig = px.bar(filtered_df, x=col_dept, y=col_value, color=col_dept, text_auto=True)
        
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 ดูข้อมูลดิบจาก Google Sheet แบบเรียลไทม์"):
        st.dataframe(filtered_df, use_container_width=True)
