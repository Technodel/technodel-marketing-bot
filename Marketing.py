import streamlit as st
import pandas as pd
import random
from groq import Groq
from duckduckgo_search import DDGS

# --- 1. UI SETTINGS (MUST BE FIRST) ---
st.set_page_config(page_title="Technodel Marketing Bot 📱", layout="wide")

# --- 2. AI & STATE SETUP ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# Initialize greeting in session state so it only changes on 'Pick Random'
if 'greeting' not in st.session_state:
    st.session_state.greeting = "يا هلا بـ زنوبة، منقيّلك شي عالمي لليوم! ✨"

# --- 3. DATA LOADING ---
def load_data_from_gsheets():
    try:
        base_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        csv_url = f"{base_url.rstrip('/')}/export?format=csv"
        df = pd.read_csv(csv_url)
        all_items = []
        # Row 4 logic: skip index 0 and 1. B=1 (Name), C=2 (Price)
        for index, row in df.iloc[2:].iterrows():
            name_val = row.iloc[1]   
            price_val = row.iloc[2]  
            if pd.notna(name_val) and pd.notna(price_val):
                try:
                    clean_price = str(price_val).replace('$', '').replace(',', '').strip()
                    price = int(round(float(clean_price), 0))
                    all_items.append({"name": str(name_val), "price": price})
                except: continue
        return all_items
    except Exception as e:
        st.error(f"⚠️ Connection check: {e}")
        return []

def get_real_specs(product_name):
    try:
        with DDGS() as ddgs:
            query = f"{product_name} full technical specifications features TGP wattage"
            results = [r['body'] for r in ddgs.text(query, max_results=5)]
            return "\n".join(results)
    except: return "No detailed info found online."

# --- 4. STYLING ---
st.markdown("""
    <style>
    .arabic-output { 
        direction: rtl; text-align: right; background-color: #ffffff; 
        padding: 25px; border-radius: 15px; border: 1px solid #eef2f6; 
        font-family: 'Arial'; line-height: 1.8; color: #1a1a1a; font-size: 1.15em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. MAIN UI ---
st.image("https://technodel.net/wp-content/uploads/2024/08/technodel-site-logo-01.webp", width=150)
st.title("Technodel Marketing Bot")

items = load_data_from_gsheets()

col1, col2 = st.columns([1, 2])

with col1:
    if st.button("🎲 Pick Random Product"):
        if items:
            st.session_state.target = random.choice(items)
            st.session_state.output = None
            greetings = [
                "يا هلا بـ زنوبة، هيدا العرض صار جاهز! ✨",
                "أهلا زنوب، نقّينا لك قطعة ولا أروع، شوفي العرض: 🔥",
                "يسعد هالمسا يا زينب، هيدا الوحش رح يطير ع السريع! 🚀",
                "بونجور زينب، هيدا عرض بيكسر الأرض، جاهز للنشر: 📱",
                "يا هلا بـ ستّ الكل، هيدا المنتج لليوم، شو رأيك؟ 🌟"
            ]
            st.session_state.greeting = random.choice(greetings)
        else:
            st.warning("Sheet is empty.")

    if 'target' in st.session_state:
        target = st.session_state.target
        promo_price = int(round(target['price'] * 0.95, 0))
        st.success(f"📦 Selected: {target['name']}")
        
        if st.button("✨ Generate Professional Post"):
            with st.spinner("Writing like a Tech Guru..."):
                real_info = get_real_specs(target['name'])
                
                system_instructions = (
                    "You are a HIGH-END Tech Guru at Technodel Lebanon. "
                    "Rule 1: STRICT Lebanese Ammiya. No formal Arabic. No 'Finglish' translations. "
                    "Rule 2: Use PRO tech terms (e.g., 'RTX 5090', 'OLED 240Hz', 'NVMe Gen5'). "
                    "Rule 3: Focus on PERFORMANCE. Why is this machine a beast? Talk about FPS, Rendering, and Power. "
                    "Rule 4: Structure with Emojis: 🔥 Title | 🚀 Performance | 🖥️ Display | 💰 Price."
                )
                
                user_prompt = (
                    f"Product: {target['name']}\n"
                    f"Web Intel: {real_info}\n"
                    f"Price: ${promo_price} (Was ${target['price']})\n"
                    "Task: Write an aggressive, professional, and exciting post. "
                    "Ignore the column headers 'Sia Al-Dhakira' and use 'RAM' or 'Memory'. "
                    "Make it sound like the best deal in Lebanon."
                )

                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": user_prompt}
                    ],
                )
                st.session_state.output = completion.choices[0].message.content

with col2:
    if st.session_state.get('output'):
        st.subheader(st.session_state.greeting)
        formatted_text = st.session_state.output.replace('\n', '<br>')
        st.markdown(f'<div class="arabic-output">{formatted_text}</div>', unsafe_allow_html=True)
