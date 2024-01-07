from django.urls import path
from .views import haram_halal_detection, add_product, allergic_detection, cuisine_uses_prediction

urlpatterns = [
    path('haram-halal/<barcode>/', haram_halal_detection, name='haram_halal_detection'),
    path('add-product/', add_product, name='add_product'),
    path('allergic-detection/<barcode>/', allergic_detection, name='allergic_detection'),
    path('cuisine-uses-prediction/<barcode>/', cuisine_uses_prediction, name='cuisine_uses_prediction'),
]

