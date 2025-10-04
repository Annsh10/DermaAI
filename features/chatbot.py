import os
import json
import requests
from flask import Blueprint, render_template, request, jsonify, session
from dotenv import load_dotenv

chatbot_bp = Blueprint('chatbot', __name__, template_folder='../templates')

# Load API key once
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------- FAQ Knowledge Base ----------------
faq_data = {
    "skin": {
        "acne": {
            "definition": "Acne is a common skin condition caused by clogged hair follicles and excess oil production. It can present as pimples, blackheads, or whiteheads.",
            "treatment": "• Wash your face twice daily with a mild cleanser.\n• Avoid oily or comedogenic products.\n• Consider topical treatments like benzoyl peroxide or salicylic acid creams.\n• For persistent or severe acne, consult a dermatologist.",
            "precautions": "• Avoid squeezing or picking pimples.\n• Limit exposure to harsh scrubs or abrasive products.\n• Follow dermatologist instructions carefully."
        },
        "eczema": {
            "definition": "Eczema is a chronic skin condition characterized by dry, itchy, and inflamed patches of skin.",
            "treatment": "• Moisturize frequently using fragrance-free creams.\n• Take lukewarm showers and avoid hot water.\n• Use topical corticosteroids if prescribed.\n• Identify and avoid triggers (stress, allergens).",
            "precautions": "• Avoid scratching affected areas.\n• Avoid harsh soaps and detergents.\n• Seek medical care if symptoms worsen."
        },
        "psoriasis": {
            "definition": "Psoriasis is an autoimmune skin disorder causing red, scaly patches, often on elbows, knees, and scalp.",
            "treatment": "• Keep the skin moisturized.\n• Avoid triggers like stress, alcohol, or smoking.\n• Follow prescribed topical or systemic treatments.\n• Light therapy may be recommended in some cases.",
            "precautions": "• Avoid scratching or picking scales.\n• Regularly follow up with a dermatologist.\n• Monitor for joint pain (psoriatic arthritis)."
        }
    },
    "hair": {
        "dandruff": {
            "definition": "Dandruff is a scalp condition causing flaking, itching, and irritation.",
            "treatment": "• Use anti-dandruff shampoos containing zinc pyrithione or ketoconazole.\n• Wash hair regularly but gently.\n• Avoid excessive use of hair styling products.",
            "precautions": "• Avoid scratching the scalp aggressively.\n• Maintain good scalp hygiene."
        },
        "hairfall": {
            "definition": "Hairfall is excessive shedding of hair, which can result from genetics, stress, or nutritional deficiencies.",
            "treatment": "• Maintain a balanced diet rich in vitamins and minerals.\n• Avoid excessive heat styling and harsh chemical treatments.\n• Consult a dermatologist for underlying causes.",
            "precautions": "• Handle hair gently while brushing or washing.\n• Avoid tight hairstyles that pull on hair."
        },
        "alopecia": {
            "definition": "Alopecia is hair loss that can be patchy or complete, often autoimmune in nature.",
            "treatment": "• Seek medical evaluation to determine the type of alopecia.\n• Treatments may include minoxidil, corticosteroid injections, or laser therapy.\n• Supportive care includes gentle hair care and scalp protection.",
            "precautions": "• Avoid self-medicating with unverified treatments.\n• Follow dermatologist guidance closely."
        }
    },
    "nails": {
        "fungal": {
            "definition": "Fungal nail infection (onychomycosis) causes thickened, discolored, and brittle nails.",
            "treatment": "• Keep nails dry and clean.\n• Avoid sharing nail clippers.\n• Use topical antifungal creams or oral medication if prescribed.",
            "precautions": "• Avoid nail trauma.\n• Monitor for worsening infection and consult a doctor if needed."
        },
        "brittle": {
            "definition": "Brittle nails are weak, splitting, or peeling nails often due to dryness or nutritional deficiency.",
            "treatment": "• Moisturize cuticles regularly.\n• Wear gloves during cleaning or harsh chores.\n• Take biotin supplements if advised by a healthcare professional.",
            "precautions": "• Avoid excessive nail polish or harsh chemicals.\n• Keep nails trimmed and filed gently."
        },
        "ingrown": {
            "definition": "An ingrown nail occurs when the nail grows into the surrounding skin, causing pain and sometimes infection.",
            "treatment": "• Soak feet in warm water several times a day.\n• Gently lift the nail edge using clean cotton or dental floss.\n• Seek medical care if signs of infection appear.",
            "precautions": "• Avoid tight-fitting shoes.\n• Do not cut nails too short or dig into corners."
        }
    }
}

# ---------------- Prompt Template ----------------
PROMPT_TEMPLATE = """
You are a professional dermatologist assistant chatbot.

Rules:
1. Answer concisely, professionally, and human-like.
2. Use structured format with only relevant sections:
   - Definition
   - Recommendation
   - Precautions
   - RedFlags
3. Return your answer strictly in JSON format, e.g.:
{{
  "Definition": "...",
  "Recommendation": ["...", "..."],
  "Precautions": ["...", "..."],
  "RedFlags": ["...", "..."]
}}
Include only the relevant sections for the user's query.
Avoid paragraphs; use bullet points in lists.
Friendly and professional tone.

Conversation so far:
{messages}

User Query: {query}
Context Info (if relevant): {context}
"""

# ---------------- Groq API Query ----------------
def query_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=data)
    try:
        result = response.json()
    except Exception as e:
        print("⚠️ Failed to parse JSON:", e)
        return "⚠️ Error: Invalid response from Groq API."

    if "choices" not in result:
        return f"⚠️ API Error: {result.get('error', 'Unexpected response')}"

    return result["choices"][0]["message"]["content"]

# ---------------- Blueprint Routes ----------------
@chatbot_bp.route('/')
def chat_page():
    if not session.get('user_id'):
        from flask import redirect
        return redirect('/login?next=/chat/')
    return render_template('chatbot.html', reply=None, history=session.get('chat_history', []))

@chatbot_bp.route('/api/chat', methods=['POST'])
def chat_api():
    user_query = request.json.get("message", "").strip()
    if not user_query:
        return jsonify({"reply": "Please enter a valid query."})

    query_lower = user_query.lower()

    # Initialize session memory
    if "chat_history" not in session:
        session["chat_history"] = []

    # Append user query to memory
    session["chat_history"].append({"role": "user", "content": user_query})
    MAX_MEMORY = 5
    session["chat_history"] = session["chat_history"][-MAX_MEMORY:]

    # --- 1. Handle greetings ---
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if query_lower in greetings:
        reply = "Hello! 👋 How can I assist you with skin, hair, or nail concerns today?"
        session["chat_history"].append({"role": "bot", "content": reply})
        return jsonify({"reply": reply})

    # --- 2. Handle casual/polite messages ---
    casual_responses = ["thanks", "thank you", "ok thanks", "ok thank you", "thanks a lot", "thanks!"]
    if any(phrase in query_lower for phrase in casual_responses):
        reply = "You're welcome! 😊 Let me know if you have any more questions about skin, hair, or nails."
        session["chat_history"].append({"role": "bot", "content": reply})
        return jsonify({"reply": reply})

    # --- 3. Intent-aware FAQ handling ---
    def detect_intent(user_query):
        if any(word in query_lower for word in ["what is", "define", "definition"]):
            return "definition"
        elif any(word in query_lower for word in ["treat", "treatment", "how to cure", "recommend"]):
            return "treatment"
        elif any(word in query_lower for word in ["precaution", "avoid", "care", "prevent"]):
            return "precautions"
        else:
            return "general"

    intent = detect_intent(user_query)
    context_info = {}

    for category, items in faq_data.items():
        for condition, info in items.items():
            if condition in query_lower:
                context_info = info
                # Use structured response directly if possible
                reply_dict = {}
                if intent == "definition" and "definition" in info:
                    reply_dict["Definition"] = info["definition"]
                elif intent == "treatment" and "treatment" in info:
                    reply_dict["Recommendation"] = info["treatment"]
                elif intent == "precautions" and "precautions" in info:
                    reply_dict["Precautions"] = info["precautions"]
                else:  # fallback: include all relevant info
                    for k, v in info.items():
                        reply_dict[k.capitalize()] = v
                # Convert to HTML bullet format
                reply_html = ""
                for k, v in reply_dict.items():
                    if isinstance(v, list):
                        reply_html += f"<strong>{k}:</strong><ul>"
                        for item in v:
                            reply_html += f"<li>{item}</li>"
                        reply_html += "</ul>"
                    else:
                        reply_html += f"<strong>{k}:</strong> {v}<br>"
                session["chat_history"].append({"role": "bot", "content": reply_html})
                return jsonify({"reply": reply_html})

    # --- 4. Fallback to LLM with memory context ---
    messages_text = "\n".join([h['content'] for h in session.get('chat_history', [])][-6:])  # Last 6
    structured_prompt = PROMPT_TEMPLATE.format(
        query=user_query,
        messages=messages_text,
        context=json.dumps(context_info) if context_info else "None"
    )

    llm_reply = query_groq(structured_prompt)

    # Parse JSON safely
    try:
        structured = json.loads(llm_reply)
    except:
        structured = {"Response": llm_reply}  # fallback

    # Convert to HTML bullet format
    reply_html = ""
    for key, value in structured.items():
        if isinstance(value, list):
            reply_html += f"<strong>{key}:</strong><ul>"
            for item in value:
                reply_html += f"<li>{item}</li>"
            reply_html += "</ul>"
        else:
            reply_html += f"<strong>{key}:</strong> {value}<br>"

    session["chat_history"].append({"role": "bot", "content": reply_html})
    session.modified = True

    return jsonify({"reply": reply_html})