# -*- coding: utf-8 -*-
import streamlit as st

st.set_page_config(page_title="Deogirkar Water Monitor", layout="wide")
st.title("अभिप्राजमेयार्णव पाणी व्यवस्थापन प्रणाली")
st.markdown("---")

# १. ॲनिमेशनचा CSS कोड एकदाच सर्वात वर ठेवला आहे (जेणेकरून कोड दिसणार नाही)
st.markdown("<style>@keyframes waterPour { 0% { background-position: 0 0px; } 100% { background-position: 0 16px; } }</style>", unsafe_allow_html=True)

# २. टाक्या आणि पाणी दाखवणारे फंक्शन (हे आता पूर्णपणे 'Single-line' केले आहे)
def draw_tank(tank_name, level_cm, tank_type="overhead", inlets=[]):
    percentage = min(int((level_cm / 100) * 100), 100)
    water_color = "#00b4d8" if tank_type == "overhead" else "#0077b6"
    tank_height = "160px" if tank_type == "underground" else "220px"
    tank_width = "100%" if tank_type == "underground" else "160px"

    pipes_html = ""
    for idx, inlet in enumerate(inlets):
        offset = 50 if len(inlets) == 1 else (30 if idx == 0 else 70)
        active_pour = ""
        if inlet['active']:
            active_pour = f"<div style='position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 12px; height: {tank_height}; background-image: repeating-linear-gradient(transparent, #00b4d8 4px, transparent 8px); background-size: 100% 16px; animation: waterPour 0.4s infinite linear; z-index: 1;'></div>"
        
        pipes_html += f"<div style='position: absolute; bottom: 100%; left: {offset}%; transform: translateX(-50%); text-align: center; width: 120px;'><div style='font-size: 13px; font-weight: bold; color: #555; margin-bottom: 2px;'>{inlet['name']}</div><div style='width: 30px; height: 18px; background-color: #7f8c8d; border-radius: 4px; margin: 0 auto; border: 1px solid #555;'></div><div style='width: 14px; height: 25px; background-color: #bdc3c7; margin: 0 auto; position: relative; border-left: 1px solid #7f8c8d; border-right: 1px solid #7f8c8d; z-index: 3;'>{active_pour}</div></div>"

    html = f"<div style='margin-top: 80px; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center;'><div style='width: {tank_width}; max-width: 400px; height: {tank_height}; border: 3px solid #333; position: relative; background-color: #eef2f3; border-top: none; border-radius: 0 0 12px 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);'>{pipes_html}<div style='position: absolute; bottom: 0; width: 100%; height: {percentage}%; background-color: {water_color}; transition: height 1s; display: flex; align-items: center; justify-content: center; border-radius: 0 0 9px 9px; z-index: 2; border-top: 2px solid rgba(255,255,255,0.4);'><span style='color: white; font-weight: bold; font-size: 20px; text-shadow: 1px 1px 3px black;'>{percentage}%</span></div></div><div style='margin-top: 15px; font-weight: bold; font-size: 16px; background: #333; color: white; padding: 4px 15px; border-radius: 6px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'>{tank_name}</div></div>"
    st.markdown(html, unsafe_allow_html=True)

# ॲमीटर डिझाईन
def draw_ammeter(is_on, name):
    color = "#2ecc71" if is_on else "#e74c3c"
    rotation = "45deg" if is_on else "-45deg"
    html = f"<div style='text-align: center; margin-bottom: 10px;'><div style='width: 60px; height: 30px; border: 2px solid #555; border-bottom: none; border-radius: 60px 60px 0 0; background: #fff; margin: 0 auto; position: relative; overflow: hidden; box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);'><div style='width: 2px; height: 26px; background: red; position: absolute; bottom: 0; left: 29px; transform-origin: bottom; transform: rotate({rotation}); transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);'></div></div><div style='width: 16px; height: 16px; border-radius: 50%; background: {color}; margin: 5px auto; box-shadow: 0 0 10px {color}; border: 1px solid #fff;'></div></div>"
    st.markdown(html, unsafe_allow_html=True)

# नॉब डिझाईन
def draw_knob(is_on, name):
    color = "#2ecc71" if is_on else "#e74c3c"
    rotation = "0deg" if is_on else "90deg" 
    html = f"<div style='text-align: center; margin-bottom: 10px;'><div style='width: 50px; height: 50px; border-radius: 50%; background: #2c3e50; border: 3px solid {color}; margin: 0 auto; position: relative; transform: rotate({rotation}); transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); box-shadow: 2px 2px 6px rgba(0,0,0,0.4);'><div style='width: 6px; height: 22px; background: {color}; position: absolute; top: 2px; left: 19px; border-radius: 3px;'></div></div></div>"
    st.markdown(html, unsafe_allow_html=True)

# ३. सिम्युलेटरसाठी डमी डेटा 
tank1_lvl = 45
tank2_lvl = 60
ug_lvl = 75

col_left, col_right = st.columns([1.5, 1])

with col_right:
    # --- Control Panel ---
    st.markdown("<div style='border: 2px solid #444; padding: 15px; border-radius: 10px; background: #f8f9fa; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);'><h4 style='margin-top: 0; text-align: center; color: #2c3e50;'>⚡ Control Panel</h4><hr style='margin: 5px 0 15px 0; border-color: #ccc;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: 
        ug_pump = st.toggle("UG Pump", value=True)
        draw_ammeter(ug_pump, "UG")
    with c2: 
        bw1_pump = st.toggle("Borewell 1", value=False)
        draw_ammeter(bw1_pump, "BW1")
    with c3: 
        bw2_pump = st.toggle("Borewell 2", value=False)
        draw_ammeter(bw2_pump, "BW2")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Valves ---
    st.markdown("<div style='border: 2px solid #444; padding: 15px; border-radius: 10px; background: #f8f9fa; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);'><h4 style='margin-top: 0; text-align: center; color: #2c3e50;'>🎛️ Valves</h4><hr style='margin: 5px 0 15px 0; border-color: #ccc;'>", unsafe_allow_html=True)
    v1, v2, v3 = st.columns(3)
    with v1: 
        valve1 = st.toggle("V1 (UG)", value=False)
        draw_knob(valve1, "V1")
    with v2: 
        valve2 = st.toggle("V2 (Tank1)", value=True)
        draw_knob(valve2, "V2")
    with v3: 
        valve3 = st.toggle("V3 (Tank2)", value=False)
        draw_knob(valve3, "V3")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Status Board ---
    status_msgs = []
    if ug_pump: status_msgs.append("🔸 टँकरचा पंप सुरू आहे.")
    if bw1_pump: status_msgs.append("🔸 बोअरवेल १ सुरू आहे.")
    if bw2_pump: status_msgs.append("🔸 बोअरवेल २ सुरू आहे.")
    if valve2: status_msgs.append("🔹 'Tank 1' मध्ये पाणी भरत आहे.")
    if valve3: status_msgs.append("🔹 'Tank 2' मध्ये पाणी भरत आहे.")
    if not any([ug_pump, bw1_pump, bw2_pump, valve1, valve2, valve3]):
        status_msgs.append("सध्या सर्व पंप आणि वाल्व्ह बंद आहेत.")

    status_html = "".join([f"<li style='margin-bottom: 8px;'>{msg}</li>" for msg in status_msgs])
    st.markdown(f"<div style='border: 2px solid #e67e22; padding: 15px; border-radius: 10px; background: #fffdf5; box-shadow: inset 0 0 10px rgba(0,0,0,0.05);'><h4 style='margin-top: 0; text-align: center; color: #d35400;'>📋 स्थिती फलक</h4><hr style='margin: 5px 0 15px 0; border-color: #f39c12;'><ul style='font-size: 15px; color: #333; font-weight: 600; padding-left: 20px;'>{status_html}</ul></div>", unsafe_allow_html=True)

with col_left:
    # --- टाक्या ---
    t1_col, t2_col = st.columns(2)
    with t1_col:
        draw_tank("Tank 1", tank1_lvl, tank_type="overhead", inlets=[{"name": "Valve 2", "active": valve2}])
    with t2_col:
        draw_tank("Tank 2", tank2_lvl, tank_type="overhead", inlets=[{"name": "Valve 3", "active": valve3}])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    ug_inlets = [{"name": "Tanker", "active": ug_pump}, {"name": "Borewell 1", "active": bw1_pump}]
    draw_tank("Underground Tank", ug_lvl, tank_type="underground", inlets=ug_inlets)
