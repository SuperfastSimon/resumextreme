# Log 2025-12-16 08:11
# ==== resume.py ====

import base64
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any


# -----------------------------
# Resume Data Model
# -----------------------------

@dataclass
class Resume:
    name: str = ""
    title: str = ""
    summary: str = ""
    experience: List[Dict[str, Any]] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    education: List[Dict[str, Any]] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    hobbies: List[str] = field(default_factory=list)
    contact: Dict[str, str] = field(default_factory=dict)
    photo_base64: str = ""   # base64 encoded image
    theme: str = "premium"   # premium, minimal, creative, sidebar
    sidebar_color: str = "teal"  # green, teal, mono

    # -----------------------------
    # Validation
    # -----------------------------
    def validate(self):
        if not isinstance(self.experience, list):
            raise ValueError("experience must be a list")
        if not isinstance(self.projects, list):
            raise ValueError("projects must be a list")
        if not isinstance(self.education, list):
            raise ValueError("education must be a list")
        if not isinstance(self.skills, list):
            raise ValueError("skills must be a list")

    # -----------------------------
    # Merge AI-updates into resume
    # -----------------------------
    def merge(self, updates: Dict[str, Any]):
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)

    # -----------------------------
    # Photo handling
    # -----------------------------
    def set_photo(self, file_bytes: bytes):
        self.photo_base64 = base64.b64encode(file_bytes).decode("utf-8")

    def has_photo(self):
        return bool(self.photo_base64)

    # -----------------------------
    # Export helpers
    # -----------------------------
    def to_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "summary": self.summary,
            "experience": self.experience,
            "projects": self.projects,
            "education": self.education,
            "skills": self.skills,
            "languages": self.languages,
            "hobbies": self.hobbies,
            "contact": self.contact,
            "photo_base64": self.photo_base64,
            "theme": self.theme,
            "sidebar_color": self.sidebar_color,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

# ==== templates.py ====

from jinja2 import Environment, BaseLoader

# -----------------------------
# Base HTML wrapper
# -----------------------------
HTML_WRAPPER = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}}
{extra_css}
</style>
</head>
<body>
{content}
</body>
</html>
"""

# -----------------------------
# Premium Template
# -----------------------------
TEMPLATE_PREMIUM = """
<div style="padding:40px;">
  <h1>{{ resume.name }}</h1>
  <h3>{{ resume.title }}</h3>

  {% if resume.photo_base64 %}
  <img src="data:image/jpeg;base64,{{ resume.photo_base64 }}" 
       style="width:120px;border-radius:10px;float:right;margin-top:-80px;">
  {% endif %}

  <h2>Summary</h2>
  <p>{{ resume.summary }}</p>

  <h2>Experience</h2>
  {% for job in resume.experience %}
    <p><strong>{{ job.role }}</strong> — {{ job.company }} ({{ job.period }})</p>
    <ul>
      {% for b in job.bullets %}
      <li>{{ b }}</li>
      {% endfor %}
    </ul>
  {% endfor %}

  <h2>Skills</h2>
  <ul>
    {% for s in resume.skills %}
    <li>{{ s }}</li>
    {% endfor %}
  </ul>
</div>
"""

# -----------------------------
# Minimal Template
# -----------------------------
TEMPLATE_MINIMAL = """
<div style="padding:40px;max-width:700px;margin:auto;">
  <h1 style="margin-bottom:0;">{{ resume.name }}</h1>
  <p style="color:#666;">{{ resume.title }}</p>

  <p>{{ resume.summary }}</p>

  <h2>Experience</h2>
  {% for job in resume.experience %}
    <p><strong>{{ job.role }}</strong> — {{ job.company }}</p>
    <p><em>{{ job.period }}</em></p>
    <ul>
      {% for b in job.bullets %}
      <li>{{ b }}</li>
      {% endfor %}
    </ul>
  {% endfor %}
</div>
"""

# -----------------------------
# Creative Template
# -----------------------------
TEMPLATE_CREATIVE = """
<div style="padding:40px;">
  <div style="background:#222;color:white;padding:20px;border-radius:8px;">
    <h1>{{ resume.name }}</h1>
    <p>{{ resume.title }}</p>
  </div>

  <h2>Summary</h2>
  <p>{{ resume.summary }}</p>

  <h2>Projects</h2>
  {% for p in resume.projects %}
    <p><strong>{{ p.name }}</strong> — {{ p.period }}</p>
    <p>{{ p.description }}</p>
  {% endfor %}
</div>
"""

# -----------------------------
# Sidebar Template (3 colors)
# -----------------------------
SIDEBAR_COLORS = {
    "green": "#2e7d32",
    "teal": "#004d4d",
    "mono": "#222"
}

TEMPLATE_SIDEBAR = """
<div style="display:flex;min-height:100vh;">
  
  <!-- SIDEBAR -->
  <div style="width:30%;background:{{ color }};color:white;padding:30px;">
    
    {% if resume.photo_base64 %}
    <img src="data:image/jpeg;base64,{{ resume.photo_base64 }}"
         style="width:120px;height:120px;border-radius:50%;object-fit:cover;margin-bottom:20px;">
    {% endif %}

    <h2>Contact</h2>
    <p>{{ resume.contact.phone }}</p>
    <p>{{ resume.contact.email }}</p>
    <p>{{ resume.contact.location }}</p>

    <h2>Skills</h2>
    <ul>
      {% for s in resume.skills %}
      <li>{{ s }}</li>
      {% endfor %}
    </ul>

    <h2>Languages</h2>
    <ul>
      {% for l in resume.languages %}
      <li>{{ l }}</li>
      {% endfor %}
    </ul>

    <h2>Hobbies</h2>
    <ul>
      {% for h in resume.hobbies %}
      <li>{{ h }}</li>
      {% endfor %}
    </ul>

  </div>

  <!-- MAIN -->
  <div style="width:70%;padding:40px;">
    <h1>{{ resume.name }}</h1>
    <h3>{{ resume.title }}</h3>

    <h2>Summary</h2>
    <p>{{ resume.summary }}</p>

    <h2>Experience</h2>
    {% for job in resume.experience %}
      <p><strong>{{ job.role }}</strong> — {{ job.company }} ({{ job.period }})</p>
      <ul>
        {% for b in job.bullets %}
        <li>{{ b }}</li>
        {% endfor %}
      </ul>
    {% endfor %}
  </div>

</div>
"""

# -----------------------------
# Template Loader
# -----------------------------
def render_template(resume):
    env = Environment(loader=BaseLoader())

    if resume.theme == "premium":
        tpl = TEMPLATE_PREMIUM

    elif resume.theme == "minimal":
        tpl = TEMPLATE_MINIMAL

    elif resume.theme == "creative":
        tpl = TEMPLATE_CREATIVE

    elif resume.theme == "sidebar":
        color = SIDEBAR_COLORS.get(resume.sidebar_color, "#004d4d")
        tpl = TEMPLATE_SIDEBAR.replace("{{ color }}", color)

    else:
        raise ValueError(f"Unknown theme: {resume.theme}")

    template = env.from_string(tpl)
    html = template.render(resume=resume)

    return HTML_WRAPPER.format(content=html, extra_css="")

# ==== ai.py ====

import json
from typing import Dict, Any
from resume import Resume
from utils import color, print_json
from openai import OpenAI


# -----------------------------
# OpenAI Client
# -----------------------------
client = OpenAI()


# -----------------------------
# Generic AI call
# -----------------------------
def call_ai(system_prompt: str, user_prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[AI ERROR] {e}"


# -----------------------------
# Extract structured resume JSON from PDF text
# -----------------------------
def ai_extract_resume(pdf_text: str) -> Dict[str, Any]:
    system = """
Je bent een CV-analyse AI. Je taak is om ruwe tekst uit een PDF te converteren
naar een gestructureerde JSON voor een CV-maker app.

Gebruik dit schema:

{
  "name": "",
  "title": "",
  "summary": "",
  "experience": [
    {
      "role": "",
      "company": "",
      "period": "",
      "bullets": []
    }
  ],
  "projects": [
    {
      "name": "",
      "period": "",
      "description": ""
    }
  ],
  "education": [
    {
      "degree": "",
      "school": "",
      "period": ""
    }
  ],
  "skills": [],
  "languages": [],
  "hobbies": [],
  "contact": {
    "phone": "",
    "email": "",
    "location": ""
  }
}
"""
    user = f"Zet deze PDF-tekst om naar JSON:\n\n{pdf_text}"

    raw = call_ai(system, user)

    try:
        return json.loads(raw)
    except:
        return {"error": "AI kon JSON niet parsen", "raw": raw}


# -----------------------------
# AI rewrite for manual editing
# -----------------------------
def ai_rewrite_text(text: str, instruction: str) -> str:
    system = "Je herschrijft tekst volgens instructies. Houd het professioneel en beknopt."
    user = f"Originele tekst:\n{text}\n\nInstructie:\n{instruction}"
    return call_ai(system, user)


# -----------------------------
# AI regenerate a specific resume field
# -----------------------------
def ai_regenerate_field(field_name: str, resume: Resume) -> str:
    system = "Je genereert professionele CV-tekst voor één veld."
    user = f"""
Genereer het veld '{field_name}' opnieuw op basis van deze CV:

{resume.to_json()}
"""
    return call_ai(system, user)


# -----------------------------
# AI Review Wizard
# -----------------------------
def ai_review_wizard(resume: Resume) -> Resume:
    print(color("\n=== AI REVIEW WIZARD ===\n", "cyan"))

    fields = [
        "summary",
        "experience",
        "projects",
        "education",
        "skills",
    ]

    for field in fields:
        print(color(f"\n--- {field.upper()} ---", "yellow"))
        current_value = getattr(resume, field)
        print_json(current_value)

        print("\nOpties:")
        print("[a] Accepteren")
        print("[e] Bewerken (AI rewrite)")
        print("[r] Opnieuw genereren")
        print("[s] Overslaan")

        choice = input("Keuze: ").strip().lower()

        if choice == "a":
            continue

        elif choice == "e":
            instruction = input("Herschrijf instructie: ")
            new_text = ai_rewrite_text(json.dumps(current_value), instruction)
            try:
                setattr(resume, field, json.loads(new_text))
            except:
                setattr(resume, field, new_text)

        elif choice == "r":
            regenerated = ai_regenerate_field(field, resume)
            try:
                setattr(resume, field, json.loads(regenerated))
            except:
                setattr(resume, field, regenerated)

        elif choice == "s":
            continue

    print(color("\n✅ AI Review voltooid!\n", "green"))
    return resume


# -----------------------------
# AI Summary Generator
# -----------------------------
def ai_generate_summary(resume: Resume) -> str:
    system = "Je schrijft een krachtige professionele CV-samenvatting."
    user = f"Schrijf een samenvatting voor deze persoon:\n\n{resume.to_json()}"
    return call_ai(system, user)