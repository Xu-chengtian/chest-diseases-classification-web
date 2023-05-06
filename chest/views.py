from django.shortcuts import render
from django.http import HttpResponse
from chest.models import Chest
from PIL import Image
import os
from django import forms
from test import test_pic
from heatmap import heatmap
# Create your views here.

disease_en={1: 'Atelectasis', 2: 'Cardiomegaly', 3: 'Effusion', 4: 'Infiltration', 5: 'Mass', 
         6: 'Nodule', 7: 'Pneumonia', 8: 'Pneumothorax', 9: 'Consolidation', 10: 'Edema', 
         11: 'Emphysema', 12: 'Fibrosis', 13: 'Pleural_Thickening', 14: 'Hernia'}

disease_cn={1: '肺不张', 2: '心脏肥大', 3: '积液', 4: '浸润', 5: '肿块', 
         6: '结节', 7: '肺炎', 8: '气胸', 9: '变实', 10: '水肿', 
         11: '肺气肿', 12: '纤维变性', 13: '胸膜增厚', 14: '疝气'}

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

        diagnose=[]
        img_name=[]
        for i in range(14):
            diagnose.append({'disease_en':disease_en[i+1],'disease_cn':disease_cn[i+1],'diagnose':test_result[i]})
            if test_result[i]==1:
                img_name.append('heatmap'+str(i+1)+'.jpg')

        return render(request, 'classification.html',
                      {
                          'diagnose':diagnose,
                          'imgs':img_name
                      }
                      )
 
    return render(request, 'upload.html')