# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# १. पेज पूर्ण स्क्रीनवर दिसावे यासाठी
st.set_page_config(page_title="Deogirkar Water Monitor", layout="wide")
st.title("अभिराजमेयार्णव पाणी व्यवस्थापन प्रणाली")
st.markdown("---")

# २. टाकी आणि नळ (Pipe) डिझाईन करण्याचे फंक्शन
def draw_tank_with_pipe(tank_name, level_cm, is_pouring=False, tank_type="overhead", source_names=["नळ"]):
    percentage = min(int((level_cm / 100) * 100), 100)
    water_color = "#00b4d8" if tank_type == "overhead" else "#0077b6"
    
    # पाणी पडण्याचे ॲनिमेशन (is_pouring = True असेल तरच दिसेल)
    pouring_html = ""
    if is_pouring:
        pouring_html = """
        <div style="position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 12px; height: 100%; background-image: repeating-linear-gradient(transparent, #00b4d8 4px, transparent 8px); background-size: 100% 16px; animation: pour 0.5s infinite linear; z-index: 1;"></div>
        <style>@keyframes pour { from { background-position: 0 0; } to { background-position: 0 100%; } }</style>
        """

    # नळाचे चित्र (Pipe UI)
    pipes_html = ""
    for idx, name in enumerate(source_names):
        offset = 50 if len(source_names) == 1 else (30 if idx == 0 else 70)
        pipes_html += f"""
        <div style="position: absolute; top: -40px; left: {offset}%; transform: translateX(-50%); text-align: center;">
            <span style="font-size: 12px; font-weight: bold; color: #555;">{name}</span>
            <div style="width: 30px; height: 20px; background-color: #7f8c8d; border-radius: 4px; margin: 0 auto;"></div>
            <div style="width: 14px; height: 20px; background-color: #95a5a6; margin: 0 auto; position: relative;">
                {pouring_html if is_pouring else ""}
            </div>
        </div>
        """

    width = "100%" if tank_type == "underground" else "180px"
    height = "150px" if tank_type == "underground" else "220px"

    html = f"""
    <div style="margin-top: 50px; display: flex; flex-direction: column; align-items: center;">
        <div style="width: {width}; max-width: 400px; height: {height}; border: 3px solid #333; position: relative; background-color: #f4f4f4; border-top: none;">
            {pipes_html}
            <div style="position: absolute; bottom: 0; width: 100%; height: {percentage}%; background-color: {water_color}; transition: height 1s; display: flex; align-items: center; justify-content: center; z-index: 2;">
                <span style="color: white; font-weight: bold;">{percentage}%</span>
            </div>
        </div>
        <div style="margin-top: 5px; font-weight: bold; font-size: 18px;">{tank_name}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ३. गुगल शीटची लिंक आणि डेटा वाचणे
SHEET_URL = "https://docs.google.com/spreadsheets/d/1oys9fFlUwlwiw1dzYwWMbu0AiZuCszwPLzZWpb34_rA/edit?usp=sharing"
csv_url = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')

try:
    # लाईव्ह डेटा वाचणे
    df = pd.read_csv(csv_url, encoding='utf-8')
    latest_data = df.iloc[-1]
    
    # गुगल शीटमधून टाक्यांची पातळी घेणे (सध्या आपण रकाणा 3 आणि 5 वापरत आहोत)
    tank1_lvl = int(latest_data.iloc[3]) if pd.notna(latest_data.iloc[3]) else 0
    tank2_lvl = int(latest_data.iloc[5]) if pd.notna(latest_data.iloc[5]) else 0
    underground_lvl = 80 # अंडरग्राउंडसाठी सध्या डमी आकडा, नंतर आपण याचाही रकाना जोडू
    
    # ४. डॅशबोर्डची मुख्य रचना (Layout)
    col_left, col_right = st.columns([1.5, 1]) # डावा भाग थोडा मोठा

    # आपण 'उजवा भाग' कोडमध्ये आधी लिहितो, जेणेकरून त्याची बटणे डावीकडच्या ॲनिमेशनला कंट्रोल करू शकतील
    with col_right:
        # --- १. Control Panel ---
        st.markdown("""<div style="border: 2px solid #555; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            <h4 style="margin-top: 0; text-align: center;">Control Panel</h4>""", unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: ug_pump = st.toggle("UG Tank", value=False)
        with col_c2: bw1_pump = st.toggle("Borewell 1", value=False)
        with col_c3: bw2_pump = st.toggle("Borewell 2", value=False)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- २. Valves (कॉक) ---
        st.markdown("""<div style="border: 2px solid #555; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            <h4 style="margin-top: 0; text-align: center;">Valves</h4>""", unsafe_allow_html=True)
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1: valve1 = st.toggle("Valve 1 (UG)", value=False)
        with col_v2: valve2 = st.toggle("Valve 2 (T1)", value=False)
        with col_v3: valve3 = st.toggle("Valve 3 (T2)", value=False)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- ३. Status Board (स्थिती फलक लॉजिक) ---
        status_msgs = []
        if bw1_pump: status_msgs.append("Borewell 1 पंप सुरू आहे.")
        if bw2_pump: status_msgs.append("Borewell 2 पंप सुरू आहे.")
        if ug_pump: status_msgs.append("Underground टँकर पंप सुरू आहे.")
        if valve2: status_msgs.append("Tank 1 मध्ये पाणी भरत आहे.")
        if valve3: status_msgs.append("Tank 2 मध्ये पाणी भरत आहे.")
        if not any([bw1_pump, bw2_pump, ug_pump, valve1, valve2, valve3]):
            status_msgs.append("सध्या सर्व पंप आणि वाल्व्ह बंद आहेत.")

        status_html = "".join([f"<li style='margin-bottom: 5px;'>{msg}</li>" for msg in status_msgs])

        st.markdown(f"""<div style="border: 2px solid #555; padding: 15px; border-radius: 5px; min-height: 150px; background-color: #fffaf0;">
            <h4 style="margin-top: 0; text-align: center; border-bottom: 1px dashed #ccc; padding-bottom: 5px;">स्थिती फलक</h4>
            <ul style="font-size: 16px; color: #111; font-weight: bold; padding-left: 20px;">
                {status_html}
            </ul>
            </div>""", unsafe_allow_html=True)

    with col_left:
        # --- डावा भाग: टाक्या (गुगल शीटच्या डेटासह) ---
        top_tanks_col1, top_tanks_col2 = st.columns(2)
        with top_tanks_col1:
            draw_tank_with_pipe("Tank 1", tank1_lvl, is_pouring=valve2, tank_type="overhead", source_names=["Valve 2"])
        with top_tanks_col2:
            draw_tank_with_pipe("Tank 2", tank2_lvl, is_pouring=valve3, tank_type="overhead", source_names=["Valve 3"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # जर अंडरग्राउंड पंप किंवा बोअरवेल चालू असेल, तरच अंडरग्राउंड टाकीत पाणी पडेल
        is_ug_pouring = ug_pump or bw1_pump or bw2_pump
        draw_tank_with_pipe("Underground Tank", underground_lvl, is_pouring=is_ug_pouring, tank_type="underground", source_names=["Tanker", "Borewell 1"])

except Exception as e:
    st.error(f"डेटा वाचण्यात अडचण आली. कृपया गुगल शीटची लिंक तपासा. Error: {e}")
