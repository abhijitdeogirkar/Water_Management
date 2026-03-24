# -*- coding: utf-8 -*-
import streamlit as st

st.set_page_config(page_title="Deogirkar Water Monitor", layout="wide")

# १. टायटल बॅनर
st.markdown("""
<div style='text-align: center; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 12px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15); border: 1px solid #4a6fa5;'>
    <h2 style='color: #ffffff; margin: 0; font-weight: 800; letter-spacing: 1px;'>अभिप्राजामेयार्णव</h2>
    <h4 style='color: #81d4fa; margin: 3px 0 0 0; font-weight: 500;'>पाणी व्यवस्थापन प्रणाली</h4>
</div>
""", unsafe_allow_html=True)

# २. समुद्राच्या लाटांचे (Ocean Waves) CSS
css = """
<style>
@keyframes waterPour { 0% { background-position: 0 0px; } 100% { background-position: 0 16px; } }
@keyframes waveMove { 0% { background-position-x: 0px; } 100% { background-position-x: 40px; } }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ३. टाक्या आणि समुद्राच्या लाटांचे डिझाईन
def draw_tank(tank_name, level_cm, tank_type="overhead", inlets=[]):
    percentage = min(int((level_cm / 100) * 100), 100)
    water_color = "#00b4d8" if tank_type == "overhead" else "#0077b6"
    dark_wave_color = "%23004b7c" if tank_type == "overhead" else "%23003366" 
    tank_height = "160px" if tank_type == "underground" else "220px"
    tank_width = "100%" if tank_type == "underground" else "160px"

    # पाणी पडत आहे का? हे तपासणे
    is_pouring = any(inlet['active'] for inlet in inlets)
    
    # 🌟 कडक लॉजिक: पाणी पडत असेल तरच लाटा हलतील, नाहीतर 'none' (स्थिर) राहतील
    wave_style = "animation: waveMove 1s linear infinite;" if is_pouring else "animation: none !important;"

    wave_html = f"<div style='position: absolute; top: -10px; left: 0; width: 100%; height: 15px; background: url(\"data:image/svg+xml;utf8,<svg viewBox=\\\"0 0 40 15\\\" xmlns=\\\"http://www.w3.org/2000/svg\\\"><path d=\\\"M0 8 Q 10 15, 20 8 T 40 8 L 40 15 L 0 15 Z\\\" fill=\\\"{dark_wave_color}\\\"/></svg>\") repeat-x; background-size: 40px 15px; {wave_style} z-index: 10;'></div>"

    pipes_html = ""
    for idx, inlet in enumerate(inlets):
        offset = 50 if len(inlets) == 1 else (30 if idx == 0 else 70)
        active_pour = ""
        if inlet['active']:
            active_pour = f"<div style='position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 12px; height: {tank_height}; background-image: repeating-linear-gradient(transparent, #00b4d8 4px, transparent 8px); background-size: 100% 16px; animation: waterPour 0.3s infinite linear; z-index: 1;'></div>"
        
        pipes_html += f"<div style='position: absolute; bottom: 100%; left: {offset}%; transform: translateX(-50%); text-align: center; width: 120px;'><div style='font-size: 13px; font-weight: bold; color: #555; margin-bottom: 2px;'>{inlet['name']}</div><div style='width: 30px; height: 18px; background-color: #7f8c8d; border-radius: 4px; margin: 0 auto; border: 1px solid #555;'></div><div style='width: 14px; height: 25px; background-color: #bdc3c7; margin: 0 auto; position: relative; border-left: 1px solid #7f8c8d; border-right: 1px solid #7f8c8d; z-index: 3;'>{active_pour}</div></div>"

    html = f"<div style='margin-top: 50px; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center;'><div style='width: {tank_width}; max-width: 400px; height: {tank_height}; border: 3px solid #333; position: relative; background-color: #eef2f3; border-top: none; border-radius: 0 0 12px 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);'>{pipes_html}<div style='position: absolute; bottom: 0; width: 100%; height: {percentage}%; background-color: {water_color}; transition: height 1s ease-in-out; display: flex; align-items: center; justify-content: center; border-radius: 0 0 9px 9px; z-index: 2; border-top: 2px solid rgba(255,255,255,0.4);'>{wave_html}<span style='color: white; font-weight: bold; font-size: 22px; text-shadow: 1px 1px 3px black; z-index: 11;'>{percentage}%</span></div></div><div style='margin-top: 15px; font-weight: bold; font-size: 16px; background: #333; color: white; padding: 4px 15px; border-radius: 6px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'>{tank_name}</div></div>"
    st.markdown(html, unsafe_allow_html=True)

# ४. ॲमीटर आणि नॉब डिझाईन
def draw_ammeter(is_on):
    color = "#2ecc71" if is_on else "#e74c3c"
    rotation = "45deg" if is_on else "-45deg"
    st.markdown(f"<div style='text-align: center; margin-bottom: 5px;'><div style='width: 50px; height: 25px; border: 2px solid #555; border-bottom: none; border-radius: 50px 50px 0 0; background: #fff; margin: 0 auto; position: relative; overflow: hidden; box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);'><div style='width: 2px; height: 22px; background: red; position: absolute; bottom: 0; left: 24px; transform-origin: bottom; transform: rotate({rotation}); transition: transform 0.5s;'></div></div><div style='width: 12px; height: 12px; border-radius: 50%; background: {color}; margin: 3px auto; box-shadow: 0 0 8px {color}; border: 1px solid #fff;'></div></div>", unsafe_allow_html=True)

def draw_knob(is_on):
    color = "#2ecc71" if is_on else "#e74c3c"
    rotation = "0deg" if is_on else "90deg" 
    st.markdown(f"<div style='text-align: center; margin-bottom: 5px;'><div style='width: 40px; height: 40px; border-radius: 50%; background: #2c3e50; border: 3px solid {color}; margin: 0 auto; position: relative; transform: rotate({rotation}); transition: transform 0.4s; box-shadow: 2px 2px 4px rgba(0,0,0,0.4);'><div style='width: 5px; height: 18px; background: {color}; position: absolute; top: 2px; left: 14px; border-radius: 3px;'></div></div></div>", unsafe_allow_html=True)

# ५. डमी डेटा
tank1_lvl = 45
tank2_lvl = 60
ug_lvl = 75

col_left, col_right = st.columns([1.5, 1])

with col_right:
    # --- कार्ड १: स्थितीदर्शक बोर्ड (सर्वात वर) ---
    status_card = st.empty()

    # --- कार्ड २: कंट्रोल पॅनल (नारंगी रंग) ---
    with st.container(border=True):
        st.markdown("<div style='background-color: #ffe0b2; padding: 10px; border-radius: 6px; margin-bottom: 15px; text-align: center;'><h5 style='margin: 0; color: #e65100; font-weight: bold;'>⚡ कंट्रोल पॅनल (पंप)</h5></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        # सर्व बटणे डिफॉल्ट 'बंद' (False) ठेवली आहेत
        with c1: ug_pump = st.toggle("UG Pump", value=False); draw_ammeter(ug_pump)
        with c2: bw1_pump = st.toggle("Borewell 1", value=False); draw_ammeter(bw1_pump)
        with c3: bw2_pump = st.toggle("Borewell 2", value=False); draw_ammeter(bw2_pump)

    # --- कार्ड ३: वाल्व्ह (हिरवा रंग) ---
    with st.container(border=True):
        st.markdown("<div style='background-color: #c8e6c9; padding: 10px; border-radius: 6px; margin-bottom: 15px; text-align: center;'><h5 style='margin: 0; color: #2e7d32; font-weight: bold;'>🎛️ वाल्व्ह (कॉक)</h5></div>", unsafe_allow_html=True)
        v1, v2, v3 = st.columns(3)
        # सर्व बटणे डिफॉल्ट 'बंद' (False) ठेवली आहेत
        with v1: valve1 = st.toggle("V1 (UG)", value=False); draw_knob(valve1)
        with v2: valve2 = st.toggle("V2 (Tank1)", value=False); draw_knob(valve2)
        with v3: valve3 = st.toggle("V3 (Tank2)", value=False); draw_knob(valve3)

    # --- स्मार्ट लॉजिक ---
    any_pump_on = ug_pump or bw1_pump or bw2_pump
    tank1_pouring = valve2 and any_pump_on
    tank2_pouring = valve3 and any_pump_on

    # --- स्थितीदर्शक बोर्डात माहिती भरणे ---
    with status_card.container(border=True):
        st.markdown("<div style='background-color: #e3f2fd; padding: 10px; border-radius: 6px; margin-bottom: 10px; text-align: center;'><h5 style='margin: 0; color: #1565c0; font-weight: bold;'>📋 स्थितीदर्शक</h5></div>", unsafe_allow_html=True)
        status_msgs = []
        
        if not any_pump_on:
            status_msgs.append("⚠️ सर्व पंप बंद आहेत. (पाणी प्रवाहित होणार नाही)")
        else:
            if ug_pump: status_msgs.append("🔸 टँकरचा पंप सुरू आहे.")
            if bw1_pump: status_msgs.append("🔸 बोअरवेल १ सुरू आहे.")
            if bw2_pump: status_msgs.append("🔸 बोअरवेल २ सुरू आहे.")
        
        if valve2: 
            if any_pump_on: status_msgs.append("🔹 'Tank 1' मध्ये पाणी भरत आहे.")
            else: status_msgs.append("⚠️ Valve 2 चालू आहे, पण पंप बंद आहे.")
        
        if valve3: 
            if any_pump_on: status_msgs.append("🔹 'Tank 2' मध्ये पाणी भरत आहे.")
            else: status_msgs.append("⚠️ Valve 3 चालू आहे, पण पंप बंद आहे.")

        status_html = "".join([f"<li style='margin-bottom: 5px;'>{msg}</li>" for msg in status_msgs])
        st.markdown(f"<ul style='font-size: 14px; color: #333; font-weight: 600; padding-left: 20px; margin-bottom: 0;'>{status_html}</ul>", unsafe_allow_html=True)

with col_left:
    # --- टाक्या आणि लाटा ---
    t1_col, t2_col = st.columns(2)
    with t1_col:
        draw_tank("Tank 1", tank1_lvl, tank_type="overhead", inlets=[{"name": "Valve 2", "active": tank1_pouring}])
    with t2_col:
        draw_tank("Tank 2", tank2_lvl, tank_type="overhead", inlets=[{"name": "Valve 3", "active": tank2_pouring}])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    ug_pouring = ug_pump or bw1_pump
    ug_inlets = [{"name": "Tanker", "active": ug_pump}, {"name": "Borewell 1", "active": bw1_pump}]
    draw_tank("Underground Tank", ug_lvl, tank_type="underground", inlets=ug_inlets)
