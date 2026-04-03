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

st.set_page_config(page_title="Deogirkar Smart Home", layout="wide")

# =========================================================
# ⚙️ सुरक्षित Google Web App URL (Secrets मधून वाचणे)
# =========================================================
try:
    GOOGLE_WEB_APP_URL = st.secrets["google"]["web_app_url"]
except:
    GOOGLE_WEB_APP_URL = ""
    st.error("⚠️ Google Web App URL सापडली नाही. कृपया GitHub च्या Secrets मध्ये ती जोडल्याची खात्री करा.")

# ---------------------------------------------------------
# 💧 गुगल शीटवरून डेटा आणणे आणि गणिते (TANK 1 साठी)
# ---------------------------------------------------------
def get_tank_distance_from_google():
    if not GOOGLE_WEB_APP_URL:
        return None
    try:
        response = requests.get(GOOGLE_WEB_APP_URL + "?action=read", timeout=5)
        data = response.json()
        if data and 'distance' in data and data['distance'] != "":
            return float(data['distance'])
        return None
    except: return None

def calc_tank1_data(sensor_distance_cm):
    if sensor_distance_cm is None: return 0, 0.0, 0.0
    
    # =========================================================
    # ⚙️ टाकी क्रमांक १ चे डायमेन्शन्स (मापे) येथे बदला! ⚙️
    # =========================================================
    TANK_LENGTH_CM = 200.0    # टाकीची लांबी (cm)
    TANK_WIDTH_CM = 200.0     # टाकीची रुंदी (cm)
    MAX_WATER_HEIGHT = 100.0  # तळापासून ओव्हरफ्लो पाईपपर्यंतची उंची (cm)
    SENSOR_GAP_CM = 25.0      # ओव्हरफ्लो पाईपच्या वर सेन्सर किती अंतरावर आहे? (cm)
    
    base_area = TANK_LENGTH_CM * TANK_WIDTH_CM
    sensor_total_height = MAX_WATER_HEIGHT + SENSOR_GAP_CM
    
    # पाण्याची उंची = सेन्सरची एकूण उंची - सेन्सरने मोजलेले रिकामे अंतर
    water_level_cm = sensor_total_height - sensor_distance_cm
    
    # व्हॅलिडेशन (पाणी उंचीच्या बाहेर जाऊ नये)
    if water_level_cm < 0: water_level_cm = 0
    if water_level_cm > MAX_WATER_HEIGHT: water_level_cm = MAX_WATER_HEIGHT
    
    percentage = int((water_level_cm / MAX_WATER_HEIGHT) * 100)
    liters = (base_area * water_level_cm) / 1000.0
    
    return percentage, liters, water_level_cm

# ---------------------------------------------------------
# 📸 फोटो बेस-६४ मध्ये बदलण्याचे फंक्शन
# ---------------------------------------------------------
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    except: return ""

# ---------------------------------------------------------
# 🕉️ संपूर्ण पंचांग
# ---------------------------------------------------------
def get_panchang_details(selected_date):
    observer = ephem.Observer()
    observer.lat, observer.lon, observer.elevation = '20.1059', '77.1358', 414
    local_dt = datetime.combine(selected_date, datetime.min.time())
    utc_dt = local_dt - timedelta(hours=5, minutes=30)
    observer.date = utc_dt
    try: sunrise = observer.next_rising(ephem.Sun())
    except: sunrise = ephem.Date(utc_dt + timedelta(hours=6))
    
    def calc_tithi(t): s = math.degrees(ephem.Ecliptic(ephem.Sun(t)).lon); m = math.degrees(ephem.Ecliptic(ephem.Moon(t)).lon); return int(((m - s) % 360) / 12) + 1
    def calc_nakshatra(t): m = math.degrees(ephem.Ecliptic(ephem.Moon(t)).lon); return int(((m - 24.11) % 360) / 13.333333)
    def calc_yoga(t): s = math.degrees(ephem.Ecliptic(ephem.Sun(t)).lon); m = math.degrees(ephem.Ecliptic(ephem.Moon(t)).lon); return int((((s - 24.11) + (m - 24.11)) % 360) / 13.333333)
    def calc_karana(t): s = math.degrees(ephem.Ecliptic(ephem.Sun(t)).lon); m = math.degrees(ephem.Ecliptic(ephem.Moon(t)).lon); return int(((m - s) % 360) / 6)

    cur_tithi, cur_nak, cur_yoga, cur_kar = calc_tithi(sunrise), calc_nakshatra(sunrise), calc_yoga(sunrise), calc_karana(sunrise)
    
    def find_start(t_ref, cur_val, func):
        t = t_ref
        for _ in range(120):
            t -= ephem.hour / 2
            if func(t) != cur_val:
                for _ in range(35):
                    t += ephem.minute
                    if func(t) == cur_val: return (ephem.Date(t).datetime() + timedelta(hours=5, minutes=30)).strftime("%d %b, %I:%M %p")
        return "-"
    def find_end(t_ref, cur_val, func):
        t = t_ref
        for _ in range(120):
            t += ephem.hour / 2
            if func(t) != cur_val:
                for _ in range(35):
                    t -= ephem.minute
                    if func(t) == cur_val: return (ephem.Date(t).datetime() + timedelta(hours=5, minutes=30)).strftime("%d %b, %I:%M %p")
        return "-"

    tithi_names = ["", "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी", "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "पौर्णिमा", "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी", "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "अमावस्या"]
    nakshatra_names = ["अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशीर्ष", "आर्द्रा", "पुनर्वसू", "पुष्य", "आश्लेषा", "मघा", "पूर्वा फाल्गुनी", "उत्तरा फाल्गुनी", "हस्त", "चित्रा", "स्वाती", "विशाखा", "अनुराधा", "ज्येष्ठा", "मूळ", "पूर्वाषाढा", "उत्तराषाढा", "श्रवण", "धनिष्ठा", "शततारका", "पूर्वा भाद्रपदा", "उत्तरा भाद्रपदा", "रेवती"]
    yoga_names = ["विष्कंभ", "प्रीती", "आयुष्मान", "सौभाग्य", "शोभन", "अतिगंड", "सुकर्मा", "धृती", "शूल", "गंड", "वृद्धी", "ध्रुव", "व्याघात", "हर्षण", "वज्र", "सिद्धी", "व्यतीपात", "वरीयान", "परिघ", "शिव", "सिद्ध", "साध्य", "शुभ", "शुक्ल", "ब्रह्म", "ऐंद्र", "वैधृती"]
    
    k_name = "किंस्तुघ्न" if cur_kar == 0 else "शकुनी" if cur_kar == 57 else "चतुष्पाद" if cur_kar == 58 else "नाग" if cur_kar == 59 else ["बव", "बालव", "कौलव", "तैतिल", "गर", "वणिज", "विष्टी (भद्रा)"][(cur_kar - 1) % 7]
    paksha = "शुक्ल पक्ष" if cur_tithi <= 15 else "कृष्ण पक्ष"
    
    return {
        "tithi": f"{paksha} {tithi_names[cur_tithi]}", "t_start": find_start(sunrise, cur_tithi, calc_tithi), "t_end": find_end(sunrise, cur_tithi, calc_tithi),
        "nakshatra": nakshatra_names[cur_nak % 27], "n_start": find_start(sunrise, cur_nak, calc_nakshatra), "n_end": find_end(sunrise, cur_nak, calc_nakshatra),
        "yoga": yoga_names[cur_yoga % 27], "y_start": find_start(sunrise, cur_yoga, calc_yoga), "y_end": find_end(sunrise, cur_yoga, calc_yoga),
        "karana": k_name, "k_start": find_start(sunrise, cur_kar, calc_karana), "k_end": find_end(sunrise, cur_kar, calc_karana),
        "is_chaturthi": cur_tithi in [4, 19], "is_ekadashi": cur_tithi in [11, 26]
    }

# ---------------------------------------------------------
# 🔐 १. Solarman API
# ---------------------------------------------------------
def get_solarman_token():
    try:
        app_id, app_secret, email, raw_password = st.secrets["sofar"]["app_id"], st.secrets["sofar"]["app_secret"], st.secrets["sofar"]["email"], st.secrets["sofar"]["password"]
        hashed_password = hashlib.sha256(raw_password.encode('utf-8')).hexdigest().lower()
        res = requests.post(f"https://globalapi.solarmanpv.com/account/v1.0/token?appId={app_id}&language=en", json={"appSecret": app_secret, "email": email, "password": hashed_password}, timeout=10).json()
        return res.get("access_token") if res.get("success") else None
    except: return None

def fetch_live_solar_data():
    token = get_solarman_token()
    if not token: return None
    try:
        app_id = st.secrets["sofar"]["app_id"]
        headers = {"Authorization": f"bearer {token}"}
        res_list = requests.post(f"https://globalapi.solarmanpv.com/station/v1.0/list?appId={app_id}&language=en", headers=headers, json={"page": 1, "size": 10}, timeout=10).json()
        if not res_list.get("success") or not res_list.get("stationList"): return None
        station_id = res_list["stationList"][0]["id"]
        daily_energy = float(res_list["stationList"][0].get("generationToday", res_list["stationList"][0].get("dailyEnergy", 0.0)))
        
        live_data = requests.post(f"https://globalapi.solarmanpv.com/station/v1.0/realTime?appId={app_id}&language=en", headers=headers, json={"stationId": station_id}, timeout=10).json()
        
        history_data = {}
        try:
            today_str = datetime.now().strftime('%Y-%m-%d')
            hist_url = f"https://globalapi.solarmanpv.com/station/v1.0/history?appId={app_id}&language=en"
            r_day = requests.post(hist_url, headers=headers, json={"stationId": station_id, "timeType": 1, "startTime": today_str, "endTime": today_str}, timeout=10).json()
            r_month = requests.post(hist_url, headers=headers, json={"stationId": station_id, "timeType": 2, "startTime": today_str, "endTime": today_str}, timeout=10).json()
            r_year = requests.post(hist_url, headers=headers, json={"stationId": station_id, "timeType": 3, "startTime": today_str, "endTime": today_str}, timeout=10).json()
            r_total = requests.post(hist_url, headers=headers, json={"stationId": station_id, "timeType": 4, "startTime": today_str, "endTime": today_str}, timeout=10).json()
            for res in [r_day, r_month, r_year, r_total]:
                if isinstance(res, dict):
                    for k, v in res.items():
                        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                            if res == r_day: history_data['day'] = [float(i.get('value', i.get('generation', i.get('power', 0))) or 0.0) for i in v]
                            if res == r_month: history_data['month'] = [float(i.get('value', i.get('generation', i.get('power', 0))) or 0.0) for i in v]
                            if res == r_year: history_data['year'] = [float(i.get('value', i.get('generation', i.get('power', 0))) or 0.0) for i in v]
                            if res == r_total: history_data['total'] = [float(i.get('value', i.get('generation', i.get('power', 0))) or 0.0) for i in v]
        except: pass
        if live_data.get("success"): live_data.update({"custom_daily_energy": daily_energy, "network_status": res_list["stationList"][0].get("networkStatus", "UNKNOWN"), "history": history_data}); return live_data
        return None
    except: return None

# ---------------------------------------------------------
# ३. CSS
# ---------------------------------------------------------
css = """
<style>
@keyframes waterPour { 0% { background-position: 0 0px; } 100% { background-position: 0 16px; } }
@keyframes waveMove { 0% { background-position-x: 0px; } 100% { background-position-x: 40px; } }
@keyframes sunGlow { 0% { box-shadow: 0 0 5px #fbc02d; } 50% { box-shadow: 0 0 10px #fbc02d; } 100% { box-shadow: 0 0 5px #fbc02d; } }
@keyframes energyFlow { 0% { background-position: 0px 0; } 100% { background-position: 20px 0; } }
@keyframes sirenFlash { 0% { background-color: #ffebee; border: 4px solid #d32f2f; } 50% { background-color: #d32f2f; color: white; box-shadow: 0 0 40px #d32f2f; } 100% { background-color: #ffebee; border: 4px solid #d32f2f; } }
.flashing-alert { animation: sirenFlash 0.5s infinite; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 20px; }
.normal-banner { text-align: center; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 12px; border-radius: 8px; margin-bottom: 5px; box-shadow: 0 4px 10px rgba(0,0,0,0.15); border: 1px solid #4a6fa5; }
.stButton button { font-weight: bold !important; border-radius: 6px !important; border: 2px solid #555 !important; }
.panchang-strip { background-color: #fffde7; border-radius: 6px; padding: 8px 15px; border: 1px solid #fbc02d; margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
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
# ⚙️ ५. साईडबार (येथे ऑटो-रिफ्रेश जोडले आहे)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔄 लाईव्ह सिस्टीम")
    auto_refresh = st.toggle("🟢 ऑटो-रिफ्रेश (Live Sync)", value=True, help="हे चालू ठेवल्यास पाण्याचे आकडे दर ५ सेकंदांनी आपोआप अपडेट होतील.")
    
    st.markdown("---")
    st.markdown("### ⚙️ टेस्टिंग सिम्युलेटर")
    sim_tanker = st.checkbox("🚚 टँकरचे पाणी चालू करा")
    st.markdown("---")
    st.markdown("#### 🏃‍♂️ घुसखोर (Motion Detection)")
    simulate_motion = st.checkbox("🚶 हालचाल करा (Test Motion)")
    st.markdown("---")
    st.markdown("#### 🔌 खऱ्या सोलरचे API कनेक्शन")
    
    if st.button("🔄 सोलर डेटा रिफ्रेश करा", type="primary"):
        with st.spinner("इन्व्हर्टरकडून लाईव्ह माहिती आणत आहे..."):
            data = fetch_live_solar_data()
            if data:
                power_watts = float(data.get("generationPower", 0))
                st.session_state.real_solar_power = power_watts / 1000.0 if power_watts > 10 else power_watts
                st.session_state.real_solar_total = float(data.get("generationTotal", 0))
                st.session_state.real_solar_daily = float(data.get("custom_daily_energy", 0.0))
                st.session_state.inverter_status = data.get("network_status", "UNKNOWN")
                hist = data.get("history", {})
                for k in ['day', 'month', 'year', 'total']:
                    if hist.get(k): st.session_state[f"chart_{k}"] = hist[k]
                st.session_state.is_solar_live = True
                st.success("✅ डेटा यशस्वीरीत्या अपडेट झाला!")

# ---------------------------------------------------------
# ६. टाक्यांचे डिझाईन
# ---------------------------------------------------------
def get_tank_html(tank_name, percentage, tank_type="overhead", inlets=[]):
    water_grad = "linear-gradient(to bottom, #4facfe 0%, #00f2fe 100%)" if tank_type == "overhead" else "linear-gradient(to bottom, #0077b6 0%, #023e8a 100%)"
    dark_wave_color = "%23005b96" if tank_type == "overhead" else "%23023e8a"
    tank_height, tank_width = ("160px", "100%") if tank_type == "underground" else ("220px", "160px")
    is_pouring = any(inlet['active'] for inlet in inlets)
    wave_html = f"<div style='position: absolute; top: 0; left: 0; width: 100%; height: 5px; background-color: {dark_wave_color.replace('%23', '#')}; border-top: 2px solid rgba(255,255,255,0.4); z-index: 10;'></div>" if not is_pouring else f"<div style='position: absolute; top: -10px; left: 0; width: 100%; height: 15px; background: url(\"data:image/svg+xml;utf8,<svg viewBox=\\\"0 0 40 15\\\" xmlns=\\\"http://www.w3.org/2000/svg\\\"><path d=\\\"M0 8 Q 10 15, 20 8 T 40 8 L 40 15 L 0 15 Z\\\" fill=\\\"{dark_wave_color}\\\"/></svg>\") repeat-x; background-size: 40px 15px; animation: waveMove 1s linear infinite; z-index: 10;'></div>"

    pipes_html = ""
    for idx, inlet in enumerate(inlets):
        offset = 50 if len(inlets) == 1 else (35 if idx == 0 else 65)
        active_pour = f"<div style='position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 12px; height: {tank_height}; background-image: repeating-linear-gradient(transparent, #00b4d8 4px, transparent 8px); background-size: 100% 16px; animation: waterPour 0.3s infinite linear; z-index: 1;'></div>" if inlet['active'] else ""
        pipes_html += f"<div style='position: absolute; bottom: 100%; left: {offset}%; transform: translateX(-50%); text-align: center; width: 120px;'><div style='font-size: 13px; font-weight: bold; color: #555; margin-bottom: 2px;'>{inlet['name']}</div><div style='width: 30px; height: 18px; background-color: #7f8c8d; border-radius: 4px; margin: 0 auto; border: 1px solid #555;'></div><div style='width: 14px; height: 25px; background-color: #bdc3c7; margin: 0 auto; position: relative; border-left: 1px solid #7f8c8d; border-right: 1px solid #7f8c8d; z-index: 3;'>{active_pour}</div></div>"

    html = f"<div style='margin-top: 50px; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center; width: 100%;'><div style='width: {tank_width}; max-width: 400px; height: {tank_height}; border: 3px solid #333; position: relative; background-color: #eef2f3; border-top: none; border-radius: 0 0 12px 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1); border-top: 1px solid #aaa;'>{pipes_html}<div style='position: absolute; bottom: 0; width: 100%; height: {percentage}%; background: {water_grad}; transition: height 1s ease-in-out; display: flex; align-items: center; justify-content: center; border-radius: 0 0 9px 9px; z-index: 2; border-top: 1px solid rgba(255,255,255,0.4);'>{wave_html}<span style='color: white; font-weight: bold; font-size: 22px; text-shadow: 1px 1px 3px black; z-index: 11;'>{percentage}%</span></div></div><div style='margin-top: 15px; font-weight: bold; font-size: 16px; background: #333; color: white; padding: 4px 15px; border-radius: 6px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'>{tank_name}</div></div>"
    return html

# ७. स्टार्टर पॅनेल
def render_compact_starter(col_obj, pump_name, state_key):
    is_on = st.session_state[state_key]
    needle_rot = -12 if is_on else -45
    on_glow = "background: radial-gradient(circle, #00ff00, #004d00); box-shadow: 0 0 10px #00ff00; color: white; border: 1px solid #00ff00;" if is_on else "background: #111; color: #555; border: 1px solid #222;"
    off_glow = "background: radial-gradient(circle, #ff0000, #4d0000); box-shadow: 0 0 10px #ff0000; color: white; border: 1px solid #ff0000;" if not is_on else "background: #111; color: #555; border: 1px solid #222;"

    html = f"""<div style="background-color: #1c1c1c; padding: 10px; border-radius: 8px; border: 2px solid #333; text-align: center; margin-bottom: 8px; box-shadow: 3px 3px 10px rgba(0,0,0,0.3);"><div style="color: #ddd; font-weight: bold; font-size: 11px; margin-bottom: 8px; text-transform: uppercase;">{pump_name}</div><div style="background-color: #f9f9f9; border-radius: 4px; padding: 5px; margin-bottom: 10px; border: 1px solid #aaa; position: relative; height: 50px;"><svg width="100%" height="100%" viewBox="0 0 100 65"><path d="M 15 45 A 40 40 0 0 1 85 45" fill="none" stroke="#222" stroke-width="1.5"/><text x="15" y="58" font-size="10" text-anchor="middle" font-weight="bold">0</text><text x="50" y="60" font-size="14" text-anchor="middle" font-weight="bold">A</text><text x="85" y="58" font-size="10" text-anchor="middle" font-weight="bold">30</text><line x1="50" y1="58" x2="50" y2="12" stroke="#222" stroke-width="2.5" transform="rotate({needle_rot} 50 58)" style="transition: transform 0.5s cubic-bezier(0.25, 1, 0.5, 1);"/><circle cx="50" cy="58" r="3" fill="black"/></svg></div><div style="display: flex; justify-content: space-around; align-items: center; margin-bottom: 5px;"><div style="width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 6px; {on_glow} transition: 0.3s;">ON</div><div style="width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 6px; {off_glow} transition: 0.3s;">OFF</div></div></div>"""
    col_obj.markdown(html, unsafe_allow_html=True)
    bc1, bc2 = col_obj.columns(2)
    bc1.button("ON", key=f"btn_on_{state_key}", on_click=set_pump_state, args=(state_key, True), use_container_width=True)
    bc2.button("OFF", key=f"btn_off_{state_key}", on_click=set_pump_state, args=(state_key, False), use_container_width=True)

# 🎛️ ८. ॲनिमेटेड वाल्व्ह डिझाईन
def render_animated_valve(col_obj, valve_name, state_key):
    is_on = st.session_state[state_key]
    handle_rot = 90 if is_on else 0 
    handle_color = "#2ecc71" if is_on else "#e74c3c"
    status_text = "ON" if is_on else "OFF"
    html = f"""<div style="text-align: center; margin-bottom: 5px;"><div style="font-size: 12px; font-weight: bold; color: #333; margin-bottom: 5px;">{valve_name}</div><svg width="60" height="90" viewBox="0 0 60 90"><rect x="22" y="0" width="16" height="90" fill="#95a5a6" /><polygon points="15,25 45,25 50,45 45,65 15,65 10,45" fill="#bdc3c7" stroke="#7f8c8d" stroke-width="1.5"/><rect x="18" y="20" width="24" height="50" fill="#ecf0f1" rx="2" stroke="#7f8c8d" stroke-width="1"/><g transform="rotate({handle_rot} 30 45)" style="transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);"><path d="M 35 40 L 5 40 C 2 40 0 42 0 45 C 0 48 2 50 5 50 L 35 50 Z" fill="{handle_color}" /><circle cx="30" cy="45" r="6" fill="#ecf0f1" stroke="#bdc3c7" stroke-width="1"/><circle cx="30" cy="45" r="2.5" fill="#7f8c8d" /></g></svg><div style="font-size: 14px; font-weight: 900; color: {handle_color}; margin-top: 2px;">{status_text}</div></div>"""
    col_obj.markdown(html, unsafe_allow_html=True)
    col_obj.toggle(valve_name, key=state_key, label_visibility="collapsed")

# ---------------------------------------------------------
# 🧠 ९. मुख्य लॉजिक
# ---------------------------------------------------------
trigger_siren = st.session_state.alarm_armed and simulate_motion
ug_pump, bw1_pump, bw2_pump = st.session_state['ug_pump'], st.session_state['bw1_pump'], st.session_state['bw2_pump']
valve_t1, valve_t2, valve_ug = st.session_state['valve_t1'], st.session_state['valve_t2'], st.session_state['valve_ug']

any_pump_on = ug_pump or bw1_pump or bw2_pump
any_borewell_on = bw1_pump or bw2_pump
tank1_pouring = valve_t1 and any_pump_on
tank2_pouring = valve_t2 and any_pump_on
ug_pouring_from_bw = valve_ug and any_borewell_on
ug_pouring_from_tanker = sim_tanker
garden_watering = ug_pump and not valve_t1 and not valve_t2
is_any_water_pouring = tank1_pouring or tank2_pouring or ug_pouring_from_bw or ug_pouring_from_tanker or garden_watering

# १०. मुख्य डॅशबोर्ड लेआउट
col_left, col_right = st.columns([1.5, 1])

with col_right:
    status_board = st.empty()

    # 🛡️ सुरक्षा प्रणाली
    with st.container(border=True):
        st.markdown("<div style='background-color: #f5f5f5; padding: 8px; border-radius: 6px; margin-bottom: 10px; text-align: center;'><h5 style='margin: 0; color: #c2185b; font-weight: bold;'>🛡️ सुरक्षा प्रणाली</h5></div>", unsafe_allow_html=True)
        sec_c1, sec_c2 = st.columns([1.5, 1], vertical_alignment="center")
        with sec_c1: st.session_state.alarm_armed = st.toggle("🚨 अलार्म (Arm)", value=st.session_state.alarm_armed)
        with sec_c2:
            cctv_pop = st.popover("📹 कॅमेरे", use_container_width=True)
            with cctv_pop:
                if st.button("⬅️ डॅशबोर्डवर परत जा", key="close_cctv_btn", use_container_width=True): st.rerun()
                st.markdown("<h5 style='color: #1e3c72; text-align: center; margin-bottom: 15px;'>📹 सुरक्षा कॅमेरे (Live CCTV)</h5>", unsafe_allow_html=True)
                placeholder_style = "background-color: #111; height: 200px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #888; font-family: monospace; border: 2px solid #444; position: relative; text-align: center;"
                recording_dot = "<div style='position: absolute; top: 15px; right: 15px; width: 12px; height: 12px; background-color: #ff3333; border-radius: 50%; animation: pulseRed 1s infinite; box-shadow: 0 0 8px #ff3333;'></div>"
                cam_col1, cam_col2 = st.columns(2)
                with cam_col1: st.markdown(f"<div style='{placeholder_style}'>{recording_dot}CAM 1<br><br>RTSP Stream</div><div style='text-align: center; font-weight: bold; margin-top: 5px; color: #555;'>📍 मुख्य प्रवेशद्वार</div>", unsafe_allow_html=True)
                with cam_col2: st.markdown(f"<div style='{placeholder_style}'>{recording_dot}CAM 2<br><br>RTSP Stream</div><div style='text-align: center; font-weight: bold; margin-top: 5px; color: #555;'>📍 पार्किंग</div>", unsafe_allow_html=True)

    # ☀️ सोलर ऊर्जा
    with st.container(border=True):
        current_power, daily_kwh = st.session_state.real_solar_power, st.session_state.real_solar_daily
        is_generating = current_power > 0
        is_offline = "OFFLINE" in st.session_state.inverter_status
        display_power = f"{current_power:.2f} kW"
        display_daily = f"{int(daily_kwh * 1000)} Wh" if daily_kwh < 1.0 else f"{daily_kwh:.2f} kWh"

        if not st.session_state.is_solar_live: solar_glow, line_style, status_color, status_text, data_source_badge = "border: 1px solid #ccc;", "background-color: #bdc3c7;", "#555", "🔄 कृपया 'लाईव्ह डेटा रिफ्रेश करा' बटण दाबा", "<span style='background-color: #9e9e9e; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;'>⏳ PENDING</span>"
        elif is_offline: solar_glow, line_style, status_color, status_text, data_source_badge = "border: 1px solid #95a5a6;", "background-color: #bdc3c7;", "#7f8c8d", "🌙 इन्व्हर्टर स्लीप मोडमध्ये आहे (रात्र)", "<span style='background-color: #7f8c8d; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;'>🌙 OFFLINE</span>"
        else: solar_glow, line_style, status_color, status_text, data_source_badge = "animation: sunGlow 3s infinite;" if is_generating else "border: 1px solid #ccc;", "background-image: repeating-linear-gradient(90deg, #00b4d8 0px, #00b4d8 10px, transparent 10px, transparent 20px); background-size: 20px 100%; animation: energyFlow 0.5s linear infinite;" if is_generating else "background-image: repeating-linear-gradient(90deg, #bdc3c7 0px, #bdc3c7 10px, transparent 10px, transparent 20px);", "#2e7d32" if is_generating else "#c62828", "🟢 सौर ऊर्जेची निर्मिती सुरू आहे (Live)" if is_generating else "🔴 सौर निर्मिती सध्या 0 W आहे", "<span style='background-color: #4CAF50; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;'>🟢 LIVE DATA</span>"

        solar_panel_svg = """<svg width="45" height="45" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="10" fill="#FFA500"/><polyline points="75,90 85,90 80,40" fill="none" stroke="#999" stroke-width="4"/><polygon points="35,85 45,35 85,30 70,80" fill="#1e5799" stroke="#ddd" stroke-width="2"/></svg>"""
        grid_tower_svg = """<svg width="40" height="40" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><polyline points="50,10 30,90" fill="none" stroke="#555" stroke-width="3"/><polyline points="50,10 70,90" fill="none" stroke="#555" stroke-width="3"/><line x1="20" y1="50" x2="80" y2="50" stroke="#555" stroke-width="3"/></svg>"""

        st.markdown(f"<div style='background-color: #fffde7; padding: 8px; border-radius: 6px; margin-bottom: 12px; text-align: center; position: relative; {solar_glow}'><div style='position: absolute; top: 5px; right: 5px;'>{data_source_badge}</div><h5 style='margin: 0; color: #f57f17; font-weight: bold;'>☀️ सोलर ऊर्जा (Sofar Inverter)</h5></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='display: flex; justify-content: space-around; align-items: center; margin-bottom: 10px;'><div style='text-align: center;'><div style='font-size: 13px; color: #666;'>सध्याची निर्मिती</div><div style='font-size: 20px; font-weight: bold; color: #2e7d32;'>{display_power}</div></div><div style='text-align: center;'><div style='font-size: 13px; color: #666;'>आजची निर्मिती</div><div style='font-size: 20px; font-weight: bold; color: #1565c0;'>{display_daily}</div></div></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='background-color: #f8f9fa; padding: 12px; border-radius: 8px; border: 1px solid #eee; margin-top: 5px;'><div style='display: flex; align-items: center; justify-content: space-between;'><div style='text-align: center; width: 60px;'>{solar_panel_svg}<div style='font-size: 11px; font-weight: bold; color:#555;'>Panels</div></div><div style='flex-grow: 1; height: 4px; margin: 0 5px; {line_style}'></div><div style='text-align: center; width: 40px;'><div style='font-size: 28px;'>🎛️</div><div style='font-size: 11px; font-weight: bold; color:#555;'>Inverter</div></div><div style='flex-grow: 1; height: 4px; margin: 0 5px; {line_style}'></div><div style='text-align: center; width: 60px;'>{grid_tower_svg}<div style='font-size: 11px; font-weight: bold; color:#555;'>Grid</div></div></div></div>", unsafe_allow_html=True)
        
        sc1, sc2 = st.columns([3, 2])
        with sc1: st.markdown(f"<div style='margin-top: 5px; font-weight: bold; font-size: 13px; color: {status_color};'>{status_text}</div>", unsafe_allow_html=True)
        
        with sc2:
            report_pop = st.popover("📊 सोलर रिपोर्ट", use_container_width=True)
            with report_pop:
                if st.button("⬅️ डॅशबोर्डवर परत जा", key="close_solar_btn", use_container_width=True): st.rerun()
                st.markdown("<div style='background-color: #f3e5f5; padding: 8px; border-radius: 6px; margin-bottom: 12px; text-align: center;'><h5 style='margin: 0; color: #6a1b9a; font-weight: bold;'>📊 सोलर रिपोर्ट आणि आकडेवारी</h5></div>", unsafe_allow_html=True)
                tab_day, tab_month, tab_year, tab_total = st.tabs(["Day", "Month", "Year", "Total"])
                with tab_day: st.line_chart(st.session_state.chart_day, height=150) 
                with tab_month: st.bar_chart(st.session_state.chart_month, height=150)
                with tab_year: st.bar_chart(st.session_state.chart_year, height=150)
                with tab_total: st.line_chart(st.session_state.chart_total, height=150)

    # ⚡ कंट्रोल पॅनल
    with st.container(border=True):
        st.markdown("<div style='background-color: #424242; padding: 10px; border-radius: 6px; margin-bottom: 15px; text-align: center; border: 1px solid #222;'><h5 style='margin: 0; color: #fff; font-weight: bold;'>⚡ स्टार्टर कंट्रोल पॅनल</h5></div>", unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        render_compact_starter(sc1, "UG PUMP", "ug_pump")
        render_compact_starter(sc2, "BW-1", "bw1_pump")
        render_compact_starter(sc3, "BW-2", "bw2_pump")

    # 🎛️ वाल्व्ह पॅनल
    with st.container(border=True):
        st.markdown("<div style='background-color: #c8e6c9; padding: 10px; border-radius: 6px; margin-bottom: 15px; text-align: center;'><h5 style='margin: 0; color: #2e7d32; font-weight: bold;'>🎛️ वाल्व्ह (कॉक) स्थिती</h5></div>", unsafe_allow_html=True)
        v1, v2, v3 = st.columns(3)
        with v1: render_animated_valve(v1, "V1 (Tank 1)", "valve_t1")
        with v2: render_animated_valve(v2, "V2 (Tank 2)", "valve_t2")
        with v3: render_animated_valve(v3, "V3 (UG Tank)", "valve_ug")

    # 📋 स्थितीदर्शक बोर्ड अपडेट
    with status_board.container(border=True):
        st.markdown("<div style='background-color: #e3f2fd; padding: 10px; border-radius: 6px; margin-bottom: 10px; text-align: center;'><h5 style='margin: 0; color: #1565c0; font-weight: bold;'>📋 स्थितीदर्शक</h5></div>", unsafe_allow_html=True)
        status_msgs = []
        if trigger_siren: status_msgs.append("🚨 घुसखोर आढळला! अलार्म सुरू आहे.")
        if not any_pump_on and not sim_tanker: status_msgs.append("⚠️ सर्व पंप बंद आहेत.")
        else:
            if ug_pump: status_msgs.append("🔸 अंडरग्राउंड पंप सुरू आहे.")
            if bw1_pump: status_msgs.append("🔸 बोअरवेल १ सुरू आहे.")
            if bw2_pump: status_msgs.append("🔸 बोअरवेल २ सुरू মাঠে आहे.")
            if sim_tanker: status_msgs.append("🚚 टँकरद्वारे पाणी येत आहे.")
        if tank1_pouring: status_msgs.append("🔹 'Tank 1' मध्ये पाणी भरत आहे.")
        if tank2_pouring: status_msgs.append("🔹 'Tank 2' मध्ये पाणी भरत आहे.")
        if ug_pouring_from_bw: status_msgs.append("🔹 बोअरवेलचे पाणी 'UG Tank' मध्ये जात आहे.")
        if garden_watering: status_msgs.append("🌿 पाणी 'गार्डन/झाडांना' दिले जात आहे.")
        
        status_html = "".join([f"<li style='margin-bottom: 5px;'>{msg}</li>" for msg in status_msgs])
        st.markdown(f"<ul style='font-size: 14px; color: #333; font-weight: 600; padding-left: 20px; margin-bottom: 0;'>{status_html}</ul>", unsafe_allow_html=True)

with col_left:
    # 🌟 Google Sheet वरून डेटा आणणे आणि TANK 1 चे गणित करणे
    dist_from_gs = get_tank_distance_from_google()
    live_pct, live_liters, live_level_cm = calc_tank1_data(dist_from_gs)
    
    # मॅन्युअल रिफ्रेश बटण काढून टाकले आहे, कारण आता सिस्टीम 'ऑटो-रिफ्रेश' आहे.
    
    # ⬇️ इथे Tank 1 ला लाईव्ह डेटा जोडला आहे
    html_t1 = get_tank_html(f"Tank 1 ({live_pct}%)", live_pct, tank_type="overhead", inlets=[{"name": "Main Line", "active": tank1_pouring}])
    html_t2 = get_tank_html("Tank 2", 60, tank_type="overhead", inlets=[{"name": "Main Line", "active": tank2_pouring}])
    
    # अंडरग्राउंड टाकी आता स्थिर (Static) ठेवली आहे
    html_ug = get_tank_html("Underground Tank", 75, tank_type="underground", inlets=[{"name": "Borewell (V3)", "active": ug_pouring_from_bw}, {"name": "Tanker", "active": ug_pouring_from_tanker}])

    garden_active_html = "<div style='position: absolute; top: -30px; left: 50%; transform: translateX(-50%); width: 8px; height: 40px; background-image: repeating-linear-gradient(transparent, #4facfe 2px, transparent 6px); background-size: 100% 10px; animation: waterPour 0.3s infinite linear;'></div>" if garden_watering else ""

    html_combined = (
        "<div style='display: flex; justify-content: space-around; width: 100%; gap: 10px;'>"
        f"<div style='flex: 1; display: flex; justify-content: center;'>{html_t1}</div>"
        f"<div style='flex: 1; display: flex; justify-content: center;'>{html_t2}</div>"
        "</div>"
        
        # लाईव्ह डेटा दाखवण्यासाठी एक छोटी पट्टी (Tank 1 साठी)
        "<div style='background-color: #e3f2fd; padding: 10px; border-radius: 8px; margin-top: 15px; display: flex; justify-content: space-around; border: 1px solid #90caf9;'>"
        f"<div style='text-align: center;'><div style='font-size: 12px; color: #555;'>Tank 1 सेन्सर अंतर</div><div style='font-weight: bold; color: #1565c0;'>{dist_from_gs if dist_from_gs is not None else 0} cm</div></div>"
        f"<div style='text-align: center;'><div style='font-size: 12px; color: #555;'>Tank 1 पाण्याची उंची</div><div style='font-weight: bold; color: #1565c0;'>{live_level_cm:.1f} cm</div></div>"
        f"<div style='text-align: center;'><div style='font-size: 12px; color: #555;'>Tank 1 एकूण पाणी</div><div style='font-weight: bold; font-size: 18px; color: #d32f2f;'>{live_liters:,.0f} Liters</div></div>"
        "</div>"

        "<div style='display: flex; justify-content: space-around; width: 100%; gap: 15px; align-items: flex-end;'>"
        f"<div style='flex: 1; display: flex; justify-content: center; width: 100%;'>{html_ug}</div>"
        f"<div style='flex: 1; display: flex; justify-content: center; width: 100%; margin-bottom: 20px;'>"
        "<div style='width: 100%; max-width: 250px; height: 160px; border: 3px solid #2e7d32; border-radius: 12px; background: #e8f5e9; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; position: relative; box-shadow: inset 0 0 10px rgba(0,0,0,0.05);'>"
        f"{garden_active_html}"
        "<div style='font-size: 40px;'>🌳🏡🌿</div>"
        "<h4 style='color: #2e7d32; margin: 10px 0 0 0;'>गार्डन / झाडे</h4>"
        "<p style='font-size: 11px; color: #555; margin: 5px 0 0 0;'>अंडरग्राउंड टाकीतून</p>"
        "</div></div></div>"
    )
    st.markdown(html_combined, unsafe_allow_html=True)

# ---------------------------------------------------------
# 📢 ११. सायरन आणि 🕉️ कॉम्पेक्ट पंचांग पट्टी 
# ---------------------------------------------------------
if trigger_siren:
    top_banner.markdown("<div class='flashing-alert'><h1 style='color: white; margin: 0; font-size: 36px; font-weight: 900; text-shadow: 2px 2px 5px black;'>🚨 सावधान! घरात घुसखोर आढळला! 🚨</h1></div>", unsafe_allow_html=True)
    panchang_banner.empty()
    st.markdown("""<audio autoplay loop><source src="https://upload.wikimedia.org/wikipedia/commons/4/40/Siren_Noise.ogg" type="audio/ogg"><source src="https://actions.google.com/sounds/v1/alarms/burglar_alarm.ogg" type="audio/ogg"></audio>""", unsafe_allow_html=True)
else:
    top_banner.markdown("<div class='normal-banner'><h2 style='color: #ffffff; margin: 0; font-weight: 800; letter-spacing: 1px;'>अभिप्राजामेयार्णव</h2><h4 style='color: #81d4fa; margin: 3px 0 0 0; font-weight: 500;'>पाणी, ऊर्जा व सुरक्षा व्यवस्थापन प्रणाली</h4></div>", unsafe_allow_html=True)
    today_dt = datetime.now().date()
    vaar_names = ["सोमवार", "मंगळवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
    today_vaar = vaar_names[today_dt.weekday()]
    tdy_panchang = get_panchang_details(today_dt)
    
    festival_html = ""
    if tdy_panchang["is_chaturthi"]:
        b64_img = get_base64_image("ganpati.png")
        festival_html = f"<img src='data:image/png;base64,{b64_img}' width='35' style='vertical-align:middle; border-radius:50%; margin-right:8px;'> <span style='color: #D32F2F; font-weight: bold;'>|| श्री गणेशाय नमः ||</span>" if b64_img else "<span style='color: #D32F2F; font-weight: bold;'>🐘 || श्री गणेशाय नमः ||</span>"
    elif tdy_panchang["is_ekadashi"]:
        b64_img = get_base64_image("vitthal.png")
        festival_html = f"<img src='data:image/png;base64,{b64_img}' width='35' style='vertical-align:middle; border-radius:50%; margin-right:8px;'> <span style='color: #1976D2; font-weight: bold;'>|| राम कृष्ण हरी ||</span>" if b64_img else "<span style='color: #1976D2; font-weight: bold;'>🚩 || राम कृष्ण हरी ||</span>"

    with panchang_banner.container():
        p_col1, p_col2 = st.columns([5, 1])
        with p_col1: st.markdown(f"<div class='panchang-strip'><div style='font-size: 15px; color: #333;'><b>वार:</b> {today_vaar} &nbsp;|&nbsp; <b>तिथी:</b> {tdy_panchang['tithi']}</div><div>{festival_html}</div></div>", unsafe_allow_html=True)
        with p_col2:
            with st.popover("📅 पंचांग", help="विस्तृत पंचांग आणि वेळा पहा"):
                if st.button("⬅️ डॅशबोर्डवर परत जा", key="close_panchang_btn", use_container_width=True): st.rerun()
                st.markdown("<h5 style='text-align: center; color: #e67e22;'>🕉️ विस्तृत पंचांग</h5>", unsafe_allow_html=True)
                selected_date = st.date_input("तारीख निवडा:", today_dt)
                sel_panchang = tdy_panchang if selected_date == today_dt else get_panchang_details(selected_date)
                sel_vaar = vaar_names[selected_date.weekday()]
                st.markdown(f"<div style='text-align:center; font-size:14px; font-weight:bold; margin-bottom:10px;'>{selected_date.strftime('%d-%m-%Y')} ({sel_vaar})</div>", unsafe_allow_html=True)
                st.markdown(f"""<table style="width:100%; border-collapse: collapse; font-size: 13px;"><tr style="border-bottom: 2px solid #ddd; background-color: #f9f9f9;"><th style="padding: 6px; text-align: left; color:#555;">अंग</th><th style="padding: 6px; text-align: left; color:#555;">नाव</th><th style="padding: 6px; text-align: center; color:#555;">सुरुवात<br><span style="font-size:11px;">(दिनांक व वेळ)</span></th><th style="padding: 6px; text-align: center; color:#555;">समाप्ती<br><span style="font-size:11px;">(दिनांक व वेळ)</span></th></tr><tr style="border-bottom: 1px solid #eee;"><td style="padding: 6px;"><b>🌙 तिथी</b></td><td style="padding: 6px; color:#d35400;"><b>{sel_panchang['tithi']}</b></td><td style="padding: 6px; text-align: center; color:#444;">{sel_panchang['t_start']}</td><td style="padding: 6px; text-align: center; color:#444;">{sel_panchang['t_end']}</td></tr><tr style="border-bottom: 1px solid #eee;"><td style="padding: 6px;"><b>✨ नक्षत्र</b></td><td style="padding: 6px; color:#d35400;"><b>{sel_panchang['nakshatra']}</b></td><td style="padding: 6px; text-align: center; color:#444;">{sel_panchang['n_start']}</td><td style="padding: 6px; text-align: center; color:#444;">{sel_panchang['n_end']}</td></tr><tr style="border-bottom: 1px solid #eee;"><td style="padding: 6px;"><b>🧘 योग</b></td><td style="padding: 6px; color:#d35400;"><b>{sel_panchang['yoga']}</b></td><td style="padding: 6px; text-align: center; color:#444;">{sel_panchang['y_start']}</td><td style="padding: 6px; text-align: center; color:#444;">{sel_panchang['y_end']}</td></tr><tr><td style="padding: 6px;"><b>🚩 करण</b></td><td style="padding: 6px; color:#d35400;"><b>{sel_panchang['karana']}</b></td><td style="padding: 6px; text-align: center; color:#444;">{sel_panchang['k_start']}</td><td style="padding: 6px; text-align: center; color:#444;">{sel_panchang['k_end']}</td></tr></table>""", unsafe_allow_html=True)

if is_any_water_pouring and not trigger_siren:
    st.markdown("""<audio autoplay loop id="waterAudio"><source src="https://actions.google.com/sounds/v1/water/stream_water.ogg" type="audio/ogg"></audio><script>document.getElementById("waterAudio").volume = 0.4;</script>""", unsafe_allow_html=True)

alert_to_speak = ""
if trigger_siren: alert_to_speak = "सावधान! घरात घुसखोर आढळला आहे. सुरक्षा प्रणाली सुरू झाली आहे."
elif (valve_t1 or valve_t2) and not any_pump_on: alert_to_speak = "सावधान! वाल्व्ह उघडा आहे, पण पंप बंद आहे."
elif tank1_pouring and tank2_pouring: alert_to_speak = "टाकी एक आणि टाकी दोन मध्ये पाणी भरत आहे."
elif tank1_pouring: alert_to_speak = "टाकी एक मध्ये पाणी भरत आहे."
elif tank2_pouring: alert_to_speak = "टाकी दोन मध्ये पाणी भरत आहे."
elif ug_pouring_from_bw or ug_pouring_from_tanker: alert_to_speak = "अंडरग्राउंड टाकीत पाणी भरत आहे."
elif garden_watering: alert_to_speak = "गार्डन मध्ये पाणी दिले जात आहे."

if 'last_speech' not in st.session_state: st.session_state.last_speech = ""
if alert_to_speak == "": st.session_state.last_speech = ""
elif alert_to_speak != st.session_state.last_speech:
    st.session_state.last_speech = alert_to_speak
    components.html(f"<script>var msg = new SpeechSynthesisUtterance('{alert_to_speak}'); msg.lang = 'mr-IN'; msg.rate = 0.95; window.speechSynthesis.speak(msg);</script>", height=0, width=0)

# ---------------------------------------------------------
# १२. ऑटो-रिफ्रेश लॉजिक (Live Dashboard)
# ---------------------------------------------------------
if auto_refresh:
    time.sleep(5)  # दर ५ सेकंदांनी गुगल शीट तपासेल (जेणेकरून सर्व्हरवर लोड येणार नाही)
    st.rerun()     # ॲप स्वतःहून रिफ्रेश करेल
