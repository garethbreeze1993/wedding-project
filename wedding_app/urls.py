from django.urls import path
from .views import (HomeView, ItemDetailView, add_to_cart, checkout_page, remove_from_cart, puchased_gifts, purchase,
                    generate_report)

app_name = 'wedding_app'

urlpatterns = [
    path('', HomeView.as_view(), name='item-list'),
    path('product/<slug>/', ItemDetailView.as_view(), name='products'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('checkout/', checkout_page, name='checkout'),
    path('purchased-gifts/', puchased_gifts, name='purchased-gifts'),
    path('purchase/', purchase, name='purchase'),
    path('generate-report/', generate_report, name='generate-report')]

