# ============================================================
# PATCH: Replace ONLY the ai_symptom_checker view in
#        pharmacy_system/inventory/views.py
#
# Also add these imports at the TOP of views.py if not present:
#   import json, requests
#   from django.http import JsonResponse
#   from django.views.decorators.csrf import csrf_exempt
# ============================================================

import json
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

# ── Put your free Gemini API key in settings.py as:
#    GEMINI_API_KEY = 'YOUR_KEY_HERE'
from django.conf import settings


# ─────────────────────────────────────────────
# HELPER: call Gemini with a tight prompt
# ─────────────────────────────────────────────
def _call_gemini(prompt: str) -> dict | None:
    """
    Calls Gemini 2.0 Flash (free tier).
    Returns parsed JSON dict or None on failure.
    Keeps token usage minimal by using a strict system instruction.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        return None

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.0-flash:generateContent"
        f"?key={api_key}"
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,          # low = consistent, factual
            "maxOutputTokens": 400,      # tight cap → fewer tokens used
            "responseMimeType": "application/json"
        }
    }

    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw)
    except Exception:
        return None


# ─────────────────────────────────────────────
# HELPER: build a minimal Gemini prompt
# ─────────────────────────────────────────────
def _build_prompt(symptoms: list, severity: str, cart_meds: list) -> str:
    """
    Constructs an ultra-compact prompt so we waste zero tokens.
    cart_meds = list of medication names already in the user's cart
                (used to check dangerous combinations).
    """
    sym_str      = ", ".join(symptoms)
    cart_str     = ", ".join(cart_meds) if cart_meds else "none"

    return f"""You are a pharmacy AI. Respond ONLY with valid JSON — no extra text.

Symptoms: {sym_str}
Severity: {severity}
Patient already has: {cart_str}

Return this exact JSON structure:
{{
  "recommendations": [
    {{
      "medicine": "Name",
      "confidence": 85,
      "risk": "Low",
      "explanation": "One sentence why this helps.",
      "warnings": "Any specific warning or empty string.",
      "dangerous_combo": true/false,
      "combo_reason": "Why dangerous to combine with existing meds, or empty string."
    }}
  ],
  "allergy_note": "General allergy caution if relevant, else empty string.",
  "disclaimer": "Short safety disclaimer."
}}

Rules:
- Max 3 recommendations.
- confidence is integer 0-100.
- risk is one of: Low, Medium, High.
- dangerous_combo is true if this med conflicts with any med in 'Patient already has'.
- Keep all strings under 20 words.
- OTC medications only unless clearly needed.
- If symptoms are unclear, recommend consulting a pharmacist."""


# ─────────────────────────────────────────────
# MAIN VIEW
# ─────────────────────────────────────────────
@login_required
def ai_symptom_checker(request):
    from inventory.models import Medication, CartItem, AIRecommendationLog

    step              = 1
    medication_objects = []
    ai_result         = None
    error             = None

    # ── STEP 1: symptom form (GET)
    if request.method == "GET":
        return render(request, 'ai_checker.html', {'step': 1})

    # ── STEP 1 → 2: user submitted symptoms
    if request.method == "POST" and "symptoms" in request.POST:
        symptoms = request.POST.getlist('symptoms')
        custom   = request.POST.get('custom_symptom', '').strip()
        if custom:
            symptoms.append(custom)

        if not symptoms:
            return render(request, 'ai_checker.html', {
                'step': 1,
                'error': 'Please select at least one symptom.'
            })

        request.session['symptoms'] = symptoms
        return render(request, 'ai_checker.html', {
            'step': 2,
            'symptoms': symptoms
        })

    # ── STEP 2 → 3: user submitted severity → call Gemini
    if request.method == "POST" and "severity" in request.POST:
        symptoms = request.session.get('symptoms', [])
        severity = request.POST.get('severity', 'Mild')

        # Grab medications already in the user's cart for combo-check
        cart_items = CartItem.objects.filter(
            user=request.user
        ).select_related('medication')
        cart_meds  = [ci.medication.name for ci in cart_items]

        # ── Call Gemini
        prompt    = _build_prompt(symptoms, severity, cart_meds)
        ai_result = _call_gemini(prompt)

        # ── Fallback if Gemini fails
        if not ai_result:
            ai_result = {
                "recommendations": [
                    {
                        "medicine": "Consult Pharmacist",
                        "confidence": 50,
                        "risk": "High",
                        "explanation": "Unable to reach AI service. Please consult a pharmacist.",
                        "warnings": "",
                        "dangerous_combo": False,
                        "combo_reason": ""
                    }
                ],
                "allergy_note": "",
                "disclaimer": "AI service unavailable. Seek professional advice."
            }
            error = "AI service could not be reached. Showing fallback advice."

        # ── Match recommended medicines to DB products
        for rec in ai_result.get("recommendations", []):
            med = Medication.objects.filter(
                name__iexact=rec["medicine"]
            ).first()

            medication_objects.append({
                'med':  med,   # may be None if not in stock
                'info': rec
            })

            # ── Log every recommendation
            if med or rec["medicine"] != "Consult Pharmacist":
                AIRecommendationLog.objects.create(
                    user=request.user,
                    symptoms=", ".join(symptoms),
                    recommended_medication=rec["medicine"],
                    confidence_score=rec["confidence"],
                    risk_level=rec["risk"],
                    explanation=rec["explanation"]
                )

        return render(request, 'ai_checker.html', {
            'step':               3,
            'medication_objects': medication_objects,
            'severity':           severity,
            'symptoms':           symptoms,
            'allergy_note':       ai_result.get('allergy_note', ''),
            'disclaimer':         ai_result.get('disclaimer', ''),
            'cart_meds':          cart_meds,
            'error':              error,
        })

    # fallback
    return render(request, 'ai_checker.html', {'step': 1})