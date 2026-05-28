import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บให้เป็นแบบ Wide และใส่ชื่อไตเติล
st.set_page_config(page_title="Executive Dashboard", layout="wide", page_icon="📊")

# 🎨 2. ใส่ Custom CSS ปรับแต่งหน้าตาให้สวยงามตามแบบ Figma (Fonts, Cards, และ Colors)
st.markdown("""
    <style>
        @import url('https://googleapis.com');
        html, body, [data-testid="stSidebar"] {
            font-family: 'Sarabun', sans-serif;
        }
        .kpi-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border-left: 5px solid #4F46E5;
            margin-bottom: 20px;
        }
        .kpi-title {
            color: #6B7280;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .kpi-value {
            color: #111827;
            font-size: 28px;
            font-weight: bold;
        }
        [data-testid="stSidebar"] {
            background-color: #F9FAFB;
            border-right: 1px solid #E5E7EB;
        }
    </style>
""", unsafe_allow_html=True)

# 3. เชื่อมต่อฐานข้อมูล Google Sheet มาสเตอร์ไฟล์
url = "https://google.com"

@st.cache_data(ttl=1) # บังคับให้อัปเดตข้อมูลสดใหม่เกือบเรียลไทม์
def load_data():
    try:
        # กำหนดดึงข้อมูล และถ้าเจอแถวว่างระบบจะพยายามจัดการให้อัตโนมัติ
        data = pd.read_csv(url)
        data.dropna(how='all', inplace=True) # ลบแถวที่ว่างเปล่าออกทั้งหมด
        data.columns = data.columns.str.strip().str.lower()
        return data
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheet ได้: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    # ค้นหาคอลัมน์ที่เกี่ยวกับเดือนโดยอัตโนมัติ (ไม่ว่าจะพิมพ์ month หรือ Month หรือ MONTH)
    month_cols = [col for col in df.columns if 'month' in col]
    
    if len(month_cols) > 0:
        col_month = month_cols[0]
        
        # 🛠️ ดึงชื่อคอลัมน์แผนกทั้งหมดจากในตารางจริงโดยอัตโนมัติ! ป้องกันปัญหา KeyError หันไปใช้ชื่อตรงตาม Sheet จริง
        departments = [col for col in df.columns if col != col_month and not col.startswith('unnamed')]
        
        try:
            # แปลงโครงสร้างข้อมูลตารางจากหน้ากว้างให้กลายเป็นแกนพล็อตกราฟแนวตั้ง (Wide to Long)
            df_melted = pd.melt(df, id_vars=[col_month], value_vars=departments, 
                                var_name='แผนก (Department)', value_name='ผลงาน/ยอดขาย (Value)')
            
            # 🛠️ 4. จัดวางโครงสร้างเมนูด้านข้าง (Sidebar Filters)
            st.sidebar.markdown("### 🛠️ ตัวกรองข้อมูล (Filters)")
            available_months = df[col_month].dropna().unique().tolist()
            
            filter_mode = st.sidebar.radio("รูปแบบการดูข้อมูล:", ["เปรียบเทียบทุกเดือน", "กรองดูเฉพาะเดือน"])
            
            if filter_mode == "กรองดูเฉพาะเดือน":
                default_selection = available_months[:3] if len(available_months) >= 3 else available_months
                selected_months = st.sidebar.multiselect("เลือกเดือนที่ต้องการดู:", options=available_months, default=default_selection)
                filtered_df = df_melted[df_melted[col_month].isin(selected_months)]
            else:
                filtered_df = df_melted.copy()
                
            # 🌟 5. หน้าจอหลัก (Main Content Dashboard)
            st.markdown("<h2 style='font-weight: 600; color: #111827; margin-bottom: 0px;'>📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #6B7280; font-size: 14px;'>ข้อมูลเชื่อมโยงแบบเรียลไทม์จากระบบ Google Sheet Master File</p>", unsafe_allow_html=True)
            st.markdown("<hr style='margin-top: 10px; margin-bottom: 25px;'>", unsafe_allow_html=True)

            # 📈 ส่วนที่ 1: การ์ดสรุปผลงานระดับบริหาร (KPI Cards)
            kpi1, kpi2, kpi3 = st.columns(3)
            with kpi1:
                total_sum = pd.to_numeric(filtered_df['ผลงาน/ยอดขาย (Value)'], errors='coerce').sum()
                st.markdown(f"""
                    <div class="kpi-card" style="border-left-color: #4F46E5;">
                        <div class="kpi-title">ผลรวมยอดขาย/ผลงานทั้งหมด</div>
                        <div class="kpi-value">{total_sum:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)
            with kpi2:
                dept_count = filtered_df['แผนก (Department)'].nunique()
                st.markdown(f"""
                    <div class="kpi-card" style="border-left-color: #10B981;">
                        <div class="kpi-title">จำนวนแผนกที่กำลังดำเนินงาน</div>
                        <div class="kpi-value">{dept_count} แผนก</div>
                    </div>
                """, unsafe_allow_html=True)
            with kpi3:
                month_count = filtered_df[col_month].nunique()
                st.markdown(f"""
                    <div class="kpi-card" style="border-left-color: #F59E0B;">
                        <div class="kpi-title">จำนวนเดือนที่เลือกแสดงผล</div>
                        <div class="kpi-value">{month_count} เดือน</div>
                    </div>
                """, unsafe_allow_html=True)

            # 📊 ส่วนที่ 2: การพล็อตกราฟเปรียบเทียบ (Charts Area)
            st.markdown(f"<h4 style='font-weight: 600; color: #374151; margin-top: 15px;'>📈 กราฟแสดงผลในโหมด: {filter_mode}</h4>", unsafe_allow_html=True)
            
            modern_colors = ['#4F46E5', '#10B981', '#F59E0B', '#EC4899', '#3B82F6', '#8B5CF6']
            
            fig = px.bar(
                filtered_df,
                x='แผนก (Department)',
                y='ผลงาน/ยอดขาย (Value)',
                color=col_month,
                barmode="group",
                color_discrete_sequence=modern_colors,
                labels={col_month: 'เดือน', 'แผนก (Department)': 'แผนก', 'ผลงาน/ยอดขาย (Value)': 'จำนวน'},
                text_auto='.0f'
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_tickangle=0,
                legend_title_text='ตัวแปรแยกสี (เดือน)',
                margin=dict(l=20, r=20, t=20, b=20),
                font=dict(family='Sarabun', size=13)
            )
            fig.update_yaxes(showgrid=True, gridcolor='#E5E7EB')
            
            st.plotly_chart(fig, use_container_width=True)

            # 📋 ส่วนที่ 3: ตารางข้อมูลดิบด้านล่างสุด
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("📋 คลิกเพื่อตรวจสอบตารางข้อมูลดิบจาก Google Sheet (Real-time Table)"):
                st.dataframe(df, use_container_width=True)
                
        except Exception as ex:
            st.error(f"เกิดข้อผิดพลาดในการประมวลผลโครงสร้างตาราง: {ex}")
    else:
        st.error("❌ หาคอลัมน์ระบุเวลาหรือเดือน 'month' ใน Google Sheet ไม่เจอ กรุณาเช็กชื่อคอลัมน์แรกใน Sheet ของคุณอีกครั้งครับ")
else:
    st.info("💡 คำแนะนำ: ไม่พบข้อมูลในแผ่นงาน หรือโปรดตรวจสอบสิทธิ์การแชร์ของ Google Sheet อีกครั้ง")
