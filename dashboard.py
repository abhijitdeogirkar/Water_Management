import streamlit as st
import pandas as pd

st.set_page_config(page_title="Deogirkar Water Monitor", page_icon="💧", layout="wide")
st.title("💧 The Deogirkars' Smart Water Dashboard")
st.markdown("---")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1oys9fFlUwlwiw1dzYwWMbu0AiZuCszwPLzZWpb34_rA/edit?usp=sharing"
csv_url = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')

try:
    df = pd.read_csv(csv_url)
    latest_data = df.iloc[-1]
    
    st.subheader("📊 सध्याची पाण्याची स्थिती (Live Status)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="छतावरील टाकी १ (पातळी)", value=f"{latest_data['Tank_1_Level_cm']} cm")
    with col2:
        st.metric(label="छतावरील टाकी २ (पातळी)", value=f"{latest_data['Tank_2_Level_cm']} cm")
    with col3:
        st.metric(label="सध्याचा पाण्याचा स्रोत", value=f"{latest_data['Water_Source']}")

    st.markdown("---")
    st.subheader("📝 शेवटच्या काही नोंदी (Recent Logs)")
    st.dataframe(df.tail(5))

except Exception as e:
    st.error(f"डेटा वाचण्यात अडचण आली. कृपया गुगल शीटची लिंक तपासा. Error: {e}")
