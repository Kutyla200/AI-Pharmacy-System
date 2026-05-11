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

    warnings = set()

    medications = [item.medication for item in items]

    for med1 in medications:
        for med2 in medications:

            if med1 != med2:

                interaction = DrugInteraction.objects.filter(
                    medication1=med1,
                    medication2=med2
                ).first()

                reverse_interaction = DrugInteraction.objects.filter(
                    medication1=med2,
                    medication2=med1
                ).first()

                if interaction and interaction not in warnings:
                    warnings.add(interaction)

                if reverse_interaction and reverse_interaction not in warnings:
                    warnings.add(reverse_interaction)

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

@login_required
def ai_symptom_checker(request):

    medication_objects = []

    step = 1

    # STEP 1 → SELECT SYMPTOMS
    if request.method == "POST" and "symptoms" in request.POST:

        symptoms = request.POST.getlist('symptoms')

        request.session['symptoms'] = symptoms

        step = 2

        return render(request, 'ai_checker.html', {
            'step': step,
            'symptoms': symptoms
        })

    # STEP 2 → SELECT SEVERITY
    elif request.method == "POST" and "severity" in request.POST:

        symptoms = request.session.get('symptoms', [])

        severity = request.POST.get('severity')

        recommendations = []

        message = " ".join(symptoms).lower()

        # HEADACHE / FEVER
        if 'headache' in message or 'fever' in message:

            recommendations.append({
                'medicine': 'Paracetamol',
                'confidence': 90,
                'risk': 'Low',
                'explanation': f'I understand your symptoms are {severity.lower()}. Paracetamol may help reduce fever and headache.'
            })

            recommendations.append({
                'medicine': 'Panado',
                'confidence': 85,
                'risk': 'Low',
                'explanation': 'Panado may help relieve pain and fever symptoms.'
            })

        # ALLERGIES
        if 'allergies' in message or 'sneezing' in message:

            recommendations.append({
                'medicine': 'Loratadine',
                'confidence': 88,
                'risk': 'Low',
                'explanation': 'Loratadine may help reduce allergy symptoms and sneezing.'
            })

            recommendations.append({
                'medicine': 'Cetirizine',
                'confidence': 82,
                'risk': 'Medium',
                'explanation': 'Cetirizine helps relieve allergic reactions.'
            })

        # PAIN / INFLAMMATION
        if 'pain' in message or 'inflammation' in message:

            recommendations.append({
                'medicine': 'Ibuprofen',
                'confidence': 90,
                'risk': 'Medium',
                'explanation': 'Ibuprofen is commonly used for pain and inflammation.'
            })

            recommendations.append({
                'medicine': 'Aspirin',
                'confidence': 75,
                'risk': 'Medium',
                'explanation': 'Aspirin may assist with mild pain relief.'
            })

        # NOTHING MATCHED
        if not recommendations:

            recommendations.append({
                'medicine': 'Consult Pharmacist',
                'confidence': 50,
                'risk': 'High',
                'explanation': 'Symptoms unclear. Professional medical advice is recommended.'
            })

        # SAVE LOGS
        for rec in recommendations:

            AIRecommendationLog.objects.create(
                user=request.user,
                symptoms=", ".join(symptoms),
                recommended_medication=rec['medicine'],
                confidence_score=rec['confidence'],
                risk_level=rec['risk'],
                explanation=rec['explanation']
            )

        # GET MEDICATION OBJECTS
        for rec in recommendations:

            med = Medication.objects.filter(
                name__iexact=rec['medicine']
            ).first()

            if med:

                medication_objects.append({
                    'med': med,
                    'info': rec
                })

        step = 3

        return render(request, 'ai_checker.html', {
            'step': step,
            'medication_objects': medication_objects,
            'severity': severity,
            'symptoms': symptoms
        })

    return render(request, 'ai_checker.html', {
        'step': step
    })