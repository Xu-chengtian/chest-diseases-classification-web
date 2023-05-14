from django.urls import path, include
import chest.views

urlpatterns = [
    path('', chest.views.index),
    path('dataset', chest.views.dataset),
    path('preprocess', chest.views.preprocess),
    path('hello_world', chest.views.hello_world),
    path('patient', chest.views.patient),
    path('classification', chest.views.classification),
    path('randompreprocess', chest.views.preprocess_random),
    path('model', chest.views.model),
    path('randomclassification', chest.views.classification_random),
]