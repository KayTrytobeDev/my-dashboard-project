import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าต่างเบราว์เซอร์ให้เป็นแบบ Wide โทนมืดตั้งต้น
st.set_page_config(page_title="Executive Dashboard", layout="wide")

# 🎨 2. ใส่ Custom CSS ปรับแต่งหน้าตาเป็น "โทนมืด" และปรับขนาดฟอนต์ให้เข้ากับมือถือ
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600&display=swap');
        
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
        
        /* ปรับขนาดตัวอักษรให้เหมาะสมกับหน้าจอมือถือ */
        h1 {
            font-size: 1.8rem !important;
            font-weight: 600;
        }
        h3, label {
            font-size: 1.1rem !important;
        }
        
        hr {
            border-color: #334155 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 🔗 3. ใส่ลิงก์ที่ได้จากปุ่ม "เผยแพร่ไปยังเว็บ" (Publish to web) ของคุณที่นี่
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTeRQBZil1P--FNOmDZYT1sKePSfWgjynp9VvVY-ttHHJ93UkHxHPbf0iG0196eZ587WmOdz70QDMST/pubhtml"  # <--- เปลี่ยนเป็นลิงก์ Google Sheet ของคุณ

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
        
        # หัวข้อหลัก (กระชับขึ้นเพื่อไม่ให้ตกบรรทัดบนจอมือถือ)
        st.title("📊 แดชบอร์ดรายแผนกและรายเดือน")
        st.markdown("---")
        
        # 🛠 4. ตัวกรองข้อมูล (Filters) ใน Sidebar 
        # สำหรับมือถือ เมนูนี้จะถูกพับไว้ในปุ่มลูกศรซ้ายบนอัตโนมัติ ไม่เกะกะสายตา
        st.sidebar.markdown("### 🛠️ ตัวกรองข้อมูล (Filters)")
        
        all_months = df[col_month].dropna().astype(str).unique().tolist()
        selected_months = st.sidebar.multiselect(
            "1. เลือกเดือน:", 
            options=all_months, 
            default=all_months
        )
        
        selected_depts = st.sidebar.multiselect(
            "2. เลือกแผนก:", 
            options=departments, 
            default=departments
        )
        
        filtered_df = df_melted[
            (df_melted[col_month].astype(str).isin(selected_months)) & 
            (df_melted['Department'].isin(selected_depts))
        ]
        
        # 📈 5. พล็อตกราฟแท่ง (ปรับจูนพิเศษเพื่อหน้าจอมือถือ)
        modern_colors = ['#6366F1', '#10B981', '#F59E0B', '#F43F5E', '#06B6D4', '#A855F7', '#EC4899']
        
        fig = px.bar(
            filtered_df,
            x='Department',
            y='Value',
            color=col_month,
            barmode="relative",  # 💡 ปรับเป็นแกนสะสม (Stacked) จะดูบนมือถือง่ายกว่าแบบ Group เยอะมากครับ
            color_discrete_sequence=modern_colors,
            labels={col_month: 'เดือน', 'Department': 'แผนก', 'Value': 'จำนวน'},
            text_auto='.0f',
            template="plotly_dark"
        )
        
        # 📱 ปรับ Layout ให้เข้ากับ Mobile View
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45,  # เอียงชื่อแผนก 45 องศา เพื่อไม่ให้ชื่อเบียดกันบนจอมือถือ
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(family='Sarabun', size=11, color='#F8FAFC'),
            
            # 💡 ย้ายคำอธิบาย (Legend) ไปไว้ด้านล่าง เพื่อให้กราฟแสดงผลได้กว้างเต็มตาบนมือถือ
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.5,
                xanchor="center",
                x=0.5,
                font=dict(size=10, color='#F8FAFC'),
                title=None
            )
        )
        
        fig.update_xaxes(tickfont=dict(color='#94A3B8'))
        fig.update_yaxes(showgrid=True, gridcolor='#334151', tickfont=dict(color='#94A3B8'))
        
        # แสดงผลกราฟ
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}) # ซ่อนปุ่มเครื่องมือของ Plotly บนมือถือเพื่อความสะอาดตา
        
        # 📋 6. ส่วนตรวจสอบตารางข้อมูลดิบ (ซ่อนไว้ใน Expander เพื่อเซฟพื้นที่บนมือถือ)
        st.markdown("---")
        with st.expander("📋 แตะเพื่อดูตารางข้อมูลดิบจาก Google Sheet"):
            st.dataframe(df, use_container_width=True)
            
    except Exception as ex:
        st.error(f"เกิดข้อผิดพลาดในการประมวลผลตารางข้อมูล: {ex}")
else:
    st.info("💡 คำแนะนำ: ไม่พบข้อมูลในแผ่นงาน หรือโปรดตรวจสอบว่าใส่ลิงก์ Google Sheet ถูกต้องแล้ว")
