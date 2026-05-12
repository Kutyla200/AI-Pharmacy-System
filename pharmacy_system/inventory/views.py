from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from .models import Medication, CartItem, Order, OrderItem
from .models import DrugInteraction
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
    return medication_list(request)

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

    # 🔥 THIS MUST COME BEFORE ANY USE
    warnings = []

    medications = [item.medication for item in items]

    print([m.name for m in medications])  # debug OK

    # interaction logic goes here
    for i in range(len(medications)):
        for j in range(i + 1, len(medications)):

            med1 = medications[i]
            med2 = medications[j]

            interaction = DrugInteraction.objects.filter(
                medication1=med1,
                medication2=med2
            ).first()

            if interaction:
                warnings.append(interaction)

    print(warnings)  # debug OK

    return render(request, 'cart.html', {
        'items': items,
        'total': total,
        'warnings': warnings
    })

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