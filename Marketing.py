import streamlit as st
import pandas as pd
import random
from groq import Groq
from duckduckgo_search import DDGS

# --- 1. UI SETTINGS (MUST BE THE FIRST ST COMMAND) ---
st.set_page_config(page_title="Technodel Marketing Bot 📱", layout="wide")

# --- 2. AI & STATE SETUP ---
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# Session state to keep greeting fixed until "Pick Random" is clicked
if 'greeting' not in st.session_state:
    st.session_state.greeting = "يا هلا بـ زنوبة، منقيّلك شي عالمي لليوم! ✨"

# --- 3. GOOGLE SHEETS LOADING ---
def load_data_from_gsheets():
    try:
        base_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # Direct CSV export is the most reliable method for your link
        csv_url = f"{base_url.rstrip('/')}/export?format=csv"
        df = pd.read_csv(csv_url)
        
        all_items = []
        # Row 4 logic: index 2. Name is Col B (1), Price is Col C (2) [2026-02-16]
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

# --- 4. DEEP WEB SEARCH ---
def get_real_specs(product_name):
    try:
        with DDGS() as ddgs:
            # Query focused on technical datasheets
            query = f"{product_name} official technical specifications datasheet features"
            results = [r['body'] for r in ddgs.text(query, max_results=5)]
            return "\n".join(results)
    except: return "No detailed info found online."

# --- 5. STYLING ---
st.markdown("""
    <style>
    .arabic-output { 
        direction: rtl; text-align: right; background-color: #ffffff; 
        padding: 30px; border-radius: 20px; border: 2px solid #f0f2f6; 
        font-family: 'Arial'; line-height: 1.8; color: #1a1a1a; font-size: 1.2em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 6. MAIN UI ---
st.image("https://technodel.net/wp-content/uploads/2024/08/technodel-site-logo-01.webp", width=150)
st.title("Technodel Marketing Bot")

items = load_data_from_gsheets()

col1, col2 = st.columns([1, 2])

with col1:
    if st.button("🎲 Pick Random Product"):
        if items:
            st.session_state.target = random.choice(items)
            st.session_state.output = None
            
            # Random Greetings list
            greetings = [
                "يا هلا بـ زنوبة، هيدا العرض صار جاهز! ✨",
                "أهلا زنوب، نقّينا لك قطعة ولا أروع، شوفي العرض: 🔥",
                "يسعد هالمسا يا زينب، هيدا الوحش رح يطير ع السريع! 🚀",
                "بونجور زينب، هيدا عرض بيكسر الأرض، جاهز للنشر: 📱",
                "يا هلا بـ ستّ الكل، هيدا المنتج لليوم، شو رأيك؟ 🌟"
            ]
            st.session_state.greeting = random.choice(greetings)
        else:
            st.warning("Sheet is empty or connection failed.")

    if 'target' in st.session_state:
        target = st.session_state.target
        promo_price = int(round(target['price'] * 0.95, 0))
        st.success(f"📦 Selected: {target['name']}")
        
        if st.button("✨ Generate Professional Post"):
            with st.spinner("Analyzing hardware specs..."):
                real_info = get_real_specs(target['name'])
                
                # STRICT AI PERSONALITY [2026-02-20]
                system_instructions = (
                    "You are a Senior Tech Guru at Technodel Lebanon. "
                    "Rule 1: Write ONLY in Arabic Script. Never use Latin/Franco letters. "
                    "Rule 2: Speak in professional Lebanese Ammiya. "
                    "Rule 3: Keep technical terms in English (e.g., 4K, OLED, RTX 5090, HDMI 2.1, SSD). "
                    "Rule 4: DO NOT translate tech terms into Arabic words like 'Siyeha'. "
                    "Rule 5: Focus on technical facts (Watts, Refresh Rate, Resolution). "
                    "Rule 6: Structure: 🔥 Catchy Title | 🚀 Performance Details | 💰 Special Price."
                )
                
                user_prompt = (
                    f"Product Name: {target['name']}\n"
                    f"Web Intel: {real_info}\n"
                    f"Discounted Price: ${promo_price} (Original: ${target['price']})\n"
                    "Instructions: Identify the product type (TV, Laptop, etc.). "
                    "Extract the real hardware specs from the Web Intel and list them clearly in a professional Lebanese post. "
                    "Ignore 'Warranty' and 'Delivery' - focus on hardware power."
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
        # Convert newlines to HTML breaks for proper display
        formatted_text = st.session_state.output.replace('\n', '<br>')
        st.markdown(f'<div class="arabic-output">{formatted_text}</div>', unsafe_allow_html=True)
