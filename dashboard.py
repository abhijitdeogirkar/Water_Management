# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import time
import hashlib
import requests
import ephem
import math
import base64
from datetime import datetime, timedelta

# 'wide' लेआउट आणि कॉम्पॅक्ट UI साठी पेज कॉन्फिगरेशन
st.set_page_config(page_title="Abhiprajameyarnav Smart Home", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------
# 📸 फोटो बेस-६४ मध्ये बदलण्याचे फंक्शन
# ---------------------------------------------------------
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# ---------------------------------------------------------
# 🕉️ संपूर्ण पंचांग आणि (पासून - पर्यंत) वेळा
# ---------------------------------------------------------
def get_panchang_details(selected_date):
    observer = ephem.Observer()
    observer.lat, observer.lon, observer.elevation = '20.1059', '77.1358', 414 # Washim
    
    local_dt = datetime.combine(selected_date, datetime.min.time())
    utc_dt = local_dt - timedelta(hours=5, minutes=30)
    observer.date = utc_dt
    
    try: sunrise = observer.next_rising(ephem.Sun())
    except: sunrise = ephem.Date(utc_dt + timedelta(hours=6))
    
    def calc_tithi(t):
        s = math.degrees(ephem.Ecliptic(ephem.Sun(t)).lon)
        m = math.degrees(ephem.Ecliptic(ephem.Moon(t)).lon)
        return int(((m - s) % 360) / 12) + 1
    def calc_nakshatra(t):
        m = math.degrees(ephem.Ecliptic(ephem.Moon(t)).lon)
        return int(((m - 24.11) % 360) / 13.333333)
    def calc_yoga(t):
        s = math.degrees(ephem.Ecliptic(ephem.Sun(t)).lon)
        m = math.degrees(ephem.Ecliptic(ephem.Moon(t)).lon)
        return int((((s - 24.11) + (m - 24.11)) % 360) / 13.333333)
    def calc_karana(t):
        s = math.degrees(ephem.Ecliptic(ephem.Sun(t)).lon)
        m = math.degrees(ephem.Ecliptic(ephem.Moon(t)).lon)
        return int(((m - s) % 360) / 6)

    cur_tithi = calc_tithi(sunrise)
    cur_nak = calc_nakshatra(sunrise)
    cur_yoga = calc_yoga(sunrise)
    cur_kar = calc_karana(sunrise)
    
    def find_start(t_ref, cur_val, func):
        t = t_ref
        for _ in range(120):
            t -= ephem.hour / 2
            if func(t) != cur_val:
                for _ in range(35):
                    t += ephem.minute
                    if func(t) == cur_val:
                        dt = ephem.Date(t).datetime() + timedelta(hours=5, minutes=30)
                        return dt.strftime("%d %b, %I:%M %p")
        return "-"

    def find_end(t_ref, cur_val, func):
        t = t_ref
        for _ in range(120):
            t += ephem.hour / 2
            if func(t) != cur_val:
                for _ in range(35):
                    t -= ephem.minute
                    if func(t) == cur_val:
                        dt = ephem.Date(t).datetime() + timedelta(hours=5, minutes=30)
                        return dt.strftime("%d %b, %I:%M %p")
        return "-"

    tithi_names = ["", "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी", "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "पौर्णिमा", "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी", "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "अमावस्या"]
    nakshatra_names = ["अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशीर्ष", "आर्द्रा", "पुनर्वसू", "पुष्य", "आश्लेषा", "मघा", "पूर्वा फाल्गुनी", "उत्तरा फाल्गुनी", "हस्त", "चित्रा", "स्वाती", "विशाखा", "अनुराधा", "ज्येष्ठा", "मूळ", "पूर्वाषाढा", "उत्तराषाढा", "श्रवण", "धनिष्ठा", "शततारका", "पूर्वा भाद्रपदा", "उत्तरा भाद्रपदा", "रेवती"]
    yoga_names = ["विष्कंभ", "प्रीती", "आयुष्मान", "सौभाग्य", "शोभन", "अतिगंड", "सुकर्मा", "धृती", "शूल", "गंड", "वृद्धी", "ध्रुव", "व्याघात", "हर्षण", "वज्र", "सिद्धी", "व्यतीपात", "वरीयान", "परिघ", "शिव", "सिद्ध", "साध्य", "शुभ", "शुक्ल", "ब्रह्म", "ऐंद्र", "वैधृती"]
    
    if cur_kar == 0: k_name = "किंस्तुघ्न"
    elif cur_kar == 57: k_name = "शकुनी"
    elif cur_kar == 58: k_name = "चतुष्पाद"
    elif cur_kar == 59: k_name = "नाग"
    else: k_name = ["बव", "बालव", "कौलव", "तैतिल", "गर", "वणिज", "विष्टी (भद्रा)"][(cur_kar - 1) % 7]

    paksha = "शुक्ल पक्ष" if cur_tithi <= 15 else "कृष्ण पक्ष"
    
    return {
        "tithi": f"{paksha} {tithi_names[cur_tithi]}",
        "t_start": find_start(sunrise, cur_tithi, calc_tithi),
        "t_end": find_end(sunrise, cur_tithi, calc_tithi),
        "nakshatra": nakshatra_names[cur_nak % 27],
        "n_start": find_start(sunrise, cur_nak, calc_nakshatra),
        "n_end": find_end(sunrise, cur_nak, calc_nakshatra),
        "yoga": yoga_names[cur_yoga % 27],
        "y_start": find_start(sunrise, cur_yoga, calc_yoga),
        "y_end": find_end(sunrise, cur_yoga, calc_yoga),
        "karana": k_name,
        "k_start": find_start(sunrise, cur_kar, calc_karana),
        "k_end": find_end(sunrise, cur_kar, calc_karana),
        "is_chaturthi": cur_tithi in [4, 19],
        "is_ekadashi": cur_tithi in [11, 26]
    }

# ---------------------------------------------------------
# 🔐 १. Solarman API 
# ---------------------------------------------------------
def get_solarman_token():
    try:
        app_id, app_secret, email, raw_pwd = st.secrets["sofar"]["app_id"], st.secrets["sofar"]["app_secret"], st.secrets["sofar"]["email"], st.secrets["sofar"]["password"]
        hashed_pwd = hashlib.sha256(raw_pwd.encode('utf-8')).hexdigest().lower()
        url = f"https://globalapi.solarmanpv.com/account/v1.0/token?appId={app_id}&language=en"
        res = requests.post(url, json={"appSecret": app_secret, "email": email, "password": hashed_pwd}, timeout=10).json()
        if res.get("success"): return res.get("access_token")
        else: return None
    except: return None

def fetch_live_solar_data():
    token = get_solarman_token()
    if not token: return None
    try:
        app_id = st.secrets["sofar"]["app_id"]
        headers = {"Authorization": f"bearer {token}"}
        
        url_list = f"https://globalapi.solarmanpv.com/station/v1.0/list?appId={app_id}&language=en"
        res_list = requests.post(url_list, headers=headers, json={"page": 1, "size": 10}, timeout=10).json()
        if not res_list.get("success") or not res_list.get("stationList"): return None
            
        station_info = res_list["stationList"][0]
        station_id = station_info["id"]
        
        network_status = station_info.get("networkStatus", "UNKNOWN")
        daily_energy = float(station_info.get("generationToday", station_info.get("dailyEnergy", station_info.get("todayGeneration", station_info.get("todayEnergy", station_info.get("dailyGeneration", 0.0))))))
        
        url_realtime = f"https://globalapi.solarmanpv.com/station/v1.0/realTime?appId={app_id}&language=en"
        live_data = requests.post(url_realtime, headers=headers, json={"stationId": station_id}, timeout=10).json()
        
        history_data = {}
        try:
            today_str = datetime.now().strftime('%Y-%m-%d')
            hist_url = f"https://globalapi.solarmanpv.com/station/v1.0/history?appId={app_id}&language=en"
            r_day = requests.post(hist_url, headers=headers, json={"stationId": station_id, "timeType": 1, "startTime": today_str, "endTime": today_str}, timeout=10).json()
            r_month = requests.post(hist_url, headers=headers, json={"stationId": station_id, "timeType": 2, "startTime": today_str, "endTime": today_str}, timeout=10).json()
            r_year = requests.post(hist_url, headers=headers, json={"stationId": station_id, "timeType": 3, "startTime": today_str, "endTime": today_str}, timeout=10).json()
            r_total = requests.post(hist_url, headers=headers, json={"stationId": station_id, "timeType": 4, "startTime": today_str, "endTime": today_str}, timeout=10).json()
            
            def extract_vals(res):
                if isinstance(res, dict):
                    for k, v in res.items():
                        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                            return [float(i.get('value', i.get('generation', i.get('power', 0))) or 0.0) for i in v]
                return []
            history_data['day'] = extract_vals(r_day)
            history_data['month'] = extract_vals(r_month)
            history_data['year'] = extract_vals(r_year)
            history_data['total'] = extract_vals(r_total)
        except: pass
        
        if live_data.get("success"):
            live_data["custom_daily_energy"] = daily_energy 
            live_data["network_status"] = network_status 
            live_data["history"] = history_data
            return live_data
        else: return None
    except: return None

# ---------------------------------------------------------
# ३. 🌟 UI/UX प्रीमियम CSS (अल्ट्रा-कॉम्पॅक्ट)
# ---------------------------------------------------------
css = """
<style>
/* Global Layout Adjustments */
.stApp { background-color: #f0f2f6; }
.block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }

/* Custom Cards */
div[data-testid="stVerticalBlock"] > div[style*="border"] {
    border: 1px solid #e0e6ed !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03) !important;
    background-color: #ffffff !important;
    padding: 1rem !important;
    margin-bottom: 0.5rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
    box-shadow: 0 4px 15px rgba(0,0,0,0.06) !important;
}

/* UI Grid for Solar Report */
.report-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 8px;
    margin-top: 10px;
}
.metric-box {
    background: #f8f9fa;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    border: 1px solid #e9ecef;
}
.metric-title { font-size: 10px; font-weight: 700; color: #7f8c8d; text-transform: uppercase; margin-bottom: 4px; }
.metric-val { font-size: 16px; font-weight: 900; color: #2c3e50; }

/* Animations */
@keyframes waterPour { 0% { background-position: 0 0px; } 100% { background-position: 0 16px; } }
@keyframes waveMove { 0% { background-position-x: 0px; } 100% { background-position-x: 40px; } }
@keyframes sunGlow { 0% { box-shadow: 0 0 8px rgba(251, 192, 45, 0.3); } 50% { box-shadow: 0 0 15px rgba(251, 192, 45, 0.6); } 100% { box-shadow: 0 0 8px rgba(251, 192, 45, 0.3); } }
@keyframes energyFlow { 0% { background-position: 0px 0; } 100% { background-position: 20px 0; } }

/* Banners */
.normal-banner { 
    text-align: center; background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); 
    padding: 15px; border-radius: 12px; margin-bottom: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
}
.panchang-strip { 
    background: #fff; border-radius: 8px; padding: 8px 15px; border-left: 5px solid #fbc02d; 
    margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 6px rgba(0,0,0,0.05); 
}
.stButton > button { border-radius: 8px !important; font-weight: 600 !important; border: 1px solid #d1d9e6 !important; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

top_banner = st.empty()
panchang_banner = st.empty()

# ---------------------------------------------------------
# ४. स्टेट्स
# ---------------------------------------------------------
for key in ['ug_pump', 'bw1_pump', 'bw2_pump', 'valve_t1', 'valve_t2', 'valve_ug', 'is_solar_live']:
    if key not in st.session_state: st.session_state[key] = False
for key, default in [('alarm_armed', False), ('real_solar_power', 0.0), ('real_solar_total', 0.0), ('real_solar_daily', 0.0), ('inverter_status', "PENDING"), ('chart_day', [0]*10), ('chart_month', [0]*12), ('chart_year', [0]*5), ('chart_total', [0]*10)]:
    if key not in st.session_state: st.session_state[key] = default

def set_pump_state(key, state): st.session_state[key] = state

# ---------------------------------------------------------
# ⚙️ ५. साईडबार 
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h4 style='color:#2c3e50; font-weight:700;'>⚙️ कंट्रोल्स</h4>", unsafe_allow_html=True)
    sim_tanker = st.checkbox("🚚 टँकर सुरू करा")
    simulate_motion = st.checkbox("🚶 मोशन अलार्म टेस्ट")
    
    if st.button("🔄 लाईव्ह डेटा रिफ्रेश करा", type="primary", use_container_width=True):
        with st.spinner("इन्व्हर्टर सिंक करत आहे..."):
            data = fetch_live_solar_data()
            if data:
                p_watts = float(data.get("generationPower", 0))
                st.session_state.real_solar_power = p_watts / 1000.0 if p_watts > 10 else p_watts
                st.session_state.real_solar_total = float(data.get("generationTotal", 0))
                st.session_state.real_solar_daily = float(data.get("custom_daily_energy", 0.0))
                st.session_state.inverter_status = data.get("network_status", "UNKNOWN")
                
                hist = data.get("history", {})
                for k in ['day', 'month', 'year', 'total']:
                    if hist.get(k): st.session_state[f"chart_{k}"] = hist[k]
                
                st.session_state.is_solar_live = True
                if "OFFLINE" in st.session_state.inverter_status: st.warning("🌙 इन्व्हर्टर ऑफलाईन आहे.")
                else: st.success("✅ डेटा सिंक यशस्वी!")

# ---------------------------------------------------------
# ६. UI/UX: टाक्यांचे डिझाईन
# ---------------------------------------------------------
def get_tank_html(tank_name, level_cm, tank_type="overhead", inlets=[]):
    percentage = min(int((level_cm / 100) * 100), 100)
    water_grad = "linear-gradient(to bottom, #4facfe 0%, #00f2fe 100%)" if tank_type == "overhead" else "linear-gradient(to bottom, #0077b6 0%, #023e8a 100%)"
    dark_wave = "%23005b96" if tank_type == "overhead" else "%23023e8a" 
    tank_height, tank_width = ("140px", "100%") if tank_type == "underground" else ("180px", "100%")
    border_rad = "0 0 12px 12px" if tank_type == "overhead" else "8px"
    tank_border = "border: 3px solid #b0bec5; border-top: none;" if tank_type == "overhead" else "border: 3px solid #90a4ae;"

    is_pouring = any(inlet['active'] for inlet in inlets)
    wave_html = f"<div style='position: absolute; top: -6px; left: 0; width: 100%; height: 10px; background: url(\"data:image/svg+xml;utf8,<svg viewBox=\\\"0 0 40 12\\\" xmlns=\\\"http://www.w3.org/2000/svg\\\"><path d=\\\"M0 6 Q 10 12, 20 6 T 40 6 L 40 12 L 0 12 Z\\\" fill=\\\"{dark_wave}\\\"/></svg>\") repeat-x; background-size: 30px 10px; animation: waveMove 1.5s linear infinite; z-index: 10; opacity: 0.8;'></div>" if is_pouring else f"<div style='position: absolute; top: 0; left: 0; width: 100%; height: 4px; background-color: {dark_wave.replace('%23','#')}; border-top: 1px solid rgba(255,255,255,0.5); z-index: 10;'></div>"

    pipes_html = ""
    for idx, inlet in enumerate(inlets):
        offset = 50 if len(inlets) == 1 else (35 if idx == 0 else 65)
        active_pour = f"<div style='position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 8px; height: {tank_height}; background-image: repeating-linear-gradient(transparent, #4facfe 3px, transparent 6px); background-size: 100% 12px; animation: waterPour 0.2s infinite linear; z-index: 1;'></div>" if inlet['active'] else ""
        pipes_html += f"<div style='position: absolute; bottom: 100%; left: {offset}%; transform: translateX(-50%); text-align: center;'><div style='font-size: 10px; font-weight: 700; color: #546e7a; margin-bottom: 2px; white-space: nowrap;'>{inlet['name']}</div><div style='width: 24px; height: 10px; background-color: #78909c; border-radius: 3px 3px 0 0; margin: 0 auto;'></div><div style='width: 10px; height: 20px; background: linear-gradient(to right, #cfd8dc, #eceff1, #cfd8dc); margin: 0 auto; position: relative; z-index: 3;'>{active_pour}</div></div>"

    html = f"""<div style='margin-top: 35px; display: flex; flex-direction: column; align-items: center; width: 100%;'>
        <div style='width: {tank_width}; max-width: 220px; height: {tank_height}; {tank_border} position: relative; background-color: rgba(236, 240, 241, 0.4); border-radius: {border_rad}; overflow: visible;'>
            {pipes_html}
            <div style='position: absolute; bottom: 0; width: 100%; height: {percentage}%; background: {water_grad}; transition: height 1s ease-in-out; display: flex; align-items: center; justify-content: center; border-radius: {border_rad}; z-index: 2;'>
                {wave_html}
                <span style='color: white; font-weight: 800; font-size: 20px; text-shadow: 0px 1px 3px rgba(0,0,0,0.5); z-index: 11;'>{percentage}%</span>
            </div>
        </div>
        <div style='margin-top: 10px; font-weight: 700; font-size: 12px; color: #2c3e50; text-transform: uppercase;'>{tank_name}</div>
    </div>"""
    return html

# ७. UI/UX: मॉडर्न स्टार्टर 
def render_compact_starter(col_obj, pump_name, state_key):
    is_on = st.session_state[state_key]
    on_glow = "background: #00e676; box-shadow: 0 0 8px #00e676; color: #1b5e20;" if is_on else "background: #37474f; color: #78909c;"
    off_glow = "background: #ff5252; box-shadow: 0 0 8px #ff5252; color: #b71c1c;" if not is_on else "background: #37474f; color: #78909c;"

    html = f"""<div style="background: linear-gradient(145deg, #263238, #37474f); padding: 8px; border-radius: 10px; text-align: center; box-shadow: inset 0 2px 4px rgba(255,255,255,0.1);">
<div style="color: #cfd8dc; font-weight: 700; font-size: 10px; margin-bottom: 8px;">{pump_name}</div>
<div style="display: flex; justify-content: space-evenly; align-items: center; margin-bottom: 5px;">
<div style="width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 7px; {on_glow}">ON</div>
<div style="width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 7px; {off_glow}">OFF</div>
</div></div>"""
    col_obj.markdown(html, unsafe_allow_html=True)
    bc1, bc2 = col_obj.columns(2)
    bc1.button("ON", key=f"btn_on_{state_key}", on_click=set_pump_state, args=(state_key, True), use_container_width=True)
    bc2.button("OFF", key=f"btn_off_{state_key}", on_click=set_pump_state, args=(state_key, False), use_container_width=True)

# 🎛️ ८. UI/UX: ॲनिमेटेड वाल्व्ह
def render_animated_valve(col_obj, valve_name, state_key):
    is_on = st.session_state[state_key]
    handle_rot = 90 if is_on else 0 
    handle_color = "#00c853" if is_on else "#d50000"
    html = f"""<div style="text-align: center;">
<div style="font-size: 10px; font-weight: 700; color: #546e7a; margin-bottom: 4px;">{valve_name}</div>
<svg width="40" height="60" viewBox="0 0 60 90">
<rect x="22" y="0" width="16" height="90" fill="#b0bec5" />
<polygon points="15,25 45,25 50,45 45,65 15,65 10,45" fill="#eceff1" stroke="#90a4ae" stroke-width="1.5"/>
<g transform="rotate({handle_rot} 30 45)" style="transition: transform 0.4s ease;"><path d="M 35 40 L 5 40 C 2 40 0 42 0 45 C 0 48 2 50 5 50 L 35 50 Z" fill="{handle_color}" /><circle cx="30" cy="45" r="7" fill="#ffffff"/><circle cx="30" cy="45" r="3" fill="#546e7a" /></g>
</svg></div>"""
    col_obj.markdown(html, unsafe_allow_html=True)
    col_obj.toggle("T", key=state_key, label_visibility="collapsed")

# ---------------------------------------------------------
# 🧠 ९. मुख्य लॉजिक
# ---------------------------------------------------------
trigger_siren = st.session_state.alarm_armed and simulate_motion
ug_pump, bw1_pump, bw2_pump = st.session_state['ug_pump'], st.session_state['bw1_pump'], st.session_state['bw2_pump']
valve_t1, valve_t2, valve_ug = st.session_state['valve_t1'], st.session_state['valve_t2'], st.session_state['valve_ug']

any_pump_on = ug_pump or bw1_pump or bw2_pump
tank1_pouring = valve_t1 and any_pump_on
tank2_pouring = valve_t2 and any_pump_on
ug_pouring_from_bw = valve_ug and (bw1_pump or bw2_pump)
ug_pouring_from_tanker = sim_tanker
garden_watering = ug_pump and not valve_t1 and not valve_t2
is_any_water_pouring = tank1_pouring or tank2_pouring or ug_pouring_from_bw or ug_pouring_from_tanker or garden_watering

# १०. मुख्य डॅशबोर्ड लेआउट (Compact)
col_left, col_right = st.columns([1.2, 1], gap="medium")

with col_right:
    status_board = st.empty()

    # 🛡️ सुरक्षा
    with st.container(border=True):
        st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'><h5 style='margin:0; color:#c2185b; font-weight:800; font-size:14px;'>🛡️ अलार्म सिस्टीम</h5></div>", unsafe_allow_html=True)
        st.session_state.alarm_armed = st.toggle("Arm / Disarm", value=st.session_state.alarm_armed)

    # ☀️ सोलर ऊर्जा (Premium UI + Exact Running Days Grid)
    with st.container(border=True):
        cp = st.session_state.real_solar_power
        dk = st.session_state.real_solar_daily
        is_gen = cp > 0
        is_off = "OFFLINE" in st.session_state.inverter_status
        
        d_pow = f"{cp:.2f} kW"
        d_day = f"{int(dk * 1000)} Wh" if dk < 1.0 else f"{dk:.2f} kWh"

        if not st.session_state.is_solar_live:
            glow, line, s_col, s_txt, badge = "border: 1px solid #e0e0e0;", "background: #cfd8dc;", "#78909c", "🔄 सिंक करा", "<span style='background:#9e9e9e; color:white; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700;'>PENDING</span>"
        elif is_off:
            glow, line, s_col, s_txt, badge = "border: 1px solid #cfd8dc; background: #fafafa;", "background: #cfd8dc;", "#78909c", "🌙 स्लीप मोड", "<span style='background:#78909c; color:white; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700;'>OFFLINE</span>"
        else:
            glow = "animation: sunGlow 3s infinite; border: 1px solid #fbc02d;" if is_gen else "border: 1px solid #e0e0e0;"
            line = "background-image: repeating-linear-gradient(90deg, #4caf50 0px, #4caf50 10px, transparent 10px, transparent 20px); background-size: 20px 100%; animation: energyFlow 0.5s linear infinite;" if is_gen else "background: #cfd8dc;"
            s_col, s_txt = ("#2e7d32", "🟢 निर्मिती सुरू") if is_gen else ("#c62828", "🔴 निर्मिती 0 W")
            badge = "<span style='background:#4CAF50; color:white; padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700;'>LIVE</span>"

        s_svg = """<svg width="30" height="30" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="12" fill="#FFca28"/><polyline points="75,90 85,90 80,40" fill="none" stroke="#90a4ae" stroke-width="4"/><polygon points="35,85 45,35 85,30 70,80" fill="#1976d2" stroke="#e3f2fd" stroke-width="2"/></svg>"""
        g_svg = """<svg width="25" height="25" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><polyline points="50,10 30,90" fill="none" stroke="#546e7a" stroke-width="3"/><polyline points="50,10 70,90" fill="none" stroke="#546e7a" stroke-width="3"/><line x1="45" y1="30" x2="55" y2="30" stroke="#546e7a" stroke-width="3"/><line x1="40" y1="50" x2="60" y2="50" stroke="#546e7a" stroke-width="3"/><line x1="35" y1="70" x2="65" y2="70" stroke="#546e7a" stroke-width="3"/><line x1="20" y1="50" x2="80" y2="50" stroke="#546e7a" stroke-width="3"/></svg>"""

        st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;'><h5 style='margin:0; color:#f57f17; font-weight:800; font-size:14px;'>☀️ सोलर ऊर्जा</h5>{badge}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<div style='display: flex; justify-content: space-around; background: #fffde7; border-radius: 8px; padding: 10px 0; margin-bottom: 10px; {glow}'><div style='text-align: center;'><div style='font-size: 10px; color: #7f8c8d; font-weight:700;'>सध्याची निर्मिती</div><div style='font-size: 20px; font-weight: 900; color: #2e7d32;'>{d_pow}</div></div><div style='width: 1px; background: #e0e0e0;'></div><div style='text-align: center;'><div style='font-size: 10px; color: #7f8c8d; font-weight:700;'>आजची निर्मिती</div><div style='font-size: 20px; font-weight: 900; color: #1565c0;'>{d_day}</div></div></div>", unsafe_allow_html=True)
        
        st.markdown(f"<div style='display: flex; align-items: center; justify-content: space-between; padding: 5px; border-radius: 8px; border: 1px solid #ecf0f1; background: #fafafa;'><div style='text-align: center; width: 40px;'>{s_svg}</div><div style='flex-grow: 1; height: 3px; margin: 0 5px; border-radius:3px; {line}'></div><div style='text-align: center; width: 30px;'><div style='font-size: 18px;'>🎛️</div></div><div style='flex-grow: 1; height: 3px; margin: 0 5px; border-radius:3px; {line}'></div><div style='text-align: center; width: 40px;'>{g_svg}</div></div>", unsafe_allow_html=True)
        
        # UI/UX: Compact Popup
        sc1, sc2 = st.columns([3, 2], vertical_alignment="center")
        with sc1: st.markdown(f"<div style='font-weight: 700; font-size: 11px; color: {s_col}; margin-top:5px;'>{s_txt}</div>", unsafe_allow_html=True)
        with sc2:
            with st.popover("📊 रिपोर्ट", use_container_width=True):
                st.markdown("<h6 style='color: #6a1b9a; font-weight: 800; text-align:center;'>📊 अहवाल</h6>", unsafe_allow_html=True)
                t_day, t_mon, t_yr, t_tot = st.tabs(["Day", "Month", "Year", "Total"])
                with t_day: st.line_chart(st.session_state.chart_day, height=150) 
                with t_mon: st.bar_chart(st.session_state.chart_month, height=150)
                with t_yr: st.bar_chart(st.session_state.chart_year, height=150)
                with t_tot: st.line_chart(st.session_state.chart_total, height=150)

                # ✨ Exact Running Days Logic (from 21 July 2024 timestamp 1721561718)
                t_kwh = st.session_state.real_solar_total
                start_date = datetime.fromtimestamp(1721561718)
                run_days = (datetime.now() - start_date).days if st.session_state.is_solar_live else 618

                st.markdown(f"""
                <div class='report-grid'>
                    <div class='metric-box'><div class='metric-title'>🕐 एकूण दिवस</div><div class='metric-val'>{run_days}</div></div>
                    <div class='metric-box'><div class='metric-title'>⚡ एकूण (MWh)</div><div class='metric-val'>{t_kwh/1000.0:.2f}</div></div>
                    <div class='metric-box'><div class='metric-title'>💰 नफा (INR)</div><div class='metric-val' style='color:#27ae60;'>₹{int(t_kwh*7.5):,}</div></div>
                    <div class='metric-box'><div class='metric-title'>☁️ CO2 (t)</div><div class='metric-val' style='color:#2980b9;'>{0.000793*t_kwh:.2f}</div></div>
                    <div class='metric-box'><div class='metric-title'>🍃 झाडे</div><div class='metric-val' style='color:#16a085;'>{int((t_kwh*0.997)/18.3)}</div></div>
                </div>
                """, unsafe_allow_html=True)

    # ⚡ पंप आणि वाल्व्ह (Compact CSS)
    with st.container(border=True):
        st.markdown("<h5 style='margin: 0 0 10px 0; color: #2c3e50; font-weight: 800; font-size:14px;'>⚡ पंप आणि वाल्व्ह</h5>", unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        render_compact_starter(sc1, "UG PUMP", "ug_pump")
        render_compact_starter(sc2, "BW-1", "bw1_pump")
        render_compact_starter(sc3, "BW-2", "bw2_pump")
        st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
        v1, v2, v3 = st.columns(3)
        with v1: render_animated_valve(v1, "T-1", "valve_t1")
        with v2: render_animated_valve(v2, "T-2", "valve_t2")
        with v3: render_animated_valve(v3, "UG", "valve_ug")

    # 📋 स्थितीदर्शक 
    with status_board.container(border=True):
        st.markdown("<h5 style='margin: 0 0 8px 0; color: #1565c0; font-weight: 800; font-size:13px;'>📋 स्थिती</h5>", unsafe_allow_html=True)
        s_msgs = ["🚨 घुसखोर आढळला!"] if trigger_siren else []
        if not any_pump_on and not sim_tanker: s_msgs.append("सर्व पंप बंद आहेत.")
        else:
            if ug_pump: s_msgs.append("UG पंप सुरू.")
            if bw1_pump: s_msgs.append("बोअरवेल १ सुरू.")
            if bw2_pump: s_msgs.append("बोअरवेल २ सुरू.")
            if sim_tanker: s_msgs.append("टँकर सुरू.")
        if tank1_pouring: s_msgs.append("Tank 1 भरत आहे.")
        if tank2_pouring: s_msgs.append("Tank 2 भरत आहे.")
        if ug_pouring_from_bw: s_msgs.append("BW -> UG Tank.")
        if garden_watering: s_msgs.append("गार्डन पाणी सुरू.")
        
        html_li = "".join([f"<li style='margin-bottom: 2px;'>{m}</li>" for m in s_msgs])
        st.markdown(f"<ul style='font-size: 11px; color: #455a64; font-weight: 600; padding-left: 15px; margin:0;'>{html_li}</ul>", unsafe_allow_html=True)

with col_left:
    # 🌟 टाक्यांचे डिझाईन (Flex Layout)
    html_t1 = get_tank_html("Tank 1", 45, "overhead", [{"name": "Main", "active": tank1_pouring}])
    html_t2 = get_tank_html("Tank 2", 60, "overhead", [{"name": "Main", "active": tank2_pouring}])
    html_ug = get_tank_html("Underground", 75, "underground", [{"name": "Borewell", "active": ug_pouring_from_bw}, {"name": "Tanker", "active": ug_pouring_from_tanker}])

    st.markdown(f"""
    <div style="display: flex; justify-content: space-around; width: 100%; gap: 10px;">
        <div style="flex: 1; display: flex; justify-content: center;">{html_t1}</div>
        <div style="flex: 1; display: flex; justify-content: center;">{html_t2}</div>
    </div>
    <div style="width: 100%; display: flex; justify-content: center;">{html_ug}</div>
    """, unsafe_allow_html=True)

    g_act = "<div style='position: absolute; top: -20px; left: 50%; transform: translateX(-50%); width: 6px; height: 30px; background-image: repeating-linear-gradient(transparent, #4facfe 2px, transparent 4px); background-size: 100% 6px; animation: waterPour 0.3s infinite linear;'></div>" if garden_watering else ""
    st.markdown(f"<div style='margin-top: 15px; border: 1px solid #a5d6a7; border-radius: 12px; background: #f1f8e9; padding: 10px; text-align: center; position: relative;'>{g_act}<div style='font-size: 30px;'>🌳🏡🌿</div><h6 style='color: #2e7d32; margin: 5px 0 0 0; font-weight:800;'>गार्डन / झाडे</h6></div>", unsafe_allow_html=True)
    
    # 📹 सुरक्षा कॅमेरे (Compact)
    st.markdown("<h5 style='color: #2c3e50; text-align: center; font-weight:800; margin-top:20px;'>📹 CCTV</h5>", unsafe_allow_html=True)
    c_style = "background: #111; height: 160px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #555; font-size:12px; font-family: monospace; border: 3px solid #333; position: relative; text-align: center;"
    r_dot = "<div style='position: absolute; top: 10px; right: 10px; width: 8px; height: 8px; background-color: #ff5252; border-radius: 50%; animation: pulseRed 1s infinite;'></div>"
    
    cam1, cam2 = st.columns(2)
    with cam1: st.markdown(f"<div style='{c_style}'>{r_dot}CAM 1 Stream</div><div style='text-align:center; font-weight:700; font-size:11px; margin-top:5px; color:#546e7a;'>📍 मुख्य गेट</div>", unsafe_allow_html=True)
    with cam2: st.markdown(f"<div style='{c_style}'>{r_dot}CAM 2 Stream</div><div style='text-align:center; font-weight:700; font-size:11px; margin-top:5px; color:#546e7a;'>📍 पार्किंग</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📢 ११. सायरन आणि 🕉️ पंचांग 
# ---------------------------------------------------------
if trigger_siren:
    top_banner.markdown("<div class='flashing-alert'><h2 style='color: white; margin: 0; font-weight: 900;'>🚨 सावधान! घुसखोर आढळला! 🚨</h2></div>", unsafe_allow_html=True)
    panchang_banner.empty()
    st.markdown("""<audio autoplay loop><source src="https://upload.wikimedia.org/wikipedia/commons/4/40/Siren_Noise.ogg" type="audio/ogg"></audio>""", unsafe_allow_html=True)
else:
    top_banner.markdown("""
    <div class='normal-banner'>
        <h2 style='color: #ffffff; margin: 0; font-weight: 900; letter-spacing: 1px;'>अभिप्राजामेयार्णव</h2>
        <h6 style='color: #b2ebf2; margin: 2px 0 0 0; font-weight: 600;'>स्मार्ट होम मॅनेजमेंट सिस्टीम</h6>
    </div>
    """, unsafe_allow_html=True)
    
    tdy = datetime.now().date()
    v_nm = ["सोमवार", "मंगळवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
    pan = get_panchang_details(tdy)
    
    f_htm = ""
    if pan["is_chaturthi"]:
        b64 = get_base64_image("ganpati.png")
        f_htm = f"<img src='data:image/png;base64,{b64}' width='25' style='border-radius:50%; margin-right:5px;'> <span style='color:#c62828; font-weight:800; font-size:12px;'>|| श्री गणेशाय नमः ||</span>" if b64 else "<span style='color:#c62828; font-weight:800; font-size:12px;'>🐘 || श्री गणेशाय नमः ||</span>"
    elif pan["is_ekadashi"]:
        b64 = get_base64_image("vitthal.png")
        f_htm = f"<img src='data:image/png;base64,{b64}' width='25' style='border-radius:50%; margin-right:5px;'> <span style='color:#1565c0; font-weight:800; font-size:12px;'>|| राम कृष्ण हरी ||</span>" if b64 else "<span style='color:#1565c0; font-weight:800; font-size:12px;'>🚩 || राम कृष्ण हरी ||</span>"

    with panchang_banner.container():
        p1, p2 = st.columns([5, 1], vertical_alignment="center")
        with p1:
            st.markdown(f"<div class='panchang-strip'><div style='font-size: 13px; color: #455a64; font-weight:700;'><b>{v_nm[tdy.weekday()]}</b> &nbsp;|&nbsp; <b>{pan['tithi']}</b></div><div style='display:flex; align-items:center;'>{f_htm}</div></div>", unsafe_allow_html=True)
        with p2:
            with st.popover("📅 पंचांग", use_container_width=True):
                st.markdown("<h6 style='text-align: center; color: #e67e22; font-weight:800;'>🕉️ पंचांग</h6>", unsafe_allow_html=True)
                sel_d = st.date_input("तारीख:", tdy, label_visibility="collapsed")
                s_pan = pan if sel_d == tdy else get_panchang_details(sel_d)
                
                st.markdown(f"<div style='text-align:center; font-size:12px; font-weight:800; color:#546e7a; margin-bottom: 5px;'>{sel_d.strftime('%d-%m-%Y')} ({v_nm[sel_d.weekday()]})</div>", unsafe_allow_html=True)
                st.markdown(f"""
                <table style="width:100%; border-collapse: collapse; font-size: 11px; background:#fff;">
                  <tr style="background: #f8f9fa; border-bottom: 1px solid #eceff1;">
                    <th style="padding: 4px;">अंग</th><th style="padding: 4px;">नाव</th><th style="padding: 4px;">सुरुवात</th><th style="padding: 4px;">समाप्ती</th>
                  </tr>
                  <tr style="border-bottom: 1px solid #f1f3f4;">
                    <td style="padding: 4px;"><b>🌙 तिथी</b></td><td style="padding: 4px; color:#d35400; font-weight:700;">{s_pan['tithi']}</td><td style="padding: 4px; color:#78909c;">{s_pan['t_start']}</td><td style="padding: 4px; color:#78909c;">{s_pan['t_end']}</td>
                  </tr>
                  <tr style="border-bottom: 1px solid #f1f3f4;">
                    <td style="padding: 4px;"><b>✨ नक्षत्र</b></td><td style="padding: 4px; color:#d35400; font-weight:700;">{s_pan['nakshatra']}</td><td style="padding: 4px; color:#78909c;">{s_pan['n_start']}</td><td style="padding: 4px; color:#78909c;">{s_pan['n_end']}</td>
                  </tr>
                  <tr style="border-bottom: 1px solid #f1f3f4;">
                    <td style="padding: 4px;"><b>🧘 योग</b></td><td style="padding: 4px; color:#d35400; font-weight:700;">{s_pan['yoga']}</td><td style="padding: 4px; color:#78909c;">{s_pan['y_start']}</td><td style="padding: 4px; color:#78909c;">{s_pan['y_end']}</td>
                  </tr>
                  <tr>
                    <td style="padding: 4px;"><b>🚩 करण</b></td><td style="padding: 4px; color:#d35400; font-weight:700;">{s_pan['karana']}</td><td style="padding: 4px; color:#78909c;">{s_pan['k_start']}</td><td style="padding: 4px; color:#78909c;">{s_pan['k_end']}</td>
                  </tr>
                </table>
                """, unsafe_allow_html=True)

if is_any_water_pouring and not trigger_siren:
    st.markdown("""<audio autoplay loop id="wAudio"><source src="https://actions.google.com/sounds/v1/water/stream_water.ogg" type="audio/ogg"></audio><script>document.getElementById("wAudio").volume=0.3;</script>""", unsafe_allow_html=True)

a_spk = ""
if trigger_siren: a_spk = "सावधान! घरात घुसखोर आढळला आहे."
elif (valve_t1 or valve_t2) and not any_pump_on: a_spk = "सावधान! वाल्व्ह उघडा आहे, पण पंप बंद आहे."
elif tank1_pouring and tank2_pouring: a_spk = "टाकी एक आणि दोन भरत आहे."
elif tank1_pouring: a_spk = "टाकी एक भरत आहे."
elif tank2_pouring: a_spk = "टाकी दोन भरत आहे."
elif ug_pouring_from_bw or ug_pouring_from_tanker: a_spk = "अंडरग्राउंड टाकी भरत आहे."
elif garden_watering: a_spk = "गार्डन पाणी सुरू आहे."

if 'l_spk' not in st.session_state: st.session_state.l_spk = ""
if a_spk == "": st.session_state.l_spk = ""
elif a_spk != st.session_state.l_spk:
    st.session_state.l_spk = a_spk
    components.html(f"<script>var m=new SpeechSynthesisUtterance('{a_spk}');m.lang='mr-IN';m.rate=0.95;window.speechSynthesis.speak(m);</script>", height=0, width=0)
