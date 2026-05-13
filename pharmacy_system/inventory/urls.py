from django.urls import path
from . import views

urlpatterns = [
    
    path('medications/', views.medication_list, name='medications'),
    path('medication/<int:id>/', views.medication_detail, name='medication_detail'),

    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:med_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('bot-pharmacist/', views.bot_pharmacist, name='bot_pharmacist'),
    path('ai-checker/', views.ai_symptom_checker, name='ai_checker'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]