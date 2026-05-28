import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บให้เป็นแบบ Wide และใส่ชื่อไตเติล
st.set_page_config(page_title="Executive Dashboard", layout="wide", page_icon="📊")

# 🎨 2. ใส่ Custom CSS ปรับแต่งหน้าตาเป็น "โทนมืด (Dark Mode)" สไตล์ Figma พรีเมียม
st.markdown("""
    <style>
        @import url('https://googleapis.com');
        
        /* ปรับสีพื้นหลังหน้าจอหลักและฟอนต์เป็นโทนมืด */
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
        
        /* ปรับแต่งดีไซน์ของการ์ดสรุปตัวเลข (KPI Cards) */
        .kpi-card {
            background-color: #1E293B;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
            border-left: 5px solid #6366F1;
            margin-bottom: 20px;
        }
        .kpi-title {
            color: #94A3B8;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .kpi-value {
            color: #F8FAFC;
            font-size: 28px;
            font-weight: bold;
        }
        
        /* ปรับแต่งสีข้อความหัวข้อเรื่อง */
        h2, h4, p, label {
            color: #F8FAFC !important;
        }
        hr {
            border-color: #334155 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. ลิงก์เชื่อมต่อฐานข้อมูล Google Sheet มาสเตอร์ไฟล์ (ดึงค่าเป็นไฟล์ CSV ดิบโดยตรง)
url = "https://google.com"

@st.cache_data(ttl=1) # 🔄 ตั้งค่าล้างความจำเก่าทุก 1 วินาที เพื่อให้ดึงค่าใหม่ล่าสุดจาก Google Sheet เสมอ
def load_data():
    try:
        # อ่านข้อมูลสดจาก Google Sheet
        data = pd.read_csv(url)
        
        # ลบแถวที่เป็นช่องว่างเปล่าออกทั้งหมด (ช่วยให้คุณกดเว้นบรรทัดพิมพ์ใน Sheet ได้โดยที่ระบบไม่พัง)
        data.dropna(how='all', inplace=True)
        
        # ปรับชื่อคอลัมน์ทั้งหมดให้เป็นระเบียบโดยลบช่องว่างส่วนเกินออก
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheet ได้: {e}")
        return None

df = load_data()

# ตรวจสอบว่ามีข้อมูลวิ่งเข้ามาในระบบจริงไหม
if df is not None and not df.empty:
    
    # บังคับคอลัมน์แรกสุดในตารางให้ทำหน้าที่เป็นแกนระบุเวลา/เดือนอัตโนมัติ (จะตั้งชื่ออะไรระบบก็รองรับ)
    col_month = df.columns[0]
    
    # ดึงคอลัมน์แผนกที่เหลือทั้งหมดแบบอัตโนมัติ (รองรับการเพิ่มหรือเปลี่ยนตัวเลขแผนกในอนาคต)
    departments = [col for col in df.columns if col != col_month and not col.startswith('Unnamed')]
    
    try:
        # แปลงโครงสร้างตารางข้อมูลเพื่อนำไปพล็อตกราฟเปรียบเทียบ (Wide to Long Format)
        df_melted = pd.melt(df, id_vars=[col_month], value_vars=departments, 
                            var_name='แผนก (Department)', value_name='ผลงาน/ยอดขาย (Value)')
        
        # บังคับค่าผลงาน/ยอดขายให้เป็นตัวเลขเสมอ แถวไหนกรอกตัวหนังสือปนมาระบบจะเปลี่ยนเป็นเลข 0 ให้ทันทีเพื่อป้องกันกราฟเออร์เรอร์
        df_melted['ผลงาน/ยอดขาย (Value)'] = pd.to_numeric(df_melted['ผลงาน/ยอดขาย (Value)'], errors='coerce').fillna(0)
        
        # 🛠️ 4. จัดวางระบบตัวกรองข้อมูลด้านข้าง (Sidebar Filters)
        st.sidebar.markdown("### 🛠️ ตัวกรองข้อมูล (Filters)")
        
        # รายชื่อเดือนทั้งหมดจะอัปเดตเพิ่มขึ้นเองอัตโนมัติเมื่อคุณไปพิมพ์แถวเพิ่มใน Google Sheet
        available_months = df[col_month].dropna().astype(str).unique().tolist()
        
        filter_mode = st.sidebar.radio("รูปแบบการดูข้อมูล:", ["เปรียบเทียบทุกเดือน", "กรองดูเฉพาะเดือน"])
        
        if filter_mode == "กรองดูเฉพาะเดือน":
            default_selection = available_months[:3] if len(available_months) >= 3 else available_months
            selected_months = st.sidebar.multiselect("เลือกเดือนที่ต้องการดู:", options=available_months, default=default_selection)
            filtered_df = df_melted[df_melted[col_month].isin(selected_months)]
        else:
            filtered_df = df_melted.copy()
            
        # 🌟 5. หน้าจอหลัก (Main Content Dashboard)
        st.markdown("<h2 style='font-weight: 600; margin-bottom: 0px;'>📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8; font-size: 14px;'>ดึงข้อมูลเรียลไทม์และรองรับการเพิ่มแถวอัตโนมัติจาก Google Sheet</p>", unsafe_allow_html=True)
        st.markdown("<hr style='margin-top: 10px; margin-bottom: 25px;'>", unsafe_allow_html=True)

        # 📈 ส่วนที่ 1: การ์ดสรุปผลงานระดับบริหาร (KPI Cards อัปเดตตัวเลขตามข้อมูลที่เพิ่มใหม่ทันที)
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            total_sum = filtered_df['ผลงาน/ยอดขาย (Value)'].sum()
            st.markdown(f"""
                <div class="kpi-card" style="border-left-color: #6366F1;">
                    <div class="kpi-title">ผลรวมยอดรวมผลงานทั้งหมด (ที่เลือก)</div>
                    <div class="kpi-value">{total_sum:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
        with kpi2:
            dept_count = filtered_df['แผนก (Department)'].nunique()
            st.markdown(f"""
                <div class="kpi-card" style="border-left-color: #10B981;">
                    <div class="kpi-title">จำนวนแผนกดำเนินงานทั้งหมด</div>
                    <div class="kpi-value">{dept_count} แผนก</div>
                </div>
            """, unsafe_allow_html=True)
        with kpi3:
            month_count = filtered_df[col_month].nunique()
            st.markdown(f"""
                <div class="kpi-card" style="border-left-color: #F59E0B;">
                    <div class="kpi-title">จำนวนเวลา/เดือนที่แสดงผล</div>
                    <div class="kpi-value">{month_count} เดือน</div>
                </div>
            """, unsafe_allow_html=True)

        # 📊 ส่วนที่ 2: การพล็อตกราฟเปรียบเทียบ (Charts Area)
        st.markdown(f"<h4 style='font-weight: 600; margin-top: 15px;'>📈 กราฟแสดงผลในโหมด: {filter_mode}</h4>", unsafe_allow_html=True)
        
        # เซ็ตสีพรีเมียมนีออนสว่างสะท้อนแสงสำหรับ Dark Mode
        modern_colors = ['#6366F1', '#10B981', '#F59E0B', '#F43F5E', '#06B6D4', '#A855F7', '#EC4899']
        
        fig = px.bar(
            filtered_df,
            x='แผนก (Department)',
            y='ผลงาน/ยอดขาย (Value)',
            color=col_month,
            barmode="group",
            color_discrete_sequence=modern_colors,
            labels={col_month: 'เดือน', 'แผนก (Department)': 'แผนก', 'ผลงาน/ยอดขาย (Value)': 'จำนวน'},
            text_auto='.0f' # แสดงตัวเลขสรุปบนแท่งกราฟแบบสวยงามอัตโนมัติ
        )
        
        # ปรับแต่งรายละเอียดโครงสร้างกราฟแท่ง
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=0,
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(family='Sarabun', size=13, color='#F8FAFC'),
            legend=dict(font=dict(color='#F8FAFC'), title=dict(font=dict(color='#F8FAFC')))
        )
        fig.update_xaxes(tickfont=dict(color='#94A3B8'), title_font=dict(color='#F8FAFC'))
        fig.update_yaxes(showgrid=True, gridcolor='#334151', tickfont=dict(color='#94A3B8'), title_font=dict(color='#F8FAFC'))
        
        st.plotly_chart(fig, use_container_width=True)

        # 📋 ส่วนที่ 3: ตารางข้อมูลดิบด้านล่างสุด (ขยายเพื่อตรวจสอบความถูกต้องได้)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📋 คลิกเพื่อตรวจสอบตารางข้อมูลดิบแบบเรียลไทม์จาก Google Sheet"):
            st.dataframe(df, use_container_width=True)
            
    except Exception as ex:
        st.error(f"เกิดข้อผิดพลาดในการประมวลผลตารางข้อมูล: {ex}")
else:
    st.info("💡 คำแนะนำ: ไม่พบข้อมูลในแผ่นงาน หรือโปรดตรวจสอบสิทธิ์การแชร์ของ Google Sheet อีกครั้ง")
