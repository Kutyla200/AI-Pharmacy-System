from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from .models import Medication, CartItem, Order, OrderItem
from .models import DrugInteraction
from .models import AIRecommendationLog
from django.db.models import Q

def medication_detail(request, id):

    medication = get_object_or_404(Medication, id=id)

    return render(request, 'medication_detail.html', {'medication': medication})

def medication_list(request):
    query = request.GET.get('q')
    if query:
        medications = Medication.objects.filter(
    name__icontains=query
) | Medication.objects.filter(
    description__icontains=query
)
    else:
        medications = Medication.objects.all()
    context = {
        'medications': medications,
        'query': query
    }
    return render(request, 'medications.html', context)

@login_required
def dashboard(request):

    medications = Medication.objects.all()

    print("COUNT:", medications.count())

    for med in medications:
        print(med.name)

    return render(request, 'dashboard.html', {
        'medications': medications
    })

@login_required
def add_to_cart(request, med_id):

    medication = get_object_or_404(Medication, id=med_id)

    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        medication=medication
    )

    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity

    cart_item.save()
    return redirect('medications')

@login_required
def view_cart(request):

    items = CartItem.objects.filter(user=request.user)

    total = sum(item.medication.price * item.quantity for item in items)

    warnings = []

    medications = [item.medication for item in items]

    for i in range(len(medications)):
        for j in range(i + 1, len(medications)):

            med1 = medications[i]
            med2 = medications[j]

            interaction = DrugInteraction.objects.filter(
                medication1=med1,
                medication2=med2
            ).first()

            reverse_interaction = DrugInteraction.objects.filter(
                medication1=med2,
                medication2=med1
            ).first()

            if interaction:
                warnings.append(interaction)

            elif reverse_interaction:
                warnings.append(reverse_interaction)

    return render(request, 'cart.html', {
        'items': items,
        'total': total,
        'warnings': warnings
    })

@login_required
def remove_from_cart(request, item_id):

    item = CartItem.objects.get(id=item_id)

    if item.user == request.user:
        item.delete()

    return redirect('view_cart')

@login_required
def checkout(request):

    items = CartItem.objects.filter(user=request.user)

    if not items.exists():
        return redirect('view_cart')

    order = Order.objects.create(user=request.user)

    order_items = []
    total = 0

    for item in items:

        medication = item.medication

        # 🔥 CHECK STOCK FIRST
        if item.quantity > medication.stock:
            return render(request, 'cart.html', {
                'items': items,
                'total': total,
                'error': f"Not enough stock for {medication.name}"
            })

        # 🔥 REDUCE STOCK
        medication.stock -= item.quantity
        medication.save()

        # CREATE ORDER ITEM
        oi = OrderItem.objects.create(
            order=order,
            medication=medication,
            quantity=item.quantity
        )

        order_items.append(oi)

        total += medication.price * item.quantity

    # CLEAR CART
    items.delete()

    return render(request, 'order_success.html', {
        'order': order,
        'items': order_items,
        'total': total
    })

@login_required
def my_orders(request):

    orders = Order.objects.filter(user=request.user).order_by('-id')

    return render(request, 'my_orders.html', {
        'orders': orders
    })

import json
import urllib.request
import urllib.error
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Medication, AIRecommendationLog

GEMINI_API_KEY = "AIzaSyBGSCx9Y5FNFXocgHFi5-9-N1tWxeGz6Cc"  # <-- REPLACE THIS

SYSTEM_PROMPT = """You are a pharmacist AI. Respond ONLY with valid JSON, no markdown.
Given symptoms and optional allergies/current medications, recommend ONE OTC medication.
Rules: Only recommend unscheduled/OTC medications. Never recommend Schedule 3+.
Always warn about dangerous combinations. Be concise.

JSON format (strict):
{
  "medication": "medication name",
  "confidence": 85,
  "risk_level": "Low",
  "explanation": "Brief reason (1-2 sentences)",
  "warnings": "Any allergy or interaction warnings, or null",
  "disclaimer": "Always consult a healthcare professional for persistent symptoms.",
  "alternatives": ["alt1", "alt2"]
}

risk_level must be: Low, Medium, or High
confidence: integer 0-100"""


def call_gemini(symptoms, allergies, current_meds):
    """Call Gemini API with minimal tokens."""
    user_msg = f"Symptoms: {symptoms}"
    if allergies:
        user_msg += f". Allergies: {allergies}"
    if current_meds:
        user_msg += f". Current medications: {current_meds}"

    payload = json.dumps({
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT + "\n\nUser query: " + user_msg}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 300,
            "temperature": 0.1
        }
    }).encode('utf-8')

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read())
    
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    # Strip markdown code blocks if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


@login_required
def bot_pharmacist(request):
    """Main Bot Pharmacist page."""
    result = None
    error = None

    if request.method == "POST":
        symptoms = request.POST.get("symptoms", "").strip()
        allergies = request.POST.get("allergies", "").strip()
        current_meds = request.POST.get("current_meds", "").strip()

        if symptoms:
            try:
                result = call_gemini(symptoms, allergies, current_meds)

                # Log to DB
                AIRecommendationLog.objects.create(
                    user=request.user,
                    symptoms=symptoms,
                    recommended_medication=result.get("medication", "Unknown"),
                    confidence_score=result.get("confidence", 0),
                    risk_level=result.get("risk_level", "Unknown"),
                    explanation=result.get("explanation", "")
                )

            except urllib.error.HTTPError as e:
                error = f"API Error {e.code}: Check your Gemini API key."
            except Exception as e:
                error = f"Something went wrong: {str(e)}"
        else:
            error = "Please describe your symptoms."

    return render(request, "bot_pharmacist.html", {
        "result": result,
        "error": error,
        "symptoms": request.POST.get("symptoms", ""),
        "allergies": request.POST.get("allergies", ""),
        "current_meds": request.POST.get("current_meds", ""),
    })

@login_required
def ai_symptom_checker(request):

    step = 1
    symptoms = []
    allergies = []
    severity = ""

    all_symptoms = set()
    all_allergies = set()

    medications = Medication.objects.all()

    for med in medications:
        if med.keywords:
            for word in med.keywords.lower().split(","):
                clean_word = word.strip()
                if len(clean_word) > 2:
                    all_symptoms.add(clean_word)

        # allergy options based on medicine names
        all_allergies.add(med.name.lower())

    all_symptoms = sorted(all_symptoms)
    all_allergies = sorted(all_allergies)

    # STEP 1: symptoms
    if request.method == "POST" and "symptoms" in request.POST:

        symptoms = request.POST.getlist("symptoms")
        request.session["symptoms"] = symptoms

        return render(request, "ai_checker.html", {
            "step": 2,
            "symptoms": symptoms,
            "all_symptoms": all_symptoms,
            "all_allergies": all_allergies,
        })

    # STEP 2: allergies
    elif request.method == "POST" and "allergy_step" in request.POST:

        allergies = request.POST.getlist("allergies")
        request.session["allergies"] = allergies

        symptoms = request.session.get("symptoms", [])

        return render(request, "ai_checker.html", {
            "step": 3,
            "symptoms": symptoms,
            "allergies": allergies,
            "all_symptoms": all_symptoms,
            "all_allergies": all_allergies,
        })

    # STEP 3: severity + recommendation
    elif request.method == "POST" and "severity" in request.POST:

        symptoms = request.session.get("symptoms", [])
        allergies = request.session.get("allergies", [])
        severity = request.POST.get("severity")

        recommendations = []

        for med in medications:

            searchable_text = (
                med.name + " " +
                med.description + " " +
                med.uses + " " +
                med.keywords
            ).lower()

            matched_symptoms = []

            for symptom in symptoms:
                if symptom.lower() in searchable_text:
                    matched_symptoms.append(symptom)

            if matched_symptoms:

                allergy_match = False

                for allergy in allergies:
                    allergy = allergy.lower().strip()

                    if allergy and allergy in med.name.lower():
                        allergy_match = True
                        break

                if allergy_match:
                    continue  # do not recommend medicine user is allergic to

                symptom_score = len(matched_symptoms) / len(symptoms) * 100

                keyword_matches = sum(
                    1 for s in symptoms if s.lower() in med.keywords.lower()
                )

                keyword_score = keyword_matches / len(symptoms) * 100

                if severity == "Mild":
                    severity_score = 90
                elif severity == "Moderate":
                    severity_score = 70
                else:
                    severity_score = 50

                confidence = round(
                    symptom_score * 0.5 +
                    keyword_score * 0.3 +
                    severity_score * 0.2
                )

                if severity == "Severe":
                    risk = "Medium"
                elif confidence < 50:
                    risk = "Medium"
                else:
                    risk = "Low"

                explanation = (
                    f"{med.name} was recommended because it matched "
                    f"{len(matched_symptoms)} symptom(s): "
                    f"{', '.join(matched_symptoms)}. "

                    f"The recommendation confidence score is "
                    f"{round(confidence)}%. "

                    f"Risk level assessed: {risk}. "

                    f"Your selected severity level was {severity}."
                )

                recommendations.append({
                    "med": med,
                    "confidence": confidence,
                    "risk": risk,
                    "explanation": explanation
                })

        recommendations = sorted(
            recommendations,
            key=lambda x: x["confidence"],
            reverse=True
        )[:3]

        if not recommendations:

            return render(request, 'ai_checker.html', {
                'step': 4,
                'safe_message': 'No safe recommendation was found based on your symptoms and allergies.',
                'all_symptoms': all_symptoms,
                'all_allergies': all_allergies,
            })

        for rec in recommendations:
            AIRecommendationLog.objects.create(
                user=request.user,
                symptoms=", ".join(symptoms),
                recommended_medication=rec["med"].name,
                confidence_score=rec["confidence"],
                risk_level=rec["risk"],
                explanation=rec["explanation"]
            )

        return render(request, "ai_checker.html", {
            "step": 4,
            "medication_objects": recommendations,
            "severity": severity,
            "symptoms": symptoms,
            "allergies": allergies,
            "all_symptoms": all_symptoms,
            "all_allergies": all_allergies,
        })

    return render(request, "ai_checker.html", {
        "step": step,
        "all_symptoms": all_symptoms,
        "all_allergies": all_allergies,
    })

