import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าต่างเบราว์เซอร์ให้เป็นแบบกว้าง (Wide)
st.set_page_config(page_title="Executive Dashboard", layout="wide")

# 🔗 2. ลิงก์ข้อมูลดิบจาก Google Sheet ของคุณในรูปแบบส่งออกตาราง CSV โดยตรง
url = "https://google.com"

@st.cache_data(ttl=1) # 🔄 ดึงข้อมูลสดใหม่เกือบเรียลไทม์ทุก 1 วินาทีเมื่อมีการกด Filter หรือรีเฟรชหน้าจอ
def load_data():
    try:
        # เปิดดึงตารางด้วยรหัส UTF-8 สากลเพื่อป้องกันตัวหนังสือขยะและสระภาษาไทยเพี้ยน
        data = pd.read_csv(url, encoding='utf-8')
        data.dropna(how='all', inplace=True) # ลบแถวเปล่าทิ้งอัตโนมัติหากมีการเคาะบรรทัดเพิ่มใน Sheet
        data.columns = data.columns.str.strip().str.lower() # ลบช่องว่างและตั้งเป็นพิมพ์เล็กเพื่อความปลอดภัย
        return data
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อระบบ Google Sheet ได้เนื่องจากสิทธิ์ความปลอดภัย: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    # ระบุคอลัมน์แกนเวลาตามโครงสร้างตารางจริงของคุณ
    col_month = 'month'
    
    # ดึงคอลัมน์ชื่อแผนกจริงทั้งหมด 6 แผนกจากหัวตาราง Google Sheet ของคุณอัตโนมัติ
    available_depts = [col for col in df.columns if col != col_month and not col.startswith('unnamed')]
    
    try:
        # แปลงโครงสร้างจากหน้ากว้างให้เป็นแนวตั้งเพื่อนำข้อมูลแผนกไปประมวลผล (Wide to Long Format)
        df_melted = pd.melt(df, id_vars=[col_month], value_vars=available_depts, 
                            var_name='Department', value_name='Value')
        
        # บังคับแปลงค่าข้อมูลทั้งหมดในคอลัมน์ผลงานให้เป็นตัวเลขทศนิยม/จำนวนเต็มเสมอ
        df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce').fillna(0)
        
        # 🌟 หน้าจอหลักของระบบ (Main Application Header)
        st.title("📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน")
        st.write("ระบบดึงข้อมูลเรียลไทม์และสแตนด์บายรองรับการพิมพ์เพิ่มแถวข้อมูลออโต้จาก Google Sheet")
        st.markdown("---")
        
        # 🛠️ 3. แถบควบคุมข้อมูลด้านข้างคู่ (Sidebar Filters) - จัดระเบียบครบทั้ง 2 ฟังก์ชัน
        st.sidebar.header("🛠️ ตัวกรองข้อมูล (Filters)")
        
        # ฟิลเตอร์ชุดที่ 1: เลือกกรองตามรายเดือน (ดึงรายการชื่อเดือน Jan-Dec มาอัปเดตแบบเรียลไทม์เมื่อมีการพิมพ์เพิ่มแถวลงไป)
        all_months = df[col_month].dropna().unique().tolist()
        selected_months = st.sidebar.multiselect(
            "1. เลือกเดือนที่ต้องการดูข้อมูล:", 
            options=all_months, 
            default=all_months
        )
        
        # ฟิลเตอร์ชุดที่ 2: เลือกกรองตามรายแผนก (คัดกรอง engineering, sales, marketing, hr, operations, it)
        selected_depts = st.sidebar.multiselect(
            "2. เลือกแผนกที่ต้องการตรวจสอบ:", 
            options=[dept.capitalize() for dept in available_depts], 
            default=[dept.capitalize() for dept in available_depts]
        )
        
        # แปลงข้อมูลตัวเลือกแผนกกลับเป็นตัวพิมพ์เล็กเพื่อนำไปแมตช์หาค่าในฐานข้อมูลหลัก
        selected_depts_lower = [dept.lower() for dept in selected_depts]
        
        # 4. ประมวลผลคัดกรองข้อมูลดิบตามการกดติ๊ก Filter ทั้งสองส่วนของผู้ใช้พร้อมกัน
        filtered_df = df_melted[
            (df_melted[col_month].isin(selected_months)) & 
            (df_melted['Department'].isin(selected_depts_lower))
        ]
        
        # ปรับรูปแบบการแสดงผลของตัวอักษรให้ออกมาสวยงามพรีเมียมพิมพ์ใหญ่ตัวแรก
        filtered_df['Month_Disp'] = filtered_df[col_month].astype(str).str.capitalize()
        filtered_df['Dept_Disp'] = filtered_df['Department'].astype(str).str.capitalize()
        
        # 📈 5. พล็อตกราฟแท่งจัดกลุ่มเปรียบเทียบในรูปแบบโทนมืด (Dark Theme Bar Chart)
        # กำหนดชุดสีสว่างพรีเมียมตัดกับโทนสีดำ-น้ำเงินเข้ม
        modern_colors = ['#6366F1', '#10B981', '#F59E0B', '#F43F5E', '#06B6D4', '#A855F7', '#EC4899']
        
        fig = px.bar(
            filtered_df,
            x='Dept_Disp',
            y='Value',
            color='Month_Disp',
            barmode="group",
            color_discrete_sequence=modern_colors,
            labels={'Month_Disp': 'เดือน', 'Dept_Disp': 'แผนก', 'Value': 'จำนวน'},
            text_auto='.0f',
            template="plotly_dark" # เปลี่ยนดีไซน์พื้นหลังและกรอบของตัวกราฟเป็นโทนมืดสากล
        )
        
        # จัดพื้นที่แสงเงาและระยะขอบของแท่งกราฟให้อ่านง่าย สะอาดตา
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=0,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        fig.update_yaxes(showgrid=True, gridcolor='#334151') # ใส่เส้นกริดจางๆ 
        
        # ดันโครงสร้างภาพพล็อตขึ้นแสดงบนตัวเว็บไซต์
        st.plotly_chart(fig, use_container_width=True)
        
        # 📋 6. ส่วนตรวจสอบโครงสร้างตารางข้อมูลดิบด้านล่างสุด
        st.markdown("---")
        with st.expander("📋 คลิกเพื่อตรวจสอบตารางข้อมูลดิบแบบเรียลไทม์จากระบบ Google Sheet"):
            df_display = df.copy()
            df_display.columns = df_display.columns.str.capitalize()
            st.dataframe(df_display, use_container_width=True)
            
    except Exception as ex:
        st.error(f"เกิดข้อผิดพลาดในการแปลและประมวลผลตารางข้อมูล: {ex}")
else:
    st.info("💡 คำแนะนำ: ไม่พบข้อมูลในแผ่นงาน หรือโปรดตรวจสอบการตั้งค่าแชร์ลิงก์ของ Google Sheet อีกครั้ง")
