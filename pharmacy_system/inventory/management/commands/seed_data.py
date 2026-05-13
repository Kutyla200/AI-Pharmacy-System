from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import Medication, DrugInteraction

class Command(BaseCommand):
    help = "Seed default medications and test admin user"

    def handle(self, *args, **kwargs):

        medications = [
            {
                "name": "Panado",
                "description": "Paracetamol tablets commonly used for headache relief.",
                "uses": "Relief of headaches and mild pain.",
                "side_effects": "Nausea, rash, liver damage in overdose.",
                "warnings": "Do not exceed recommended dosage. Avoid alcohol.",
                "dosage": "500mg to 1000mg every 4-6 hours.",
                "keywords": "headache, fever, pain",
                "price": 35.99,
                "stock": 120,
            },
            {
                "name": "Grand-Pa",
                "description": "Powder medication used for headaches and body pain.",
                "uses": "Relief of headaches and mild fever.",
                "side_effects": "Dizziness, nausea, stomach irritation.",
                "warnings": "Contains caffeine. Avoid excessive use.",
                "dosage": "1 powder every 6 hours.",
                "keywords": "headache, body pain, fever",
                "price": 28.50,
                "stock": 90,
            },
            {
                "name": "Calpol",
                "description": "Paracetamol syrup for reducing fever.",
                "uses": "Relieves fever and mild pain.",
                "side_effects": "Nausea, allergic reactions.",
                "warnings": "Use correct dosage for age group.",
                "dosage": "10ml every 4-6 hours.",
                "keywords": "fever, pain",
                "price": 45.00,
                "stock": 80,
            },
            {
                "name": "Empaped",
                "description": "Paracetamol-based medication for fever reduction.",
                "uses": "Used to reduce fever and pain.",
                "side_effects": "Rash, nausea, liver issues in overdose.",
                "warnings": "Do not exceed daily dosage limit.",
                "dosage": "500mg every 6 hours.",
                "keywords": "fever, headache, pain",
                "price": 39.99,
                "stock": 100,
            },
            {
                "name": "Myprodol",
                "description": "Combination pain relief capsules.",
                "uses": "Relief of moderate pain and muscle aches.",
                "side_effects": "Drowsiness, nausea, constipation.",
                "warnings": "May cause dependence if overused.",
                "dosage": "1-2 capsules every 6 hours.",
                "keywords": "pain, body pain, muscle pain",
                "price": 69.99,
                "stock": 70,
            },
            {
                "name": "Adco-Dol",
                "description": "Pain relief tablets for moderate pain.",
                "uses": "Relieves body pain and discomfort.",
                "side_effects": "Dizziness, nausea, constipation.",
                "warnings": "Avoid driving if drowsy.",
                "dosage": "2 tablets every 6 hours.",
                "keywords": "pain, body pain",
                "price": 59.99,
                "stock": 85,
            },
            {
                "name": "Brufen",
                "description": "Ibuprofen tablets used for inflammation and pain.",
                "uses": "Relieves inflammation, swelling and pain.",
                "side_effects": "Stomach irritation, nausea, dizziness.",
                "warnings": "Take after meals. Avoid prolonged use.",
                "dosage": "400mg every 8 hours.",
                "keywords": "pain, inflammation, swelling, muscle pain",
                "price": 74.50,
                "stock": 110,
            },
            {
                "name": "Nurofen",
                "description": "Ibuprofen medication for pain and inflammation.",
                "uses": "Relieves inflammation and muscle pain.",
                "side_effects": "Heartburn, stomach pain, dizziness.",
                "warnings": "Do not use with other NSAIDs.",
                "dosage": "200mg to 400mg every 8 hours.",
                "keywords": "pain, inflammation, swelling, headache",
                "price": 79.99,
                "stock": 95,
            },
            {
                "name": "Allergex",
                "description": "Antihistamine tablets for allergy relief.",
                "uses": "Relieves allergy symptoms and itching.",
                "side_effects": "Drowsiness, dry mouth.",
                "warnings": "Avoid alcohol while taking this medication.",
                "dosage": "1 tablet every 8 hours.",
                "keywords": "allergies, itching, sneezing, runny nose, rash",
                "price": 42.99,
                "stock": 140,
            },
            {
                "name": "Zyrtec",
                "description": "Cetirizine antihistamine tablets.",
                "uses": "Relieves allergies and hay fever symptoms.",
                "side_effects": "Drowsiness, headache, fatigue.",
                "warnings": "Use cautiously when driving.",
                "dosage": "10mg once daily.",
                "keywords": "allergies, sneezing, itching, rash",
                "price": 89.99,
                "stock": 100,
            },
            {
                "name": "Sinutab",
                "description": "Cold and flu medication for sneezing and congestion.",
                "uses": "Relieves sneezing, congestion and sinus pressure.",
                "side_effects": "Drowsiness, dry mouth, dizziness.",
                "warnings": "Do not mix with other cold medications.",
                "dosage": "2 tablets every 6 hours.",
                "keywords": "cold, flu, sneezing, congestion, blocked nose, sinus",
                "price": 65.00,
                "stock": 75,
            },
            {
                "name": "Benadryl Allergy",
                "description": "Antihistamine syrup for sneezing and allergies.",
                "uses": "Relieves sneezing and allergic reactions.",
                "side_effects": "Drowsiness, dry mouth.",
                "warnings": "May cause sleepiness.",
                "dosage": "10ml every 6 hours.",
                "keywords": "allergies, sneezing, itching, runny nose",
                "price": 54.99,
                "stock": 85,
            },
        ]

        for med in medications:

            existing = Medication.objects.filter(name=med["name"])

            if existing.exists():
                existing.first().__dict__.update()
                medication = existing.first()

                medication.description = med["description"]
                medication.uses = med["uses"]
                medication.side_effects = med["side_effects"]
                medication.warnings = med["warnings"]
                medication.dosage = med["dosage"]
                medication.keywords = med["keywords"]
                medication.price = med["price"]
                medication.stock = med["stock"]
                medication.save()

                existing.exclude(id=medication.id).delete()

            else:
                Medication.objects.create(**med)
            
        self.stdout.write(self.style.SUCCESS("Medications seeded successfully."))


        interactions = [
            {
                "med1": "Panado",
                "med2": "Calpol",
                "severity": "High",
                "description": "Both contain paracetamol. Taking them together may increase overdose and liver damage risk."
            },
            {
                "med1": "Panado",
                "med2": "Empaped",
                "severity": "High",
                "description": "Both contain paracetamol. Avoid combining unless advised by a healthcare professional."
            },
            {
                "med1": "Calpol",
                "med2": "Empaped",
                "severity": "High",
                "description": "Both are paracetamol-based medicines. Combining them may cause excessive paracetamol intake."
            },
            {
                "med1": "Brufen",
                "med2": "Nurofen",
                "severity": "High",
                "description": "Both contain ibuprofen/NSAID effects. Taking them together increases stomach irritation and bleeding risk."
            },
            {
                "med1": "Brufen",
                "med2": "Aspirin",
                "severity": "High",
                "description": "Combining NSAIDs may increase stomach bleeding, ulcers, and irritation."
            },
            {
                "med1": "Nurofen",
                "med2": "Aspirin",
                "severity": "High",
                "description": "Combining NSAIDs may increase bleeding and stomach ulcer risk."
            },
            {
                "med1": "Allergex",
                "med2": "Benadryl Allergy",
                "severity": "Medium",
                "description": "Both are antihistamines and may increase drowsiness, dry mouth, and dizziness."
            },
            {
                "med1": "Allergex",
                "med2": "Zyrtec",
                "severity": "Medium",
                "description": "Combining antihistamines may increase side effects such as drowsiness."
            },
            {
                "med1": "Zyrtec",
                "med2": "Benadryl Allergy",
                "severity": "Medium",
                "description": "Both treat allergies. Taking together may increase drowsiness and side effects."
            },
            {
                "med1": "Sinutab",
                "med2": "Allergex",
                "severity": "Medium",
                "description": "Both may cause drowsiness. Combining them may increase sleepiness and dizziness."
            },
            {
                "med1": "Sinutab",
                "med2": "Benadryl Allergy",
                "severity": "Medium",
                "description": "May increase drowsiness and dry mouth because both can affect allergy/cold symptoms."
            },
        ]

        for interaction in interactions:
            med1 = Medication.objects.filter(name=interaction["med1"]).first()
            med2 = Medication.objects.filter(name=interaction["med2"]).first()

            if med1 and med2:
                DrugInteraction.objects.update_or_create(
                    medication1=med1,
                    medication2=med2,
                    defaults={
                        "severity": interaction["severity"],
                        "description": interaction["description"]
                    }
                )

        self.stdout.write(self.style.SUCCESS("Drug interactions seeded successfully."))

        
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin123"
            )
            self.stdout.write(self.style.SUCCESS("Default superuser created: admin / admin123"))
        else:
            self.stdout.write(self.style.WARNING("Superuser 'admin' already exists."))