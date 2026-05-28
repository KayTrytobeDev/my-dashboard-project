import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บให้เป็นแบบ Wide และใส่ชื่อไตเติล
st.set_page_config(page_title="Executive Dashboard", layout="wide", page_icon="📊")

# 🎨 2. ใส่ Custom CSS ปรับแต่งหน้าตาให้สวยงามตามแบบ Figma (Fonts, Cards, และ Colors)
st.markdown("""
    <style>
        /* ปรับฟอนต์และพื้นหลังให้ดูสบายตาแบบมินิมอล */
        @import url('https://googleapis.com');
        html, body, [data-testid="stSidebar"] {
            font-family: 'Sarabun', sans-serif;
        }
        
        /* ปรับแต่งดีไซน์ของการ์ดสรุปตัวเลข (KPI Cards) */
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
        
        /* ปรับแต่งแถบเมนูด้านซ้าย (Sidebar) ให้ดูโมเดิร์น */
        [data-testid="stSidebar"] {
            background-color: #F9FAFB;
            border-right: 1px solid #E5E7EB;
        }
    </style>
""", unsafe_allow_html=True)

# 3. เชื่อมต่อฐานข้อมูล Google Sheet มาสเตอร์ไฟล์โดยใช้ลิงก์ Export CSV มาตรฐาน
url = "https://google.com"

@st.cache_data(ttl=1) # บังคับล้างข้อมูลเก่าทันทีทุก 1 วินาที
def load_data():
    try:
        # ดึงข้อมูลจากไฟล์มาสเตอร์โดยตรง
        data = pd.read_csv(url)
        data.dropna(how='all', inplace=True) # ลบแถวว่างทิ้งถ้ามี
        # ลบช่องว่างส่วนเกินที่ชื่อคอลลัมน์ออกอย่างเดียว
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheet ได้: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    # บังคับคอลัมน์แรกสุดใน Google Sheet เป็นแกนเวลาออโต้
    col_month = df.columns[0]
    
    # ดึงคอลัมน์แผนกที่เหลือทั้งหมดโดยอิงจากตำแหน่งที่ 2 เป็นต้นไป
    departments = [col for col in df.columns if col != col_month and not col.startswith('Unnamed')]
    
    try:
        # 🛠️ ขั้นตอนคัดกรองขยะพิเศษ: ล้างแถวในคอลัมน์เดือนที่ติดรหัสสคริปต์โปรแกรมทิ้งไปอัตโนมัติ
        # ระบบจะลบแถวที่เริ่มด้วยคำว่า var, function, try, html หรือสัญลักษณ์ขยะโปรแกรมทิ้งทั้งหมด
        df[col_month] = df[col_month].astype(str).str.strip()
        noise_keywords = ['var ', 'function', 'try {', 'document.', 'spdx-', 'copyright', 'closure', 'html']
        
        # ครองเอาไว้เฉพาะแถวที่ไม่ได้มีคำศัพท์ขยะเหล่านี้ปนอยู่
        for keyword in noise_keywords:
            df = df[~df[col_month].str.contains(keyword, case=False, na=False)]
            
        # ลบแถวเพิ่มเติมหากมีความยาวตัวอักษรมากเกินไปจนผิดสังเกต (ชื่อเดือนปกติไม่ควรเกิน 20 ตัวอักษร)
        df = df[df[col_month].str.len() < 25]

        # แปลงโครงสร้างข้อมูลตารางจากหน้ากว้างให้กลายเป็นแกนพล็อตกราฟแนวตั้ง (Wide to Long)
        df_melted = pd.melt(df, id_vars=[col_month], value_vars=departments, 
                            var_name='แผนก (Department)', value_name='ผลงาน/ยอดขาย (Value)')
        
        # คัดกรองแปลงตัวเลขเพื่อป้องกันค่า Error
        df_melted['ผลงาน/ยอดขาย (Value)'] = pd.to_numeric(df_melted['ผลงาน/ยอดขาย (Value)'], errors='coerce').fillna(0)
        
        # จัดรูปแบบตัวอักษรให้อ่านง่ายและสวยงาม
        df_melted[col_month] = df_melted[col_month].astype(str).str.capitalize()
        df_melted['แผนก (Department)'] = df_melted['แผนก (Department)'].astype(str).str.capitalize()
        
        # 🛠️ 4. จัดวางโครงสร้างเมนูด้านข้าง (Sidebar Filters)
        st.sidebar.markdown("### 🛠️ ตัวกรองข้อมูล (Filters)")
        available_months = sorted(df_melted[col_month].dropna().unique().tolist())
        
        filter_mode = st.sidebar.radio("รูปแบบการดูข้อมูล:", ["เปรียบเทียบทุกเดือน", "กรองดูเฉพาะเดือน"])
        
        if filter_mode == "กรองดูเฉพาะเดือน":
            default_selection = available_months[:3] if len(available_months) >= 3 else available_months
            selected_months = st.sidebar.multiselect("เลือกเดือนที่ต้องการดู:", options=available_months, default=default_selection)
            filtered_df = df_melted[df_melted[col_month].isin(selected_months)]
        else:
            filtered_df = df_melted.copy()
            
        # 🌟 5. หน้าจอหลัก (Main Content Dashboard)
        st.markdown("<h2 style='font-weight: 600; color: #111827; margin-bottom: 0px;'>📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #6B7280; font-size: 14px;'>ข้อมูลเชื่อมโยน์แบบเรียลไทม์จากระบบ Google Sheet Master File</p>", unsafe_allow_html=True)
        st.markdown("<hr style='margin-top: 10px; margin-bottom: 25px;'>", unsafe_allow_html=True)

        # 📈 ส่วนที่ 1: การ์ดสรุปผลงานระดับบริหาร (KPI Cards)
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            total_sum = filtered_df['ผลงาน/ยอดขาย (Value)'].sum()
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
        
        # ชุดสีโมเดิร์นแบบงานดีไซน์ Figma
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
            legend_title_text='เดือน',
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
        st.error(f"เกิดข้อผิดพลาดในการประมวลผลโครงสร้างตารางข้อมูล: {ex}")
else:
    st.info("💡 คำแนะนำ: ไม่พบข้อมูลในแผ่นงาน หรือโปรดตรวจสอบสิทธิ์การแชร์ของ Google Sheet อีกครั้ง")
