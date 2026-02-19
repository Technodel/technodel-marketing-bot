import streamlit as st
import pandas as pd
import random
from groq import Groq
from duckduckgo_search import DDGS

# --- 1. AI SETUP ---
# We pull the API key and the URL from your [connections.gsheets] block
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# --- 2. THE STURDY GOOGLE SHEETS LOGIC ---
def load_data_from_gsheets():
    try:
        # Get the base URL from your secrets
        base_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        
        # We force Google to export the 'search' tab as a CSV
        # This is the most reliable way to avoid 404/400 errors
        csv_url = f"{base_url.rstrip('/')}/export?format=csv&sheet=search"
        
        df = pd.read_csv(csv_url)
        
        all_items = []
        # Row 4 logic (iloc index 2). Name is Col B (1), Price is Col C (2)
        for index, row in df.iloc[2:].iterrows():
            name_val = row.iloc[1]   
            price_val = row.iloc[2]  
            
            if pd.notna(name_val) and pd.notna(price_val):
                try:
                    # Clean price: remove $, commas, and handle decimals
                    clean_price = str(price_val).replace('$', '').replace(',', '').strip()
                    price = int(round(float(clean_price), 0))
                    all_items.append({"name": str(name_val), "price": price})
                except: continue
        return all_items
    except Exception as e:
        st.error(f"⚠️ Still having trouble: {e}")
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
st.set
