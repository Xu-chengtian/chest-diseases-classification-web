from django.shortcuts import render
from django.http import HttpResponse
from chest.models import Chest
from PIL import Image
import os
import random
from django import forms
from test import test_pic
from heatmap import heatmap
from torchvision import transforms
import shutil
import subprocess
# Create your views here.

disease_en={1: 'Atelectasis', 2: 'Cardiomegaly', 3: 'Effusion', 4: 'Infiltration', 5: 'Mass', 
         6: 'Nodule', 7: 'Pneumonia', 8: 'Pneumothorax', 9: 'Consolidation', 10: 'Edema', 
         11: 'Emphysema', 12: 'Fibrosis', 13: 'Pleural_Thickening', 14: 'Hernia'}

disease_cn={1: '肺不张', 2: '心脏肥大', 3: '积液', 4: '浸润', 5: '肿块', 
         6: '结节', 7: '肺炎', 8: '气胸', 9: '变实', 10: '水肿', 
         11: '肺气肿', 12: '纤维变性', 13: '胸膜增厚', 14: '疝气'}

def handle_uploaded_file(f,folder):
    if folder=='heatmap':
        shutil.rmtree(os.path.join(os.getcwd(),'chest','static','heatmap'))
        os.makedirs(os.path.join(os.getcwd(),'chest','static','heatmap'))
    with open(os.path.join(os.getcwd(),'chest','static',folder,'photo.jpg'), "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def preprocess_photo():
    picture = Image.open(os.path.join(os.getcwd(),'chest','static','preprocess','photo.jpg'))
    transform_test = transforms.Compose([
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize(256),
    ])
    picture = transform_test(picture)
    picture.save(os.path.join(os.getcwd(),'chest','static','preprocess','photo_resize.jpg'))
    transform_test = transforms.Compose([
        transforms.CenterCrop(224),
    ])
    picture = transform_test(picture)
    picture.save(os.path.join(os.getcwd(),'chest','static','preprocess','photo_crop.jpg'))
    transform_test = transforms.Compose([
        transforms.RandomHorizontalFlip(),
    ])
    picture = transform_test(picture)
    picture.save(os.path.join(os.getcwd(),'chest','static','preprocess','photo_horizontal.jpg'))
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4722708), (0.22180891)),
        transforms.ToPILImage(),
    ])
    picture = transform_test(picture)
    picture.save(os.path.join(os.getcwd(),'chest','static','preprocess','photo_normalize.jpg'))

def index(request):
    return render(request, 'index.html')

def dataset(request):
    return  render(request, 'dataset.html')

def preprocess(request):
    if request.method == "POST":
        handle_uploaded_file(request.FILES["image[]"],'preprocess')
        preprocess_photo()
        return render(request, 'show_preprocess.html',)
    
    return render(request, 'preprocess.html')

def preprocess_random(request):
    if request.method == "POST":
        # 随机获取图片
        preprocess_photo()
        return render(request, 'show_preprocess.html',)

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
        handle_uploaded_file(request.FILES["image[]"],'heatmap')
        model_path=os.path.join(os.getcwd(),'models','05-06-21-44-epoch30.pth')
        test_result = heatmap(os.path.join(os.getcwd(),'chest','static','heatmap','photo.jpg'),model_path)
        print(test_result)
        
        diagnose=[]
        imgs=[]
        for i in range(14):
            diagnose.append({'disease_en':disease_en[i+1],'disease_cn':disease_cn[i+1],'diagnose':test_result[i]})
            if test_result[i]==1:
                imgs.append({'disease':disease_cn[i+1],'image':'heatmap'+str(i+1)+'.jpg'})

        return render(request, 'show_classification.html',
                      {
                          'diagnose':diagnose,
                          'imgs':imgs
                      }
                      )
    
    return render(request, 'classification.html')

def classification_random(request):
    if request.method == "POST":
        shutil.rmtree(os.path.join(os.getcwd(),'chest','static','heatmap'))
        os.makedirs(os.path.join(os.getcwd(),'chest','static','heatmap'))
        picture = Image.open(os.path.join(os.getcwd(),'chest','static','xray','photo.jpg'))
        picture.save(os.path.join(os.getcwd(),'chest','static','heatmap','photo.jpg'))
        model_path=os.path.join(os.getcwd(),'models','05-06-21-44-epoch30.pth')
        test_result = heatmap(os.path.join(os.getcwd(),'chest','static','heatmap','photo.jpg'),model_path)
        diagnose=[]
        imgs=[]
        for i in range(14):
            diagnose.append({'disease_en':disease_en[i+1],'disease_cn':disease_cn[i+1],'diagnose':test_result[i]})
            if test_result[i]==1:
                imgs.append({'disease':disease_cn[i+1],'image':'heatmap'+str(i+1)+'.jpg'})

        return render(request, 'show_classification.html',
                      {
                          'diagnose':diagnose,
                          'imgs':imgs
                      }
                      )

def model(request):
    model_parameter=[]
    hardware=[]
    model_parameter.append({'picture':'../static/model/learning_rate.png','head':'学习率','content':'学习率是在梯度下降中，根据模型损失函数调整模型各部分权重的超参数。'})
    model_parameter.append({'picture':'../static/model/test_loss.png','head':'测试集损失','content':'测试集数据经过模型计算后的损失值'})
    model_parameter.append({'picture':'../static/model/accuracy.png','head':'整体准确率','content':'所有结果与标签完全一致的图像在测试集中的占比'})
    model_parameter.append({'picture':'../static/model/label_accuracy.png','head':'标签准确率','content':'所有预测准确的标签在14个标签中的占比，并求测试集所有图像的该准确率的平均值'})
    model_parameter.append({'picture':'../static/model/precision.png','head':'精准率','content':'表示预测为真的标签中预测正确的标签所占的比例'})
    model_parameter.append({'picture':'../static/model/recall.png','head':'召回率','content':'表示预测为真的标签在应该预测为真的标签中的比例'})
    model_parameter.append({'picture':'../static/model/F1_score.png','head':'F1分数','content':'综合了精准率和召回率的调和平均数'})
    model_parameter.append({'picture':'../static/model/hamming_loss.png','head':'汉明损失','content':'统计被误分类的标签在所有标签中的占比'})
    model_parameter.append({'picture':'../static/model/01_loss.png','head':'0-1损失','content':'计算分类任务的损失，当预测标签与真实标签不符时记为1，相符时记为0'})
    hardware.append({'picture':'../static/model/GPU_usage.png','head':'GPU利用率','content':'在训练集训练时，主要使用GPU进行计算'})
    hardware.append({'picture':'../static/model/GPU_temp.png','head':'GPU温度','content':'长时间的训练会导致GPU温度升高'})
    hardware.append({'picture':'../static/model/CPU_usage.png','head':'CPU利用率','content':'测试集测试主要使用CPU计算'})
    return render(request, 'model.html',
                  {
                      'model_parameter':model_parameter,
                      'hardwares':hardware
                  }
                  )