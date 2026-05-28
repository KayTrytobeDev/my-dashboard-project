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
        st.title("📊 แดชบอร์ดวิเคราะห์ข้อมูลสากล (รองรับทุกอุปกรณ์)")
        st.markdown("---")
        
        # 🛠️ 4. ตัวช่วยจัดการ 40 แผนก (แก้ปัญหาการคลิกเลือกยากบนมือถือ)
        st.markdown("### 🛠️ ตัวกรองข้อมูลความเร็วสูง")
        
        # ตัวเลือกช่วยชีวิต: เลือกทั้งหมด หรือ ล้างทั้งหมดเพื่อเลือกเอง
        select_mode = st.radio(
            "💡 โหมดการเลือกแผนก:",
            ["แสดงทุกแผนกพร้อมกัน (ทั้งหมด)", "เลือกติ๊กเฉพาะแผนกที่ต้องการดู"],
            horizontal=True
        )
        
        # แยกแถวตัวกรองให้กดง่ายขึ้นบน Tablet/Mobile
        col_f1, col_f2 = st.columns([1, 1])
        
        with col_f1:
            all_months = df[col_month].dropna().astype(str).unique().tolist()
            selected_months = st.multiselect(
                "📅 เลือกเดือนที่ต้องการดู:", 
                options=all_months, 
                default=all_months
            )
            
        with col_f2:
            if select_mode == "แสดงทุกแผนกพร้อมกัน (ทั้งหมด)":
                selected_depts = departments  # บังคับเลือก 40 แผนกอัตโนมัติ
                st.info(f"✨ ระบบกำลังแสดงผลทั้งหมด {len(departments)} แผนก (สามารถสลับโหมดด้านบนเพื่อเลือกเฉพาะบางแผนกได้)")
            else:
                selected_depts = st.multiselect(
                    "🏢 ติ๊กเลือกแผนก (พิมพ์ค้นหาได้):", 
                    options=departments,
                    default=departments[:3] # ค่าตั้งต้นโชว์แค่ 3 แผนกแรก ไม่ให้รกตา
                )
                
        # ประมวลผลตัวกรอง
        filtered_df = df_melted[
            (df_melted[col_month].astype(str).isin(selected_months)) & 
            (df_melted['Department'].isin(selected_depts))
        ]
        
        st.markdown("---")
        
        # 📈 5. พล็อตกราฟแท่งแนวนอน (Horizontal Bar Chart) เพื่อความสมบูรณ์แบบบนมือถือ
        modern_colors = ['#6366F1', '#10B981', '#F59E0B', '#F43F5E', '#06B6D4', '#A855F7', '#EC4899']
        
        # คำนวณความสูงของกราฟแปรผันตามจำนวนแผนกที่เลือก (ถ้าเลือกเยอะ กราฟจะยาวลงล่างตามตัว ทำให้ไม่เบียดกัน)
        dynamic_height = max(400, len(selected_depts) * len(selected_months) * 35)
        
        fig = px.bar(
            filtered_df,
            x='Value',            # 💡 สลับเอาตัวเลขมาไว้แกน X
            y='Department',       # 💡 สลับเอาชื่อแผนกไปไว้แกน Y (ทำให้ยาวลงข้างล่าง ไม่บีบด้านข้าง)
            color=col_month,
            barmode="group",      # แสดงแท่งเปรียบเทียบแต่ละเดือนคู่กันชัดๆ
            color_discrete_sequence=modern_colors,
            labels={col_month: 'เดือน', 'Department': 'แผนก', 'Value': 'จำนวน'},
            text_auto='.0f',
            template="plotly_dark",
            orientation='h'       # 💡 บังคับเปิดใช้งานกราฟแนวนอน
        )
        
        # ปรับการจัดตำแหน่งของ Layout ให้แสดงได้ดีบน PC, Tablet, Mobile
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=15, t=10, b=10),
            font=dict(family='Sarabun', size=12, color='#F8FAFC'),
            height=dynamic_height,  # ใช้ความสูงแบบ Dynamic
            
            # ย้ายคำอธิบายเดือนไปไว้ด้านล่างสุดของหน้าจอ เพื่อให้หน้าจอกว้างเต็มที่
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(size=11),
                title=None
            )
        )
        
        fig.update_xaxes(showgrid=True, gridcolor='#334151', tickfont=dict(color='#94A3B8'))
        fig.update_yaxes(tickfont=dict(color='#F8FAFC'), categoryorder='total ascending') # เรียงจากแผนกที่ยอดเยอะที่สุดขึ้นไป
        
        # แสดงผลกราฟ
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # 📋 6. ส่วนตรวจสอบตารางข้อมูลดิบ
        st.markdown("---")
        with st.expander("📋 แตะ/คลิก เพื่อเปิดดูตารางข้อมูลดิบทั้งหมดจาก Google Sheet"):
            st.dataframe(df, use_container_width=True)
            
    except Exception as ex:
        st.error(f"เกิดข้อผิดพลาดในการประมวลผลตารางข้อมูล: {ex}")
else:
    st.info("💡 คำแนะนำ: ไม่พบข้อมูลในแผ่นงาน หรือโปรดตรวจสอบว่าใส่ลิงก์ Google Sheet ถูกต้องแล้ว")
