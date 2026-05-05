import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="UAC Care Analytics", layout="wide", page_icon="🏥")

st.markdown("""
<style>
.main { background-color: #0e1117; }
.metric-card {
    background: linear-gradient(135deg, #1e3a5f, #0d47a1);
    padding: 20px; border-radius: 15px;
    text-align: center; color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.title-style {
    font-size: 36px; font-weight: bold;
    color: #4fc3f7; text-align: center;
    padding: 20px 0;
}
.subtitle {
    text-align: center; color: #90caf9;
    font-size: 16px; margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

df = pd.read_csv('data/clean_data.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna()

df['Transfer_Efficiency'] = df.iloc[:,3] / df.iloc[:,2]
df['Discharge_Effectiveness'] = df.iloc[:,5] / df.iloc[:,4]
df['Backlog'] = df.iloc[:,1] - df.iloc[:,5]
df['Pipeline_Throughput'] = (df.iloc[:,3] + df.iloc[:,5]) / df.iloc[:,1]

st.markdown('<div class="title-style">🏥 UAC Care Transition Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">U.S. Department of Health & Human Services | Real-Time Pipeline Dashboard</div>', unsafe_allow_html=True)

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Seal_of_the_United_States_Department_of_Health_%26_Human_Services.svg/200px-Seal_of_the_United_States_Department_of_Health_%26_Human_Services.svg.png", width=100)
st.sidebar.markdown("## 📅 Filter Data")
start = st.sidebar.date_input("Start Date", df['Date'].min())
end = st.sidebar.date_input("End Date", df['Date'].max())
filtered = df[(df['Date'] >= pd.Timestamp(start)) & (df['Date'] <= pd.Timestamp(end))]

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dashboard Info")
st.sidebar.info(f"Total Records: {len(filtered)}\nDate Range: {start} to {end}")

st.markdown("### 📊 Key Performance Indicators")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🔄 Transfer Efficiency", f"{filtered['Transfer_Efficiency'].mean():.2%}", delta="CBP→HHS Speed")
c2.metric("✅ Discharge Effectiveness", f"{filtered['Discharge_Effectiveness'].mean():.2%}", delta="Placement Success")
c3.metric("⚠️ Avg Daily Backlog", f"{abs(filtered['Backlog'].mean()):.0f}", delta="Cases Pending")
c4.metric("🚀 Pipeline Throughput", f"{filtered['Pipeline_Throughput'].mean():.2%}", delta="Overall Flow")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Care Load Over Time")
    fig1 = px.area(filtered, x='Date',
                   y=[filtered.columns[2], filtered.columns[4]],
                   title="CBP vs HHS Care Load",
                   color_discrete_sequence=['#4fc3f7','#f48fb1'],
                   template='plotly_dark')
    fig1.update_layout(legend_title="Care Type", hovermode='x unified')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### 🚨 Backlog Accumulation")
    colors = ['#ef5350' if x > 0 else '#66bb6a' for x in filtered['Backlog']]
    fig2 = go.Figure(go.Bar(x=filtered['Date'], y=filtered['Backlog'],
                            marker_color=colors, name='Backlog'))
    fig2.update_layout(title="Daily Backlog Rate",
                       template='plotly_dark', hovermode='x unified')
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("### ⚡ Transfer Efficiency Trend")
    fig3 = px.line(filtered, x='Date', y='Transfer_Efficiency',
                   title="Transfer Efficiency Over Time",
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
                   title="Discharge Effectiveness Over Time",
                   color_discrete_sequence=['#ffcc80'],
                   template='plotly_dark')
    fig4.add_hline(y=filtered['Discharge_Effectiveness'].mean(),
                   line_dash="dash", line_color="red",
                   annotation_text="Average")
    fig4.update_layout(hovermode='x unified')
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.markdown("### 📋 Raw Data Preview")
st.dataframe(filtered.tail(20).style.background_gradient(cmap='Blues'),
             use_container_width=True)

st.markdown("---")
st.markdown('<div style="text-align:center; color:gray;">UAC Analytics Dashboard | Unified Mentor Project | 2025</div>', unsafe_allow_html=True)
