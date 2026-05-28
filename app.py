import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บให้เป็นแบบ Wide โทนมืดตั้งต้น
st.set_page_config(page_title="Executive Dashboard", layout="wide")

# ลิงก์ข้อมูลดิบจาก Google Sheet ของคุณโดยตรง
url = "https://google.com"

@st.cache_data(ttl=1)
def load_data():
    try:
        # อ่านข้อมูลสดและระบุรหัสภาษาเพื่อป้องกันสระภาษาไทยเพี้ยน
        data = pd.read_csv(url, encoding='utf-8')
        data.dropna(how='all', inplace=True)
        # ลบช่องว่างส่วนเกินที่ชื่อคอลัมน์ออกทั้งหมด
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheet ได้: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    # ระบุชื่อคอลัมน์ตรงตามไฟล์ข้อมูลดิบของคุณเป๊ะๆ
    col_month = 'month'
    departments = ['engineering', 'sales', 'marketing', 'hr', 'operations', 'it']
    
    try:
        # แปลงโครงสร้างข้อมูลตารางดิบให้เป็นแนวตั้งเพื่อเตรียมพล็อตกราฟ (Wide to Long)
        df_melted = pd.melt(df, id_vars=[col_month], value_vars=departments, 
                            var_name='Department', value_name='Value')
        
        # บังคับค่าผลงาน/ยอดขายให้เป็นตัวเลขเสมอเพื่อป้องกันกราฟเออร์เรอร์
        df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce').fillna(0)
        
        # หัวข้อแอปพลิเคชัน
        st.title("📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน")
        st.write("ข้อมูลอัปเดตเรียลไทม์รองรับการเพิ่มแถวจากฐานข้อมูลมาสเตอร์ไฟล์ของคุณ")
        st.markdown("---")
        
        # สร้างตัวควบคุมฟิลเตอร์เลือกเดือนที่แถบด้านข้าง (Sidebar)
        st.sidebar.header("🛠️ ตัวกรองข้อมูล (Filters)")
        available_months = df[col_month].dropna().unique().tolist()
        selected_months = st.sidebar.multiselect("เลือกเดือนที่ต้องการดูข้อมูล:", options=available_months, default=available_months)
        
        # กรองข้อมูลตามเดือนที่เลือกคลิก
        filtered_df = df_melted[df_melted[col_month].isin(selected_months)]
        
        # 📈 พล็อตกราฟแท่งแบบกลุ่มเปรียบเทียบ (Grouped Bar Chart)
        # ใช้โทนสีสว่างคมชัดตัดกับพื้นหลังมืด (Dark Theme)
        modern_colors = ['#6366F1', '#10B981', '#F59E0B', '#F43F5E', '#06B6D4', '#A855F7', '#EC4899']
        
        fig = px.bar(
            filtered_df,
            x='Department',
            y='Value',
            color=col_month,
            barmode="group",
            color_discrete_sequence=modern_colors,
            labels={col_month: 'เดือน', 'Department': 'แผนก', 'Value': 'จำนวน'},
            text_auto='.0f',
            template="plotly_dark" # บังคับให้ตัวกราฟและแกนพล็อตเป็นโทนมืดสากล
        )
        
        # จัดการสัดส่วนของกราฟให้สะอาดตา อ่านง่าย
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=0,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        fig.update_yaxes(showgrid=True, gridcolor='#334151')
        
        # แสดงผลกราฟลงหน้าเว็บจริง
        st.plotly_chart(fig, use_container_width=True)
        
        # 📋 ตารางตรวจสอบข้อมูลดิบด้านล่างสุด
        st.markdown("---")
        with st.expander("📋 คลิกเพื่อตรวจสอบตารางข้อมูลดิบจริงจาก Google Sheet"):
            st.dataframe(df, use_container_width=True)
            
    except Exception as ex:
        st.error(f"เกิดข้อผิดพลาดในการประมวลผลตารางข้อมูล: {ex}")
else:
    st.info("💡 คำแนะนำ: ไม่พบข้อมูลในแผ่นงาน หรือโปรดตรวจสอบสิทธิ์การแชร์ของ Google Sheet อีกครั้ง")
