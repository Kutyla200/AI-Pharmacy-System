from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Medication(models.Model):

    name = models.CharField(max_length=200)
    description = models.TextField()
    uses = models.TextField()
    side_effects = models.TextField()
    warnings = models.TextField()
    dosage = models.TextField()

    # Needed for AI symptom matching
    keywords = models.TextField(default="", blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name


class CartItem(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.medication.name}"


class Order(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.medication.name


class DrugInteraction(models.Model):

    medication1 = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name='interaction_med1'
    )

    medication2 = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name='interaction_med2'
    )

    severity_choices = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    severity = models.CharField(
        max_length=10,
        choices=severity_choices
    )

    description = models.TextField()

    def __str__(self):
        return f"{self.medication1.name} + {self.medication2.name}"


class AIRecommendationLog(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symptoms = models.TextField()
    recommended_medication = models.CharField(max_length=200)
    confidence_score = models.IntegerField()
    risk_level = models.CharField(max_length=20)
    explanation = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.recommended_medication}"


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    allergies = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

    if created:
        Profile.objects.create(user=instance)