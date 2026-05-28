import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บแดชบอร์ด
st.set_page_config(page_title="แผนก & รายเดือน แดชบอร์ด", layout="wide", page_icon="📊")
st.title("📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน")
st.markdown("---")

# เชื่อมต่อ Google Sheet ของคุณ (ตรวจสอบความถูกต้องเรียบร้อยแล้ว)
SHEET_ID = "14u71fDUsnE9uMl5G1PieIWaxWmeqAT1YRTOnzSbtr4o"
SHEET_NAME = "Sheet1"  

url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=5) # อัปเดตข้อมูลไวขึ้น ทุกๆ 5 วินาทีเมื่อมีการรีเฟรชหน้าเว็บ
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
    # 2. ปรับโครงสร้างข้อมูลจากแบบกว้าง (Wide format) ให้เป็นแบบยาว (Long format) เพื่อให้จัดกลุ่มพล็อตกราฟง่าย
    # แปลงคอลัมน์แผนกต่างๆ มารวมกันให้อยู่ในคอลัมน์เดี่ยว
    departments = [col for col in df.columns if col != 'month']
    df_melted = pd.melt(df, id_vars=['month'], value_vars=departments, 
                        var_name='แผนก (Department)', value_name='ผลงาน/ยอดขาย (Value)')
    
    # 3. เมนูด้านข้าง (Sidebar Filters)
    st.sidebar.header("🛠️ ตัวกรองข้อมูล (Filters)")
    
    # รายชื่อเดือนทั้งหมดที่มีใน Google Sheet ของคุณ (Jan - Dec)
    available_months = df['month'].dropna().unique().tolist()
    
    # เมนูเลือกโหมดแสดงผล
    filter_mode = st.sidebar.radio("รูปแบบการดูข้อมูล:", ["เปรียบเทียบทุกเดือน", "กรองดูเฉพาะเดือน"])
    
    if filter_mode == "กรองดูเฉพาะเดือน":
        selected_months = st.sidebar.multiselect("เลือกเดือนที่ต้องการดู:", options=available_months, default=available_months[:3])
        filtered_df = df_melted[df_melted['month'].isin(selected_months)]
    else:
        filtered_df = df_melted.copy()

    # 4. แสดงผลกราฟแท่งแบบกลุ่ม (Grouped Bar Chart)
    st.subheader(f"📈 กราฟแสดงผลในโหมด: {filter_mode}")
    
    fig = px.bar(
        filtered_df,
        x='แผนก (Department)',
        y='ผลงาน/ยอดขาย (Value)',
        color='month', # แยกสีตามเดือนเพื่อให้เปรียบเทียบง่าย
        barmode="group", # จัดกลุ่มแท่งกราฟให้อยู่ข้างกัน
        title="กราฟเปรียบเทียบข้อมูลแต่ละแผนกแยกตามรายเดือน",
        labels={'month': 'เดือน', 'แผนก (Department)': 'แผนก', 'ผลงาน/ยอดขาย (Value)': 'จำนวน'},
        text_auto=True # แสดงตัวเลขยอดบนแท่งกราฟอัตโนมัติ
    )
        
    fig.update_layout(xaxis_tickangle=0, legend_title_text='เดือน')
    st.plotly_chart(fig, use_container_width=True)

    # 5. แสดงตารางข้อมูลดิบด้านล่าง
    with st.expander("📋 ดูข้อมูลดิบจาก Google Sheet แบบเรียลไทม์"):
        st.dataframe(df, use_container_width=True)
else:
    st.info("💡 กำแนะนำ: ตรวจสอบลิงก์และสิทธิ์การแชร์ของ Google Sheet อีกครั้ง")
