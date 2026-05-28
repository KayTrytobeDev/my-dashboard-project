import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บให้เป็นแบบ Wide และใส่ชื่อไตเติล
st.set_page_config(page_title="Executive Dashboard", layout="wide", page_icon="📊")

# 3. เชื่อมต่อฐานข้อมูล Google Sheet มาสเตอร์ไฟล์โดยใช้ลิงก์ Export CSV มาตรฐาน
url = "https://google.com"

@st.cache_data(ttl=1) # บังคับล้างข้อมูลเก่าทันทีทุก 1 วินาที
def load_data():
    try:
        # 🛠️ แก้ไขจุดสำคัญ: เพิ่ม encoding='utf-8' เพื่อให้ระบบรองรับและเปิดอ่านภาษาไทยได้ 100% ไร้ข้อผิดพลาด
        data = pd.read_csv(url, encoding='utf-8')
        data.dropna(how='all', inplace=True) # ลบแถวว่างทิ้งถ้ามี
        data.columns = data.columns.str.strip() # ลบช่องว่างส่วนเกินที่ชื่อคอลลัมน์ออก
        return data
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheet ได้: {e}")
        return None

df = load_data()

if df is not None and not df.empty:
    # บังคับคอลัมน์แรกสุดใน Google Sheet เป็นแกนเวลาออโต้ (ไม่ว่าจะชื่อ Month หรือภาษาไทยก็ตาม)
    col_month = df.columns[0]
    
    # ดึงคอลัมน์แผนกที่เหลือทั้งหมดโดยอิงจากตำแหน่งที่ 2 เป็นต้นไป
    departments = [col for col in df.columns if col != col_month and not col.startswith('Unnamed')]
    
    try:
        # แปลงโครงสร้างข้อมูลตารางจากหน้ากว้างให้กลายเป็นแกนพล็อตกราฟแนวตั้ง (Wide to Long)
        df_melted = pd.melt(df, id_vars=[col_month], value_vars=departments, 
                            var_name='แผนก (Department)', value_name='ผลงาน/ยอดขาย (Value)')
        
        # คัดกรองแปลงตัวเลขเพื่อป้องกันค่า Error
        df_melted['ผลงาน/ยอดขาย (Value)'] = pd.to_numeric(df_melted['ผลงาน/ยอดขาย (Value)'], errors='coerce').fillna(0)
        
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
        st.title("📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน")
        st.markdown("ข้อมูลเชื่อมโยงแบบเรียลไทม์รองรับการเพิ่มแถวจากระบบ Google Sheet Master File")
        st.markdown("---")

        # 📈 ส่วนที่ 1: การ์ดสรุปผลงานระดับบริหาร (KPI Cards)
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            total_sum = filtered_df['ผลงาน/ยอดขาย (Value)'].sum()
            st.metric(label="ผลรวมยอดรวมผลงานทั้งหมด (ที่เลือก)", value=f"{total_sum:,.0f}")
        with kpi2:
            dept_count = filtered_df['แผนก (Department)'].nunique()
            st.metric(label="จำนวนแผนกดำเนินงาน", value=f"{dept_count} แผนก")
        with kpi3:
            month_count = filtered_df[col_month].nunique()
            st.metric(label="จำนวนเวลา/เดือนที่แสดงผล", value=f"{month_count} เดือน")

        st.markdown("---")

        # 📊 ส่วนที่ 2: การพล็อตกราฟเปรียบเทียบ (Charts Area)
        st.subheader(f"📈 กราฟแสดงผลในโหมด: {filter_mode}")
        
        # ชุดสีโมเดิร์นคัดสรรพิเศษเพื่อความชัดเจนตามดีไซน์ UI/UX
        modern_colors = ['#4F46E5', '#10B981', '#F59E0B', '#EC4899', '#3B82F6', '#8B5CF6', '#14B8A6']
        
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
            margin=dict(l=20, r=20, t=20, b=20)
        )
        fig.update_yaxes(showgrid=True, gridcolor='#E5E7EB')
        
        st.plotly_chart(fig, use_container_width=True)

        # 📋 ส่วนที่ 3: ตารางข้อมูล
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📋 คลิกเพื่อตรวจสอบตารางข้อมูลดิบจาก Google Sheet (Real-time Table)"):
            st.dataframe(df, use_container_width=True)
            
    except Exception as ex:
        st.error(f"เกิดข้อผิดพลาดในการประมวลผลโครงสร้างตารางข้อมูล: {ex}")
else:
    st.info("💡 คำแนะนำ: ไม่พบข้อมูลในแผ่นงาน หรือโปรดตรวจสอบสิทธิ์การแชร์ของ Google Sheet อีกครั้ง")
