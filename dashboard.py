# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import time

st.set_page_config(page_title="Deogirkar Smart Home", layout="wide")

# १. प्रगत CSS (मोबाईलवर बटणे शेजारी ठेवण्यासाठी 'कॉलम लॉक' हॅक)
css = """
<style>
@keyframes waterPour { 0% { background-position: 0 0px; } 100% { background-position: 0 16px; } }
@keyframes waveMove { 0% { background-position-x: 0px; } 100% { background-position-x: 40px; } }
@keyframes sunGlow { 0% { box-shadow: 0 0 5px #fbc02d; } 50% { box-shadow: 0 0 10px #fbc02d; } 100% { box-shadow: 0 0 5px #fbc02d; } }
@keyframes energyFlow { 0% { background-position: 0px 0; } 100% { background-position: 20px 0; } }
@keyframes sirenFlash { 
    0% { background-color: #ffebee; border: 4px solid #d32f2f; } 
    50% { background-color: #d32f2f; color: white; box-shadow: 0 0 40px #d32f2f; } 
    100% { background-color: #ffebee; border: 4px solid #d32f2f; } 
}
.flashing-alert { animation: sirenFlash 0.5s infinite; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 20px; }
.normal-banner { text-align: center; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 12px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15); border: 1px solid #4a6fa5; }

/* 🌟 मोबाईलवर ON/OFF बटणे हमखास शेजारी ठेवण्यासाठी (१००% सपोर्टेड CSS) 🌟 */
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] [data-testid="stHorizontalBlock"] [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
    }
    [data-testid="stHorizontalBlock"] [data-testid="stHorizontalBlock"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        width: 50% !important;
        min-width: 50% !important;
        flex: 1 1 50% !important;
    }
}
.stButton button {
    font-weight: 900 !important;
    border-radius: 6px !important;
    border: 2px solid #555 !important;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 🌟 'Top Banner' आणि 'स्थितीदर्शक' साठी जागा
top_banner = st.empty()

# ⚙️ टेस्टिंग सिम्युलेटर (लपलेले साईडबार)
with st.sidebar:
    st.markdown("### ⚙️ टेस्टिंग सिम्युलेटर")
    sim_tanker = st.checkbox("🚚 टँकरचे पाणी चालू करा")
    sim_solar = st.checkbox("☀️ सोलर वीज निर्मिती चालू करा", value=True)
    st.markdown("---")
    st.markdown("#### 🏃‍♂️ घुसखोर (Motion Detection)")
    simulate_motion = st.checkbox("🚶 हालचाल करा (Test Motion)")

# २. स्टेट्स (Session State)
for key in ['ug_pump', 'bw1_pump', 'bw2_pump']:
    if key not in st.session_state:
        st.session_state[key] = False

if 'alarm_armed' not in st.session_state:
    st.session_state.alarm_armed = False

def set_pump_state(key, state):
    st.session_state[key] = state

# ३. टाक्यांचे डिझाईन 
def get_tank_html(tank_name, level_cm, tank_type="overhead", inlets=[]):
    percentage = min(int((level_cm / 100) * 100), 100)
    water_color = "#00b4d8" if tank_type == "overhead" else "#0077b6"
    dark_wave_color = "%23004b7c" if tank_type == "overhead" else "%23003366" 
    tank_height = "160px" if tank_type == "underground" else "220px"
    tank_width = "100%" if tank_type == "underground" else "160px"

    is_pouring = any(inlet['active'] for inlet in inlets)
    wave_html = f"<div style='position: absolute; top: 0; left: 0; width: 100%; height: 5px; background-color: {dark_wave_color.replace('%23', '#')}; border-top: 2px solid rgba(255,255,255,0.4); z-index: 10;'></div>" if not is_pouring else f"<div style='position: absolute; top: -10px; left: 0; width: 100%; height: 15px; background: url(\"data:image/svg+xml;utf8,<svg viewBox=\\\"0 0 40 15\\\" xmlns=\\\"http://www.w3.org/2000/svg\\\"><path d=\\\"M0 8 Q 10 15, 20 8 T 40 8 L 40 15 L 0 15 Z\\\" fill=\\\"{dark_wave_color}\\\"/></svg>\") repeat-x; background-size: 40px 15px; animation: waveMove 1s linear infinite; z-index: 10;'></div>"

    pipes_html = ""
    for idx, inlet in enumerate(inlets):
        offset = 50 if len(inlets) == 1 else (35 if idx == 0 else 65)
        active_pour = f"<div style='position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 12px; height: {tank_height}; background-image: repeating-linear-gradient(transparent, #00b4d8 4px, transparent 8px); background-size: 100% 16px; animation: waterPour 0.3s infinite linear; z-index: 1;'></div>" if inlet['active'] else ""
        pipes_html += f"<div style='position: absolute; bottom: 100%; left: {offset}%; transform: translateX(-50%); text-align: center; width: 120px;'><div style='font-size: 13px; font-weight: bold; color: #555; margin-bottom: 2px;'>{inlet['name']}</div><div style='width: 30px; height: 18px; background-color: #7f8c8d; border-radius: 4px; margin: 0 auto; border: 1px solid #555;'></div><div style='width: 14px; height: 25px; background-color: #bdc3c7; margin: 0 auto; position: relative; border-left: 1px solid #7f8c8d; border-right: 1px solid #7f8c8d; z-index: 3;'>{active_pour}</div></div>"

    html = f"<div style='margin-top: 50px; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center; width: 100%;'><div style='width: {tank_width}; max-width: 400px; height: {tank_height}; border: 3px solid #333; position: relative; background-color: #eef2f3; border-top: none; border-radius: 0 0 12px 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1); border-top: 1px solid #aaa;'>{pipes_html}<div style='position: absolute; bottom: 0; width: 100%; height: {percentage}%; background-color: {water_color}; transition: height 1s ease-in-out; display: flex; align-items: center; justify-content: center; border-radius: 0 0 9px 9px; z-index: 2; border-top: 1px solid rgba(255,255,255,0.4);'>{wave_html}<span style='color: white; font-weight: bold; font-size: 22px; text-shadow: 1px 1px 3px black; z-index: 11;'>{percentage}%</span></div></div><div style='margin-top: 15px; font-weight: bold; font-size: 16px; background: #333; color: white; padding: 4px 15px; border-radius: 6px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'>{tank_name}</div></div>"
    return html

# ४. वाल्व्ह आणि स्टार्टर्सचे डिझाईन
def draw_knob(is_on):
    color = "#2ecc71" if is_on else "#e74c3c"
    rotation = "0deg" if is_on else "90deg" 
    st.markdown(f"<div style='text-align: center; margin-bottom: 5px;'><div style='width: 40px; height: 40px; border-radius: 50%; background: #2c3e50; border: 3px solid {color}; margin: 0 auto; position: relative; transform: rotate({rotation}); transition: transform 0.4s; box-shadow: 2px 2px 4px rgba(0,0,0,0.4);'><div style='width: 5px; height: 18px; background: {color}; position: absolute; top: 2px; left: 14px; border-radius: 3px;'></div></div></div>", unsafe_allow_html=True)

def render_compact_starter(col_obj, pump_name, state_key):
    is_on = st.session_state[state_key]
    needle_rot = -12 if is_on else -45
    on_glow = "background: radial-gradient(circle, #00ff00, #004d00); box-shadow: 0 0 10px #00ff00; color: white; border: 1px solid #00ff00;" if is_on else "background: #111; color: #555; border: 1px solid #222;"
    off_glow = "background: radial-gradient(circle, #ff0000, #4d0000); box-shadow: 0 0 10px #ff0000; color: white; border: 1px solid #ff0000;" if not is_on else "background: #111; color: #555; border: 1px solid #222;"

    html = f"""<div style="background-color: #1c1c1c; padding: 10px; border-radius: 8px; border: 2px solid #333; text-align: center; margin-bottom: 8px; box-shadow: 3px 3px 10px rgba(0,0,0,0.3);">
<div style="color: #ddd; font-weight: bold; font-size: 11px; margin-bottom: 8px; text-transform: uppercase;">{pump_name}</div>
<div style="background-color: #f9f9f9; border-radius: 4px; padding: 5px; margin-bottom: 10px; border: 1px solid #aaa; position: relative; height: 50px;">
<svg width="100%" height="100%" viewBox="0 0 100 65">
<path d="M 15 45 A 40 40 0 0 1 85 45" fill="none" stroke="#222" stroke-width="1.5"/>
<text x="15" y="58" font-size="10" text-anchor="middle" font-weight="bold">0</text>
<text x="50" y="60" font-size="14" text-anchor="middle" font-weight="bold">A</text>
<text x="85" y="58" font-size="10" text-anchor="middle" font-weight="bold">30</text>
<line x1="50" y1="58" x2="50" y2="12" stroke="#222" stroke-width="2.5" transform="rotate({needle_rot} 50 58)" style="transition: transform 0.5s cubic-bezier(0.25, 1, 0.5, 1);"/>
<circle cx="50" cy="58" r="3" fill="black"/>
</svg>
</div>
<div style="display: flex; justify-content: space-around; align-items: center; margin-bottom: 5px;">
<div style="width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 10px; {on_glow} transition: 0.3s;">ON</div>
<div style="width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 10px; {off_glow} transition: 0.3s;">OFF</div>
</div>
</div>"""
    col_obj.markdown(html, unsafe_allow_html=True)
    
    # 🌟 डेस्कटॉपसाठी कॉलम्स परत आणले, CSS मुळे ते मोबाईलवरही शेजारीच राहतील 🌟
    bc1, bc2 = col_obj.columns(2)
    bc1.button("ON", key=f"btn_on_{state_key}", on_click=set_pump_state, args=(state_key, True), use_container_width=True)
    bc2.button("OFF", key=f"btn_off_{state_key}", on_click=set_pump_state, args=(state_key, False), use_container_width=True)

# ५. मुख्य डॅशबोर्ड लेआउट
col_left, col_right = st.columns([1.5, 1])

with col_right:
    # 🌟 स्थितीदर्शक बोर्ड
    status_board = st.empty()

    # 🛡️ सुरक्षा प्रणाली
    with st.container(border=True):
        st.markdown("<div style='background-color: #f5f5f5; padding: 8px; border-radius: 6px; margin-bottom: 10px; text-align: center;'><h5 style='margin: 0; color: #c2185b; font-weight: bold;'>🛡️ सुरक्षा प्रणाली (Burglar Alarm)</h5></div>", unsafe_allow_html=True)
        st.session_state.alarm_armed = st.toggle("🚨 अलार्म सिस्टीम (Arm/Disarm)", value=st.session_state.alarm_armed)

    # ☀️ सोलर ऊर्जा
    solar_glow = "animation: sunGlow 3s infinite;" if sim_solar else "border: 1px solid #ccc;"
    live_power = "3.2 kW" if sim_solar else "0.0 kW"
    line_style = "background-image: repeating-linear-gradient(90deg, #00b4d8 0px, #00b4d8 10px, transparent 10px, transparent 20px); background-size: 20px 100%; animation: energyFlow 0.5s linear infinite;" if sim_solar else "background-image: repeating-linear-gradient(90deg, #bdc3c7 0px, #bdc3c7 10px, transparent 10px, transparent 20px);"
    status_color = "#2e7d32" if sim_solar else "#c62828"
    status_text = "🟢 सौर ऊर्जेची निर्मिती सुरू आहे" if sim_solar else "🔴 सौर ऊर्जेची निर्मिती बंद आहे"

    solar_panel_svg = """<svg width="45" height="45" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="10" fill="#FFA500"/><line x1="20" y1="2" x2="20" y2="7" stroke="#FFA500" stroke-width="2"/><line x1="20" y1="38" x2="20" y2="33" stroke="#FFA500" stroke-width="2"/><line x1="2" y1="20" x2="7" y2="20" stroke="#FFA500" stroke-width="2"/><line x1="38" y1="20" x2="33" y2="20" stroke="#FFA500" stroke-width="2"/><line x1="7" y1="7" x2="11" y2="11" stroke="#FFA500" stroke-width="2"/><line x1="33" y1="33" x2="29" y2="29" stroke="#FFA500" stroke-width="2"/><line x1="7" y1="33" x2="11" y2="29" stroke="#FFA500" stroke-width="2"/><line x1="33" y1="7" x2="29" y2="11" stroke="#FFA500" stroke-width="2"/><polyline points="75,90 85,90 80,40" fill="none" stroke="#999" stroke-width="4"/><polygon points="35,85 45,35 85,30 70,80" fill="#1e5799" stroke="#ddd" stroke-width="2"/><line x1="40" y1="60" x2="77" y2="55" stroke="#ddd" stroke-width="1.5"/><line x1="53" y1="35" x2="42" y2="82" stroke="#ddd" stroke-width="1.5"/><line x1="68" y1="32" x2="57" y2="80" stroke="#ddd" stroke-width="1.5"/></svg>"""
    grid_tower_svg = """<svg width="40" height="40" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><polyline points="50,10 30,90" fill="none" stroke="#555" stroke-width="3"/><polyline points="50,10 70,90" fill="none" stroke="#555" stroke-width="3"/><line x1="45" y1="30" x2="55" y2="30" stroke="#555" stroke-width="3"/><line x1="40" y1="50" x2="60" y2="50" stroke="#555" stroke-width="3"/><line x1="35" y1="70" x2="65" y2="70" stroke="#555" stroke-width="3"/><line x1="45" y1="30" x2="60" y2="50" stroke="#555" stroke-width="2"/><line x1="55" y1="30" x2="40" y2="50" stroke="#555" stroke-width="2"/><line x1="40" y1="50" x2="65" y2="70" stroke="#555" stroke-width="2"/><line x1="60" y1="50" x2="35" y2="70" stroke="#555" stroke-width="2"/><line x1="25" y1="30" x2="75" y2="30" stroke="#555" stroke-width="3"/><line x1="20" y1="50" x2="80" y2="50" stroke="#555" stroke-width="3"/></svg>"""

    with st.container(border=True):
        st.markdown(f"<div style='background-color: #fffde7; padding: 8px; border-radius: 6px; margin-bottom: 12px; text-align: center; {solar_glow}'><h5 style='margin: 0; color: #f57f17; font-weight: bold;'>☀️ सोलर ऊर्जा (Sofar Inverter)</h5></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='display: flex; justify-content: space-around; align-items: center; margin-bottom: 10px;'><div style='text-align: center;'><div style='font-size: 13px; color: #666;'>सध्याची निर्मिती</div><div style='font-size: 20px; font-weight: bold; color: #2e7d32;'>{live_power}</div></div><div style='text-align: center;'><div style='font-size: 13px; color: #666;'>आजची एकूण वीज</div><div style='font-size: 20px; font-weight: bold; color: #1565c0;'>14.5 kWh</div></div></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background-color: #f8f9fa; padding: 12px; border-radius: 8px; border: 1px solid #eee; margin-top: 5px;'><div style='display: flex; align-items: center; justify-content: space-between;'><div style='text-align: center; width: 60px;'>{solar_panel_svg}<div style='font-size: 11px; font-weight: bold; color:#555;'>Panels</div></div><div style='flex-grow: 1; height: 4px; margin: 0 5px; {line_style}'></div><div style='text-align: center; width: 40px;'><div style='font-size: 28px;'>🎛️</div><div style='font-size: 11px; font-weight: bold; color:#555;'>Inverter</div></div><div style='flex-grow: 1; height: 4px; margin: 0 5px; {line_style}'></div><div style='text-align: center; width: 60px;'>{grid_tower_svg}<div style='font-size: 11px; font-weight: bold; color:#555;'>Grid</div></div></div><div style='text-align: center; margin-top: 12px; font-weight: bold; font-size: 13px; color: {status_color};'>{status_text}</div></div>", unsafe_allow_html=True)

    # ⚡ कंट्रोल पॅनल
    with st.container(border=True):
        st.markdown("<div style='background-color: #424242; padding: 10px; border-radius: 6px; margin-bottom: 15px; text-align: center; border: 1px solid #222;'><h5 style='margin: 0; color: #fff; font-weight: bold;'>⚡ स्टार्टर कंट्रोल पॅनल</h5></div>", unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        render_compact_starter(sc1, "UG PUMP", "ug_pump")
        render_compact_starter(sc2, "BW-1", "bw1_pump")
        render_compact_starter(sc3, "BW-2", "bw2_pump")

    # 🎛️ वाल्व्ह (कॉक)
    with st.container(border=True):
        st.markdown("<div style='background-color: #c8e6c9; padding: 10px; border-radius: 6px; margin-bottom: 15px; text-align: center;'><h5 style='margin: 0; color: #2e7d32; font-weight: bold;'>🎛️ वाल्व्ह (कॉक)</h5></div>", unsafe_allow_html=True)
        v1, v2, v3 = st.columns(3)
        with v1: valve_t1 = st.toggle("V1 (Tank 1)", value=False); draw_knob(valve_t1)
        with v2: valve_t2 = st.toggle("V2 (Tank 2)", value=False); draw_knob(valve_t2)
        with v3: valve_ug = st.toggle("V3 (UG Tank)", value=False); draw_knob(valve_ug)

    # ---------------------------------------------------------
    # 🧠 लॉजिक
    # ---------------------------------------------------------
    trigger_siren = st.session_state.alarm_armed and simulate_motion
    ug_pump = st.session_state['ug_pump']
    bw1_pump = st.session_state['bw1_pump']
    bw2_pump = st.session_state['bw2_pump']
    
    any_pump_on = ug_pump or bw1_pump or bw2_pump
    any_borewell_on = bw1_pump or bw2_pump
    tank1_pouring = valve_t1 and any_pump_on
    tank2_pouring = valve_t2 and any_pump_on
    ug_pouring_from_bw = valve_ug and any_borewell_on
    ug_pouring_from_tanker = sim_tanker
    garden_watering = ug_pump and not valve_t1 and not valve_t2
    is_any_water_pouring = tank1_pouring or tank2_pouring or ug_pouring_from_bw or ug_pouring_from_tanker or garden_watering

    # 📋 स्थितीदर्शक बोर्ड अपडेट
    with status_board.container(border=True):
        st.markdown("<div style='background-color: #e3f2fd; padding: 10px; border-radius: 6px; margin-bottom: 10px; text-align: center;'><h5 style='margin: 0; color: #1565c0; font-weight: bold;'>📋 स्थितीदर्शक</h5></div>", unsafe_allow_html=True)
        status_msgs = []
        if trigger_siren: status_msgs.append("🚨 घुसखोर आढळला! अलार्म सुरू आहे.")
        if not any_pump_on and not sim_tanker: status_msgs.append("⚠️ सर्व पंप बंद आहेत.")
        else:
            if ug_pump: status_msgs.append("🔸 अंडरग्राउंड पंप सुरू आहे.")
            if bw1_pump: status_msgs.append("🔸 बोअरवेल १ सुरू आहे.")
            if bw2_pump: status_msgs.append("🔸 बोअरवेल २ सुरू মাঠে.")
            if sim_tanker: status_msgs.append("🚚 टँकरद्वारे पाणी येत आहे.")
        if tank1_pouring: status_msgs.append("🔹 'Tank 1' मध्ये पाणी भरत आहे.")
        if tank2_pouring: status_msgs.append("🔹 'Tank 2' मध्ये पाणी भरत आहे.")
        if ug_pouring_from_bw: status_msgs.append("🔹 बोअरवेलचे पाणी 'UG Tank' मध्ये जात आहे.")
        if garden_watering: status_msgs.append("🌿 पाणी 'गार्डन/झाडांना' दिले जात आहे.")
        
        status_html = "".join([f"<li style='margin-bottom: 5px;'>{msg}</li>" for msg in status_msgs])
        st.markdown(f"<ul style='font-size: 14px; color: #333; font-weight: 600; padding-left: 20px; margin-bottom: 0;'>{status_html}</ul>", unsafe_allow_html=True)

with col_left:
    # 🌟 टाक्यांचे डिझाईन
    html_t1 = get_tank_html("Tank 1", 45, tank_type="overhead", inlets=[{"name": "Main Line", "active": tank1_pouring}])
    html_t2 = get_tank_html("Tank 2", 60, tank_type="overhead", inlets=[{"name": "Main Line", "active": tank2_pouring}])
    html_ug = get_tank_html("Underground Tank", 75, tank_type="underground", inlets=[{"name": "Borewell (V3)", "active": ug_pouring_from_bw}, {"name": "Tanker", "active": ug_pouring_from_tanker}])

    st.markdown(f"""
    <div style="display: flex; justify-content: space-around; flex-wrap: nowrap; width: 100%; gap: 10px;">
        <div style="flex: 1; display: flex; justify-content: center;">{html_t1}</div>
        <div style="flex: 1; display: flex; justify-content: center;">{html_t2}</div>
    </div>
    <div style="width: 100%; margin-top: 15px;">
        {html_ug}
    </div>
    """, unsafe_allow_html=True)

    garden_active_html = "<div style='position: absolute; top: -30px; left: 50%; transform: translateX(-50%); width: 8px; height: 40px; background-image: repeating-linear-gradient(transparent, #00b4d8 2px, transparent 6px); background-size: 100% 10px; animation: waterPour 0.3s infinite linear;'></div>" if garden_watering else ""
    st.markdown(f"<div style='margin-top: 20px; border: 3px solid #2e7d32; border-radius: 12px; background: #e8f5e9; padding: 15px; text-align: center; position: relative;'>{garden_active_html}<div style='font-size: 40px;'>🌳🏡🌿</div><h4 style='color: #2e7d32; margin: 5px 0 0 0;'>गार्डन / झाडे</h4><p style='font-size: 12px; color: #555; margin: 0;'>अंडरग्राउंड टाकीतून पाणी</p></div>", unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #1e3c72; text-align: center;'>📹 सुरक्षा कॅमेरे (Live CCTV Feed)</h3>", unsafe_allow_html=True)

placeholder_style = "background-color: #111; height: 250px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #888; font-family: monospace; border: 2px solid #444; position: relative; text-align: center;"
recording_dot = "<div style='position: absolute; top: 15px; right: 15px; width: 12px; height: 12px; background-color: #ff3333; border-radius: 50%; animation: pulseRed 1s infinite; box-shadow: 0 0 8px #ff3333;'></div>"

cam_col1, cam_col2 = st.columns(2)
with cam_col1:
    st.markdown(f"<div style='{placeholder_style}'>{recording_dot}Camera 1<br><br>Connecting to RTSP Stream...</div><div style='text-align: center; font-weight: bold; margin-top: 5px; color: #555;'>📍 मुख्य प्रवेशद्वार (Main Gate)</div>", unsafe_allow_html=True)
with cam_col2:
    st.markdown(f"<div style='{placeholder_style}'>{recording_dot}Camera 2<br><br>Connecting to RTSP Stream...</div><div style='text-align: center; font-weight: bold; margin-top: 5px; color: #555;'>📍 पार्किंग (Parking Area)</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📢 ७. बोलणारी 'मराठी व्हाईस' आणि सायरन सिस्टीम 
# ---------------------------------------------------------
if trigger_siren:
    top_banner.markdown("""
    <div class='flashing-alert'>
        <h1 style='color: white; margin: 0; font-size: 36px; font-weight: 900; text-shadow: 2px 2px 5px black;'>🚨 सावधान! घरात घुसखोर आढळला! 🚨</h1>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""<audio autoplay loop><source src="https://upload.wikimedia.org/wikipedia/commons/4/40/Siren_Noise.ogg" type="audio/ogg"><source src="https://actions.google.com/sounds/v1/alarms/burglar_alarm.ogg" type="audio/ogg"></audio>""", unsafe_allow_html=True)
else:
    top_banner.markdown("""
    <div class='normal-banner'>
        <h2 style='color: #ffffff; margin: 0; font-weight: 800; letter-spacing: 1px;'>अभिप्राजामेयार्णव</h2>
        <h4 style='color: #81d4fa; margin: 3px 0 0 0; font-weight: 500;'>पाणी, ऊर्जा व सुरक्षा व्यवस्थापन प्रणाली</h4>
    </div>
    """, unsafe_allow_html=True)

# पाण्याचा आवाज
if is_any_water_pouring and not trigger_siren:
    st.markdown("""<audio autoplay loop id="waterAudio"><source src="https://actions.google.com/sounds/v1/water/stream_water.ogg" type="audio/ogg"></audio><script>document.getElementById("waterAudio").volume = 0.4;</script>""", unsafe_allow_html=True)

# 🗣️ न थांबणारे ऑडिओ लॉजिक (Timestamp Hack)
alert_to_speak = ""
if trigger_siren:
    alert_to_speak = "सावधान! घरात घुसखोर आढळला आहे. सुरक्षा प्रणाली सुरू झाली आहे."
elif (valve_t1 or valve_t2) and not any_pump_on:
    alert_to_speak = "सावधान! वाल्व्ह उघडा आहे, पण पंप बंद आहे."
elif tank1_pouring and tank2_pouring:
    alert_to_speak = "टाकी एक आणि टाकी दोन मध्ये पाणी भरत आहे."
elif tank1_pouring:
    alert_to_speak = "टाकी एक मध्ये पाणी भरत आहे."
elif tank2_pouring:
    alert_to_speak = "टाकी दोन मध्ये पाणी भरत आहे."
elif ug_pouring_from_bw or ug_pouring_from_tanker:
    alert_to_speak = "अंडरग्राउंड टाकीत पाणी भरत आहे."
elif garden_watering:
    alert_to_speak = "गार्डन मध्ये पाणी दिले जात आहे."

if 'last_speech' not in st.session_state:
    st.session_state.last_speech = ""

if alert_to_speak == "":
    st.session_state.last_speech = ""
elif alert_to_speak != st.session_state.last_speech:
    st.session_state.last_speech = alert_to_speak
    tts_js = f"<script>var msg = new SpeechSynthesisUtterance('{alert_to_speak}'); msg.lang = 'mr-IN'; msg.rate = 0.95; window.speechSynthesis.speak(msg); console.log('{time.time()}');</script>"
    components.html(tts_js, height=0, width=0)
