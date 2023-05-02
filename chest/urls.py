from django.urls import path, include
import chest.views

urlpatterns = [
    path('hello_world', chest.views.hello_world),
    path('patient', chest.views.patient),
    path('classification', chest.views.classification),
]