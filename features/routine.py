# import os
# import json
# import io
# from flask import Blueprint, render_template, request, send_file, session, jsonify
# from google import genai
# from google.genai import types
# from dotenv import load_dotenv

# routine_bp = Blueprint('routine', __name__, template_folder='../templates')

# load_dotenv()
# _GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
# _genai_client = genai.Client(api_key=_GEMINI_API_KEY) if _GEMINI_API_KEY else None


# @routine_bp.route('/', methods=['GET'])
# def form():
#     from flask import session, redirect
#     if not session.get('user_id'):
#         return redirect('/login?next=/routine/')
#     return render_template('routine.html', plan={})


# @routine_bp.route('/api/generate', methods=['POST'])
# def generate_api():
#     data = request.get_json() or {}
#     skin_type = data.get('skin_type', '')
#     age = data.get('age', '')
#     allergies = data.get('allergies', '')
#     lifestyle = data.get('lifestyle', '')

#     # Fallback routine if no API key
#     routine = {
#         'skin_analysis': 'Sample analysis',
#         'morning_routine': [
#             'Cleanser (gentle, pH-balanced)',
#             'Vitamin C serum',
#             'Moisturizer suited to skin type',
#             'Broad-spectrum SPF 50'
#         ],
#         'evening_routine': [
#             'Cleanser',
#             'Treatment based on needs (e.g., retinoid)',
#             'Ceramide-rich moisturizer'
#         ],
#         'diet_tips': ['Balanced diet', 'Hydration'],
#         'lifestyle': ['Adequate sleep', 'Stress management']
#     }

#     if _genai_client:
#         prompt = (
#             "You are an expert dermatologist assistant. "
#             "Return **strict JSON only** with keys: skin_analysis, morning_routine, evening_routine, diet_tips, lifestyle. "
#             f"Inputs: age={age}, skin_type={skin_type}, allergies={allergies}, lifestyle={lifestyle}. "
#             "No markdown, no commentary, no extra text."
#         )
#         try:
#             resp = _genai_client.models.generate_content(
#                 model='gemini-2.5-flash',
#                 contents=prompt,
#                 config=types.GenerateContentConfig(
#                     thinking_config=types.ThinkingConfig(thinking_budget=0)
#                 )
#             )
#             text = getattr(resp, 'text', '{}').strip()
            
#             # Attempt safe JSON parsing
#             text = text.replace('\n', '').replace('“','"').replace('”','"')
#             routine = json.loads(text)
#         except Exception as e:
#             print("⚠️ Gemini API or parsing error:", e)
#             routine['skin_analysis'] = 'Unable to generate routine. Showing sample plan.'

#     session['routine'] = routine
#     return jsonify({'routine': routine})


# @routine_bp.route('/download', methods=['POST'])
# def download():
#     content = request.form.get('content', '')
#     buffer = io.BytesIO(content.encode('utf-8'))
#     return send_file(buffer, as_attachment=True, download_name='routine.txt', mimetype='text/plain')
import os
import json
import io
import re
from flask import Blueprint, render_template, request, send_file, session, jsonify, redirect
from google import genai
from google.genai import types
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from dotenv import load_dotenv

routine_bp = Blueprint('routine', __name__, template_folder='../templates')

load_dotenv()
_GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
_genai_client = genai.Client(api_key=_GEMINI_API_KEY) if _GEMINI_API_KEY else None

# ---------------- Utility Functions ---------------- #

def build_prompt(age, skin_type, allergies, lifestyle):
    return f"""
You are an expert dermatologist assistant. Generate a personalized skincare plan.

INPUT:
- Age: {age}
- Skin type: {skin_type}
- Allergies: {allergies or 'none'}
- Lifestyle / Other concerns: {lifestyle or 'none'}

TASK:
Return a VALID JSON object only (no markdown, no explanations) with keys:
skin_analysis, morning_routine, evening_routine, diet_tips, lifestyle.

RULES:
- Steps as plain strings
- Concise, professional, realistic
- No brand names
- JSON must strictly follow schema above
"""

def clean_text(s: str) -> str:
    if not isinstance(s, str):
        return s
    return re.sub(r'[#*`]+', '', s).strip()

def clean_json(plan: dict) -> dict:
    for k, v in plan.items():
        if isinstance(v, str):
            plan[k] = clean_text(v)
        elif isinstance(v, list):
            plan[k] = [clean_text(i) for i in v]
    return plan

def call_gemini(prompt_text):
    if not _genai_client:
        return None
    resp = _genai_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )
    return getattr(resp, "text", None)

def parse_json_from_text(text):
    if not text:
        return None
    # Extract JSON safely (object or array)
    match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
    if match:
        try:
            clean_json_text = match.group(0).replace('“','"').replace('”','"')
            return json.loads(clean_json_text)
        except:
            print("⚠️ JSON parsing failed:", text[:200])
            return None
    print("⚠️ No JSON found in Gemini response:", text[:200])
    return None

# ---------------- Routes ---------------- #

@routine_bp.route('/', methods=['GET'])
def form():
    if not session.get('user_id'):
        return redirect('/login?next=/routine/')
    return render_template('routine.html', plan={})

@routine_bp.route('/api/generate', methods=['POST'])
def generate_api():
    data = request.get_json() or {}
    skin_type = data.get('skin_type', '')
    age = data.get('age', '')
    allergies = data.get('allergies', '')
    lifestyle = data.get('lifestyle', '')

    # Fallback routine
    routine = {
        'skin_analysis': 'Sample analysis',
        'morning_routine': [
            'Cleanser (gentle, pH-balanced)',
            'Vitamin C serum',
            'Moisturizer suited to skin type',
            'Broad-spectrum SPF 50'
        ],
        'evening_routine': [
            'Cleanser',
            'Treatment based on needs (e.g., retinoid)',
            'Ceramide-rich moisturizer'
        ],
        'diet_tips': ['Balanced diet', 'Hydration'],
        'lifestyle': ['Adequate sleep', 'Stress management']
    }

    # Call Gemini API if available
    prompt = build_prompt(age, skin_type, allergies, lifestyle)
    raw = call_gemini(prompt)
    parsed = parse_json_from_text(raw)
    if parsed:
        routine = clean_json(parsed)
    else:
        routine['skin_analysis'] = 'Unable to generate routine. Showing sample plan.'

    session['routine'] = routine
    return jsonify({'routine': routine})

@routine_bp.route('/download', methods=['GET'])
def download_pdf():
    routine = session.get('routine', {})
    if not routine:
        routine = {"message": "No routine available. Please generate first."}

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    def add_section(title, content):
        story.append(Paragraph(f"<b>{title}</b>", styles['Heading2']))
        if isinstance(content, list):
            for item in content:
                story.append(Paragraph("• " + item, styles['Normal']))
        else:
            story.append(Paragraph(content, styles['Normal']))
        story.append(Spacer(1, 12))

    add_section("Skin Analysis", routine.get("skin_analysis", ""))
    add_section("Morning Routine", routine.get("morning_routine", []))
    add_section("Evening Routine", routine.get("evening_routine", []))
    add_section("Diet Tips", routine.get("diet_tips", []))
    add_section("Lifestyle", routine.get("lifestyle", []))

    doc.build(story)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="skincare_plan.pdf",
        mimetype="application/pdf"
    )
