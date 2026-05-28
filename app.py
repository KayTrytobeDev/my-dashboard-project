import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บแดชบอร์ด
st.set_page_config(page_title="Department Dashboard", layout="wide", page_icon="📊")
st.title("📊 แดชบอร์ดเปรียบเทียบและวิเคราะห์ข้อมูลรายแผนก")
st.markdown("---")

# 2. เชื่อมต่อข้อมูลกับ Google Sheet Master File 
# (อย่าลืมเปิดแชร์ Google Sheet ให้เป็น "ทุกคนที่มีลิงก์มีสิทธิ์อ่าน")
SHEET_ID = "14u71fDUsnE9uMl5G1PieIWaxWmeqAT1YRTOnzSbtr4o"
SHEET_NAME = "Sheet1"  # เช่น Sheet1
url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=60) # รีเฟรชข้อมูลใหม่ทุกๆ 60 วินาทีเมื่อมีการกดโหลดหน้าเว็บ
def load_data():
    data = pd.read_csv(url)
    # ลบช่องว่างในชื่อคอลัมน์เพื่อป้องกันข้อผิดพลาด
    data.columns = data.columns.str.strip()
    return data

try:
    df = load_data()
    
    # ตรวจสอบชื่อคอลัมน์เพื่อให้แน่ใจว่าตรงกับใน Sheet
    # สมมติว่าคอลัมน์ชื่อ 'ลำดับแต่ละแผนก', 'เดือน' และมีคอลัมน์ตัวเลข เช่น 'ยอดขาย' หรือ 'จำนวน'
    col_dept = 'ลำดับแต่ละแผนก'
    col_month = 'เดือน'
    
    # ⚠️ โปรดเปลี่ยนชื่อคอลัมน์นี้ให้ตรงกับคอลัมน์ตัวเลขที่คุณต้องการนำมาทำกราฟเปรียบเทียบ (เช่น ยอดขาย, ค่าใช้จ่าย, ผลงาน)
    col_value = df.columns[2] if len(df.columns) > 2 else None 
    
    if not col_value:
        st.warning("⚠️ กรุณาเพิ่มคอลัมน์ตัวเลข (เช่น ยอดขาย หรือ จำนวน) ใน Google Sheet เพื่อนำมาพล็อตกราฟ")
        df['จำนวน'] = 1 # สร้างข้อมูลสมมติหากไม่มีคอลัมน์ตัวเลข
        col_value = 'จำนวน'

    # 3. ส่วนควบคุมด้านข้าง (Interactive Sidebar Controls)
    st.sidebar.header("🛠️ ตัวกรองข้อมูล (Filters)")
    
    # ดึงรายชื่อเดือนทั้งหมดที่มีในระบบมาทำตัวเลือก
    all_months = sorted(df[col_month].dropna().unique())
    
    # สร้างเมนูให้เลือกโหมดการดู
    view_mode = st.sidebar.radio("เลือกรูปแบบการแสดงผล:", ["เปรียบเทียบทุกเดือน", "กรองดูเฉพาะเดือน"])
    
    if view_mode == "กรองดูเฉพาะเดือน":
        selected_months = st.sidebar.multiselect("เลือกเดือนที่ต้องการดู:", options=all_months, default=[all_months[0]] if all_months else [])
        filtered_df = df[df[col_month].isin(selected_months)]
    else:
        filtered_df = df.copy()

    # 4. ส่วนแสดงผลกราฟและข้อมูล (Main Dashboard)
    
    # แสดงตัวเลขสรุป (Key Metrics)
    total_value = filtered_df[col_value].sum()
    total_depts = filtered_df[col_dept].nunique()
    
    metrics_col1, metrics_col2 = st.columns(2)
    with metrics_col1:
        st.metric(label=f"ผลรวม {col_value} ทั้งหมดที่เลือก", value=f"{total_value:,.2f}")
    with metrics_col2:
        st.metric(label="จำนวนแผนกทั้งหมดในระบบ", value=f"{total_depts} แผนก")
        
    st.markdown("---")

    # การพล็อตกราฟ
    st.subheader(f"📈 กราฟแสดงผลข้อมูล: โหมด {view_mode}")
    
    if view_mode == "เปรียบเทียบทุกเดือน":
        # กราฟแท่งเปรียบเทียบรายเดือน แยกสีตามแผนก หรือ แยกสีตามเดือน
        fig = px.bar(
            filtered_df, 
            x=col_dept, 
            y=col_value, 
            color=col_month, 
            barmode="group",
            title=f"กราฟเปรียบเทียบ {col_value} ของแต่ละแผนกแยกตามรายเดือน",
            labels={col_dept: "แผนก", col_value: col_value, col_month: "เดือน"}
        )
    else:
        # กราฟแท่งแสดงข้อมูลเฉพาะเดือนที่เลือกกรอง
        fig = px.bar(
            filtered_df, 
            x=col_dept, 
            y=col_value, 
            color=col_month,
            title=f"กราฟแสดง {col_value} ของแต่ละแผนกในเดือนที่เลือก",
            labels={col_dept: "แผนก", col_value: col_value}
        )
        
    # ปรับแต่งให้กราฟดูสวยงามและอ่านง่ายขึ้น
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # 5. แสดงตารางข้อมูลดิบด้านล่างกราฟ
    with st.expander("📋 คลิกเพื่อดูตารางข้อมูลดิบจาก Google Sheet ที่กรองแล้ว"):
        st.dataframe(filtered_df, use_container_width=True)

except Exception as e:
    st.error(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อข้อมูล: {e}")
    st.info("💡 คำแนะนำ: ตรวจสอบให้แน่ใจว่าได้เปลี่ยน SPREADSHEET_ID และ ชื่อคอลัมน์ในโค้ดให้ตรงกับไฟล์ของคุณจริง")
