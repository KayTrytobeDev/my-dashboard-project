import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าต่างเบราว์เซอร์ให้เป็นแบบ Wide โทนมืดตั้งต้น
st.set_page_config(page_title="Executive Dashboard", layout="wide")

# 🎨 2. ใส่ Custom CSS ปรับแต่งหน้าตาเป็น "โทนมืด" และปรับแต่งให้เหมาะกับจอมือถือ
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600&display=swap');
        
        /* เปลี่ยนสีพื้นหลังหน้าหลักและฟอนต์เป็นโทนมืด */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0F172A !important;
            color: #F8FAFC !important;
            font-family: 'Sarabun', sans-serif;
        }
        
        /* ปรับขนาดตัวอักษรหัวข้อเรื่อง */
        h1 {
            font-size: 1.6rem !important;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        /* ปรับแต่งแต่งหน้าตาตัวกรอง (ฟอนต์สีขาวเด่นชัด) */
        label {
            color: #F8FAFC !important;
            font-size: 1rem !important;
            font-weight: 600;
        }
        
        hr {
            border-color: #334155 !important;
            margin-top: 10px;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# 🔗 3. ใส่ลิงก์ที่ได้จากปุ่ม "เผยแพร่ไปยังเว็บ" (Publish to web) ของคุณที่นี่
url = "https://google.com"  # <--- เปลี่ยนเป็นลิงก์ Google Sheet ของคุณ

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
        
        # หัวข้อหลักแบบกระชับ
        st.title("📊 แดชบอร์ดรายแผนกและรายเดือน")
        st.markdown("---")
        
        # 🛠 4. ย้ายตัวกรอง (Filters) มาอยู่บนหน้าหลัก ไม่ต้องซ่อนใน Sidebar อีกต่อไป
        # แบ่งตัวกรองเป็น 2 คอลัมน์ซ้าย-ขวา เพื่อประหยัดพื้นที่แนวตั้งบนมือถือ
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            all_months = df[col_month].dropna().astype(str).unique().tolist()
            selected_months = st.multiselect(
                "📅 1. เลือกเดือน:", 
                options=all_months, 
                default=all_months
            )
            
        with filter_col2:
            selected_depts = st.multiselect(
                "🏢 2. เลือกแผนก:", 
                options=departments, 
                default=departments
            )
            
        # ประมวลผลคัดกรองข้อมูล
        filtered_df = df_melted[
            (df_melted[col_month].astype(str).isin(selected_months)) & 
            (df_melted['Department'].isin(selected_depts))
        ]
        
        st.markdown("---")
        
        # 📈 5. พล็อตกราฟแท่ง (ปรับจูนพิเศษเพื่อหน้าจอมือถือ)
        modern_colors = ['#6366F1', '#10B981', '#F59E0B', '#F43F5E', '#06B6D4', '#A855F7', '#EC4899']
        
        fig = px.bar(
            filtered_df,
            x='Department',
            y='Value',
            color=col_month,
            barmode="relative",  # แบบ Stacked สะสม เหมาะกับจอมือถือที่แคบ
            color_discrete_sequence=modern_colors,
            labels={col_month: 'เดือน', 'Department': 'แผนก', 'Value': 'จำนวน'},
            text_auto='.0f',
            template="plotly_dark"
        )
        
        # ปรับ Layout ให้สมบูรณ์แบบบนสมาร์ทโฟน
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45,  # เอียงชื่อแผนกไม่ให้ทับกันบนจอเล็ก
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(family='Sarabun', size=11, color='#F8FAFC'),
            
            # ย้ายคำอธิบายเดือนไปไว้ด้านล่างสุดของกราฟเพื่อเพิ่มพื้นที่แสดงผลกว้างๆ
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.6,
                xanchor="center",
                x=0.5,
                font=dict(size=10, color='#F8FAFC'),
                title=None
            )
        )
        
        fig.update_xaxes(tickfont=dict(color='#94A3B8'))
        fig.update_yaxes(showgrid=True, gridcolor='#334151', tickfont=dict(color='#94A3B8'))
        
        # แสดงผลกราฟหน้าหลัก (ซ่อนแถบเครื่องมือเครื่องไม้ของ Plotly เพื่อความสะอาดตาบนมือถือ)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # 📋 6. ส่วนตรวจสอบตารางข้อมูลดิบด้านล่างสุด
        st.markdown("---")
        with st.expander("📋 แตะเพื่อดูตารางข้อมูลดิบจาก Google Sheet"):
            st.dataframe(df, use_container_width=True)
            
    except Exception as ex:
        st.error(f"เกิดข้อผิดพลาดในการประมวลผลตารางข้อมูล: {ex}")
else:
    st.info("💡 คำแนะนำ: ไม่พบข้อมูลในแผ่นงาน หรือโปรดตรวจสอบว่าใส่ลิงก์ Google Sheet ถูกต้องแล้ว")
