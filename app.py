import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บแดชบอร์ด
st.set_page_config(page_title="แผนก & รายเดือน แดชบอร์ด", layout="wide", page_icon="📊")

st.title("📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน")
st.markdown("---")

# =========================================================
# 2. ป้อนข้อมูล Google Sheet ของคุณที่นี่
# แปะรหัส ID ที่ได้จากลิงก์ Google Sheet ของคุณแทนที่ตัวอักษรด้านล่างนี้
SHEET_ID = "ใส่_ID_ของ_Google_Sheet_ของคุณตรงนี้"
SHEET_NAME = "Sheet1"  # ใส่ชื่อแท็บ เช่น Sheet1 หรือ แผ่นงาน1
# =========================================================

url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=10) # ดึงข้อมูลใหม่จาก Google Sheet ทุกๆ 10 วินาทีเมื่อรีเฟรช
def load_data():
    try:
        data = pd.read_csv(url)
        data.columns = data.columns.str.strip() # ลบช่องว่างส่วนเกินในชื่อคอลัมน์
        return data
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheet ได้: {e}")
        return None

df = load_data()

if df is not None:
    # ระบุชื่อคอลัมน์ให้ตรงกับที่ระบุมา
    col_dept = 'ลำดับแต่ละแผนก'
    col_month = 'เดือน'
    
    # ค้นหาคอลัมน์ที่เป็นตัวเลขโดยอัตโนมัติเพื่อนำมาทำกราฟ
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) > 0:
        col_value = numeric_cols[0] # ใช้คอลัมน์ตัวเลขแรกที่เจอ
    else:
        st.warning("⚠️ ไม่พบคอลัมน์ที่เป็นตัวเลขใน Google Sheet ระบบจะนับจำนวนแถวให้แทน")
        df['จำนวน (แถว)'] = 1
        col_value = 'จำนวน (แถว)'

    # 3. เมนูด้านข้าง (Sidebar Filters)
    st.sidebar.header("🛠️ ตัวกรองข้อมูล (Filters)")
    
    # รายชื่อเดือนทั้งหมดที่มีใน Google Sheet
    available_months = df[col_month].dropna().unique().tolist()
    
    # เมนูเลือกโหมด
    filter_mode = st.sidebar.radio("รูปแบบการดูข้อมูล:", ["เปรียบเทียบทุกเดือน", "กรองดูเฉพาะเดือน"])
    
    if filter_mode == "กรองดูเฉพาะเดือน":
        selected_months = st.sidebar.multiselect("เลือกเดือนที่ต้องการดู:", options=available_months, default=available_months[:1])
        filtered_df = df[df[col_month].isin(selected_months)]
    else:
        filtered_df = df.copy()

    # 4. แสดงผลกราฟ
    st.subheader(f"📈 กราฟแสดงผลในโหมด: {filter_mode}")
    
    if filter_mode == "เปรียบเทียบทุกเดือน":
        # กราฟแท่งเปรียบเทียบรายเดือน แยกสีตามเดือน
        fig = px.bar(
            filtered_df,
            x=col_dept,
            y=col_value,
            color=col_month,
            barmode="group",
            title=f"กราฟเปรียบเทียบ {col_value} ของแต่ละแผนกในแต่ละเดือน",
            labels={col_dept: "แผนก", col_value: col_value, col_month: "เดือน"},
            text_auto=True
        )
    else:
        # กราฟแสดงเฉพาะเดือนที่เลือก
        fig = px.bar(
            filtered_df,
            x=col_dept,
            y=col_value,
            color=col_dept,
            title=f"กราฟแสดง {col_value} ของแต่ละแผนก ในเดือนที่เลือกฟิลเตอร์",
            labels={col_dept: "แผนก", col_value: col_value},
            text_auto=True
        )
        
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # 5. แสดงตารางข้อมูลดิบ
    with st.expander("📋 ดูข้อมูลดิบจาก Google Sheet แบบเรียลไทม์"):
        st.dataframe(filtered_df, use_container_width=True)
else:
    st.info("💡 คำแนะนำ: ตรวจสอบให้แน่ใจว่าได้เปิดแชร์ Google Sheet เป็น 'ทุกคนที่มีลิงก์มีสิทธิ์อ่าน' และใส่ ID ถูกต้อง")

