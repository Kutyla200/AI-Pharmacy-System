"""
SEEDER - AI Pharmacy System
============================
Place this file at:
pharmacy_system/inventory/management/commands/seed_all.py

You also need to create these folders if they don't exist:
  inventory/management/__init__.py
  inventory/management/commands/__init__.py

Run with:
  python manage.py seed_all
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import (
    Medication,
    CartItem,
    Order,
    OrderItem,
    DrugInteraction,
    AIRecommendationLog,
)


class Command(BaseCommand):

    help = 'Seeds the database with sample data for all models'

    def handle(self, *args, **kwargs):

        self.stdout.write('\n==============================')
        self.stdout.write('   AI PHARMACY SYSTEM SEEDER  ')
        self.stdout.write('==============================\n')

        self.seed_users()
        self.seed_medications()
        self.seed_drug_interactions()
        self.seed_cart_items()
        self.seed_orders()
        self.seed_ai_logs()

        self.stdout.write(self.style.SUCCESS('\n✅ All seeders completed successfully!\n'))


    # ------------------------------------------------------------------
    # 1. USERS
    # ------------------------------------------------------------------
    def seed_users(self):

        self.stdout.write('📌 Seeding users...')

        users_data = [
            {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@pharmacy.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'username': 'john_doe',
                'password': 'password123',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'is_superuser': False,
                'is_staff': False,
            },
            {
                'username': 'jane_doe',
                'password': 'password123',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'is_superuser': False,
                'is_staff': False,
            },
        ]

        for data in users_data:

            if User.objects.filter(username=data['username']).exists():
                self.stdout.write(f"  ⚠  User '{data['username']}' already exists, skipping.")
                continue

            User.objects.create_user(
                username=data['username'],
                password=data['password'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                is_superuser=data['is_superuser'],
                is_staff=data['is_staff'],
            )

            self.stdout.write(self.style.SUCCESS(f"  ✔  Created user: {data['username']}"))


    # ------------------------------------------------------------------
    # 2. MEDICATIONS
    # ------------------------------------------------------------------
    def seed_medications(self):

        self.stdout.write('\n📌 Seeding medications...')

        medications_data = [
            {
                'name': 'Paracetamol',
                'description': 'A common pain reliever and fever reducer.',
                'uses': 'Used to treat mild to moderate pain (headaches, muscle aches) and fever.',
                'side_effects': 'Nausea, stomach pain, loss of appetite. Rarely: skin rash.',
                'warnings': 'Do not exceed recommended dose. Avoid alcohol. Consult doctor if pregnant.',
                'dosage': 'Adults: 500mg–1g every 4–6 hours. Max 4g per day.',
                'price': 25.00,
                'stock': 150,
            },
            {
                'name': 'Panado',
                'description': 'Brand-name paracetamol commonly used in South Africa.',
                'uses': 'Relief of mild to moderate pain and fever.',
                'side_effects': 'Rare side effects include allergic reactions and liver damage in overdose.',
                'warnings': 'Do not take with other paracetamol-containing products.',
                'dosage': 'Adults: 1–2 tablets every 4–6 hours as needed.',
                'price': 35.00,
                'stock': 120,
            },
            {
                'name': 'Ibuprofen',
                'description': 'A nonsteroidal anti-inflammatory drug (NSAID).',
                'uses': 'Treats pain, fever, and inflammation. Effective for arthritis and muscle pain.',
                'side_effects': 'Stomach upset, heartburn, dizziness. May increase risk of stomach bleeding.',
                'warnings': 'Avoid on empty stomach. Not recommended for patients with kidney/heart issues.',
                'dosage': 'Adults: 200mg–400mg every 4–6 hours. Max 1200mg per day (OTC).',
                'price': 45.00,
                'stock': 100,
            },
            {
                'name': 'Aspirin',
                'description': 'An NSAID used for pain relief, fever, and anti-platelet therapy.',
                'uses': 'Mild pain relief. Also used in low doses to prevent heart attacks and strokes.',
                'side_effects': 'Stomach irritation, bleeding, tinnitus at high doses.',
                'warnings': 'Not for children under 16. Avoid if allergic to NSAIDs or have bleeding disorders.',
                'dosage': 'Pain/fever: 300mg–600mg every 4 hours. Cardiac: 75mg–150mg once daily.',
                'price': 20.00,
                'stock': 90,
            },
            {
                'name': 'Loratadine',
                'description': 'A second-generation antihistamine for allergy relief.',
                'uses': 'Relieves symptoms of allergic rhinitis, hives, and other allergy conditions.',
                'side_effects': 'Headache, dry mouth, drowsiness (less than older antihistamines).',
                'warnings': 'Use with caution in liver impairment. Avoid alcohol.',
                'dosage': 'Adults and children 12+: 10mg once daily.',
                'price': 55.00,
                'stock': 80,
            },
            {
                'name': 'Cetirizine',
                'description': 'An antihistamine used to treat allergy symptoms.',
                'uses': 'Allergic rhinitis, chronic urticaria (hives), hay fever.',
                'side_effects': 'Drowsiness, dry mouth, fatigue, headache.',
                'warnings': 'May impair driving. Use caution with alcohol. Adjust dose for renal impairment.',
                'dosage': 'Adults: 10mg once daily, or 5mg twice daily.',
                'price': 60.00,
                'stock': 75,
            },
            {
                'name': 'Amoxicillin',
                'description': 'A broad-spectrum penicillin-type antibiotic.',
                'uses': 'Treats bacterial infections including ear, nose, throat, skin, and urinary tract infections.',
                'side_effects': 'Diarrhea, nausea, rash. Rarely: severe allergic reaction (anaphylaxis).',
                'warnings': 'Prescription required. Inform doctor of penicillin allergy. Complete full course.',
                'dosage': 'Adults: 250mg–500mg every 8 hours or 500mg–1g every 12 hours.',
                'price': 85.00,
                'stock': 60,
            },
            {
                'name': 'Omeprazole',
                'description': 'A proton pump inhibitor (PPI) that reduces stomach acid.',
                'uses': 'Treats heartburn, acid reflux, peptic ulcers, and GERD.',
                'side_effects': 'Headache, diarrhea, nausea, stomach pain.',
                'warnings': 'Long-term use may affect magnesium and B12 levels. Avoid if allergic to PPIs.',
                'dosage': 'Adults: 20mg once daily before a meal. Up to 40mg for severe cases.',
                'price': 70.00,
                'stock': 85,
            },
            {
                'name': 'Metformin',
                'description': 'An oral diabetes medication that helps control blood sugar levels.',
                'uses': 'Type 2 diabetes management. May also be used in PCOS.',
                'side_effects': 'Nausea, diarrhea, stomach upset (usually temporary).',
                'warnings': 'Prescription required. Avoid in severe kidney/liver disease. Monitor B12 levels.',
                'dosage': 'Initial: 500mg twice daily with meals. Can increase to 2000mg/day.',
                'price': 95.00,
                'stock': 50,
            },
            {
                'name': 'Vitamin C 1000mg',
                'description': 'High-dose Vitamin C supplement to support immune function.',
                'uses': 'Immune support, antioxidant protection, collagen synthesis.',
                'side_effects': 'High doses may cause stomach upset or diarrhea.',
                'warnings': 'Avoid very high doses (>2000mg/day) if prone to kidney stones.',
                'dosage': 'Adults: 1000mg once daily with food.',
                'price': 40.00,
                'stock': 200,
            },
        ]

        for data in medications_data:

            if Medication.objects.filter(name=data['name']).exists():
                self.stdout.write(f"  ⚠  Medication '{data['name']}' already exists, skipping.")
                continue

            Medication.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f"  ✔  Created medication: {data['name']}"))


    # ------------------------------------------------------------------
    # 3. DRUG INTERACTIONS
    # ------------------------------------------------------------------
    def seed_drug_interactions(self):

        self.stdout.write('\n📌 Seeding drug interactions...')

        interactions_data = [
            {
                'med1': 'Aspirin',
                'med2': 'Ibuprofen',
                'severity': 'High',
                'description': (
                    'Taking Aspirin and Ibuprofen together increases the risk of gastrointestinal '
                    'bleeding and may reduce the cardioprotective effect of low-dose Aspirin.'
                ),
            },
            {
                'med1': 'Ibuprofen',
                'med2': 'Metformin',
                'severity': 'Medium',
                'description': (
                    'NSAIDs like Ibuprofen can reduce kidney function, which may affect Metformin '
                    'clearance and increase the risk of lactic acidosis.'
                ),
            },
            {
                'med1': 'Aspirin',
                'med2': 'Metformin',
                'severity': 'Low',
                'description': (
                    'Salicylates like Aspirin may enhance the glucose-lowering effect of Metformin, '
                    'potentially causing hypoglycaemia in high doses.'
                ),
            },
            {
                'med1': 'Omeprazole',
                'med2': 'Metformin',
                'severity': 'Low',
                'description': (
                    'Omeprazole may slightly increase Metformin plasma levels. Monitor blood glucose '
                    'and adjust dose if necessary.'
                ),
            },
            {
                'med1': 'Cetirizine',
                'med2': 'Loratadine',
                'severity': 'Medium',
                'description': (
                    'Combining two antihistamines is generally not recommended as it increases the '
                    'risk of sedation, dry mouth, and urinary retention without added benefit.'
                ),
            },
        ]

        for data in interactions_data:

            try:
                med1 = Medication.objects.get(name=data['med1'])
                med2 = Medication.objects.get(name=data['med2'])
            except Medication.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠  Skipping interaction {data['med1']} + {data['med2']}: medication not found."
                    )
                )
                continue

            exists = DrugInteraction.objects.filter(
                medication1=med1, medication2=med2
            ).exists() or DrugInteraction.objects.filter(
                medication1=med2, medication2=med1
            ).exists()

            if exists:
                self.stdout.write(f"  ⚠  Interaction {data['med1']} + {data['med2']} already exists, skipping.")
                continue

            DrugInteraction.objects.create(
                medication1=med1,
                medication2=med2,
                severity=data['severity'],
                description=data['description'],
            )

            self.stdout.write(self.style.SUCCESS(
                f"  ✔  Created interaction: {data['med1']} ↔ {data['med2']} [{data['severity']}]"
            ))


    # ------------------------------------------------------------------
    # 4. CART ITEMS
    # ------------------------------------------------------------------
    def seed_cart_items(self):

        self.stdout.write('\n📌 Seeding cart items...')

        try:
            john = User.objects.get(username='john_doe')
            jane = User.objects.get(username='jane_doe')
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('  ⚠  Users not found. Run user seeder first.'))
            return

        cart_data = [
            {'user': john, 'medication_name': 'Paracetamol', 'quantity': 2},
            {'user': john, 'medication_name': 'Vitamin C 1000mg', 'quantity': 1},
            {'user': jane, 'medication_name': 'Loratadine', 'quantity': 1},
            {'user': jane, 'medication_name': 'Omeprazole', 'quantity': 2},
        ]

        for data in cart_data:

            try:
                medication = Medication.objects.get(name=data['medication_name'])
            except Medication.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"  ⚠  Medication '{data['medication_name']}' not found, skipping cart item."
                ))
                continue

            item, created = CartItem.objects.get_or_create(
                user=data['user'],
                medication=medication,
                defaults={'quantity': data['quantity']}
            )

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f"  ✔  Cart item: {data['user'].username} → {medication.name} x{data['quantity']}"
                ))
            else:
                self.stdout.write(f"  ⚠  Cart item already exists for {data['user'].username} → {medication.name}, skipping.")


    # ------------------------------------------------------------------
    # 5. ORDERS & ORDER ITEMS
    # ------------------------------------------------------------------
    def seed_orders(self):

        self.stdout.write('\n📌 Seeding orders...')

        try:
            john = User.objects.get(username='john_doe')
            jane = User.objects.get(username='jane_doe')
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('  ⚠  Users not found. Run user seeder first.'))
            return

        orders_data = [
            {
                'user': john,
                'items': [
                    {'medication_name': 'Ibuprofen', 'quantity': 1},
                    {'medication_name': 'Omeprazole', 'quantity': 1},
                ],
            },
            {
                'user': jane,
                'items': [
                    {'medication_name': 'Cetirizine', 'quantity': 2},
                    {'medication_name': 'Vitamin C 1000mg', 'quantity': 3},
                ],
            },
        ]

        for order_data in orders_data:

            order = Order.objects.create(user=order_data['user'])

            for item_data in order_data['items']:

                try:
                    medication = Medication.objects.get(name=item_data['medication_name'])
                except Medication.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"  ⚠  Medication '{item_data['medication_name']}' not found, skipping order item."
                    ))
                    continue

                OrderItem.objects.create(
                    order=order,
                    medication=medication,
                    quantity=item_data['quantity'],
                )

            self.stdout.write(self.style.SUCCESS(
                f"  ✔  Created Order #{order.id} for {order_data['user'].username} "
                f"({len(order_data['items'])} items)"
            ))


    # ------------------------------------------------------------------
    # 6. AI RECOMMENDATION LOGS
    # ------------------------------------------------------------------
    def seed_ai_logs(self):

        self.stdout.write('\n📌 Seeding AI recommendation logs...')

        try:
            john = User.objects.get(username='john_doe')
            jane = User.objects.get(username='jane_doe')
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('  ⚠  Users not found. Run user seeder first.'))
            return

        logs_data = [
            {
                'user': john,
                'symptoms': 'headache, fever',
                'recommended_medication': 'Paracetamol',
                'confidence_score': 90,
                'risk_level': 'Low',
                'explanation': 'Paracetamol is recommended for headache and fever relief.',
            },
            {
                'user': john,
                'symptoms': 'pain, inflammation',
                'recommended_medication': 'Ibuprofen',
                'confidence_score': 88,
                'risk_level': 'Medium',
                'explanation': 'Ibuprofen is effective for pain and inflammation.',
            },
            {
                'user': jane,
                'symptoms': 'allergies, sneezing',
                'recommended_medication': 'Loratadine',
                'confidence_score': 85,
                'risk_level': 'Low',
                'explanation': 'Loratadine is recommended to relieve allergy and sneezing symptoms.',
            },
            {
                'user': jane,
                'symptoms': 'sneezing, allergies',
                'recommended_medication': 'Cetirizine',
                'confidence_score': 80,
                'risk_level': 'Medium',
                'explanation': 'Cetirizine helps relieve allergic reactions and sneezing.',
            },
        ]

        for data in logs_data:

            AIRecommendationLog.objects.create(
                user=data['user'],
                symptoms=data['symptoms'],
                recommended_medication=data['recommended_medication'],
                confidence_score=data['confidence_score'],
                risk_level=data['risk_level'],
                explanation=data['explanation'],
            )

            self.stdout.write(self.style.SUCCESS(
                f"  ✔  AI log: {data['user'].username} → {data['recommended_medication']}"
            ))