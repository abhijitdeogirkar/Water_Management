# -*- coding: utf-8 -*-
import streamlit as st

# १. पेज सेटिंग
st.set_page_config(page_title="Deogirkar Water Monitor", layout="wide")
st.title("अभिराजमेयार्णव पाणी व्यवस्थापन प्रणाली")
st.markdown("---")

# २. HTML/CSS ॲनिमेशन फंक्शन्स
def draw_tank(tank_name, level_cm, is_pouring=False, tank_type="overhead", inlets=[]):
    percentage = min(int((level_cm / 100) * 100), 100)
    water_color = "#00b4d8" if tank_type == "overhead" else "#0077b6"
    
    # पाणी पडण्याचे ॲनिमेशन
    pouring_html = ""
    if is_pouring:
        pouring_html = """
        <div style="position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 10px; height: 100px; background-image: repeating-linear-gradient(transparent, #00b4d8 4px, transparent 8px); background-size: 100% 16px; animation: pour 0.5s infinite linear; z-index: 1;"></div>
        <style>@keyframes pour { from { background-position: 0 0; } to { background-position: 0 100%; } }</style>
        """

    # इनलेट पाईप्स (नळ)
    pipes_html = ""
    for idx, inlet in enumerate(inlets):
        offset = 50 if len(inlets) == 1 else (30 if idx == 0 else 70)
        pipes_html += f"""
        <div style="position: absolute; top: -50px; left: {offset}%; transform: translateX(-50%); text-align: center;">
            <span style="font-size: 11px; font-weight: bold; color: #555;">{inlet['name']}</span>
            <div style="width: 25px; height: 15px; background-color: silver; border-radius: 3px; margin: 0 auto;"></div>
            <div style="width: 12px; height: 35px; background-color: #ddd; margin: 0 auto; position: relative;">
                {pouring_html if inlet['active'] else ""}
            </div>
        </div>
        """

    width = "100%" if tank_type == "underground" else "160px"
    height = "160px" if tank_type == "underground" else "220px"

    html = f"""
    <div style="margin-top: 60px; display: flex; flex-direction: column; align-items: center;">
        <div style="width: {width}; max-width: 400px; height: {height}; border: 3px solid #333; position: relative; background-color: #eef2f3; border-top: none; border-radius: 0 0 10px 10px; box-shadow: 2px 5px 10px rgba(0,0,0,0.1);">
            {pipes_html}
            <div style="position: absolute; bottom: 0; width: 100%; height: {percentage}%; background-color: {water_color}; transition: height 1s; display: flex; align-items: center; justify-content: center; border-radius: 0 0 8px 8px;">
                <span style="color: white; font-weight: bold; text-shadow: 1px 1px 2px black;">{percentage}%</span>
            </div>
        </div>
        <div style="margin-top: 10px; font-weight: bold; font-size: 16px; background: #333; color: white; padding: 2px 10px; border-radius: 5px;">{tank_name}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ॲमीटर (Ammeter) आणि लाईट डिझाईन
def draw_ammeter(is_on, name):
    color = "#2ecc71" if is_on else "#e74c3c" # हिरवा किंवा लाल
    rotation = "45deg" if is_on else "-45deg"
    html = f"""
    <div style="text-align: center; margin-bottom: 10px;">
        <div style="width: 60px; height: 30px; border: 2px solid #555; border-bottom: none; border-radius: 60px 60px 0 0; background: #fff; margin: 0 auto; position: relative; overflow: hidden;">
            <div style="width: 2px; height: 25px; background: red; position: absolute; bottom: 0; left: 29px; transform-origin: bottom; transform: rotate({rotation}); transition: transform 0.5s;"></div>
        </div>
        <div style="width: 15px; height: 15px; border-radius: 50%; background: {color}; margin: 5px auto; box-shadow: 0 0 8px {color};"></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# रोटरी नॉब (१२ आणि ३ वाजताची पोझिशन) डिझाईन
def draw_knob(is_on, name):
    color = "#2ecc71" if is_on else "#e74c3c" # हिरवा किंवा लाल
    rotation = "0deg" if is_on else "90deg" # 0deg = 12 वाजता, 90deg = 3 वाजता
    html = f"""
    <div style="text-align: center; margin-bottom: 10px;">
        <div style="width: 50px; height: 50px; border-radius: 50%; background: #2c3e50; border: 3px solid {color}; margin: 0 auto; position: relative; transform: rotate({rotation}); transition: transform 0.4s; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
            <div style="width: 6px; height: 20px; background: {color}; position: absolute; top: 2px; left: 19px; border-radius: 3px;"></div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ३. सिम्युलेटरसाठी डमी डेटा (जेव्हा सेन्सर येतील तेव्हा हे बदलू)
tank1_lvl = 45
tank2_lvl = 60
ug_lvl = 75

# ४. मुख्य लेआउट (२ कॉलम्स)
col_left, col_right = st.columns([1.5, 1])

with col_right:
    # --- Control Panel (पंप आणि ॲमीटर) ---
    st.markdown("""<div style="border: 2px solid #333; padding: 15px; border-radius: 10px; background: #f8f9fa; margin-bottom: 20px;">
        <h4 style="margin-top: 0; text-align: center; color: #333;">⚡ Control Panel</h4><hr style="margin: 5px 0 15px 0;">""", unsafe_allow_html=True)
    
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

    # --- Valves (रोटरी नॉब्स) ---
    st.markdown("""<div style="border: 2px solid #333; padding: 15px; border-radius: 10px; background: #f8f9fa; margin-bottom: 20px;">
        <h4 style="margin-top: 0; text-align: center; color: #333;">🎛️ Valves</h4><hr style="margin: 5px 0 15px 0;">""", unsafe_allow_html=True)
    
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

    # --- Status Board (स्थिती फलक) ---
    status_msgs = []
    if ug_pump: status_msgs.append("🔸 टँकरचा पंप सुरू आहे.")
    if bw1_pump: status_msgs.append("🔸 बोअरवेल १ सुरू आहे.")
    if bw2_pump: status_msgs.append("🔸 बोअरवेल २ सुरू आहे.")
    if valve2: status_msgs.append("🔹 'Tank 1' मध्ये पाणी भरत आहे.")
    if valve3: status_msgs.append("🔹 'Tank 2' मध्ये पाणी भरत आहे.")
    if not any([ug_pump, bw1_pump, bw2_pump, valve1, valve2, valve3]):
        status_msgs.append("सध्या सर्व पंप आणि वाल्व्ह बंद आहेत.")

    status_html = "".join([f"<li style='margin-bottom: 8px;'>{msg}</li>" for msg in status_msgs])
    st.markdown(f"""<div style="border: 2px solid #333; padding: 15px; border-radius: 10px; background: #fffde7; box-shadow: inset 0 0 10px rgba(0,0,0,0.05);">
        <h4 style="margin-top: 0; text-align: center; color: #d35400;">📋 स्थिती फलक</h4><hr style="margin: 5px 0 15px 0; border-color: #d35400;">
        <ul style="font-size: 15px; color: #333; font-weight: 600; padding-left: 20px;">
            {status_html}
        </ul>
        </div>""", unsafe_allow_html=True)

with col_left:
    # --- डावा भाग: टाक्या (ॲनिमेशनसह) ---
    t1_col, t2_col = st.columns(2)
    with t1_col:
        draw_tank("Tank 1", tank1_lvl, is_pouring=valve2, tank_type="overhead", inlets=[{"name": "Valve 2", "active": valve2}])
    with t2_col:
        draw_tank("Tank 2", tank2_lvl, is_pouring=valve3, tank_type="overhead", inlets=[{"name": "Valve 3", "active": valve3}])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # अंडरग्राउंड टाकी (दोन इनलेट्ससह)
    ug_inlets = [
        {"name": "Tanker (UG Pump)", "active": ug_pump},
        {"name": "Borewell 1", "active": bw1_pump}
    ]
    draw_tank("Underground Tank", ug_lvl, is_pouring=(ug_pump or bw1_pump), tank_type="underground", inlets=ug_inlets)
