# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import random # सिम्युलेशनसाठी

st.set_page_config(page_title="Deogirkar Water Monitor", page_icon="💧", layout="wide")
st.title("💧 The Deogirkars' Smart Water Dashboard")
st.markdown("---")

# १. ॲनिमेटेड टाकी आणि नळ बनवण्याचे प्रगत फंक्शन
def draw_tank(tank_name, level_cm, max_height_cm=100, tank_type="overhead", is_filling=False):
    percentage = min(int((level_cm / max_height_cm) * 100), 100)
    water_color = "#00b4d8" if tank_type == "overhead" else "#0077b6"
    border_color = "#333" if tank_type == "overhead" else "#8B4513"
    
    # नळ आणि पाण्याच्या ॲनिमेशनचा HTML
    filling_animation = f"""
        <div style="position: absolute; top: -30px; left: 50%; transform: translateX(-50%); width: 40px; height: 30px; background-color: silver; border-radius: 5px; z-index: 2;"></div>
        <div style="position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 10px; height: 180px; background-image: repeating-linear-gradient(transparent, #00b4d8 5px, transparent 10px); background-size: 100% 20px; animation: pourWater 1s infinite linear; z-index: 1;"></div>
        
        <style>
            @keyframes pourWater {{
                from {{ background-position: 0 0; }}
                to {{ background-position: 0 100%; }}
            }}
        </style>
    """ if is_filling else ""

    html_code = f"""
    <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 20px;">
        <h4 style="color: #333; margin-bottom: 10px; font-family: sans-serif;">{tank_name}</h4>
        <div style="width: 140px; height: 200px; border: 4px solid {border_color}; border-radius: 12px; background-color: #e0e0e0; position: relative; overflow: visible; box-shadow: 5px 5px 15px rgba(0,0,0,0.2);">
            {filling_animation}
            <div style="position: absolute; bottom: 0; width: 100%; height: {percentage}%; background-color: {water_color}; transition: height 1.5s ease-in-out; display: flex; align-items: center; justify-content: center; z-index: 3;">
                <span style="color: white; font-weight: bold; font-size: 22px; font-family: sans-serif; text-shadow: 1px 1px 2px black;">{percentage}%</span>
            </div>
        </div>
        <p style="margin-top: 8px; font-weight: bold; color: #555;">पाण्याची पातळी: {level_cm} cm</p>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# २. स्थिती फलक (Status Board) बनवण्याचे फंक्शन
def draw_status_board(status_messages):
    messages_html = ""
    for msg in status_messages:
        messages_html += f"""
        <li style="margin-bottom: 8px; font-size: 16px; font-family: sans-serif;">• {msg}</li>
        """
    
    html_code = f"""
    <div style="border: 2px solid #555; border-radius: 10px; padding: 15px; background-color: #f9f9f9; width: 300px; margin-top: 20px; box-shadow: 3px 3px 10px rgba(0,0,0,0.1);">
        <h4 style="color: #333; text-align: center; border-bottom: 2px solid #ddd; padding-bottom: 10px; margin-bottom: 15px;">📊 स्थिती फलक</h4>
        <p style="font-weight: bold; color: green; margin-bottom: 15px; text-align: center;">सिस्टम चालू आणि कार्यरत आहे.</p>
        <ul style="list-style-type: none; padding-left: 0;">
            {messages_html}
        </ul>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# ३. गुगल शीटमधून डेटा वाचणे (सिम्युलेशनसाठी आपण रँडम आकडे घेऊया)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1oys9fFlUwlwiw1dzYwWMbu0AiZuCszwPLzZWpb34_rA/edit?usp=sharing"
csv_url = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')

try:
    df = pd.read_csv(csv_url, encoding='utf-8')
    latest_data = df.iloc[-1]
    
    # थेट रकाण्यांच्या नंबरवरून डेटा घेणे
    tank1_lvl = int(latest_data.iloc[3]) if pd.notna(latest_data.iloc[3]) else random.randint(30, 70)
    tank2_lvl = int(latest_data.iloc[5]) if pd.notna(latest_data.iloc[5]) else random.randint(40, 80)
    underground_lvl = random.randint(60, 95) 
    water_source = str(latest_data.iloc[9]) if pd.notna(latest_data.iloc[9]) else "Borewell 1"

    # ४. आपण आत्ता टेस्ट करण्यासाठी 'टाकी १' भरत आहोत असे ठरवूया (is_filling=True)
    st.subheader("🚰 लाईव्ह कंट्रोल पॅनेल")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        # टाकी १ भरत आहे (is_filling=True)
        draw_tank("छतावरील टाकी १", tank1_lvl, max_height_cm=100, tank_type="overhead", is_filling=True)
    with col2:
        # टाकी २ शांत आहे (is_filling=False)
        draw_tank("छतावरील टाकी २", tank2_lvl, max_height_cm=100, tank_type="overhead", is_filling=False)
    with col3:
        # अंडरग्राउंड टाकी (is_filling=False)
        draw_tank("अंडरग्राउंड टाकी", underground_lvl, max_height_cm=100, tank_type="underground", is_filling=False)

    st.markdown("---")
    
    # ५. स्थिती फलक आणि कंट्रोल पॅनेल
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 शेवटच्या काही नोंदी (Logs)")
        st.dataframe(df.tail(3))
        
    with col2:
        # तुमच्या अपेक्षेप्रमाणे मराठी बुलेट पॉइंट्समधील मेसेजेस
        status_msgs = [
            f"बोअरवेल १ पंप चालू.",
            f"पाणी 'टाकी १' मध्ये भरत आहे.",
            f"वाल्व २ (टाकी १) चालू आहे.",
            f"अंडरग्राउंड टाकीची पातळी {underground_lvl}%.",
            f"सिस्टममध्ये कोणताही दोष नाही.",
            f"पुढील देखभाल दिनांक: ३० मार्च."
        ]
        draw_status_board(status_msgs)

except Exception as e:
    st.error(f"डेटा वाचण्यात अडचण आली. Error: {e}")
