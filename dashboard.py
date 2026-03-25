# -*- coding: utf-8 -*-
import streamlit as st

st.set_page_config(page_title="Deogirkar Smart Home", layout="wide")

# १. टायटल बॅनर
st.markdown("""
<div style='text-align: center; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 12px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15); border: 1px solid #4a6fa5;'>
    <h2 style='color: #ffffff; margin: 0; font-weight: 800; letter-spacing: 1px;'>अभिप्राजामेयार्णव</h2>
    <h4 style='color: #81d4fa; margin: 3px 0 0 0; font-weight: 500;'>पाणी व ऊर्जा व्यवस्थापन प्रणाली</h4>
</div>
""", unsafe_allow_html=True)

# २. CSS (लाटा, पाणी आणि ऊर्जेचा प्रवाह)
css = """
<style>
@keyframes waterPour { 0% { background-position: 0 0px; } 100% { background-position: 0 16px; } }
@keyframes waveMove { 0% { background-position-x: 0px; } 100% { background-position-x: 40px; } }
@keyframes sunGlow { 0% { box-shadow: 0 0 5px #fbc02d; } 50% { box-shadow: 0 0 10px #fbc02d; } 100% { box-shadow: 0 0 5px #fbc02d; } }
@keyframes energyFlow { 0% { background-position: 0px 0; } 100% { background-position: 20px 0; } }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ३. टाक्यांचे डिझाईन
def draw_tank(tank_name, level_cm, tank_type="overhead", inlets=[]):
    percentage = min(int((level_cm / 100) * 100), 100)
    water_color = "#00b4d8" if tank_type == "overhead" else "#0077b6"
    dark_wave_color = "%23004b7c" if tank_type == "overhead" else "%23003366" 
    tank_height = "160px" if tank_type == "underground" else "220px"
    tank_width = "100%" if tank_type == "underground" else "160px"

    is_pouring = any(inlet['active'] for inlet in inlets)
    wave_html = ""
    
    if not is_pouring:
        simple_dark_blue = dark_wave_color.replace("%23", "#")
        wave_html = f"<div style='position: absolute; top: 0; left: 0; width: 100%; height: 5px; background-color: {simple_dark_blue}; border-top: 2px solid rgba(255,255,255,0.4); z-index: 10;'></div>"
    else:
        wave_html = f"<div style='position: absolute; top: -10px; left: 0; width: 100%; height: 15px; background: url(\"data:image/svg+xml;utf8,<svg viewBox=\\\"0 0 40 15\\\" xmlns=\\\"http://www.w3.org/2000/svg\\\"><path d=\\\"M0 8 Q 10 15, 20 8 T 40 8 L 40 15 L 0 15 Z\\\" fill=\\\"{dark_wave_color}\\\"/></svg>\") repeat-x; background-size: 40px 15px; animation: waveMove 1s linear infinite; z-index: 10;'></div>"

    pipes_html = ""
    for idx, inlet in enumerate(inlets):
        if len(inlets) == 1: offset = 50
        elif len(inlets) == 2: offset = 35 if idx == 0 else 65
        else: offset = 20 + (idx * 30)

        active_pour = ""
        if inlet['active']:
            active_pour = f"<div style='position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 12px; height: {tank_height}; background-image: repeating-linear-gradient(transparent, #00b4d8 4px, transparent 8px); background-size: 100% 16px; animation: waterPour 0.3s infinite linear; z-index: 1;'></div>"
        
        pipes_html += f"<div style='position: absolute; bottom: 100%; left: {offset}%; transform: translateX(-50%); text-align: center; width: 120px;'><div style='font-size: 13px; font-weight: bold; color: #555; margin-bottom: 2px;'>{inlet['name']}</div><div style='width: 30px; height: 18px; background-color: #7f8c8d; border-radius: 4px; margin: 0 auto; border: 1px solid #555;'></div><div style='width: 14px; height: 25px; background-color: #bdc3c7; margin: 0 auto; position: relative; border-left: 1px solid #7f8c8d; border-right: 1px solid #7f8c8d; z-index: 3;'>{active_pour}</div></div>"

    html = f"<div style='margin-top: 50px; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center;'><div style='width: {tank_width}; max-width: 400px; height: {tank_height}; border: 3px solid #333; position: relative; background-color: #eef2f3; border-top: none; border-radius: 0 0 12px 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1); border-top: 1px solid #aaa;'>{pipes_html}<div style='position: absolute; bottom: 0; width: 100%; height: {percentage}%; background-color: {water_color}; transition: height 1s ease-in-out; display: flex; align-items: center; justify-content: center; border-radius: 0 0 9px 9px; z-index: 2; border-top: 1px solid rgba(255,255,255,0.4);'>{wave_html}<span style='color: white; font-weight: bold; font-size: 22px; text-shadow: 1px 1px 3px black; z-index: 11;'>{percentage}%</span></div></div><div style='margin-top: 15px; font-weight: bold; font-size: 16px; background: #333; color: white; padding: 4px 15px; border-radius: 6px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'>{tank_name}</div></div>"
    st.markdown(html, unsafe_allow_html=True)

# ४. ॲमीटर आणि नॉब
def draw_ammeter(is_on):
    color = "#2ecc71" if is_on else "#e74c3c"
    rotation = "45deg" if is_on else "-45deg"
    st.markdown(f"<div style='text-align: center; margin-bottom: 5px;'><div style='width: 50px; height: 25px; border: 2px solid #555; border-bottom: none; border-radius: 50px 50px 0 0; background: #fff; margin: 0 auto; position: relative; overflow: hidden; box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);'><div style='width: 2px; height: 22px; background: red; position: absolute; bottom: 0; left: 24px; transform-origin: bottom; transform: rotate({rotation}); transition: transform 0.5s;'></div></div><div style='width: 12px; height: 12px; border-radius: 50%; background: {color}; margin: 3px auto; box-shadow: 0 0 8px {color}; border: 1px solid #fff;'></div></div>", unsafe_allow_html=True)

def draw_knob(is_on):
    color = "#2ecc71" if is_on else "#e74c3c"
    rotation = "0deg" if is_on else "90deg" 
    st.markdown(f"<div style='text-align: center; margin-bottom: 5px;'><div style='width: 40px; height: 40px; border-radius: 50%; background: #2c3e50; border: 3px solid {color}; margin: 0 auto; position: relative; transform: rotate({rotation}); transition: transform 0.4s; box-shadow: 2px 2px 4px rgba(0,0,0,0.4);'><div style='width: 5px; height: 18px; background: {color}; position: absolute; top: 2px; left: 14px; border-radius: 3px;'></div></div></div>", unsafe_allow_html=True)

# ५. डमी डेटा
tank1_lvl = 45; tank2_lvl = 60; ug_lvl = 75

col_left, col_right = st.columns([1.5, 1])

with col_right:
    # ⚙️ टँकर व सोलर सिम्युलेटर
    with st.expander("⚙️ टेस्टिंग सिम्युलेटर"):
        sim_tanker = st.checkbox("🚚 टँकरचे पाणी चालू करा")
        sim_solar = st.checkbox("☀️ सोलर वीज निर्मिती चालू करा (Test)", value=True)

    # --- ☀️ सुधारित सोलर ऊर्जा (Sofar) कार्ड (लहान फॉन्ट आणि अचूक चित्रे) ---
    solar_glow = "animation: sunGlow 3s infinite;" if sim_solar else "border: 1px solid #ccc;"
    live_power = "3.2 kW" if sim_solar else "0.0 kW"
    
    if sim_solar:
        line_style = "background-image: repeating-linear-gradient(90deg, #00b4d8 0px, #00b4d8 10px, transparent 10px, transparent 20px); background-size: 20px 100%; animation: energyFlow 0.5s linear infinite;"
        status_color = "#2e7d32"
        status_text = "🟢 सौर ऊर्जेची निर्मिती सुरू आहे"
    else:
        line_style = "background-image: repeating-linear-gradient(90deg, #bdc3c7 0px, #bdc3c7 10px, transparent 10px, transparent 20px);"
        status_color = "#c62828"
        status_text = "🔴 सौर ऊर्जेची निर्मिती बंद आहे"

    # SVG Graphics (तुमच्या फोटोप्रमाणे सोलर पॅनेल आणि ग्रिड पोल)
    solar_panel_svg = """<svg width="50" height="50" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="10" fill="#FFA500"/><line x1="20" y1="2" x2="20" y2="7" stroke="#FFA500" stroke-width="2"/><line x1="20" y1="38" x2="20" y2="33" stroke="#FFA500" stroke-width="2"/><line x1="2" y1="20" x2="7" y2="20" stroke="#FFA500" stroke-width="2"/><line x1="38" y1="20" x2="33" y2="20" stroke="#FFA500" stroke-width="2"/><line x1="7" y1="7" x2="11" y2="11" stroke="#FFA500" stroke-width="2"/><line x1="33" y1="33" x2="29" y2="29" stroke="#FFA500" stroke-width="2"/><line x1="7" y1="33" x2="11" y2="29" stroke="#FFA500" stroke-width="2"/><line x1="33" y1="7" x2="29" y2="11" stroke="#FFA500" stroke-width="2"/><polyline points="75,90 85,90 80,40" fill="none" stroke="#999" stroke-width="4"/><polygon points="35,85 45,35 85,30 70,80" fill="#1e5799" stroke="#ddd" stroke-width="2"/><line x1="40" y1="60" x2="77" y2="55" stroke="#ddd" stroke-width="1.5"/><line x1="53" y1="35" x2="42" y2="82" stroke="#ddd" stroke-width="1.5"/><line x1="68" y1="32" x2="57" y2="80" stroke="#ddd" stroke-width="1.5"/></svg>"""
    grid_tower_svg = """<svg width="40" height="40" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><polyline points="50,10 30,90" fill="none" stroke="#555" stroke-width="3"/><polyline points="50,10 70,90" fill="none" stroke="#555" stroke-width="3"/><line x1="45" y1="30" x2="55" y2="30" stroke="#555" stroke-width="3"/><line x1="40" y1="50" x2="60" y2="50" stroke="#555" stroke-width="3"/><line x1="35" y1="70" x2="65" y2="70" stroke="#555" stroke-width="3"/><line x1="45" y1="30" x2="60" y2="50" stroke="#555" stroke-width="2"/><line x1="55" y1="30" x2="40" y2="50" stroke="#555" stroke-width="2"/><line x1="40" y1="50" x2="65" y2="70" stroke="#555" stroke-width="2"/><line x1="60" y1="50" x2="35" y2="70" stroke="#555" stroke-width="2"/><line x1="25" y1="30" x2="75" y2="30" stroke="#555" stroke-width="3"/><line x1="20" y1="50" x2="80" y2="50" stroke="#555" stroke-width="3"/></svg>"""

    with st.container(border=True):
        st.markdown(f"<div style='background-color: #fffde7; padding: 8px; border-radius: 6px; margin-bottom: 12px; text-align: center; {solar_glow}'><h5 style='margin: 0; color: #f57f17; font-weight: bold;'>☀️ सोलर ऊर्जा (Sofar Inverter)</h5></div>", unsafe_allow_html=True)
        
        # फॉन्ट साईज लहान करून साध्या टेक्स्टमध्ये आकडे दाखवले आहेत
        s1, s2 = st.columns(2)
        with s1: st.markdown(f"<div style='text-align: center;'><div style='font-size: 13px; color: #666;'>सध्याची निर्मिती (Live)</div><div style='font-size: 20px; font-weight: bold; color: #2e7d32;'>{live_power}</div></div>", unsafe_allow_html=True)
        with s2: st.markdown(f"<div style='text-align: center;'><div style='font-size: 13px; color: #666;'>आजची एकूण वीज</div><div style='font-size: 20px; font-weight: bold; color: #1565c0;'>14.5 kWh</div></div>", unsafe_allow_html=True)
        
        solar_animation_html = f"""
        <div style='background-color: #f8f9fa; padding: 12px; border-radius: 8px; border: 1px solid #eee; margin-top: 15px;'>
            <div style='display: flex; align-items: center; justify-content: space-between;'>
                <div style='text-align: center; width: 60px;'>{solar_panel_svg}<div style='font-size: 11px; font-weight: bold; color:#555;'>Panels</div></div>
                <div style='flex-grow: 1; height: 4px; margin: 0 5px; {line_style}'></div>
                <div style='text-align: center; width: 40px;'><div style='font-size: 28px;'>🎛️</div><div style='font-size: 11px; font-weight: bold; color:#555;'>Inverter</div></div>
                <div style='flex-grow: 1; height: 4px; margin: 0 5px; {line_style}'></div>
                <div style='text-align: center; width: 60px;'>{grid_tower_svg}<div style='font-size: 11px; font-weight: bold; color:#555;'>Grid</div></div>
            </div>
            <div style='text-align: center; margin-top: 12px; font-weight: bold; font-size: 13px; color: {status_color};'>{status_text}</div>
        </div>
        """
        st.markdown(solar_animation_html, unsafe_allow_html=True)

    # --- कार्ड १: स्थितीदर्शक बोर्ड ---
    status_card = st.empty()

    # --- कार्ड २: कंट्रोल पॅनल (पंप) ---
    with st.container(border=True):
        st.markdown("<div style='background-color: #ffe0b2; padding: 10px; border-radius: 6px; margin-bottom: 15px; text-align: center;'><h5 style='margin: 0; color: #e65100; font-weight: bold;'>⚡ कंट्रोल पॅनल (पंप)</h5></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: ug_pump = st.toggle("UG Pump", value=False); draw_ammeter(ug_pump)
        with c2: bw1_pump = st.toggle("Borewell 1", value=False); draw_ammeter(bw1_pump)
        with c3: bw2_pump = st.toggle("Borewell 2", value=False); draw_ammeter(bw2_pump)

    # --- कार्ड ३: वाल्व्ह (कॉक) ---
    with st.container(border=True):
        st.markdown("<div style='background-color: #c8e6c9; padding: 10px; border-radius: 6px; margin-bottom: 15px; text-align: center;'><h5 style='margin: 0; color: #2e7d32; font-weight: bold;'>🎛️ वाल्व्ह (कॉक)</h5></div>", unsafe_allow_html=True)
        v1, v2, v3 = st.columns(3)
        with v1: valve_t1 = st.toggle("V1 (Tank 1)", value=False); draw_knob(valve_t1)
        with v2: valve_t2 = st.toggle("V2 (Tank 2)", value=False); draw_knob(valve_t2)
        with v3: valve_ug = st.toggle("V3 (UG Tank)", value=False); draw_knob(valve_ug)

    # --- 🧠 प्रगत स्मार्ट लॉजिक ---
    any_pump_on = ug_pump or bw1_pump or bw2_pump
    any_borewell_on = bw1_pump or bw2_pump
    
    tank1_pouring = valve_t1 and any_pump_on
    tank2_pouring = valve_t2 and any_pump_on
    ug_pouring_from_bw = valve_ug and any_borewell_on
    ug_pouring_from_tanker = sim_tanker
    garden_watering = ug_pump and not valve_t1 and not valve_t2

    # --- स्थितीदर्शक बोर्ड अपडेट ---
    with status_card.container(border=True):
        st.markdown("<div style='background-color: #e3f2fd; padding: 10px; border-radius: 6px; margin-bottom: 10px; text-align: center;'><h5 style='margin: 0; color: #1565c0; font-weight: bold;'>📋 स्थितीदर्शक</h5></div>", unsafe_allow_html=True)
        status_msgs = []
        
        if not any_pump_on and not sim_tanker: status_msgs.append("⚠️ सर्व पंप बंद आहेत.")
        else:
            if ug_pump: status_msgs.append("🔸 अंडरग्राउंड पंप सुरू आहे.")
            if bw1_pump: status_msgs.append("🔸 बोअरवेल १ सुरू आहे.")
            if bw2_pump: status_msgs.append("🔸 बोअरवेल २ सुरू आहे.")
            if sim_tanker: status_msgs.append("🚚 टँकरद्वारे पाणी येत आहे.")
        
        if tank1_pouring: status_msgs.append("🔹 'Tank 1' मध्ये पाणी भरत आहे.")
        if tank2_pouring: status_msgs.append("🔹 'Tank 2' मध्ये पाणी भरत आहे.")
        if ug_pouring_from_bw: status_msgs.append("🔹 बोअरवेलचे पाणी 'UG Tank' मध्ये जात आहे.")
        if garden_watering: status_msgs.append("🌿 पाणी 'गार्डन/झाडांना' दिले जात आहे.")
        if (valve_t1 or valve_t2) and not any_pump_on: status_msgs.append("⚠️ वाल्व्ह उघडा आहे, पण पंप बंद आहे.")

        status_html = "".join([f"<li style='margin-bottom: 5px;'>{msg}</li>" for msg in status_msgs])
        st.markdown(f"<ul style='font-size: 14px; color: #333; font-weight: 600; padding-left: 20px; margin-bottom: 0;'>{status_html}</ul>", unsafe_allow_html=True)

with col_left:
    # --- टाक्या आणि लाटा ---
    t1_col, t2_col = st.columns(2)
    with t1_col: draw_tank("Tank 1", tank1_lvl, tank_type="overhead", inlets=[{"name": "Main Line", "active": tank1_pouring}])
    with t2_col: draw_tank("Tank 2", tank2_lvl, tank_type="overhead", inlets=[{"name": "Main Line", "active": tank2_pouring}])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    ug_inlets = [{"name": "Borewell (V3)", "active": ug_pouring_from_bw}, {"name": "Tanker", "active": ug_pouring_from_tanker}]
    draw_tank("Underground Tank", ug_lvl, tank_type="underground", inlets=ug_inlets)

    # --- 🌳 गार्डन व्हिज्युअल ---
    garden_active_html = ""
    if garden_watering:
        garden_active_html = "<div style='position: absolute; top: -30px; left: 50%; transform: translateX(-50%); width: 8px; height: 40px; background-image: repeating-linear-gradient(transparent, #00b4d8 2px, transparent 6px); background-size: 100% 10px; animation: waterPour 0.3s infinite linear;'></div>"
        
    st.markdown(f"""
    <div style='margin-top: 20px; border: 3px solid #2e7d32; border-radius: 12px; background: #e8f5e9; padding: 15px; text-align: center; position: relative;'>
        {garden_active_html}
        <div style='font-size: 40px;'>🌳🏡🌿</div>
        <h4 style='color: #2e7d32; margin: 5px 0 0 0;'>गार्डन / झाडे</h4>
        <p style='font-size: 12px; color: #555; margin: 0;'>अंडरग्राउंड टाकीतून पाणी</p>
    </div>
    """, unsafe_allow_html=True)
