import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าต่างเบราว์เซอร์ให้เป็นแบบ Wide โทนมืดตั้งต้น
st.set_page_config(page_title="Executive Dashboard", layout="wide")

# 🎨 2. ใส่ Custom CSS ปรับแต่งหน้าตาเป็น "โทนมืด (Dark Mode)" ทั้งหน้าเว็บและแถบข้าง
st.markdown("""
    <style>
        @import url('https://googleapis.com');
        
        /* เปลี่ยนสีพื้นหลังหน้าหลักและฟอนต์เป็นโทนมืด */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0F172A !important;
            color: #F8FAFC !important;
            font-family: 'Sarabun', sans-serif;
        }
        
        /* ปรับแต่งแถบเมนูด้านซ้าย (Sidebar) ให้เป็นโทนมืดสีเข้ม */
        [data-testid="stSidebar"] {
            background-color: #1E293B !important;
            border-right: 1px solid #334155 !important;
        }
        [data-testid="stSidebar"] * {
            color: #F8FAFC !important;
        }
        
        /* ปรับสีข้อความหัวข้อเรื่องทั้งหมดให้สว่างชัดเจน */
        h1, h2, h3, h4, h5, h6, p, label {
            color: #F8FAFC !important;
        }
        hr {
            border-color: #334155 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 🔗 3. ลิงก์ที่ได้จากปุ่ม "เผยแพร่ไปยังเว็บ" (Publish to web) ของคุณ
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTeRQBZil1P--FNOmDZYT1sKePSfWgjynp9VvVY-ttHHJ93UkHxHPbf0iG0196eZ587WmOdz70QDMST/pubhtml"

@st.cache_data(ttl=1) # 🔄 ดึงข้อมูลสดใหม่ทุก 1 วินาทีเมื่อเปลี่ยน Filter รองรับการอัปเดตและเพิ่มแถวออโต้
def load_data():
    try:
        # แปลงลิงก์รูปแบบเผยแพร่เว็บให้เป็นข้อมูลตาราง CSV ดิบออโต้
        csv_url = url.replace("/pubhtml", "/pub?output=csv")
        data = pd.read_csv(csv_url, encoding='utf-8')
        data.dropna(how='all', inplace=True) # ลบแถวว่างทิ้งอัตโนมัติ
        data.columns = data.columns.str.strip() # ลบช่องว่างส่วนเกินที่ชื่อคอลัมน์
        return data
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูลได้ โปรดตรวจสอบว่าคัดลอกลิงก์เผยแพร่มาวางถูกต้องหรือไม่: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    # บังคับให้คอลัมน์แรกสุดใน Google Sheet ทำหน้าที่เป็นแกนระบุเวลา/เดือนอัตโนมัติ
    col_month = df.columns[0]
    
    # ดึงชื่อคอลัมน์แผนกทั้งหมดที่เหลือใน Google Sheet ขึ้นมาทำงานแบบ Dynamic อัตโนมัติ (รองรับการเพิ่มแผนกใหม่)
    departments = [col for col in df.columns if col != col_month and not col.startswith('Unnamed')]
    
    try:
        # แปลงโครงสร้างจากหน้ากว้างให้เป็นแนวตั้งเพื่อนำข้อมูลแผนกไปประมวลผล (Wide to Long Format)
        df_melted = pd.melt(df, id_vars=[col_month], value_vars=departments, 
                            var_name='Department', value_name='Value')
        
        # บังคับแปลงค่าข้อมูลทั้งหมดในคอลัมน์ให้เป็นตัวเลขเสมอเพื่อป้องกันกราฟเออร์เรอร์
        df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce').fillna(0)
        
        # 🌟 หัวข้อหลักของระบบแดชบอร์ด (เอาข้อความอธิบายด้านล่างออกตามสั่งแล้วครับ)
        st.title("📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน")
        st.markdown("---")
        
        # 🛠 *4. จัดวางโครงสร้างเมนูด้านข้างคู่ (Sidebar Filters) สำหรับแผนกและเดือน
        st.sidebar.markdown("### 🛠️ ตัวกรองข้อมูล (Filters)")
        
        # ฟิลเตอร์ชุดที่ 1: เลือกกรองตามรายเดือน
        all_months = df[col_month].dropna().astype(str).unique().tolist()
        selected_months = st.sidebar.multiselect(
            "1. เลือกเดือนที่ต้องการดูข้อมูล:", 
            options=all_months, 
            default=all_months
        )
        
        # ฟิลเตอร์ชุดที่ 2: เลือกกรองตามรายแผนก
        selected_depts = st.sidebar.multiselect(
            "2. เลือกแผนกที่ต้องการตรวจสอบ:", 
            options=departments, 
            default=departments
        )
        
        # ประมวลผลคัดกรองข้อมูลดิบตามการกดติ๊ก Filter ของผู้ใช้พร้อมกัน
        filtered_df = df_melted[
            (df_melted[col_month].astype(str).isin(selected_months)) & 
            (df_melted['Department'].isin(selected_depts))
        ]
        
        # 📈 5. พล็อตกราฟแท่งจัดกลุ่มเปรียบเทียบในรูปแบบโทนมืด (Dark Theme Bar Chart)
        # ปรับเซ็ตสีพรีเมียมนีออนสว่างสไตล์ Figma ดึงดูดสายตาบนพื้นหลังสีมืด
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
            template="plotly_dark" # บังคับตัวกราฟและแกนพล็อตให้เป็นธีมมืดสมบูรณ์
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=0,
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(family='Sarabun', size=13, color='#F8FAFC'),
            legend=dict(font=dict(color='#F8FAFC'), title=dict(font=dict(color='#F8FAFC')))
        )
        # ปรับเส้นกริดและสีแกนกราฟให้อ่านง่ายในโหมดมืด
        fig.update_xaxes(tickfont=dict(color='#94A3B8'))
        fig.update_yaxes(showgrid=True, gridcolor='#334151', tickfont=dict(color='#94A3B8'))
        
        # แสดงผลกราฟลงหน้าเว็บจริง
        st.plotly_chart(fig, use_container_width=True)
        
        # 📋 6. ส่วนตรวจสอบโครงสร้างตารางข้อมูลดิบด้านล่างสุด
        st.markdown("---")
        with st.expander("📋 คลิกเพื่อตรวจสอบตารางข้อมูลดิบแบบเรียลไทม์จากระบบ Google Sheet"):
            st.dataframe(df, use_container_width=True)
            
    except Exception as ex:
        st.error(f"เกิดข้อผิดพลาดในการประมวลผลตารางข้อมูล: {ex}")
else:
    st.info("💡 คำแนะนำ: ไม่พบข้อมูลในแผ่นงาน หรือโปรดตรวจสอบว่าลิงก์ในโค้ดบรรทัดที่ 37 เป็นลิงก์ที่ถูกต้อง")
