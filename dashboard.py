# -*- coding: utf-8 -*-
import streamlit as st

st.set_page_config(page_title="Deogirkar Water Monitor", layout="wide")

# १. प्रोफेशनल टायटल बॅनर (दोन ओळींमध्ये)
st.markdown("""
<div style='text-align: center; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 25px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); border: 1px solid #4a6fa5;'>
    <h1 style='color: #ffffff; font-size: 40px; margin: 0; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.4); letter-spacing: 2px;'>अभिप्राज्ञार्णव</h1>
    <h3 style='color: #81d4fa; font-size: 22px; margin: 8px 0 0 0; font-weight: 500; letter-spacing: 1px;'>पाणी व्यवस्थापन प्रणाली</h3>
</div>
""", unsafe_allow_html=True)

# २. प्रगत वास्तववादी ॲनिमेशन CSS (पानी चळचळणे, लहरी आणि बुडबुडे)
# टिप: कंसांचा {{ }} गोंधळ टाळण्यासाठी आम्ही हा कोड एकाच सलग रेषेत लिहिला आहे.
css = """
<style>
@keyframes waterPour { 0% { background-position: 0 0px; } 100% { background-position: 0 16px; } }
@keyframes choppy { 0% { border-radius: 10% 5% 5% 10% / 10% 5% 5% 10%; } 25% { border-radius: 12% 8% 8% 12% / 12% 8% 8% 12%; } 50% { border-radius: 8% 12% 12% 8% / 8% 12% 12% 8%; } 75% { border-radius: 11% 9% 9% 11% / 11% 9% 9% 11%; } 100% { border-radius: 10% 5% 5% 10% / 10% 5% 5% 10%; } }
@keyframes surfaceRipple { 0% { transform: scaleX(0.9) translateY(0) rotate(0deg); opacity: 0.3; } 50% { transform: scaleX(1.1) translateY(-3px) rotate(2deg); opacity: 0.8; } 100% { transform: scaleX(0.9) translateY(0) rotate(-1deg); opacity: 0.3; } }
@keyframes rise { 0% { transform: translateY(0) scale(0.6); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateY(-25px) scale(1.4); opacity: 0; } }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ३. टाक्या आणि 'वास्तववादी' पाण्याचे ॲनिमेशन
def draw_tank(tank_name, level_cm, tank_type="overhead", inlets=[]):
    percentage = min(int((level_cm / 100) * 100), 100)
    water_color = "#00b4d8" if tank_type == "overhead" else "#0077b6"
    tank_height = "160px" if tank_type == "underground" else "220px"
    tank_width = "100%" if tank_type == "underground" else "160px"

    is_pouring = any(inlet['active'] for inlet in inlets)
    
    # पाण्याचा पृष्ठभागावरील 'वास्तववादी' परिणाम (चळचळ, लहरी आणि बुडबुडे - फक्त पाणी पडताना)
    surface_fx = ""
    water_top_style = "border-radius: 0;" # डीफॉल्ट सपाट पृष्ठभाग
    
    if is_pouring:
        # १. पाण्याचा वरचा भाग सरळ न ठेवता चळचळणारा (Choppy) करणे
        water_top_style = "animation: choppy 0.8s infinite alternate;"
        
        # २. पृष्ठभागावर गोल लहरी (Ripple) आणि बुडबुडे (Bubbles)
        surface_fx = f"""
        <div style='position: absolute; top: -5px; left: 0; width: 100%; height: 10px; background: rgba(255,255,255,0.4); border-radius: 50%; animation: surfaceRipple 0.6s infinite alternate; z-index: 4;'></div>
        <div style='position: absolute; top: -10px; left: 50%; transform: translateX(-50%); width: 25px; height: 12px; background: rgba(255,255,255,0.8); border-radius: 50%; animation: rise 0.4s infinite alternate; z-index: 5;'></div>
        <div style='position: absolute; top: -2px; left: 35%; width: 12px; height: 12px; background: rgba(255,255,255,0.6); border-radius: 50%; animation: rise 0.5s infinite alternate-reverse; z-index: 5;'></div>
        <div style='position: absolute; top: 2px; left: 65%; width: 10px; height: 10px; background: rgba(255,255,255,0.6); border-radius: 50%; animation: rise 0.3s infinite alternate; z-index: 5;'></div>
        """

    pipes_html = ""
    for idx, inlet in enumerate(inlets):
        offset = 50 if len(inlets) == 1 else (30 if idx == 0 else 70)
        active_pour = ""
        if inlet['active']:
            active_pour = f"<div style='position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 12px; height: {tank_height}; background-image: repeating-linear-gradient(transparent, #00b4d8 4px, transparent 8px); background-size: 100% 16px; animation: waterPour 0.3s infinite linear; z-index: 1;'></div>"
        
        pipes_html += f"<div style='position: absolute; bottom: 100%; left: {offset}%; transform: translateX(-50%); text-align: center; width: 120px;'><div style='font-size: 13px; font-weight: bold; color: #555; margin-bottom: 2px;'>{inlet['name']}</div><div style='width: 30px; height: 18px; background-color: #7f8c8d; border-radius: 4px; margin: 0 auto; border: 1px solid #555;'></div><div style='width: 14px; height: 25px; background-color: #bdc3c7; margin: 0 auto; position: relative; border-left: 1px solid #7f8c8d; border-right: 1px solid #7f8c8d; z-index: 3;'>{active_pour}</div></div>"

    html = f"<div style='margin-top: 50px; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center;'><div style='width: {tank_width}; max-width: 400px; height: {tank_height}; border: 3px solid #333; position: relative; background-color: #eef2f3; border-top: none; border-radius: 0 0 12px 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);'>{pipes_html}<div style='position: absolute; bottom: 0; width: 100%; height: {percentage}%; background-color: {water_color}; transition: height 1s ease-in-out; display: flex; align-items: center; justify-content: center; border-radius: 0 0 9px 9px; z-index: 2; border-top: 2px solid rgba(255,255,255,0.4); {water_top_style}'>{surface_fx}<span style='color: white; font-weight: bold; font-size: 22px; text-shadow: 1px 1px 3px black; z-index: 10;'>{percentage}%</span></div></div><div style='margin-top: 15px; font-weight: bold; font-size: 16px; background: #333; color: white; padding: 4px 15px; border-radius: 6px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'>{tank_name}</div></div>"
    st.markdown(html, unsafe_allow_html=True)

# --- कंट्रोल पॅनेल डिझाईन (कॉम्पॅक्ट) ---
def draw_ammeter(is_on, name):
    color = "#2ecc71" if is_on else "#e74c3c"
    rotation = "45deg" if is_on else "-45deg"
    html = f"<div style='text-align: center; margin-bottom: 0px;'><div style='width: 50px; height: 25px; border: 2px solid #555; border-bottom: none; border-radius: 50px 50px 0 0; background: #fff; margin: 0 auto; position: relative; overflow: hidden; box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);'><div style='width: 2px; height: 22px; background: red; position: absolute; bottom: 0; left: 24px; transform-origin: bottom; transform: rotate({rotation}); transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);'></div></div><div style='width: 12px; height: 12px; border-radius: 50%; background: {color}; margin: 3px auto; box-shadow: 0 0 8px {color}; border: 1px solid #fff;'></div></div>"
    st.markdown(html, unsafe_allow_html=True)

def draw_knob(is_on, name):
    color = "#2ecc71" if is_on else "#e74c3c"
    rotation = "0deg" if is_on else "90deg" 
    html = f"<div style='text-align: center; margin-bottom: 0px;'><div style='width: 40px; height: 40px; border-radius: 50%; background: #2c3e50; border: 3px solid {color}; margin: 0 auto; position: relative; transform: rotate({rotation}); transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); box-shadow: 2px 2px 4px rgba(0,0,0,0.4);'><div style='width: 5px; height: 18px; background: {color}; position: absolute; top: 2px; left: 14px; border-radius: 3px;'></div></div></div>"
    st.markdown(html, unsafe_allow_html=True)

# डमी डेटा
tank1_lvl = 45
tank2_lvl = 60
ug_lvl = 75

col_left, col_right = st.columns([1.5, 1])

with col_right:
    # --- Control Panel ---
    st.markdown("<div style='border: 2px solid #444; padding: 10px; border-radius: 8px; background: #f8f9fa; margin-bottom: 12px; box-shadow: 2px 2px 6px rgba(0,0,0,0.05);'><h5 style='margin-top: 0; margin-bottom: 5px; text-align: center; color: #2c3e50;'>⚡ Control Panel</h5><hr style='margin: 2px 0 10px 0; border-color: #ccc;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: ug_pump = st.toggle("UG Pump", value=True); draw_ammeter(ug_pump, "UG")
    with c2: bw1_pump = st.toggle("Borewell 1", value=False); draw_ammeter(bw1_pump, "BW1")
    with c3: bw2_pump = st.toggle("Borewell 2", value=False); draw_ammeter(bw2_pump, "BW2")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Valves ---
    st.markdown("<div style='border: 2px solid #444; padding: 10px; border-radius: 8px; background: #f8f9fa; margin-bottom: 15px; box-shadow: 2px 2px 6px rgba(0,0,0,0.05);'><h5 style='margin-top: 0; margin-bottom: 5px; text-align: center; color: #2c3e50;'>🎛️ Valves</h5><hr style='margin: 2px 0 10px 0; border-color: #ccc;'>", unsafe_allow_html=True)
    v1, v2, v3 = st.columns(3)
    with v1: valve1 = st.toggle("V1 (UG)", value=False); draw_knob(valve1, "V1")
    with v2: valve2 = st.toggle("V2 (Tank1)", value=True); draw_knob(valve2, "V2")
    with v3: valve3 = st.toggle("V3 (Tank2)", value=False); draw_knob(valve3, "V3")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Status Board ---
    status_msgs = []
    if ug_pump: status_msgs.append("🔸 टँकरचा पंप सुरू आहे.")
    if bw1_pump: status_msgs.append("🔸 बोअरवेल १ सुरू आहे.")
    if bw2_pump: status_msgs.append("🔸 बोअरवेल २ सुरू आहे.")
    if valve2: status_msgs.append("🔹 'Tank 1' मध्ये पाणी भरत आहे.")
    if valve3: status_msgs.append("🔹 'Tank 2' मध्ये पाणी भरत आहे.")
    if not any([ug_pump, bw1_pump, bw2_pump, valve1, valve2, valve3]): status_msgs.append("सध्या सर्व पंप आणि वाल्व्ह बंद आहेत.")
    status_html = "".join([f"<li style='margin-bottom: 5px;'>{msg}</li>" for msg in status_msgs])
    st.markdown(f"<div style='border: 2px solid #e67e22; padding: 12px; border-radius: 8px; background: #fffdf5; box-shadow: inset 0 0 8px rgba(0,0,0,0.05);'><h5 style='margin-top: 0; margin-bottom: 5px; text-align: center; color: #d35400;'>📋 स्थिती फलक</h5><hr style='margin: 2px 0 10px 0; border-color: #f39c12;'><ul style='font-size: 14px; color: #333; font-weight: 600; padding-left: 18px; margin-bottom: 0;'>{status_html}</ul></div>", unsafe_allow_html=True)

with col_left:
    # --- टाक्या ---
    t1_col, t2_col = st.columns(2)
    with t1_col: draw_tank("Tank 1", tank1_lvl, tank_type="overhead", inlets=[{"name": "Valve 2", "active": valve2}])
    with t2_col: draw_tank("Tank 2", tank2_lvl, tank_type="overhead", inlets=[{"name": "Valve 3", "active": valve3}])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    ug_inlets = [{"name": "Tanker", "active": ug_pump}, {"name": "Borewell 1", "active": bw1_pump}]
    draw_tank("Underground Tank", ug_lvl, tank_type="underground", inlets=ug_inlets)
