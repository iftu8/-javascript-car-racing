import os, sys, json, time, re, urllib.request, urllib.error

def main():
    print("==================================================")
    print("🚀 INITIATING HYBRID AUTO-SCANNER ENGINE...")
    print("==================================================")
    
    # API Key Clean-up
    raw_key = os.environ.get("GEMINI_API_KEY", "")
    api_key = raw_key.replace("[", "").replace("]", "").replace('"', "").replace("'", "").strip()
    
    if not api_key:
        print("❌ CRITICAL ERROR: GEMINI_API_KEY is missing!")
        sys.exit(1)

    issue_title = os.environ.get("ISSUE_TITLE", "Game Update")
    issue_body = os.environ.get("ISSUE_BODY", "Update features")
    file_path = "index.html"
    
    current_code = ""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            current_code = f.read()

    # 🛡️ URL Building Blocks (Prevents Markdown Link Bug)
    scheme = "https"
    domain = "generativelanguage.googleapis.com"
    
    # ==========================================
    # STEP 1: DYNAMICALLY SCAN FOR ALLOWED MODELS
    # ==========================================
    print("\n📡 Scanning Google Servers for your allowed models...")
    list_url = f"{scheme}://{domain}/v1beta/models?key={api_key}"
    
    try:
        req = urllib.request.Request(list_url)
        with urllib.request.urlopen(req) as response:
            models_data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ ERROR: Failed to fetch model list: {e}")
        sys.exit(1)

    available_models = []
    for m in models_data.get("models", []):
        name = m.get("name", "")
        if "generateContent" in m.get("supportedGenerationMethods", []):
            # Ignore non-coding/vision models
            if "image" not in name and "vision" not in name and "audio" not in name:
                # Extract clean name if it starts with 'models/'
                clean_name = name.replace("models/", "")
                available_models.append(clean_name)

    if not available_models:
        print("❌ ERROR: No active text/coding models found for your API key.")
        sys.exit(1)

    print(f"✅ Found {len(available_models)} compatible models!")

    prompt = f"""You are an elite, senior game developer. Refactor, upgrade, and add features to the HTML5 game based on the GitHub issue below.
    
    Issue Title: {issue_title}
    Issue Description: {issue_body}
    
    Current Code:
    {current_code}
    
    STRICT RULES:
    1. Return ONLY valid, optimized HTML/CSS/JS code. No explanations.
    2. DO NOT output ```html markdown blocks.
    3. Start exactly with <!DOCTYPE html> and end with </html>.
    4. Everything must remain in a single file (`index.html`).
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8192}
    }
    data = json.dumps(payload).encode('utf-8')
    headers = {"Content-Type": "application/json"}

    # ==========================================
    # STEP 2: TRY ALLOWED MODELS ONE BY ONE
    # ==========================================
    success = False
    for model in available_models:
        print(f"\n📡 Requesting Code via Model: {model} ...")
        
        url = f"{scheme}://{domain}/v1beta/models/{model}:generateContent?key={api_key}"
        
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=1200) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            new_code = result["candidates"][0]["content"]["parts"][0]["text"]
            new_code = re.sub(r'^```(html|javascript|css)?\s*', '', new_code, flags=re.IGNORECASE)
            new_code = re.sub(r'```$', '', new_code.strip())

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_code)
                
            print(f"🎉 SUCCESS! Game beautifully engineered using {model}!")
            success = True
            break 

        except urllib.error.HTTPError as e:
            print(f"⚠️ Failed with {model} (HTTP {e.code}). Moving to next...")
        except Exception as e:
            print(f"❌ Error with {model}: {e}")

    if not success:
        print("\n🚨 CRITICAL: All available models failed! Quota might be empty.")
        sys.exit(1)

if __name__ == "__main__":
    main()
