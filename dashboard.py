# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Deogirkar Water Monitor", page_icon="💧", layout="wide")
st.title("💧 The Deogirkars' Smart Water Dashboard")
st.markdown("---")

def draw_tank(tank_name, level_cm, max_height_cm=100, tank_type="overhead"):
    percentage = min(int((level_cm / max_height_cm) * 100), 100)
    water_color = "#00b4d8" if tank_type == "overhead" else "#0077b6"
    border_color = "#333" if tank_type == "overhead" else "#8B4513"
    
    html_code = f"""
    <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 20px;">
        <h4 style="color: #333; margin-bottom: 10px; font-family: sans-serif;">{tank_name}</h4>
        <div style="width: 140px; height: 200px; border: 4px solid {border_color}; border-radius: 12px; background-color: #e0e0e0; position: relative; overflow: hidden; box-shadow: 5px 5px 15px rgba(0,0,0,0.2);">
            <div style="position: absolute; bottom: 0; width: 100%; height: {percentage}%; background-color: {water_color}; transition: height 1.5s ease-in-out; display: flex; align-items: center; justify-content: center;">
                <span style="color: white; font-weight: bold; font-size: 22px; font-family: sans-serif; text-shadow: 1px 1px 2px black;">{percentage}%</span>
            </div>
        </div>
        <p style="margin-top: 8px; font-weight: bold; color: #555;">पाण्याची पातळी: {level_cm} cm</p>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1oys9fFlUwlwiw1dzYwWMbu0AiZuCszwPLzZWpb34_rA/edit?usp=sharing"
csv_url = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')

try:
    # येथे आपण encoding='utf-8' ही जादूची ओळ टाकली आहे!
    df = pd.read_csv(csv_url, encoding='utf-8')
    latest_data = df.iloc[-1]
    
    # थेट रकाण्यांच्या नंबरवरून डेटा घेणे
    tank1_lvl = int(latest_data.iloc[3]) if pd.notna(latest_data.iloc[3]) else 45
    tank2_lvl = int(latest_data.iloc[5]) if pd.notna(latest_data.iloc[5]) else 70
    underground_lvl = 85 
    
    water_source = str(latest_data.iloc[9]) if pd.notna(latest_data.iloc[9]) else "Borewell"

    st.subheader("🚰 लाईव्ह कंट्रोल पॅनेल")
    st.info(f"⚡ **पॉवर सप्लाय:** चालू (ON) &nbsp; | &nbsp; 🌊 **पाण्याचा स्रोत:** {water_source} &nbsp; | &nbsp; 🚰 **सुरू असलेला कॉक:** टाकी २ (उदा.)")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        draw_tank("छतावरील टाकी १", tank1_lvl, max_height_cm=100, tank_type="overhead")
    with col2:
        draw_tank("छतावरील टाकी २", tank2_lvl, max_height_cm=100, tank_type="overhead")
    with col3:
        draw_tank("अंडरग्राउंड टाकी", underground_lvl, max_height_cm=100, tank_type="underground")

    st.markdown("---")
    st.subheader("📝 शेवटच्या काही नोंदी (Logs)")
    st.dataframe(df.tail(3))

except Exception as e:
    st.error(f"डेटा वाचण्यात अडचण आली. Error: {e}")
