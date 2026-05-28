import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าต่างเบราว์เซอร์ให้เป็นแบบ Wide โทนมืดตั้งต้น
st.set_page_config(page_title="Executive Dashboard", layout="wide")

# 🔗 2. นำลิงก์ที่ได้หลังจากกดปุ่ม "เผยแพร่ไปยังเว็บ" (Publish to web) มาวางในเครื่องหมายคำพูดด้านล่างนี้แทนลิงก์เดิมทั้งหมด
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTeRQBZil1P--FNOmDZYT1sKePSfWgjynp9VvVY-ttHHJ93UkHxHPbf0iG0196eZ587WmOdz70QDMST/pubhtml"

@st.cache_data(ttl=1) # 🔄 ดึงข้อมูลสดใหม่ทุก 1 วินาทีเมื่อเปลี่ยน Filter รองรับการอัปเดตและเพิ่มแถวออโต้
def load_data():
    try:
        # ดึงข้อมูลจากหน้าเว็บที่แชร์และระบุประเภทตารางให้ถูกต้องเพื่อรองรับภาษาไทย/อังกฤษ
        # หากใช้ลิงก์สากลระบบจะช่วยล้างสคริปต์ความปลอดภัยส่วนเกินออกให้อัตโนมัติ
        csv_url = url.replace("/edit?gid=0#gid=0", "/export?format=csv&gid=0").replace("/pubhtml", "/pub?output=csv")
        data = pd.read_csv(csv_url, encoding='utf-8')
        data.dropna(how='all', inplace=True) # ลบแถวว่างทิ้งอัตโนมัติ
        data.columns = data.columns.str.strip() # ลบช่องว่างส่วนเกินที่ชื่อคอลัมน์
        return data
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูลได้ โปรดตรวจสอบว่าคัดลอกลิงก์เผยแพร่มาวางถูกต้องหรือไม่: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    # 🛠️ ระบุให้คอลัมน์แรกสุดใน Google Sheet ทำหน้าที่เป็นแกนระบุเวลา/เดือนอัตโนมัติ
    col_month = df.columns[0]
    
    # 🛠️ ดึงชื่อคอลัมน์แผนกทั้งหมดที่เหลือใน Google Sheet ขึ้นมาทำงานแบบ Dynamic อัตโนมัติ (รองรับการเพิ่มแผนกใหม่)
    departments = [col for col in df.columns if col != col_month and not col.startswith('Unnamed')]
    
    try:
        # แปลงโครงสร้างจากหน้ากว้างให้เป็นแนวตั้งเพื่อนำข้อมูลแผนกไปประมวลผล (Wide to Long Format)
        df_melted = pd.melt(df, id_vars=[col_month], value_vars=departments, 
                            var_name='Department', value_name='Value')
        
        # บังคับแปลงค่าข้อมูลทั้งหมดในคอลัมน์ให้เป็นตัวเลขเสมอเพื่อป้องกันกราฟเออร์เรอร์
        df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce').fillna(0)
        
        # หัวข้อหลักของระบบแดชบอร์ด
        st.title("📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน")
        st.write("ระบบดึงข้อมูลเรียลไทม์และสแตนด์บายรองรับการพิมพ์เพิ่มแถวข้อมูลออโต้จาก Google Sheet")
        st.markdown("---")
        
        # 🛠️ 3. แถบควบคุมข้อมูลด้านข้างคู่ (Sidebar Filters) สำหรับแผนกและเดือน
        st.sidebar.header("🛠️ ตัวกรองข้อมูล (Filters)")
        
        # ฟิลเตอร์ชุดที่ 1: เลือกกรองตามรายเดือน (รายชื่อจะเพิ่มตามตารางที่อัปเดต)
        all_months = df[col_month].dropna().astype(str).unique().tolist()
        selected_months = st.sidebar.multiselect(
            "1. เลือกเดือนที่ต้องการดูข้อมูล:", 
            options=all_months, 
            default=all_months
        )
        
        # ฟิลเตอร์ชุดที่ 2: เลือกกรองตามรายแผนก (รายชื่อแผนกจะเพิ่มตามตารางที่อัปเดต)
        selected_depts = st.sidebar.multiselect(
            "2. เลือกแผนกที่ต้องการตรวจสอบ:", 
            options=departments, 
            default=departments
        )
        
        # 4. ประมวลผลคัดกรองข้อมูลดิบตามการกดติ๊ก Filter ของผู้ใช้พร้อมกัน
        filtered_df = df_melted[
            (df_melted[col_month].astype(str).isin(selected_months)) & 
            (df_melted['Department'].isin(selected_depts))
        ]
        
        # 📈 5. พล็อตกราฟแท่งจัดกลุ่มเปรียบเทียบในรูปแบบโทนมืด (Dark Theme Bar Chart)
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
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=0,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        fig.update_yaxes(showgrid=True, gridcolor='#334151')
        
        # แสดงผลกราฟลงหน้าเว็บจริง
        st.plotly_chart(fig, use_container_width=True)
        
        # 📋 6. ส่วนตรวจสอบโครงสร้างตารางข้อมูลดิบด้านล่างสุด
        st.markdown("---")
        with st.expander("📋 คลิกเพื่อตรวจสอบตารางข้อมูลดิบแบบเรียลไทม์จากระบบ Google Sheet"):
            st.dataframe(df, use_container_width=True)
            
    except Exception as ex:
        st.error(f"เกิดข้อผิดพลาดในการประมวลผลตารางข้อมูล: {ex}")
else:
    st.info("💡 คำแนะนำ: ไม่พบข้อมูลในแผ่นงาน หรือโปรดตรวจสอบว่าลิงก์ในโค้ดบรรทัดที่ 9 เป็นลิงก์ที่ถูกต้อง")
