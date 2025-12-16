import os
import sys
import json
import base64
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Any

# Optional imports
try:
    import openai
except Exception:
    openai = None

try:
    from jinja2 import Environment, BaseLoader
except Exception:
    Environment = None
    BaseLoader = None

# -----------------------------
# Simple utilities
# -----------------------------
ANSI = {
    "reset": "\u001b[0m",
    "red": "\u001b[31m",
    "green": "\u001b[32m",
    "yellow": "\u001b[33m",
    "blue": "\u001b[34m",
    "cyan": "\u001b[36m",
}


def color(text: str, col: str) -> str:
    code = ANSI.get(col, "")
    return f"{code}{text}{ANSI['reset']}" if code else text


def print_json(obj: Any):
    print(json.dumps(obj, indent=2, ensure_ascii=False))

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

    def validate(self):
        if not isinstance(self.experience, list):
            raise ValueError("experience must be a list")
        if not isinstance(self.projects, list):
            raise ValueError("projects must be a list")
        if not isinstance(self.education, list):
            raise ValueError("education must be a list")
        if not isinstance(self.skills, list):
            raise ValueError("skills must be a list")

    def merge(self, updates: Dict[str, Any]):
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_photo(self, file_bytes: bytes):
        self.photo_base64 = base64.b64encode(file_bytes).decode("utf-8")

    def has_photo(self):
        return bool(self.photo_base64)

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

    @staticmethod
    def from_dict(d: Dict[str, Any]):
        r = Resume()
        for k, v in d.items():
            if hasattr(r, k):
                setattr(r, k, v)
        return r

# -----------------------------
# Templates (from the original project)
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


def render_template(resume: Resume) -> str:
    if Environment is None:
        raise RuntimeError("jinja2 not installed: see requirements.txt")

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

# -----------------------------
# AI Helpers (basic wrapper)
# -----------------------------

def call_ai(system_prompt: str, user_prompt: str, model: str = None) -> str:
    """
    Attempts to call OpenAI. If openai package or API key not present, a clear error is returned.
    """
    if openai is None:
        return "[AI ERROR] openai package not installed"

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "[AI ERROR] OPENAI_API_KEY not set in environment"

    try:
        openai.api_key = api_key
        chosen_model = model or os.getenv("OPENAI_MODEL", "gpt-4")

        # Use ChatCompletion endpoint (widely supported)
        resp = openai.ChatCompletion.create(
            model=chosen_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        text = resp.choices[0].message.get("content") if resp.choices else resp.choices[0].text
        return text

    except Exception as e:
        return f"[AI ERROR] {e}"


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
    except Exception:
        return {"error": "AI kon JSON niet parsen", "raw": raw}


def ai_rewrite_text(text: str, instruction: str) -> str:
    system = "Je herschrijft tekst volgens instructies. Houd het professioneel en beknopt."
    user = f"Originele tekst:\n{text}\n\nInstructie:\n{instruction}"
    return call_ai(system, user)


def ai_regenerate_field(field_name: str, resume: Resume) -> str:
    system = "Je genereert professionele CV-tekst voor één veld."
    user = f"""
Genereer het veld '{field_name}' opnieuw op basis van deze CV:

{resume.to_json()}
"""
    return call_ai(system, user)


def ai_generate_summary(resume: Resume) -> str:
    system = "Je schrijft een krachtige professionele CV-samenvatting."
    user = f"Schrijf een samenvatting voor deze persoon:\n\n{resume.to_json()}"
    return call_ai(system, user)

# -----------------------------
# CLI
# -----------------------------

def load_resume(path: str) -> Resume:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Resume.from_dict(data)


def save_resume(resume: Resume, path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(resume.to_json())


def cmd_render(args):
    r = load_resume(args.input)
    html = render_template(r)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    print(color(f"Rendered HTML written to {args.output}", "green"))


def cmd_extract(args):
    # read plain text extracted from PDF (user provides)
    with open(args.input, "r", encoding="utf-8") as f:
        pdf_text = f.read()
    print(color("Calling AI to extract structured resume...", "cyan"))
    result = ai_extract_resume(pdf_text)
    if "error" in result:
        print(color("AI extraction failed or produced non-JSON output:", "red"))
        print(result.get("raw"))
        return
    save_path = args.output or "resume_extracted.json"
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(color(f"Extracted resume saved to {save_path}", "green"))


def cmd_set_photo(args):
    r = load_resume(args.resume)
    with open(args.photo, "rb") as f:
        b = f.read()
    r.set_photo(b)
    save_resume(r, args.resume)
    print(color("Photo embedded into resume JSON.", "green"))


def cmd_summary(args):
    r = load_resume(args.resume)
    print(color("Calling AI to generate a summary...", "cyan"))
    s = ai_generate_summary(r)
    print("--- AI SUMMARY ---")
    print(s)
    if args.save:
        r.summary = s
        save_resume(r, args.resume)
        print(color("Saved AI summary into resume file.", "green"))


def cmd_review(args):
    r = load_resume(args.resume)
    print(color("=== AI REVIEW WIZARD ===", "cyan"))
    fields = ["summary", "experience", "projects", "education", "skills"]
    for field in fields:
        print(color(f"\n--- {field.upper()} ---", "yellow"))
        val = getattr(r, field)
        print_json(val)
        print("Options: [a] Accept  [e] Edit (AI rewrite)  [r] Regenerate  [s] Skip")
        choice = input("Choice: ").strip().lower()
        if choice == "a":
            continue
        elif choice == "e":
            instruction = input("Rewrite instruction: ")
            new_text = ai_rewrite_text(json.dumps(val, ensure_ascii=False), instruction)
            # Try to parse JSON, else set raw text
            try:
                parsed = json.loads(new_text)
                setattr(r, field, parsed)
            except Exception:
                setattr(r, field, new_text)
        elif choice == "r":
            regenerated = ai_regenerate_field(field, r)
            try:
                parsed = json.loads(regenerated)
                setattr(r, field, parsed)
            except Exception:
                setattr(r, field, regenerated)
        elif choice == "s":
            continue
    save_resume(r, args.resume)
    print(color("\n✅ AI Review voltooid! Geslagen naar bestand.", "green"))


def main():
    parser = argparse.ArgumentParser(description="Resume CLI: render, extract and call AI helpers")
    sub = parser.add_subparsers(dest="cmd")

    p_render = sub.add_parser("render", help="Render resume JSON to HTML")
    p_render.add_argument("input", help="resume JSON file")
    p_render.add_argument("output", help="output HTML file")
    p_render.set_defaults(func=cmd_render)

    p_extract = sub.add_parser("extract", help="Extract structured resume JSON from plain text (AI)")
    p_extract.add_argument("input", help="text file (PDF text extracted externally)")
    p_extract.add_argument("-o", "--output", help="output resume JSON file")
    p_extract.set_defaults(func=cmd_extract)

    p_photo = sub.add_parser("set-photo", help="Embed photo into resume JSON (base64)")
    p_photo.add_argument("resume", help="resume JSON file")
    p_photo.add_argument("photo", help="image file (jpg/png)")
    p_photo.set_defaults(func=cmd_set_photo)

    p_summary = sub.add_parser("summary", help="AI: generate a summary for resume")
    p_summary.add_argument("resume", help="resume JSON file")
    p_summary.add_argument("--save", action="store_true", help="save generated summary back to resume file")
    p_summary.set_defaults(func=cmd_summary)

    p_review = sub.add_parser("review", help="Interactive AI review wizard")
    p_review.add_argument("resume", help="resume JSON file")
    p_review.set_defaults(func=cmd_review)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as e:
        print(color(f"Error: {e}", "red"))
        sys.exit(2)


if __name__ == "__main__":
    main()
