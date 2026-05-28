import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าต่างเบราว์เซอร์ให้เป็นแบบกว้าง (Wide)
st.set_page_config(page_title="Executive Dashboard", layout="wide")

# 🔗 2. แก้ไขทางผ่านลิงก์ใหม่: เปลี่ยนเป็นลิงก์ดึงข้อมูลผ่านการ Publish เพื่อหลบระบบบล็อกรักษาความปลอดภัยของกูเกิล
url = "https://google.com"
# (หมายเหตุ: หากลิงก์ pub ด้านบนดึงข้อมูลไม่สำเร็จ โค้ดจะใช้ระบบฟิลเตอร์ดักจับข้อมูลขยะด้านล่างซ้ำอีกชั้นเพื่อความปลอดภัยสูงสุด)

@st.cache_data(ttl=1)
def load_data():
    try:
        # ใช้ลิงก์สำรองของคุณหากระบบหลักยังติดแคชความปลอดภัย โดยบังคับแกะรหัสสากล
        fallback_url = "https://google.com"
        data = pd.read_csv(fallback_url, encoding='utf-8')
        data.dropna(how='all', inplace=True)
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อระบบ Google Sheet ได้: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    # กำหนดคอลัมน์แรกสุดเป็นแกนเวลาออโต้
    col_month = df.columns[0]
    
    # ดึงคอลัมน์ชื่อแผนกจริงทั้งหมดจากไฟล์ข้อมูลของคุณ
    available_depts = [col for col in df.columns if col != col_month and not col.startswith('Unnamed')]
    
    try:
        # 🛠️ ระบบเคลียร์ขยะขั้นเด็ดขาด: กรองเอาเฉพาะแถวข้อมูลที่เป็นชื่อเดือนภาษาอังกฤษสากล 12 เดือนเท่านั้น!
        # แถวไหนที่เป็นข้อความยาวๆ หรือสคริปต์ JavaScript แปลกๆ ระบบจะลบทิ้งไปจากหน้าจอทั้งหมดทันที
        df[col_month] = df[col_month].astype(str).str.strip()
        valid_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                        'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        df = df[df[col_month].str.lower().isin([m.lower() for m in valid_months])]

        # แปลงโครงสร้างข้อมูลจากหน้ากว้างให้เป็นแนวตั้งเพื่อนำข้อมูลแผนกไปประมวลผล (Wide to Long)
        df_melted = pd.melt(df, id_vars=[col_month], value_vars=available_depts, 
                            var_name='Department', value_name='Value')
        
        # บังคับแปลงค่าผลงานทั้งหมดให้เป็นตัวเลข แถวไหนเป็นข้อความเสียระบบจะเปลี่ยนเป็น 0 เพื่อป้องกันกราฟพัง
        df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce').fillna(0)
        
        # ปรับแต่งตัวอักษรชื่อเดือนและแผนกให้พิมพ์ใหญ่ตัวแรกสวยงามสไตล์ Figma
        df_melted['Month_Disp'] = df_melted[col_month].astype(str).str.capitalize()
        df_melted['Dept_Disp'] = df_melted['Department'].astype(str).str.capitalize()

        # 🌟 หน้าจอหลักของระบบ (Main Application Header)
        st.title("📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน")
        st.write("ระบบดึงข้อมูลเรียลไทม์และสแตนด์บายรองรับการพิมพ์เพิ่มแถวข้อมูลออโต้จาก Google Sheet")
        st.markdown("---")
        
        # 🛠️ 3. แถบควบคุมข้อมูลด้านข้างคู่ (Sidebar Filters)
        st.sidebar.header("🛠️ ตัวกรองข้อมูล (Filters)")
        
        # ฟิลเตอร์ชุดที่ 1: เลือกกรองตามรายเดือน
        all_months = df_melted['Month_Disp'].dropna().unique().tolist()
        selected_months = st.sidebar.multiselect(
            "1. เลือกเดือนที่ต้องการดูข้อมูล:", 
            options=all_months, 
            default=all_months[:3] if len(all_months) >= 3 else all_months
        )
        
        # ฟิลเตอร์ชุดที่ 2: เลือกกรองตามรายแผนก
        all_depts_disp = df_melted['Dept_Disp'].dropna().unique().tolist()
        selected_depts = st.sidebar.multiselect(
            "2. เลือกแผนกที่ต้องการตรวจสอบ:", 
            options=all_depts_disp, 
            default=all_depts_disp
        )
        
        # 4. คัดกรองข้อมูลในตารางตามตัวเลือก Filter ที่ผู้ใช้ติ๊กเลือกจริงพร้อมกัน
        filtered_df = df_melted[
            (df_melted['Month_Disp'].isin(selected_months)) & 
            (df_melted['Dept_Disp'].isin(selected_depts))
        ]
        
        # 📈 5. พล็อตกราฟแท่งจัดกลุ่มเปรียบเทียบในรูปแบบโทนมืด (Dark Theme Bar Chart)
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
            template="plotly_dark" # เปลี่ยนกราฟและแกนเป็นโทนมืดสากลพรีเมียม
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=0,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        fig.update_yaxes(showgrid=True, gridcolor='#334151')
        
        # แสดงผลกราฟลงหน้าเว็บจริง
        st.plotly_chart(fig, use_container_width=True)
        
        # 📋 6. ส่วนตรวจสอบตารางข้อมูลดิบด้านล่างสุด
        st.markdown("---")
        with st.expander("📋 คลิกเพื่อตรวจสอบตารางข้อมูลดิบแบบเรียลไทม์จากระบบ Google Sheet"):
            st.dataframe(df, use_container_width=True)
            
    except Exception as ex:
        st.error(f"เกิดข้อผิดพลาดในการแปลและประมวลผลตารางข้อมูล: {ex}")
else:
    st.info("💡 คำแนะนำ: ตารางข้อมูลว่างเปล่า หรือสิทธิ์การแชร์ของ Google Sheet ถูกปิดกั้น โปรดตรวจสอบการตั้งค่าไฟล์มาสเตอร์ของคุณ")
