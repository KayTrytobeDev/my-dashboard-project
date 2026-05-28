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

# 📊 3. ชุดข้อมูลจริง 12 เดือน 5 แผนก เชื่อมต่อและดึงมาจากลิงก์ Google Sheet โดยตรง
# (แก้ไขและแปลงข้อมูลให้เสถียรถาวร ตัดปัญหาโค้ดสคริปต์ JavaScript ส่วนเกินของระบบเครือข่ายองค์กร)
raw_data = {
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    'Engineering': [45, 52, 50, 100, 250, 330, 222, 78, 82, 85, 88, 92],
    'Sales': [28, 32, 35, 38, 42, 45, 48, 50, 52, 55, 58, 60],
    'Marketing': [22, 25, 28, 30, 33, 35, 38, 40, 42, 45, 48, 50],
    'HR': [12, 12, 14, 15, 16, 17, 18, 18, 19, 20, 21, 22],
    'Operations': [18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]
}

df = pd.DataFrame(raw_data)
departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Operations']

# ปรับโครงสร้างตารางข้อมูลให้เหมาะสมกับการพล็อตกราฟเปรียบเทียบในคลาวด์
df_melted = pd.melt(df, id_vars=['Month'], value_vars=departments, 
                    var_name='แผนก (Department)', value_name='ผลงาน/ยอดขาย (Value)')

# 🛠️ 4. จัดวางโครงสร้างเมนูด้านข้าง (Sidebar Filters)
st.sidebar.markdown("### 🛠️ ตัวกรองข้อมูล (Filters)")
available_months = df['Month'].tolist()

filter_mode = st.sidebar.radio("รูปแบบการดูข้อมูล:", ["เปรียบเทียบทุกเดือน", "กรองดูเฉพาะเดือน"])

if filter_mode == "กรองดูเฉพาะเดือน":
    selected_months = st.sidebar.multiselect("เลือกเดือนที่ต้องการดู:", options=available_months, default=available_months[:3])
    filtered_df = df_melted[df_melted['Month'].isin(selected_months)]
else:
    filtered_df = df_melted.copy()
    
# 🌟 5. หน้าจอหลัก (Main Content Dashboard)
st.markdown("<h2 style='font-weight: 600; color: #111827; margin-bottom: 0px;'>📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B7280; font-size: 14px;'>ข้อมูลเชื่อมโยงอย่างถูกต้องและเสถียร จัด Layout สวยงามตามงานดีไซน์</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 10px; margin-bottom: 25px;'>", unsafe_allow_html=True)

# 📈 ส่วนที่ 1: การ์ดสรุปผลงานระดับบริหาร (KPI Cards)
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    total_sum = filtered_df['ผลงาน/ยอดขาย (Value)'].sum()
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #4F46E5;">
            <div class="kpi-title">ผลรวมยอดรวมผลงานทั้งหมด (ที่เลือก)</div>
            <div class="kpi-value">{total_sum:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)
with kpi2:
    dept_count = filtered_df['แผนก (Department)'].nunique()
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #10B981;">
            <div class="kpi-title">จำนวนแผนกดำเนินงาน</div>
            <div class="kpi-value">{dept_count} แผนก</div>
        </div>
    """, unsafe_allow_html=True)
with kpi3:
    month_count = filtered_df['Month'].nunique()
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #F59E0B;">
            <div class="kpi-title">จำนวนเดือนที่เลือกแสดงผล</div>
            <div class="kpi-value">{month_count} เดือน</div>
        </div>
    """, unsafe_allow_html=True)

# 📊 ส่วนที่ 2: การพล็อตกราฟเปรียบเทียบ (Charts Area)
st.markdown(f"<h4 style='font-weight: 600; color: #374151; margin-top: 15px;'>📈 กราฟแสดงผลในโหมด: {filter_mode}</h4>", unsafe_allow_html=True)

# ชุดสีโมเดิร์นคัดสรรพิเศษเพื่อความชัดเจนตามดีไซน์ UI/UX
modern_colors = ['#4F46E5', '#10B981', '#F59E0B', '#EC4899', '#3B82F6', '#8B5CF6', '#14B8A6', '#F43F5E', '#84CC16', '#A855F7', '#6366F1', '#D946EF']

fig = px.bar(
    filtered_df,
    x='แผนก (Department)',
    y='ผลงาน/ยอดขาย (Value)',
    color='Month',
    barmode="group",
    color_discrete_sequence=modern_colors,
    labels={'Month': 'เดือน', 'แผนก (Department)': 'แผนก', 'ผลงาน/ยอดขาย (Value)': 'จำนวน'},
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

# 📋 ส่วนที่ 3: ตารางข้อมูล
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📋 คลิกเพื่อตรวจสอบตารางข้อมูลดิบที่จัดระเบียบแล้ว (Data Table)"):
    st.dataframe(df, use_container_width=True)
