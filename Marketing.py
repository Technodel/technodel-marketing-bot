import streamlit as st
import pandas as pd
import openpyxl
import random
import google.generativeai as genai
import os

# --- 1. SETUP & AI CONFIG ---
# Replace with your actual Gemini API Key
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Technodel Marketing Bot", page_icon="📱")

# CSS for better Right-to-Left (RTL) text support for Arabic
st.markdown("""
    <style>
    .arabic-text { text-align: right; direction: rtl; font-family: 'Arial'; }
    .stTextArea textarea { text-align: right; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADING (Same logic as your Builder) ---
def load_all_items(file_path):
    all_products = []
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        if "HARDWARE" in wb.sheetnames:
            ws = wb["HARDWARE"]
            for row in ws.iter_rows(min_row=2):
                name = row[0].value
                price = row[1].value
                # Only pick rows that have a valid name and a price > 0
                if name and isinstance(price, (int, float)) and price > 0:
                    all_products.append({"ITEM": name, "PRICE": price})
    except Exception as e:
        st.error(f"Error loading Excel: {e}")
    return all_products

# --- 3. AI PROMPT (The "Magic" for TikTok) ---
def generate_arabic_offer(item_name, original_price, discount_price):
    prompt = f"""
    You are a viral social media manager for 'Technodel', a famous computer shop in Lebanon.
    Write a TikTok post in Lebanese Arabic (using Arabic script) for this product: {item_name}.
    
    Prices:
    - Original: ${original_price}
    - Sale Price (after 5% discount): ${discount_price}
    
    Structure the response as follows:
    1. A 'Hook' (خطة تسويقية) that grabs attention immediately.
    2. A brief, high-energy description of the product.
    3. Mention the 1-year warranty and 24-hour pickup at Technodel.
    4. Call to Action: 'DM us or visit Technodel.net'.
    5. Use lots of emojis (🔥, 💻, 🚀).
    6. Include hashtags: #Technodel #Lebanon #Gaming #Offers #بسي_جي
    
    Make it sound modern, friendly, and exciting!
    """
    response = model.generate_content(prompt)
    return response.text

# --- 4. APP UI ---
st.title("📱 Technodel TikTok Bot")
st.write("Generate viral Arabic offers from your Excel data.")

# File Selection (reusing your file logic)
base_path = os.path.dirname(os.path.abspath(__file__))
files = [f for f in os.listdir(base_path) if f.endswith(('.xlsx', '.xlsm'))]

if files:
    selected_file = st.selectbox("Select Database", files)
    file_path = os.path.join(base_path, selected_file)
    
    if st.button("🎲 Pick a Random Product"):
        products = load_all_items(file_path)
        if products:
            st.session_state.marketing_item = random.choice(products)
            st.session_state.marketing_done = False
        else:
            st.error("No valid products found in the 'HARDWARE' sheet.")

    if 'marketing_item' in st.session_state:
        item = st.session_state.marketing_item
        orig_p = item['PRICE']
        disc_p = int(orig_p * 0.95) # 5% Discount
        
        st.info(f"📍 **Selected:** {item['ITEM']} | **Price:** ${orig_p}")
        
        if st.button(f"✨ Generate Arabic Offer for ${disc_p}"):
            with st.spinner("Writing your Arabic TikTok post..."):
                offer = generate_arabic_offer(item['ITEM'], orig_p, disc_p)
                st.session_state.final_offer_arabic = offer
                st.session_state.marketing_done = True

    if st.session_state.get('marketing_done'):
        st.subheader("📝 Your TikTok Content:")
        st.text_area("Copy and Paste:", st.session_state.final_offer_arabic, height=400)
        st.caption("Tip: You can edit the text before copying it!")

else:
    st.warning("Please upload your hardware Excel file to the app folder.")