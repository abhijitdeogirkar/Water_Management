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

# 'wide' लेआउटसह पेज कॉन्फिगरेशन
st.set_page_config(page_title="Abhiprajameyarnav Smart Home", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------
# 📸 फोटो बेस-६४ मध्ये बदलण्याचे फंक्शन (Inline Image साठी)
# ---------------------------------------------------------
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# ---------------------------------------------------------
# 🕉️ संपूर्ण पंचांग आणि (पासून - पर्यंत) वेळा काढण्याचे फंक्शन
# ---------------------------------------------------------
def get_panchang_details(selected_date):
    observer = ephem.Observer()
    observer.lat, observer.lon, observer.elevation = '20.1059', '77.1358', 414 
    
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
# 🔐 १. Solarman (Sofar) API सुरक्षित टोकन मिळवणे
# ---------------------------------------------------------
def get_solarman_token():
    try:
        app_id = st.secrets["sofar"]["app_id"]
        app_secret = st.secrets["sofar"]["app_secret"]
        email = st.secrets["sofar"]["email"]
        raw_password = st.secrets["sofar"]["password"]
        hashed_password = hashlib.sha256(raw_password.encode('utf-8')).hexdigest().lower()
        url = f"https://globalapi.solarmanpv.com/account/v1.0/token?appId={app_id}&language=en"
        payload = {"appSecret": app_secret, "email": email, "password": hashed_password}
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        if data.get("success"): return data.get("access_token")
        else: st.error(f"⚠️ API Error: {data.get('msg')}"); return None
    except Exception as e:
        st.error(f"⚠️ कनेक्शनमध्ये अडचण (Secrets फाईल तपासा): {e}")
        return None

# ---------------------------------------------------------
# ☀️ २. इन्व्हर्टरचा Live Data मिळवण्याचे फंक्शन
# ---------------------------------------------------------
def fetch_live_solar_data():
    token = get_solarman_token()
    if not token: return None
    try:
        app_id = st.secrets["sofar"]["app_id"]
        headers = {"Authorization": f"bearer {token}"}
        url_list = f"https://globalapi.solarmanpv.com/station/v1.0/list?appId={app_id}&language=en"
        res_list = requests.post(url_list, headers=headers, json={"page": 1, "size": 10}, timeout=10)
        station_data = res_list.json()
        if not station_data.get("success") or not station_data.get("stationList"):
            st.error("⚠️ Solarman खात्यावर कोणताही प्लांट जोडलेला आढळला नाही."); return None
            
        station_info = station_data["stationList"][0]
        station_id = station_info["id"]
        st.session_state.debug_station_data = station_info
        
        network_status = station_info.get("networkStatus", "UNKNOWN")
        daily_energy = float(station_info.get("generationToday", station_info.get("dailyEnergy", station_info.get("todayGeneration", station_info.get("todayEnergy", station_info.get("dailyGeneration", 0.0))))))
        
        url_realtime = f"https://globalapi.solarmanpv.com/station/v1.0/realTime?appId={app_id}&language=en"
        res_realtime = requests.post(url_realtime, headers=headers, json={"stationId": station_id}, timeout=10)
        live_data = res_realtime.json()
        
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
        else:
            st.error("⚠️ लाईव्ह डेटा मिळवण्यात अडचण आली."); return None
    except Exception as e:
        st.error(f"⚠️ डेटा फेचिंग एरर: {e}"); return None

# ---------------------------------------------------------
# ३. 🌟 UI/UX प्रीमियम CSS (पूर्णपणे सुधारित)
# ---------------------------------------------------------
css = """
<style>
/* Global Streamlit UI Adjustments for a cleaner look */
.stApp { background-color: #f4f7f6; }

/* Custom Container / Card Styling */
div[data-testid="stVerticalBlock"] > div[style*="border"] {
    border: 1px solid #e0e6ed !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04) !important;
    background-color: #ffffff !important;
    padding: 1.2rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
    box-shadow: 0 8px 30px rgba(0,0,0,0.08) !important;
}

/* Animations */
@keyframes waterPour { 0% { background-position: 0 0px; } 100% { background-position: 0 16px; } }
@keyframes waveMove { 0% { background-position-x: 0px; } 100% { background-position-x: 40px; } }
@keyframes sunGlow { 0% { box-shadow: 0 0 10px rgba(251, 192, 45, 0.4); } 50% { box-shadow: 0 0 25px rgba(251, 192, 45, 0.8); } 100% { box-shadow: 0 0 10px rgba(251, 192, 45, 0.4); } }
@keyframes energyFlow { 0% { background-position: 0px 0; } 100% { background-position: 20px 0; } }
@keyframes sirenFlash { 
    0% { background-color: #ffebee; border-color: #ef5350; } 
    50% { background-color: #e53935; color: white; box-shadow: 0 0 40px #e53935; transform: scale(1.02); } 
    100% { background-color: #ffebee; border-color: #ef5350; } 
}

/* Banners */
.flashing-alert { animation: sirenFlash 0.6s infinite; padding: 20px; border-radius: 16px; text-align: center; margin-bottom: 20px; border: 3px solid #e53935; }
.normal-banner { 
    text-align: center; 
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); 
    padding: 20px; 
    border-radius: 16px; 
    margin-bottom: 10px; 
    box-shadow: 0 10px 25px rgba(0,0,0,0.15); 
}
.panchang-strip { 
    background: linear-gradient(to right, #ffffff, #fffdf2); 
    border-radius: 12px; 
    padding: 10px 20px; 
    border-left: 6px solid #fbc02d; 
    margin-bottom: 20px; 
    display: flex; 
    align-items: center; 
    justify-content: space-between; 
    box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
}

/* Buttons Customization */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    border: 1px solid #d1d9e6 !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    border-color: #2980b9 !important;
    color: #2980b9 !important;
    box-shadow: 0 4px 10px rgba(41, 128, 185, 0.1) !important;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 🌟 'Top Banner' आणि 'Panchang Banner'
top_banner = st.empty()
panchang_banner = st.empty()

# ---------------------------------------------------------
# ४. स्टेट्स (Session State)
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
    st.markdown("<h3 style='color:#2c3e50; font-weight:700;'>⚙️ सिस्टम कंट्रोल्स</h3>", unsafe_allow_html=True)
    sim_tanker = st.checkbox("🚚 टँकरचे पाणी सुरू करा")
    st.markdown("---")
    st.markdown("<h4 style='color:#2c3e50;'>🏃‍♂️ सुरक्षा चाचणी</h4>", unsafe_allow_html=True)
    simulate_motion = st.checkbox("🚶 हालचाल करा (Motion Test)")
    st.markdown("---")
    st.markdown("<h4 style='color:#2c3e50;'>🔌 सोलर API सिंक</h4>", unsafe_allow_html=True)
    
    if st.button("🔄 लाईव्ह डेटा रिफ्रेश करा", type="primary", use_container_width=True):
        with st.spinner("इन्व्हर्टरशी संपर्क साधत आहे..."):
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
# ६. UI/UX: टाक्यांचे मॉडर्न डिझाईन 
# ---------------------------------------------------------
def get_tank_html(tank_name, level_cm, tank_type="overhead", inlets=[]):
    percentage = min(int((level_cm / 100) * 100), 100)
    # UI Upgrade: 3D Water Gradient and Glassmorphism container
    water_grad = "linear-gradient(to bottom, #4facfe 0%, #00f2fe 100%)" if tank_type == "overhead" else "linear-gradient(to bottom, #0077b6 0%, #023e8a 100%)"
    dark_wave = "%23005b96" if tank_type == "overhead" else "%23023e8a" 
    tank_height, tank_width = ("160px", "100%") if tank_type == "underground" else ("220px", "160px")
    border_rad = "0 0 16px 16px" if tank_type == "overhead" else "12px"
    tank_border = "border: 4px solid #b0bec5; border-top: none;" if tank_type == "overhead" else "border: 4px solid #90a4ae;"

    is_pouring = any(inlet['active'] for inlet in inlets)
    wave_html = f"<div style='position: absolute; top: -8px; left: 0; width: 100%; height: 12px; background: url(\"data:image/svg+xml;utf8,<svg viewBox=\\\"0 0 40 12\\\" xmlns=\\\"http://www.w3.org/2000/svg\\\"><path d=\\\"M0 6 Q 10 12, 20 6 T 40 6 L 40 12 L 0 12 Z\\\" fill=\\\"{dark_wave}\\\"/></svg>\") repeat-x; background-size: 40px 12px; animation: waveMove 1.5s linear infinite; z-index: 10; opacity: 0.8;'></div>" if is_pouring else f"<div style='position: absolute; top: 0; left: 0; width: 100%; height: 6px; background-color: {dark_wave.replace('%23','#')}; border-top: 2px solid rgba(255,255,255,0.5); z-index: 10;'></div>"

    pipes_html = ""
    for idx, inlet in enumerate(inlets):
        offset = 50 if len(inlets) == 1 else (35 if idx == 0 else 65)
        active_pour = f"<div style='position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 10px; height: {tank_height}; background-image: repeating-linear-gradient(transparent, #4facfe 3px, transparent 6px); background-size: 100% 12px; animation: waterPour 0.2s infinite linear; z-index: 1;'></div>" if inlet['active'] else ""
        pipes_html += f"<div style='position: absolute; bottom: 100%; left: {offset}%; transform: translateX(-50%); text-align: center; width: 120px;'><div style='font-size: 12px; font-weight: 700; color: #546e7a; margin-bottom: 4px;'>{inlet['name']}</div><div style='width: 32px; height: 14px; background-color: #78909c; border-radius: 4px 4px 0 0; margin: 0 auto;'></div><div style='width: 14px; height: 25px; background: linear-gradient(to right, #cfd8dc, #eceff1, #cfd8dc); margin: 0 auto; position: relative; z-index: 3;'>{active_pour}</div></div>"

    html = f"""<div style='margin-top: 50px; margin-bottom: 20px; display: flex; flex-direction: column; align-items: center; width: 100%;'>
        <div style='width: {tank_width}; max-width: 400px; height: {tank_height}; {tank_border} position: relative; background-color: rgba(236, 240, 241, 0.4); border-radius: {border_rad}; box-shadow: inset 0 0 20px rgba(0,0,0,0.05); overflow: visible;'>
            {pipes_html}
            <div style='position: absolute; bottom: 0; width: 100%; height: {percentage}%; background: {water_grad}; transition: height 1.5s cubic-bezier(0.4, 0, 0.2, 1); display: flex; align-items: center; justify-content: center; border-radius: {border_rad}; z-index: 2; box-shadow: inset 0 10px 20px rgba(255,255,255,0.2);'>
                {wave_html}
                <span style='color: white; font-weight: 800; font-size: 24px; text-shadow: 0px 2px 4px rgba(0,0,0,0.3); z-index: 11;'>{percentage}%</span>
            </div>
            <div style='position: absolute; top:0; left: 10%; width: 20%; height: 100%; background: linear-gradient(to right, rgba(255,255,255,0.4), transparent); z-index: 12; border-radius: {border_rad}; pointer-events: none;'></div>
        </div>
        <div style='margin-top: 18px; font-weight: 700; font-size: 14px; color: #2c3e50; text-transform: uppercase; letter-spacing: 1px;'>{tank_name}</div>
    </div>"""
    return html

# ७. UI/UX: मॉडर्न स्टार्टर पॅनेल (Sleek Dark Mode Widget)
def render_compact_starter(col_obj, pump_name, state_key):
    is_on = st.session_state[state_key]
    needle_rot = -12 if is_on else -45
    on_glow = "background: #00e676; box-shadow: 0 0 12px #00e676; color: #1b5e20;" if is_on else "background: #37474f; color: #78909c;"
    off_glow = "background: #ff5252; box-shadow: 0 0 12px #ff5252; color: #b71c1c;" if not is_on else "background: #37474f; color: #78909c;"

    html = f"""<div style="background: linear-gradient(145deg, #263238, #37474f); padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 10px; box-shadow: inset 0 2px 4px rgba(255,255,255,0.1), 0 4px 10px rgba(0,0,0,0.2);">
<div style="color: #cfd8dc; font-weight: 700; font-size: 11px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">{pump_name}</div>
<div style="background-color: #eceff1; border-radius: 8px; padding: 5px; margin-bottom: 12px; box-shadow: inset 0 2px 5px rgba(0,0,0,0.1); position: relative; height: 55px;">
<svg width="100%" height="100%" viewBox="0 0 100 65">
<path d="M 15 45 A 40 40 0 0 1 85 45" fill="none" stroke="#b0bec5" stroke-width="2"/>
<text x="15" y="58" font-size="10" fill="#546e7a" text-anchor="middle" font-weight="bold">0</text>
<text x="50" y="60" font-size="14" fill="#37474f" text-anchor="middle" font-weight="bold">A</text>
<text x="85" y="58" font-size="10" fill="#546e7a" text-anchor="middle" font-weight="bold">30</text>
<line x1="50" y1="58" x2="50" y2="12" stroke="#e53935" stroke-width="2.5" stroke-linecap="round" transform="rotate({needle_rot} 50 58)" style="transition: transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);"/>
<circle cx="50" cy="58" r="4" fill="#263238"/>
</svg>
</div>
<div style="display: flex; justify-content: space-evenly; align-items: center; margin-bottom: 5px;">
<div style="width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 8px; {on_glow} transition: 0.3s;">ON</div>
<div style="width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 8px; {off_glow} transition: 0.3s;">OFF</div>
</div>
</div>"""
    col_obj.markdown(html, unsafe_allow_html=True)
    bc1, bc2 = col_obj.columns(2)
    bc1.button("ON", key=f"btn_on_{state_key}", on_click=set_pump_state, args=(state_key, True), use_container_width=True)
    bc2.button("OFF", key=f"btn_off_{state_key}", on_click=set_pump_state, args=(state_key, False), use_container_width=True)

# 🎛️ ८. UI/UX: ॲनिमेटेड वाल्व्ह
def render_animated_valve(col_obj, valve_name, state_key):
    is_on = st.session_state[state_key]
    handle_rot = 90 if is_on else 0 
    handle_color = "#00c853" if is_on else "#d50000"
    status_text = "OPEN" if is_on else "CLOSED"
    
    html = f"""<div style="text-align: center; margin-bottom: 5px;">
<div style="font-size: 11px; font-weight: 700; color: #546e7a; margin-bottom: 8px; text-transform: uppercase;">{valve_name}</div>
<svg width="60" height="90" viewBox="0 0 60 90" style="filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.1));">
<rect x="22" y="0" width="16" height="90" fill="#b0bec5" />
<polygon points="15,25 45,25 50,45 45,65 15,65 10,45" fill="#eceff1" stroke="#90a4ae" stroke-width="1.5"/>
<rect x="18" y="20" width="24" height="50" fill="#ffffff" rx="4" stroke="#90a4ae" stroke-width="1"/>
<g transform="rotate({handle_rot} 30 45)" style="transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);">
<path d="M 35 40 L 5 40 C 2 40 0 42 0 45 C 0 48 2 50 5 50 L 35 50 Z" fill="{handle_color}" />
<circle cx="30" cy="45" r="7" fill="#ffffff" stroke="#cfd8dc" stroke-width="2"/>
<circle cx="30" cy="45" r="3" fill="#546e7a" />
</g>
</svg>
<div style="font-size: 12px; font-weight: 800; color: {handle_color}; margin-top: 4px; letter-spacing: 1px;">{status_text}</div>
</div>"""
    col_obj.markdown(html, unsafe_allow_html=True)
    col_obj.toggle("Toggle", key=state_key, label_visibility="collapsed")

# ---------------------------------------------------------
# 🧠 ९. मुख्य लॉजिक
# ---------------------------------------------------------
trigger_siren = st.session_state.alarm_armed and simulate_motion
ug_pump = st.session_state['ug_pump']
bw1_pump = st.session_state['bw1_pump']
bw2_pump = st.session_state['bw2_pump']
valve_t1 = st.session_state['valve_t1']
valve_t2 = st.session_state['valve_t2']
valve_ug = st.session_state['valve_ug']

any_pump_on = ug_pump or bw1_pump or bw2_pump
any_borewell_on = bw1_pump or bw2_pump
tank1_pouring = valve_t1 and any_pump_on
tank2_pouring = valve_t2 and any_pump_on
ug_pouring_from_bw = valve_ug and any_borewell_on
ug_pouring_from_tanker = sim_tanker
garden_watering = ug_pump and not valve_t1 and not valve_t2
is_any_water_pouring = tank1_pouring or tank2_pouring or ug_pouring_from_bw or ug_pouring_from_tanker or garden_watering

# १०. मुख्य डॅशबोर्ड लेआउट (UI Adjustments)
st.markdown("<div style='margin-top: -20px;'></div>", unsafe_allow_html=True)
col_left, col_right = st.columns([1.4, 1.1], gap="large")

with col_right:
    status_board = st.empty()

    # 🛡️ सुरक्षा प्रणाली (Clean UI)
    with st.container(border=True):
        st.markdown("<div style='display:flex; align-items:center; justify-content:space-between; margin-bottom: 10px;'><h5 style='margin: 0; color: #c2185b; font-weight: 800;'>🛡️ सुरक्षा प्रणाली</h5></div>", unsafe_allow_html=True)
        st.session_state.alarm_armed = st.toggle("🚨 अलार्म सिस्टीम (Arm/Disarm)", value=st.session_state.alarm_armed)

    # ☀️ सोलर ऊर्जा (Premium UI - Compact Button included)
    with st.container(border=True):
        cp = st.session_state.real_solar_power
        dk = st.session_state.real_solar_daily
        is_gen = cp > 0
        is_off = "OFFLINE" in st.session_state.inverter_status
        
        d_pow = f"{cp:.2f} kW"
        d_day = f"{int(dk * 1000)} Wh" if dk < 1.0 else f"{dk:.2f} kWh"

        if not st.session_state.is_solar_live:
            glow, line, s_col, s_txt, badge = "border: 1px solid #e0e0e0;", "background: #cfd8dc;", "#78909c", "🔄 कृपया 'लाईव्ह डेटा रिफ्रेश करा' दाबा", "<span style='background:#9e9e9e; color:white; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 700;'>⏳ PENDING</span>"
        elif is_off:
            glow, line, s_col, s_txt, badge = "border: 1px solid #cfd8dc; background: #fafafa;", "background: #cfd8dc;", "#78909c", "🌙 इन्व्हर्टर स्लीप मोड (ऑफलाइन)", "<span style='background:#78909c; color:white; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 700;'>🌙 OFFLINE</span>"
        else:
            glow = "animation: sunGlow 3s infinite; border: 1px solid #fbc02d;" if is_gen else "border: 1px solid #e0e0e0;"
            line = "background-image: repeating-linear-gradient(90deg, #4caf50 0px, #4caf50 10px, transparent 10px, transparent 20px); background-size: 20px 100%; animation: energyFlow 0.5s linear infinite;" if is_gen else "background: #cfd8dc;"
            s_col, s_txt = ("#2e7d32", "🟢 निर्मिती सुरू आहे (Live)") if is_gen else ("#c62828", "🔴 निर्मिती 0 W आहे")
            badge = "<span style='background:#4CAF50; color:white; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: 700; box-shadow: 0 2px 5px rgba(76,175,80,0.3);'>🟢 LIVE</span>"

        s_svg = """<svg width="40" height="40" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="12" fill="#FFca28"/><polyline points="75,90 85,90 80,40" fill="none" stroke="#90a4ae" stroke-width="4"/><polygon points="35,85 45,35 85,30 70,80" fill="#1976d2" stroke="#e3f2fd" stroke-width="2"/><line x1="40" y1="60" x2="77" y2="55" stroke="#90caf9" stroke-width="1.5"/><line x1="53" y1="35" x2="42" y2="82" stroke="#90caf9" stroke-width="1.5"/><line x1="68" y1="32" x2="57" y2="80" stroke="#90caf9" stroke-width="1.5"/></svg>"""
        g_svg = """<svg width="35" height="35" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><polyline points="50,10 30,90" fill="none" stroke="#546e7a" stroke-width="3"/><polyline points="50,10 70,90" fill="none" stroke="#546e7a" stroke-width="3"/><line x1="45" y1="30" x2="55" y2="30" stroke="#546e7a" stroke-width="3"/><line x1="40" y1="50" x2="60" y2="50" stroke="#546e7a" stroke-width="3"/><line x1="35" y1="70" x2="65" y2="70" stroke="#546e7a" stroke-width="3"/><line x1="45" y1="30" x2="60" y2="50" stroke="#546e7a" stroke-width="2"/><line x1="55" y1="30" x2="40" y2="50" stroke="#546e7a" stroke-width="2"/><line x1="40" y1="50" x2="65" y2="70" stroke="#546e7a" stroke-width="2"/><line x1="60" y1="50" x2="35" y2="70" stroke="#546e7a" stroke-width="2"/><line x1="25" y1="30" x2="75" y2="30" stroke="#546e7a" stroke-width="3"/><line x1="20" y1="50" x2="80" y2="50" stroke="#546e7a" stroke-width="3"/></svg>"""

        st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 15px;'><h5 style='margin: 0; color: #f57f17; font-weight: 800;'>☀️ सोलर ऊर्जा</h5>{badge}</div>", unsafe_allow_html=True)
        
        st.markdown(f"<div style='display: flex; justify-content: space-around; background: #fffde7; border-radius: 12px; padding: 15px 0; margin-bottom: 15px; {glow}'><div style='text-align: center;'><div style='font-size: 12px; color: #7f8c8d; text-transform:uppercase; font-weight:600;'>सध्याची निर्मिती</div><div style='font-size: 24px; font-weight: 900; color: #2e7d32;'>{d_pow}</div></div><div style='width: 1px; background: #e0e0e0;'></div><div style='text-align: center;'><div style='font-size: 12px; color: #7f8c8d; text-transform:uppercase; font-weight:600;'>आजची निर्मिती</div><div style='font-size: 24px; font-weight: 900; color: #1565c0;'>{d_day}</div></div></div>", unsafe_allow_html=True)
        
        st.markdown(f"<div style='display: flex; align-items: center; justify-content: space-between; padding: 10px; border-radius: 12px; border: 1px solid #ecf0f1; background: #fafafa;'><div style='text-align: center; width: 50px;'>{s_svg}<div style='font-size: 10px; font-weight: 700; color:#7f8c8d;'>Panels</div></div><div style='flex-grow: 1; height: 3px; margin: 0 10px; border-radius:3px; {line}'></div><div style='text-align: center; width: 40px;'><div style='font-size: 24px;'>🎛️</div><div style='font-size: 10px; font-weight: 700; color:#7f8c8d;'>Inverter</div></div><div style='flex-grow: 1; height: 3px; margin: 0 10px; border-radius:3px; {line}'></div><div style='text-align: center; width: 50px;'>{g_svg}<div style='font-size: 10px; font-weight: 700; color:#7f8c8d;'>Grid</div></div></div>", unsafe_allow_html=True)
        
        # ✨ UI/UX: Inline Compact Report Button
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        sc1, sc2 = st.columns([3, 2], vertical_alignment="center")
        with sc1: st.markdown(f"<div style='font-weight: 700; font-size: 13px; color: {s_col};'>{s_txt}</div>", unsafe_allow_html=True)
        with sc2:
            with st.popover("📊 रिपोर्ट", use_container_width=True):
                st.markdown("<h5 style='color: #6a1b9a; font-weight: 800; text-align:center; margin-bottom:15px;'>📊 सोलर अहवाल</h5>", unsafe_allow_html=True)
                t_day, t_mon, t_yr, t_tot = st.tabs(["Day", "Month", "Year", "Total"])
                with t_day: st.line_chart(st.session_state.chart_day, height=150) 
                with t_mon: st.bar_chart(st.session_state.chart_month, height=150)
                with t_yr: st.bar_chart(st.session_state.chart_year, height=150)
                with t_tot: st.line_chart(st.session_state.chart_total, height=150)

                t_kwh = st.session_state.real_solar_total
                st.markdown(f"""
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px;'>
                    <div style='background: #f8f9fa; padding: 12px; border-radius: 8px; border: 1px solid #eee; text-align:center;'>
                        <div style='font-size:11px; color:#7f8c8d; font-weight:700; text-transform:uppercase;'>⚡ Total (MWh)</div>
                        <div style='font-size:16px; font-weight:900; color:#2c3e50;'>{t_kwh/1000.0:.2f}</div>
                    </div>
                    <div style='background: #e8f5e9; padding: 12px; border-radius: 8px; border: 1px solid #c8e6c9; text-align:center;'>
                        <div style='font-size:11px; color:#2e7d32; font-weight:700; text-transform:uppercase;'>💰 Profit (INR)</div>
                        <div style='font-size:16px; font-weight:900; color:#1b5e20;'>₹ {int(t_kwh * 7.5):,}</div>
                    </div>
                    <div style='background: #e3f2fd; padding: 12px; border-radius: 8px; border: 1px solid #bbdefb; text-align:center;'>
                        <div style='font-size:11px; color:#1565c0; font-weight:700; text-transform:uppercase;'>☁️ CO2 Saved (t)</div>
                        <div style='font-size:16px; font-weight:900; color:#0d47a1;'>{0.000793 * t_kwh:.2f}</div>
                    </div>
                    <div style='background: #f1f8e9; padding: 12px; border-radius: 8px; border: 1px solid #dcedc8; text-align:center;'>
                        <div style='font-size:11px; color:#33691e; font-weight:700; text-transform:uppercase;'>🍃 Trees Planted</div>
                        <div style='font-size:16px; font-weight:900; color:#1b5e20;'>{int((t_kwh * 0.997)/18.3)}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ⚡ कंट्रोल पॅनल (Clean UI)
    with st.container(border=True):
        st.markdown("<h5 style='margin: 0 0 15px 0; color: #2c3e50; font-weight: 800;'>⚡ स्टार्टर कंट्रोल्स</h5>", unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        render_compact_starter(sc1, "UG PUMP", "ug_pump")
        render_compact_starter(sc2, "BW-1", "bw1_pump")
        render_compact_starter(sc3, "BW-2", "bw2_pump")

    # 🎛️ वाल्व्ह पॅनल (Clean UI)
    with st.container(border=True):
        st.markdown("<h5 style='margin: 0 0 15px 0; color: #2c3e50; font-weight: 800;'>🎛️ कॉक (Valves)</h5>", unsafe_allow_html=True)
        v1, v2, v3 = st.columns(3)
        with v1: render_animated_valve(v1, "Tank 1", "valve_t1")
        with v2: render_animated_valve(v2, "Tank 2", "valve_t2")
        with v3: render_animated_valve(v3, "UG Tank", "valve_ug")

    # 📋 स्थितीदर्शक (Clean UI)
    with status_board.container(border=True):
        st.markdown("<h5 style='margin: 0 0 10px 0; color: #1565c0; font-weight: 800;'>📋 लाइव्ह स्थिती</h5>", unsafe_allow_html=True)
        s_msgs = ["🚨 घुसखोर आढळला!"] if trigger_siren else []
        if not any_pump_on and not sim_tanker: s_msgs.append("⚠️ सर्व पंप बंद आहेत.")
        else:
            if ug_pump: s_msgs.append("🔸 UG पंप सुरू आहे.")
            if bw1_pump: s_msgs.append("🔸 बोअरवेल १ सुरू आहे.")
            if bw2_pump: s_msgs.append("🔸 बोअरवेल २ सुरू आहे.")
            if sim_tanker: s_msgs.append("🚚 टँकर पाणी सुरू.")
        if tank1_pouring: s_msgs.append("🔹 'Tank 1' भरत आहे.")
        if tank2_pouring: s_msgs.append("🔹 'Tank 2' भरत आहे.")
        if ug_pouring_from_bw: s_msgs.append("🔹 बोअरवेल -> UG Tank.")
        if garden_watering: s_msgs.append("🌿 गार्डनला पाणी सुरू.")
        
        html_li = "".join([f"<li style='margin-bottom: 4px;'>{m}</li>" for m in s_msgs])
        st.markdown(f"<ul style='font-size: 13px; color: #455a64; font-weight: 600; padding-left: 20px; margin:0;'>{html_li}</ul>", unsafe_allow_html=True)

with col_left:
    # 🌟 टाक्यांचे डिझाईन
    html_t1 = get_tank_html("Tank 1", 45, tank_type="overhead", inlets=[{"name": "Main Line", "active": tank1_pouring}])
    html_t2 = get_tank_html("Tank 2", 60, tank_type="overhead", inlets=[{"name": "Main Line", "active": tank2_pouring}])
    html_ug = get_tank_html("Underground Tank", 75, tank_type="underground", inlets=[{"name": "Borewell (V3)", "active": ug_pouring_from_bw}, {"name": "Tanker", "active": ug_pouring_from_tanker}])

    st.markdown(f"""
    <div style="display: flex; justify-content: space-around; width: 100%; gap: 20px;">
        <div style="flex: 1; display: flex; justify-content: center;">{html_t1}</div>
        <div style="flex: 1; display: flex; justify-content: center;">{html_t2}</div>
    </div>
    <div style="width: 100%; margin-top: 20px;">{html_ug}</div>
    """, unsafe_allow_html=True)

    g_act = "<div style='position: absolute; top: -30px; left: 50%; transform: translateX(-50%); width: 8px; height: 40px; background-image: repeating-linear-gradient(transparent, #4facfe 2px, transparent 6px); background-size: 100% 10px; animation: waterPour 0.3s infinite linear;'></div>" if garden_watering else ""
    st.markdown(f"<div style='margin-top: 25px; border: 2px solid #81c784; border-radius: 16px; background: linear-gradient(to right, #f1f8e9, #e8f5e9); padding: 20px; text-align: center; position: relative; box-shadow: 0 4px 15px rgba(0,0,0,0.05);'>{g_act}<div style='font-size: 45px;'>🌳🏡🌿</div><h4 style='color: #2e7d32; margin: 10px 0 0 0; font-weight:800;'>गार्डन / झाडे</h4><p style='font-size: 12px; color: #7cb342; margin: 0; font-weight:600;'>UG टाकीतून पाणी</p></div>", unsafe_allow_html=True)

st.markdown("<br><hr style='border: none; border-top: 1px solid #e0e6ed;'>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #2c3e50; text-align: center; font-weight:800;'>📹 सुरक्षा कॅमेरे</h3>", unsafe_allow_html=True)

c_style = "background: #111; height: 250px; border-radius: 16px; display: flex; align-items: center; justify-content: center; color: #555; font-family: monospace; border: 4px solid #333; position: relative; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.2);"
r_dot = "<div style='position: absolute; top: 15px; right: 15px; width: 12px; height: 12px; background-color: #ff5252; border-radius: 50%; animation: pulseRed 1s infinite; box-shadow: 0 0 10px #ff5252;'></div>"

cam1, cam2 = st.columns(2, gap="large")
with cam1: st.markdown(f"<div style='{c_style}'>{r_dot}CAM 01<br><br>RTSP Stream...</div><div style='text-align: center; font-weight: 700; margin-top: 10px; color: #546e7a;'>📍 मुख्य गेट</div>", unsafe_allow_html=True)
with cam2: st.markdown(f"<div style='{c_style}'>{r_dot}CAM 02<br><br>RTSP Stream...</div><div style='text-align: center; font-weight: 700; margin-top: 10px; color: #546e7a;'>📍 पार्किंग</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📢 ११. सायरन आणि 🕉️ पंचांग (UI/UX Upgrades)
# ---------------------------------------------------------
if trigger_siren:
    top_banner.markdown("<div class='flashing-alert'><h1 style='color: white; margin: 0; font-size: 36px; font-weight: 900; text-shadow: 2px 2px 10px rgba(0,0,0,0.5);'>🚨 सावधान! घुसखोर आढळला! 🚨</h1></div>", unsafe_allow_html=True)
    panchang_banner.empty()
    st.markdown("""<audio autoplay loop><source src="https://upload.wikimedia.org/wikipedia/commons/4/40/Siren_Noise.ogg" type="audio/ogg"><source src="https://actions.google.com/sounds/v1/alarms/burglar_alarm.ogg" type="audio/ogg"></audio>""", unsafe_allow_html=True)
else:
    top_banner.markdown("""
    <div class='normal-banner'>
        <h1 style='color: #ffffff; margin: 0; font-weight: 900; letter-spacing: 2px; text-shadow: 0 2px 5px rgba(0,0,0,0.3); font-size:32px;'>अभिप्राजामेयार्णव</h1>
        <h5 style='color: #b2ebf2; margin: 5px 0 0 0; font-weight: 600; letter-spacing: 1px;'>स्मार्ट होम मॅनेजमेंट सिस्टीम</h5>
    </div>
    """, unsafe_allow_html=True)
    
    tdy = datetime.now().date()
    v_nm = ["सोमवार", "मंगळवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
    t_vr = v_nm[tdy.weekday()]
    pan = get_panchang_details(tdy)
    
    f_htm = ""
    if pan["is_chaturthi"]:
        b64 = get_base64_image("ganpati.png")
        f_htm = f"<img src='data:image/png;base64,{b64}' width='30' style='border-radius:50%; margin-right:8px; box-shadow:0 2px 4px rgba(0,0,0,0.2);'> <span style='color:#c62828; font-weight:800;'>|| श्री गणेशाय नमः ||</span>" if b64 else "<span style='color:#c62828; font-weight:800;'>🐘 || श्री गणेशाय नमः ||</span>"
    elif pan["is_ekadashi"]:
        b64 = get_base64_image("vitthal.png")
        f_htm = f"<img src='data:image/png;base64,{b64}' width='30' style='border-radius:50%; margin-right:8px; box-shadow:0 2px 4px rgba(0,0,0,0.2);'> <span style='color:#1565c0; font-weight:800;'>|| राम कृष्ण हरी ||</span>" if b64 else "<span style='color:#1565c0; font-weight:800;'>🚩 || राम कृष्ण हरी ||</span>"

    with panchang_banner.container():
        p1, p2 = st.columns([5, 1], vertical_alignment="center")
        with p1:
            st.markdown(f"<div class='panchang-strip'><div style='font-size: 14px; color: #455a64; font-weight:600;'><b>{t_vr}</b> &nbsp;|&nbsp; <b>{pan['tithi']}</b></div><div style='display:flex; align-items:center;'>{f_htm}</div></div>", unsafe_allow_html=True)
        with p2:
            with st.popover("📅 पंचांग", use_container_width=True):
                st.markdown("<h5 style='text-align: center; color: #e67e22; font-weight:800;'>🕉️ पंचांग</h5>", unsafe_allow_html=True)
                sel_d = st.date_input("तारीख:", tdy, label_visibility="collapsed")
                s_pan = pan if sel_d == tdy else get_panchang_details(sel_d)
                
                st.markdown(f"<div style='text-align:center; font-size:13px; font-weight:800; color:#546e7a; margin: 10px 0;'>{sel_d.strftime('%d-%m-%Y')} ({v_nm[sel_d.weekday()]})</div>", unsafe_allow_html=True)
                st.markdown(f"""
                <table style="width:100%; border-collapse: collapse; font-size: 12px; background:#fff; border-radius:8px; overflow:hidden; box-shadow:0 1px 4px rgba(0,0,0,0.05);">
                  <tr style="background: #f8f9fa; border-bottom: 2px solid #eceff1;">
                    <th style="padding: 8px; color:#546e7a;">अंग</th>
                    <th style="padding: 8px; color:#546e7a;">नाव</th>
                    <th style="padding: 8px; text-align:center; color:#546e7a;">सुरुवात</th>
                    <th style="padding: 8px; text-align:center; color:#546e7a;">समाप्ती</th>
                  </tr>
                  <tr style="border-bottom: 1px solid #f1f3f4;">
                    <td style="padding: 8px;"><b>🌙 तिथी</b></td><td style="padding: 8px; color:#d35400; font-weight:700;">{s_pan['tithi']}</td><td style="padding: 8px; text-align:center; color:#78909c;">{s_pan['t_start']}</td><td style="padding: 8px; text-align:center; color:#78909c;">{s_pan['t_end']}</td>
                  </tr>
                  <tr style="border-bottom: 1px solid #f1f3f4;">
                    <td style="padding: 8px;"><b>✨ नक्षत्र</b></td><td style="padding: 8px; color:#d35400; font-weight:700;">{s_pan['nakshatra']}</td><td style="padding: 8px; text-align:center; color:#78909c;">{s_pan['n_start']}</td><td style="padding: 8px; text-align:center; color:#78909c;">{s_pan['n_end']}</td>
                  </tr>
                  <tr style="border-bottom: 1px solid #f1f3f4;">
                    <td style="padding: 8px;"><b>🧘 योग</b></td><td style="padding: 8px; color:#d35400; font-weight:700;">{s_pan['yoga']}</td><td style="padding: 8px; text-align:center; color:#78909c;">{s_pan['y_start']}</td><td style="padding: 8px; text-align:center; color:#78909c;">{s_pan['y_end']}</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px;"><b>🚩 करण</b></td><td style="padding: 8px; color:#d35400; font-weight:700;">{s_pan['karana']}</td><td style="padding: 8px; text-align:center; color:#78909c;">{s_pan['k_start']}</td><td style="padding: 8px; text-align:center; color:#78909c;">{s_pan['k_end']}</td>
                  </tr>
                </table>
                """, unsafe_allow_html=True)

if is_any_water_pouring and not trigger_siren:
    st.markdown("""<audio autoplay loop id="wAudio"><source src="https://actions.google.com/sounds/v1/water/stream_water.ogg" type="audio/ogg"></audio><script>document.getElementById("wAudio").volume=0.3;</script>""", unsafe_allow_html=True)

a_spk = ""
if trigger_siren: a_spk = "सावधान! घरात घुसखोर आढळला आहे."
elif (valve_t1 or valve_t2) and not any_pump_on: a_spk = "सावधान! वाल्व्ह उघडा आहे, पण पंप बंद आहे."
elif tank1_pouring and tank2_pouring: a_spk = "टाकी एक आणि टाकी दोन मध्ये पाणी भरत आहे."
elif tank1_pouring: a_spk = "टाकी एक मध्ये पाणी भरत आहे."
elif tank2_pouring: a_spk = "टाकी दोन मध्ये पाणी भरत आहे."
elif ug_pouring_from_bw or ug_pouring_from_tanker: a_spk = "अंडरग्राउंड टाकीत पाणी भरत आहे."
elif garden_watering: a_spk = "गार्डन मध्ये पाणी दिले जात आहे."

if 'l_spk' not in st.session_state: st.session_state.l_spk = ""
if a_spk == "": st.session_state.l_spk = ""
elif a_spk != st.session_state.l_spk:
    st.session_state.l_spk = a_spk
    components.html(f"<script>var m=new SpeechSynthesisUtterance('{a_spk}');m.lang='mr-IN';m.rate=0.95;window.speechSynthesis.speak(m);</script>", height=0, width=0)
