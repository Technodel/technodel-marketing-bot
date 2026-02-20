if st.button(f"✨ Generate Professional Offer"):
            with st.spinner("Analyzing technical specs & writing Lebanese post..."):
                # Get real specs from DuckDuckGo
                real_info = get_real_specs(target['name'])
                
                system_instructions = (
                    "You are a HIGH-END Tech Specialist at Technodel Lebanon. "
                    "Your goal is to sell based on TECHNICAL SUPERIORITY. "
                    "STRICT RULES:\n"
                    "1. Speak ONLY in professional Lebanese Ammiya (e.g., use 'mwasafet', 'kahraba', 'da22e').\n"
                    "2. You MUST extract at least 4-5 SPECIFIC technical features from the provided data (e.g., Watts, RPM, Material, Port types, Battery life).\n"
                    "3. Do NOT use generic marketing fluff like 'best quality'. Use hard facts.\n"
                    "4. Structure: ⚡ Title | 🛠️ Specs List | 💰 Price | ✅ Warranty/Delivery."
                )
                
                user_prompt = (
                    f"Product: {target['name']}\n"
                    f"Technical Raw Data: {real_info}\n"
                    f"Old Price: ${target['price']} | New Price: ${promo_price}\n"
                    "--- \n"
                    "Task: Create a high-conversion post. If the raw data contains details like "
                    "'1000W', 'Stainless Steel', or '4K resolution', you MUST list them clearly."
                )

                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": user_prompt}
                    ],
                )
                st.session_state.output = completion.choices[0].message.content
