import streamlit as st
import pandas as pd
import random
from groq import Groq
from duckduckgo_search import DDGS
from streamlit_gsheets import GSheetsConnection

# --- 1. AI SETUP ---
# We pull only the Groq Key here; the Sheet URL is handled by the connection tool
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# --- 2. GOOGLE SHEETS LOGIC ---
def load_data_from_gsheets():
    try:
        # This automatically looks for [connections.gsheets] in your secrets
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Read the sheet (ttl=600 keeps it fresh for 10 mins) [cite: 2026-02-19]
        df = conn.read(ttl=600)
        
        all_items = []
        # Logic: Start from Row 4 (index 2). Name is Column B (1), Price is Column C (2) [cite: 2026-02-16]
        for index, row in df.iloc[2:].iterrows():
            name_val = row.iloc[1]   
            price_val = row.iloc[2]  
            
            if pd.notna(name_val) and pd.notna(price_val):
                try:
                    # Clean the price string to make it a number
                    price = int(round(float(str(price_val).replace('$', '').replace(',', '')), 0))
                    all_items.append({"name": str(name_val), "price": price})
                except: continue
        return all_items
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return []

# --- 3. WEB SEARCH ---
def get_real_specs(product_name):
    try:
        with DDGS() as ddgs:
            query = f"{product_name} technical specifications highlights"
            results = [r['body'] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results)
    except: return "No web info found."

# --- 4. UI SETTINGS ---
st.set_page_config(page_title="Technodel Marketing Bot 📱", layout="wide")

# Custom CSS for the Lebanese output box
st.markdown("""
    <style>
    .arabic-output { 
        direction: rtl; text-align: right; background-color: #ffffff; 
        padding: 25px; border-radius: 15px; border: 1px solid #eef2f6; 
        font-family: 'Arial'; line-height: 1.8; color: #1a1a1a; font-size: 1.15em;
    }
    </style>
    """, unsafe_allow_html=True)

# Logo & Header
st.image("https://technodel.net/wp-content/uploads/2024/08/technodel-site-logo-01.webp", width=150)
st.title("Technodel Marketing Bot")

# --- 5. MAIN LOGIC ---
items = load_data_from_gsheets()

col1, col2 = st.columns([1, 2])

with col1:
    if st.button("🎲 Pick Random Product from Sheet"):
        if items:
            st.session_state.target = random.choice(items)
            st.session_state.output = None
            st.session_state.greeting = "يا هلا بـ زنوبة، هيدا العرض صار جاهز! ✨"
        else:
            st.warning("Could not find any items in the sheet. Check your Google Sheet structure.")

    if 'target' in st.session_state:
        target = st.session_state.target
        promo_price = int(round(target['price'] * 0.95, 0))
        
        st.success(f"📦 Selected: {target['name']}")
        st.info(f"💰 Current Price: ${target['price']}")
        
        if st.button(f"✨ Generate Offer (${promo_price})"):
            with st.spinner("Searching specs & writing in Lebanese..."):
                real_info = get_real_specs(target['name'])
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a Lebanese tech salesman. Speak ONLY in Lebanese Arabic (Ammiya)."},
                        {"role": "user", "content": f"Create a post for {target['name']}. Old price: ${target['price']}, New price: ${promo_price}. Specs: {real_info}. Include 1-year warranty and 24h pickup."}
                    ],
                )
                st.session_state.output = completion.choices[0].message.content

with col2:
    if st.session_state.get('output'):
        st.subheader(st.session_state.greeting)
        formatted_text = st.session_state.output.replace('\n', '<br>')
        st.markdown(f'<div class="arabic-output">{formatted_text}</div>', unsafe_allow_html=True)
