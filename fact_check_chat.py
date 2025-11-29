import streamlit as st
from openai import OpenAI
from PIL import Image
import json
import base64

# -----------------------------
# 🔑 Load API Key
# -----------------------------
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)

if not OPENAI_API_KEY:
    st.error("Missing API key! Add it in .streamlit/secrets.toml")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)


# -----------------------------
# 🧠 Base64 Converter
# -----------------------------
def to_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")


# -----------------------------
# ⚙ JSON Auto-Fix
# -----------------------------
def fix_json(s: str):
    s = s.strip()
    s = s.replace("```json", "").replace("```", "").replace("json", "")
    if s.count("{") > s.count("}"):
        s += "}"
    return s


# -----------------------------
# 🤖 MULTI-AGENT SUPER ANALYZER
# -----------------------------
def analyze_image_people_engine(image_b64):
    system_prompt = """
You are an advanced MULTI-AGENT FAKE IMAGE + PERSON DETECTION SYSTEM.

IMPORTANT RULE:
You ARE ALLOWED to identify public figures in images.
You MUST attempt to identify celebrities, politicians, actors, business leaders, athletes, creators, etc.

Allowed examples:
Elon Musk, Narendra Modi, Barack Obama, Cristiano Ronaldo, Virat Kohli,
Taylor Swift, Bill Gates, Jeff Bezos, Mark Zuckerberg, Joe Biden,
Shah Rukh Khan, Lionel Messi, Sundar Pichai, Kamala Harris, etc.

Do NOT hallucinate identities.  
If uncertain → return "unknown".

STRICT RULE:
RETURN VALID JSON ONLY.
NO markdown, NO commentary, NO extra text.

-----------------------------------------------------
0️⃣ FACE IDENTIFICATION AGENT (MANDATORY)
Detect each face. For each person, return:

If recognized public figure:
{
 "name": "Elon Musk",
 "confidence": 95,
 "description": "Tech entrepreneur, CEO of Tesla and SpaceX.",
 "is_public_figure": true
}

If NOT recognized:
{
 "name": "unknown",
 "confidence": 0,
 "description": "No match to any known public figure.",
 "is_public_figure": false
}

-----------------------------------------------------
1️⃣ IMAGE TYPE DETECTOR
Classify image as:
- whatsapp_message
- people_photo
- ai_generated_art
- normal_photo
- deepfake
- photoshopped
- meme
- document_screenshot

-----------------------------------------------------
2️⃣ AI ARTIFACT DETECTION
Look for AI-generation patterns.
Return ai_artifact_score (0-100).

-----------------------------------------------------
3️⃣ DEEPFAKE / MANIPULATION CHECK
Look for:
- face swapping
- blending issues
- warped features
- inconsistent lighting
Return manipulation_score (0-100).

-----------------------------------------------------
4️⃣ REALISM CHECK
Return realism_score (0-100).

-----------------------------------------------------
5️⃣ TRUTH SCORE
Combine all factors:
100 = very real  
0 = very fake  

-----------------------------------------------------
FINAL JSON OUTPUT (MANDATORY):

{
"image_type": "",
"people_detected": [],
"ai_artifact_score": 0,
"manipulation_score": 0,
"realism_score": 0,
"is_fake": false,
"truth_score": 0,
"reasoning": ""
}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            temperature=0.1,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                    ]
                }
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"ERROR: {str(e)}"


# -----------------------------
# 🎨 STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Advanced Fake + People Engine", layout="wide")

st.title("🕵️ Advanced Fake Image + Public Figure Identification Engine (2025)")
st.write("AI-powered detection of fake images, deepfakes, and recognition of public figures.")

uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded:

    img = Image.open(uploaded)
    st.image(img, caption="Uploaded Image", use_container_width=True)

    img_b64 = to_base64(uploaded)

    with st.spinner("Running intelligent multi-agent analysis..."):
        raw = analyze_image_people_engine(img_b64)

    fixed = fix_json(raw)

    try:
        result = json.loads(fixed)
    except:
        st.error("❌ Failed to parse output. Raw response:")
        st.code(raw)
        st.stop()

    st.success("Analysis Complete 🎉")

    # Tabs
    summary, people, scores, json_tab = st.tabs(
        ["🧠 Summary", "👤 People Detected", "📊 Scores", "🔧 Raw JSON"]
    )

    # SUMMARY
    with summary:
        st.subheader("🧠 Final Judgment")

        if result["is_fake"]:
            st.error("🟥 FAKE / Manipulated / AI-Generated")
        else:
            st.success("🟩 REAL IMAGE")

        st.markdown(f"### 📌 Image Type: `{result['image_type']}`")

        st.markdown(f"### 🎯 Truth Score: **{result['truth_score']} / 100**")

        st.markdown("### 🧩 Explanation")
        st.info(result["reasoning"])

    # PEOPLE
    with people:
        st.subheader("👤 Detected People")

        if len(result["people_detected"]) == 0:
            st.warning("No recognizable people detected.")
        else:
            for p in result["people_detected"]:
                st.markdown("---")
                st.markdown(f"### 👤 {p['name']}")
                st.write(f"**Public Figure:** {p['is_public_figure']}")
                st.write(f"**Confidence:** {p['confidence']}%")
                st.write(f"**About:** {p['description']}")

    # SCORES
    with scores:
        st.subheader("📊 Detection Scores")

        st.write("**AI Artifact Score**")
        st.progress(result["ai_artifact_score"] / 100)

        st.write("**Manipulation Score**")
        st.progress(result["manipulation_score"] / 100)

        st.write("**Realism Score**")
        st.progress(result["realism_score"] / 100)

        st.write("**Truth Score**")
        st.progress(result["truth_score"] / 100)

    # RAW JSON
    with json_tab:
        st.code(result, language="json")

else:
    st.warning("Upload an image to begin.")
