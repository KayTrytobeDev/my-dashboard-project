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
        st.title("📊 สรุปรายงานยอดของแผนก ")
        st.markdown("---")
        
        # 🛠️ 4. โหมดควบคุมแถวบนสุด: เลือกมุมมองกราฟที่เหมาะกับการตัดสินใจ
        chart_type = st.radio(
            "📈 เลือกรูปแบบการเปรียบเทียบข้อมูลที่ต้องการดู:",
            ["ดูอันดับความสูง-ต่ำ (แท่งแนวนอน)", "ดูแนวโน้มการเติบโตรายเดือน (กราฟเส้น)", "ดูสัดส่วนและยอดรวม (แท่งสะสม)"],
            horizontal=True
        )
        
        st.markdown("---")
        
        # ตัวเลือกช่วยชีวิตสำหรับ 40 แผนก
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
                selected_depts = departments
                st.info(f"✨ ระบบกำลังแสดงผลทั้งหมด {len(departments)} แผนก")
            else:
                # ถ้าเลือกกราฟเส้นหรือเลือกติ๊กเอง ตั้งต้นให้โชว์แค่ 5 แผนกแรกเพื่อไม่ให้กราฟรกไปครับ
                default_show = departments[:5] if len(departments) >= 5 else departments
                selected_depts = st.multiselect(
                    "🏢 ติ๊กเลือกแผนก (พิมพ์ค้นหาได้):", 
                    options=departments,
                    default=default_show
                )
                
        # ประมวลผลตัวกรอง
        filtered_df = df_melted[
            (df_melted[col_month].astype(str).isin(selected_months)) & 
            (df_melted['Department'].isin(selected_depts))
        ]
        
        st.markdown("---")
        
        # 📈 5. ส่วนสร้างการพล็อตกราฟแบบ Dynamic เปลี่ยนร่างตามปุ่มที่เลือกด้านบน
        modern_colors = ['#6366F1', '#10B981', '#F59E0B', '#F43F5E', '#06B6D4', '#A855F7', '#EC4899', '#38BDF8', '#F472B6']
        
       if chart_type == "ดูอันดับความสูง-ต่ำ (แท่งแนวนอน)":
    # คำนวณความสูงของกราฟให้ขยายตามจำนวนแผนกที่เลือก
    dynamic_height = max(450, len(selected_depts) * 45) # 💡 ปรับสูตรความสูงให้กระชับขึ้น
    
    fig = px.bar(
        filtered_df, 
        x='Value',       # 📊 แกน X เป็น "จำนวนตัวเลข" (ความยาวแท่ง)
        y='Department',  # 🏢 แกน Y ต้องเป็น "Department" เพื่อให้ยอมแยกชื่อแผนกแต่ละบรรทัด!
        color=col_month,
        barmode="group", 
        color_discrete_sequence=modern_colors,
        labels={col_month: 'เดือน', 'Department': 'แผนก', 'Value': 'จำนวน'},
        text_auto='.0f', 
        template="plotly_dark", 
        orientation='h'
    )
    fig.update_yaxes(categoryorder='total ascending') # เรียงลำดับเอาแผนกยอดสูงสุดไว้บนสุด
            
        elif chart_type == "ดูแนวโน้มการเติบโตรายเดือน (กราฟเส้น)":
            dynamic_height = 500
            fig = px.line(
                filtered_df, x=col_month, y='Value', color='Department',
                color_discrete_sequence=modern_colors,
                labels={col_month: 'เดือน', 'Department': 'แผนก', 'Value': 'จำนวน'},
                markers=True, template="plotly_dark"
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            
        else: # ดูสัดส่วนและยอดรวม (แท่งสะสม)
            dynamic_height = 500
            fig = px.bar(
                filtered_df, x=col_month, y='Value', color='Department',
                barmode="relative", color_discrete_sequence=modern_colors,
                labels={col_month: 'เดือน', 'Department': 'แผนก', 'Value': 'จำนวน'},
                text_auto='.0f', template="plotly_dark"
            )
        
        # ปรับการจัดตำแหน่งของ Layout ส่วนกลางให้เปิดได้ดีบนทุกอุปกรณ์
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=15, t=15, b=10),
            font=dict(family='Sarabun', size=12, color='#F8FAFC'),
            height=dynamic_height,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(size=11),
                title=None
            )
        )
        
        fig.update_xaxes(showgrid=True, gridcolor='#334151', tickfont=dict(color='#94A3B8'))
        fig.update_yaxes(showgrid=True, gridcolor='#334151', tickfont=dict(color='#94A3B8'))
        
        # แสดงผลกราฟ (ซ่อน Toolbar ของ Plotly ออกไปเพื่อให้จอมือถือสะอาด)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
    except Exception as ex:
        st.error(f"เกิดข้อผิดพลาดในการประมวลผลข้อมูล: {ex}")
else:
    st.info("💡 คำแนะนำ: ไม่พบข้อมูลในแผ่นงาน หรือโปรดตรวจสอบว่าใส่ลิงก์ Google Sheet ถูกต้องแล้ว")
