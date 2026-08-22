import os, sys, json, time, re, urllib.request, urllib.error

def main():
    print("==================================================")
    print("🚀 INITIATING ULTIMATE VIP FALLBACK ENGINE...")
    print("==================================================")
    
    # API Key Clean-up (Removes accidental brackets or quotes during copy-paste)
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

    # 🏆 The Ultimate Model Fallback List (Iterates until one works)
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-3.0-flash",
        "gemini-3.5-flash",
        "gemini-pro"
    ]

    # 🛡️ Anti-Copy-Paste Bug Defense (Breaks the URL so phones don't format it as a markdown link)
    scheme = "https"
    domain = "generativelanguage.googleapis.com"
    path_prefix = "v1beta/models"

    success = False
    for model in models_to_try:
        print(f"\n📡 Trying Model: {model} ...")
        
        # Assembling URL safely
        url = f"{scheme}://{domain}/{path_prefix}/{model}:generateContent?key={api_key}"
        
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=1200) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            new_code = result["candidates"][0]["content"]["parts"][0]["text"]
            new_code = re.sub(r'^```(html|javascript|css)?\s*', '', new_code, flags=re.IGNORECASE)
            new_code = re.sub(r'```$', '', new_code.strip())

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_code)
                
            print(f"🎉 SUCCESS! Game successfully engineered using {model}!")
            success = True
            break # ✅ Exit loop because it successfully worked!

        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"⚠️ Quota Exceeded (429) for {model}. Moving to next...")
            elif e.code == 404:
                print(f"⚠️ Model {model} is offline or not found (404). Moving to next...")
            else:
                print(f"❌ HTTP {e.code} for {model}. Moving to next...")
        except Exception as e:
            print(f"❌ Connection Error with {model}: {e}")

    if not success:
        print("\n🚨 CRITICAL: All models failed! Please check if your API Key is valid or generate a new one.")
        sys.exit(1)

if __name__ == "__main__":
    main()
