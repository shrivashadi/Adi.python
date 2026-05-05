import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="UAC Care Analytics", layout="wide", page_icon="🏥")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0e1117; }
[data-testid="stSidebar"] { background-color: #1a1a2e; }
.kpi-box {
    background: linear-gradient(135deg, #1e3a5f, #0d47a1);
    padding: 15px; border-radius: 10px;
    text-align: center; color: white;
    margin: 5px;
}
.kpi-value { font-size: 28px; font-weight: bold; color: #4fc3f7; }
.kpi-label { font-size: 13px; color: #90caf9; }
</style>
""", unsafe_allow_html=True)

df = pd.read_csv('data/clean_data.csv')
df.columns = ['Date','Apprehended','CBP_Custody','CBP_Transfers','HHS_Care','HHS_Discharged']
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date').dropna()

df['Transfer_Efficiency'] = df['CBP_Transfers'] / df['CBP_Custody']
df['Discharge_Effectiveness'] = df['HHS_Discharged'] / df['HHS_Care']
df['Backlog'] = df['Apprehended'] - df['HHS_Discharged']
df['Pipeline_Throughput'] = (df['CBP_Transfers'] + df['HHS_Discharged']) / df['Apprehended']

st.markdown("<h1 style='text-align:center; color:#4fc3f7;'>🏥 UAC Care Transition Analytics</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#90caf9;'>U.S. Department of Health & Human Services | Live Pipeline Dashboard</p>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.markdown("## 📅 Filter")
start = st.sidebar.date_input("Start Date", df['Date'].min())
end = st.sidebar.date_input("End Date", df['Date'].max())
filtered = df[(df['Date'] >= pd.Timestamp(start)) & (df['Date'] <= pd.Timestamp(end))]
st.sidebar.markdown("---")
st.sidebar.info(f"📊 Records: {len(filtered)}\n\n📅 {start} to {end}")

# KPI Cards
c1,c2,c3,c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class='kpi-box'>
    <div class='kpi-label'>🔄 Transfer Efficiency</div>
    <div class='kpi-value'>{filtered['Transfer_Efficiency'].mean():.1%}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class='kpi-box'>
    <div class='kpi-label'>✅ Discharge Effectiveness</div>
    <div class='kpi-value'>{filtered['Discharge_Effectiveness'].mean():.1%}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class='kpi-box'>
    <div class='kpi-label'>⚠️ Avg Backlog</div>
    <div class='kpi-value'>{abs(filtered['Backlog'].mean()):.0f}</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class='kpi-box'>
    <div class='kpi-label'>🚀 Pipeline Throughput</div>
    <div class='kpi-value'>{filtered['Pipeline_Throughput'].mean():.1%}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📈 Care Load Over Time")
    fig1 = px.area(filtered, x='Date',
                   y=['CBP_Custody','HHS_Care'],
                   color_discrete_sequence=['#4fc3f7','#f48fb1'],
                   template='plotly_dark',
                   labels={'value':'Children','variable':'Type'})
    fig1.update_layout(hovermode='x unified', legend_title="Care Type")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### 🚨 Daily Backlog")
    colors = ['#ef5350' if x > 0 else '#66bb6a' for x in filtered['Backlog']]
    fig2 = go.Figure(go.Bar(x=filtered['Date'], y=filtered['Backlog'],
                            marker_color=colors))
    fig2.update_layout(template='plotly_dark', hovermode='x unified',
                       xaxis_title='Date', yaxis_title='Backlog')
    st.plotly_chart(fig2, use_container_width=True)

# Charts Row 2
col3, col4 = st.columns(2)
with col3:
    st.markdown("### ⚡ Transfer Efficiency Trend")
    fig3 = px.line(filtered, x='Date', y='Transfer_Efficiency',
                   color_discrete_sequence=['#a5d6a7'],
                   template='plotly_dark')
    fig3.add_hline(y=filtered['Transfer_Efficiency'].mean(),
                   line_dash="dash", line_color="red",
                   annotation_text="Average")
    fig3.update_layout(hovermode='x unified')
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("### 🎯 Discharge Effectiveness")
    fig4 = px.line(filtered, x='Date', y='Discharge_Effectiveness',
                   color_discrete_sequence=['#ffcc80'],
                   template='plotly_dark')
    fig4.add_hline(y=filtered['Discharge_Effectiveness'].mean(),
                   line_dash="dash", line_color="red",
                   annotation_text="Average")
    fig4.update_layout(hovermode='x unified')
    st.plotly_chart(fig4, use_container_width=True)

# Charts Row 3
col5, col6 = st.columns(2)
with col5:
    st.markdown("### 📊 Monthly Intake vs Discharge")
    monthly = filtered.copy()
    monthly['Month'] = monthly['Date'].dt.to_period('M').astype(str)
    monthly = monthly.groupby('Month')[['Apprehended','HHS_Discharged']].sum().reset_index()
    fig5 = px.bar(monthly, x='Month',
                  y=['Apprehended','HHS_Discharged'],
                  template='plotly_dark',
                  color_discrete_sequence=['#ef5350','#66bb6a'],
                  barmode='group')
    fig5.update_layout(hovermode='x unified', xaxis_tickangle=45)
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.markdown("### 🔄 Pipeline Throughput")
    fig6 = px.line(filtered, x='Date', y='Pipeline_Throughput',
                   color_discrete_sequence=['#ce93d8'],
                   template='plotly_dark')
    fig6.add_hline(y=filtered['Pipeline_Throughput'].mean(),
                   line_dash="dash", line_color="yellow",
                   annotation_text="Average")
    fig6.update_layout(hovermode='x unified')
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.markdown("### 📋 Recent Data")
st.dataframe(filtered.tail(10), use_container_width=True)
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>UAC Analytics | Unified Mentor Project | 2025</p>", unsafe_allow_html=True)