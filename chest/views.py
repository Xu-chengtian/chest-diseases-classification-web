from django.shortcuts import render
from django.http import HttpResponse
from chest.models import Chest
from PIL import Image
import os
from django import forms
from test import test_pic
from heatmap import heatmap
# Create your views here.

disease={1: 'Atelectasis', 2: 'Cardiomegaly', 3: 'Effusion', 4: 'Infiltration', 5: 'Mass', 
         6: 'Nodule', 7: 'Pneumonia', 8: 'Pneumothorax', 9: 'Consolidation', 10: 'Edema', 
         11: 'Emphysema', 12: 'Fibrosis', 13: 'Pleural_Thickening', 14: 'Hernia', 0: 'No Finding'}

def handle_uploaded_file(f):
    with open(os.path.join(os.getcwd(),'photo.jpg'), "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def hello_world(request):
    return HttpResponse("Hello World")

def patient(request):
    patient = Chest.objects.all()[0]
    patient_id = patient.patient_id
    x_ray_id = patient.x_ray_id
    disease = patient.disease
    return_str = 'patient: %d, x ray id: %d, disease: %d' %(patient_id,x_ray_id,disease)

    return HttpResponse(return_str)

def classification(request):
    if request.method == "POST":
        handle_uploaded_file(request.FILES["image"])

        test_result = heatmap(os.path.join(os.getcwd(),'photo.jpg'),os.path.join(os.getcwd(),'0427115128','27-11-53-02-epoch1.pth'))
        ans=''
        for idx,i in enumerate(test_result):
            if i==0:
                continue
            ans+=disease[idx+1]+' : '+str(i)+' '
        if ans=='':
            ans='result: healthy'
        else:
            ans='result: '+ans
        return HttpResponse(ans)
 
    return render(request, 'upload.html')