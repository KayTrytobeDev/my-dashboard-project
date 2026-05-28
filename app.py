import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าต่างเบราว์เซอร์ให้ยืดหยุ่นแบบมืดตั้งต้น
st.set_page_config(page_title="Executive Dashboard", layout="wide")

# 🎨 2. Custom CSS สไตล์พรีเมียม โทนมืด และรองรับ Responsive ทุกหน้าจอ
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600&display=swap');
        
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0F172A !important;
            color: #F8FAFC !important;
            font-family: 'Sarabun', sans-serif;
        }
        
        /* สไตล์หัวข้อหลัก */
        h1 {
            font-size: 1.8rem !important;
            font-weight: 600;
            color: #F8FAFC !important;
        }
        @media (max-width: 768px) {
            h1 { font-size: 1.4rem !important; }
        }
        
        /* แต่งหน้าตาปุ่มวิเศษ (Radio Button ของตัวช่วยเลือก) */
        div[data-testid="stRadio"] > label {
            font-weight: bold;
            color: #38BDF8 !important;
        }
        
        label {
            color: #F8FAFC !important;
            font-weight: 600;
        }
        
        hr { border-color: #334155 !important; }
    </style>
""", unsafe_allow_html=True)

# 🔗 3. ลิงก์จาก Google Sheet (พ่นข้อมูลออกมาเป็น CSV อัตโนมัติ)
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTeRQBZil1P--FNOmDZYT1sKePSfWgjynp9VvVY-ttHHJ93UkHxHPbf0iG0196eZ587WmOdz70QDMST/pubhtml"  # <--- เปลี่ยนเป็นลิงก์ Google Sheet ของคุณที่นี่

@st.cache_data(ttl=1) 
def load_data():
    try:
        csv_url = url.replace("/pubhtml", "/pub?output=csv")
        data = pd.read_csv(csv_url, encoding='utf-8')
        data.dropna(how='all', inplace=True) 
        data.columns = data.columns.str.strip() 
        return data
    except Exception as e:
        st.error(f"ไม่สามารถดึงข้อมูลได้ โปรดตรวจสอบลิงก์ Google Sheet: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    col_month = df.columns[0]
    departments = [col for col in df.columns if col != col_month and not col.startswith('Unnamed')]
    
    try:
        df_melted = pd.melt(df, id_vars=[col_month], value_vars=departments, 
                            var_name='Department', value_name='Value')
        df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce').fillna(0)
        
        # ส่วนหัวแดชบอร์ด
        st.title("📊 ระบบเปรียบเทียบข้อมูลอัจฉริยะ (Universal Dashboard)")
        st.markdown("---")
        
        #
