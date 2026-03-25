# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import random # सिम्युलेशनसाठी

st.set_page_config(page_title="Deogirkar Smart Home", layout="wide")
st.title("अभिराजमेयार्णव पाणी व्यवस्थापन प्रणाली")
st.markdown("---")

# १. प्रगत वास्तववादी ॲनिमेशन CSS (लाटा, वीज आणि बुडबुडे)
# टिप: कंसांचा {{ }} गोंधळ टाळण्यासाठी आम्ही हा कोड एकाच सलग रेषेत लिहिला आहे.
css = """
<style>
@keyframes waterPour { 0% { background-position: 0 0px; } 100% { background-position: 0 16px; } }
@keyframes choppy { 0% { border-radius: 10% 5% 5% 10% / 10% 5% 5% 10%; } 25% { border-radius: 12% 8% 8% 12% / 12% 8% 8% 12%; } 50% { border-radius: 8% 12% 12% 8% / 8% 12% 12% 8%; } 75% { border-radius: 11% 9% 9% 11% / 11% 9% 9% 11%; } 100% { border-radius: 10% 5% 5% 10% / 10% 5% 5% 10%; } }
@keyframes rise { 0% { transform: translateY(0) scale(0.6); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateY(-25px) scale(1.4); opacity: 0; } }
@keyframes dottedLineFlow { 0% { background-position: 0 0px; } 100% { background-position: 0 10px; } }
@keyframes sunGlow { 0% { box-shadow: 0 0 5px #fbc02d; } 50% { box-shadow: 0 0 15px #fbc02d; } 100% { box-shadow: 0 0 5px #fbc02d; } }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# २. टाक्यांचे डिझाईन करण्याचे प्रगत फंक्शन (लाटा ॲनिमेशनसह)
def draw_tank(tank_name, level_cm, tank_type="overhead", inlets=[]):
    percentage = min(int((level_cm / 100) * 100), 100)
    water_color = "#00b4d8" if tank_type == "overhead" else "#0077b6"
    
    is_pouring = any(inlet['active'] for inlet in inlets)
    
    # पाण्याचे पृष्ठभागावरील वास्तववादी परिणाम
    surface_fx = ""
    water_top_style = "border-radius: 0;"
    
    if is_pouring:
        # १. पाण्याचा वरचा भाग सरळ न ठेवता चळचळणारा (Choppy) करणे
        water_top_style = "animation: choppy 0.8s infinite alternate;"
        
        # २. पृष्ठभागावर बुडबुडे
        surface_fx = f"""
        <div style='position: absolute; top: -10px; left: 50%; transform: translateX(-50%); width: 25px; height: 12px; background: rgba(255,255,255,0.8); border-radius: 50%; animation: rise 0.4s infinite alternate; z-index: 5;'></div>
        <div style='position: absolute; top: -2px; left: 35%; width: 12px; height: 12px; background: rgba(255,255,255,0.6); border-radius: 50%; animation: rise 0.5s infinite alternate-reverse; z-index: 5;'></div>
        <div style='position: absolute; top: 2px; left: 65%; width: 10px; height: 10px; background: rgba(255,255,255,0.6); border-radius: 50%; animation: rise 0.3s infinite alternate; z-index: 5;'></div>
        """

    width = "100%" if tank_type == "underground" else "160px"
    height = "160px" if tank_type == "underground" else "220px"

    html = f"""
    <div style="margin-top: 50px; display: flex; flex-direction: column; align-items: center;">
        <div style="width: {width}; max-width: 400px; height: {height}; border: 3px solid #333; position: relative; background-color: #eef2f3; border-top: none; border-radius: 0 0 12px 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);">
            <div style="position: absolute; bottom: 0; width: 100%; height: {percentage}%; background-color: {water_color}; transition: height 1s ease-in-out; display: flex; align-items: center; justify-content: center; border-radius: 0 0 9px 9px; z-index: 2; border-top: 2px solid rgba(255,255,255,0.4); {water_top_style}">
                {surface_fx}
                <span style="color: white; font-weight: bold; font-size: 20px; text-shadow: 1px 1px 3px black; z-index: 10;">{percentage}%</span>
            </div>
        </div>
        <div style="margin-top: 15px; font-weight: bold; font-size: 16px; background: #333; color: white; padding: 4px 15px; border-radius: 6px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">{tank_name}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ३. कंट्रोल पॅनेल आणि सोलर कार्डचे डिझाईन करण्याचे प्रगत फंक्शन (ग्लो आणि ठिपकेदार ओळीसह)
def draw_control_panel(is_solar_active=True, live_power="0.0 kW", total_daily="0.0 kWh"):
    # सोलर एनर्जी कार्डचा ग्लो इफेक्ट
    solar_glow = "animation: sunGlow 3s infinite;" if is_solar_active else ""
    # ठिपकेदार ओळींचे ॲनिमेशन
    dotted_line_pour = f"<div style='width: 8px; height: 60px; background-image: repeating-linear-gradient(transparent, #00b4d8 2px, transparent 6px); background-size: 100% 10px; animation: dottedLineFlow 0.3s infinite linear;'></div>" if is_solar_active else ""
    
    html_code = f"""
    <div style="display: flex; flex-direction: column; width: 320px; border: 2px solid #555; border-radius: 12px; background-color: #fffaf0; box-shadow: 5px 5px 15px rgba(0,0,0,0.2); overflow: hidden; position: relative;">
        <div style='background-color: #fffde7; padding: 10px; border-radius: 6px; text-align: center; border: 1px solid #fbc02d; margin: 10px; {solar_glow}'>
            <h5 style='margin: 0; color: #f57f17; font-weight: bold;'>☀️ सोलर ऊर्जा (Sofar Inverter)</h5>
            <div style="margin-top: 10px;">
                <st.metric label="सध्याची निर्मिती (Live)" value="{live_power}" delta="Active" />
                <st.metric label="आजची एकूण वीज" value="{total_daily}" />
            </div>
            <div style="margin-top: 10px;">
                <p style="font-size: 14px; font-weight: bold; color: #333; margin-bottom: 5px;">वीज निर्मिती स्थिती:</p>
                {dotted_line_pour}
            </div>
        </div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# ४. गुगल शीटमधून डेटा वाचणे (सिम्युलेशनसाठी आपण रँडम आकडे घेऊया)
SHEET_URL = "तुमची_GOOGLE_SHEET_ची_SHARE_LINK_ येते_टाका"
csv_url = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')

try:
    df = pd.read_csv(csv_url, encoding='utf-8')
    latest_data = df.iloc[-1]
    
    # थेट रकाण्यांच्या नंबरवरून डेटा घेणे
    tank1_lvl = int(latest_data.iloc[3]) if pd.notna(latest_data.iloc[3]) else random.randint(30, 70)
    tank2_lvl = int(latest_data.iloc[5]) if pd.notna(latest_data.iloc[5]) else random.randint(40, 80)
    underground_lvl = random.randint(60, 95) 
    water_source = str(latest_data.iloc[9]) if pd.notna(latest_data.iloc[9]) else "Borewell 1"

    # ५. आपण आत्ता टेस्ट करण्यासाठी सोलर चालू आहे असे ठरवूया (is_solar_active=True)
    draw_control_panel(is_solar_active=True, live_power="3.2 kW", total_daily="14.5 kWh")

    # ६. डॅशबोर्डची मुख्य रचना (Layout)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🚰 लाईव्ह कंट्रोल पॅनेल")
        st.info(f"🌊 **पाण्याचा स्रोत:** {water_source} &nbsp; | &nbsp; 🚰 **सुरू असलेला कॉक:** टाकी २ (उदा.)")
        st.markdown("---")
        
        col1_tanks, col2_tanks = st.columns(2)
        
        with col1_tanks:
            draw_tank("ছতাवरील टाकी ১", tank1_lvl, max_height_cm=100, tank_type="overhead", inlets=[{"name": "Main Line", "active": True}])
            draw_tank("অান্ডারগ্রাউন্ড टाकी", underground_lvl, max_height_cm=100, tank_type="underground", inlets=[{"name": "Main Line", "active": True}])
            
        with col2_tanks:
            draw_tank("ছতাवरील टाकी ২", tank2_lvl, max_height_cm=100, tank_type="overhead", inlets=[{"name": "Main Line", "active": False}])
            
    with col2:
        st.markdown("---")
        st.subheader("📝 शेवटच्या काही नोंदी (Logs)")
        st.dataframe(df.tail(3))

except Exception as e:
    st.error(f"डेटा वाचण्यात अडचण आली. Error: {e}")
