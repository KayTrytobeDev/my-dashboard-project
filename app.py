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
        
        /* ปรับแต่งดีไซน์ของการ์ดสรุปตัวเลข (KPI Cards ใน Dark Mode) */
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

# 📊 3. ชุดข้อมูลจริง 12 เดือน 5 แผนก จาก Google Sheet ของคุณ
raw_data = {
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    'Engineering': [45, 48, 51, 53, 56, 59, 62, 65, 68, 71, 74, 77],
    'Sales': [38, 42, 45, 47, 50, 53, 56, 59, 62, 65, 68, 71],
    'Marketing': [52, 55, 58, 60, 63, 66, 69, 72, 75, 78, 81, 84],
    'HR': [28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50],
    'Operations': [41, 44, 47, 49, 52, 55, 58, 61, 64, 67, 70, 73]
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
st.markdown("<h2 style='font-weight: 600; margin-bottom: 0px;'>📊 แดชบอร์ดวิเคราะห์ข้อมูลรายแผนก และ รายเดือน</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #94A3B8; font-size: 14px;'>ข้อมูลเชื่อมโยงอย่างถูกต้องและเสถียร จัด Layout สวยงามโทนมืด (Dark Mode)</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 10px; margin-bottom: 25px;'>", unsafe_allow_html=True)

# 📈 ส่วนที่ 1: การ์ดสรุปผลงานระดับบริหาร (KPI Cards ในสไตล์ Dark Mode)
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

# 📊 ส่วนที่ 2: การพล็อตกราฟเปรียบเทียบในโทนมืด (Dark Mode Chart)
st.markdown(f"<h4 style='font-weight: 600; margin-top: 15px;'>📈 กราฟแสดงผลในโหมด: {filter_mode}</h4>", unsafe_allow_html=True)

# ชุดสีนีออนพรีเมียม สว่างโดดเด่นตัดกับพื้นหลังสีเข้ม (น้ำเงินนีออน, เขียวมินต์, ส้มสว่าง, ชมพูสด, ฟ้าไซแอน)
dark_theme_colors = ['#6366F1', '#10B981', '#F59E0B', '#F43F5E', '#06B6D4', '#A855F7', '#EC4899']

fig = px.bar(
    filtered_df,
    x='แผนก (Department)',
    y='ผลงาน/ยอดขาย (Value)',
    color='Month',
    barmode="group",
    color_discrete_sequence=dark_theme_colors,
    labels={'Month': 'เดือน', 'แผนก (Department)': 'แผนก', 'ผลงาน/ยอดขาย (Value)': 'จำนวน'},
    text_auto='.0f'
)

# ปรับแต่งรายละเอียดกราฟให้กลมกลืนกับ Dark Mode
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis_tickangle=0,
    margin=dict(l=20, r=20, t=20, b=20),
    font=dict(family='Sarabun', size=13, color='#F8FAFC'),
    legend=dict(font=dict(color='#F8FAFC'), title=dict(font=dict(color='#F8FAFC')))
)
# ปรับสีเส้น Grid และสีตัวอักษรแกน X, Y เป็นสีสว่างจางๆ
fig.update_xaxes(tickfont=dict(color='#94A3B8'), title_font=dict(color='#F8FAFC'))
fig.update_yaxes(showgrid=True, gridcolor='#334151', tickfont=dict(color='#94A3B8'), title_font=dict(color='#F8FAFC'))

st.plotly_chart(fig, use_container_width=True)

# 📋 ส่วนที่ 3: ตารางข้อมูลดิบ
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📋 คลิกเพื่อตรวจสอบตารางข้อมูลดิบที่จัดระเบียบแล้ว (Data Table)"):
    st.dataframe(df, use_container_width=True)
