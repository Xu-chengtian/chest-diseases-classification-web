import torch
from densenet import DenseNet
from PIL import Image
from torchvision import transforms
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import shutil

features_blobs=[]

def hook_feature(module, input, output):
    features_blobs.append(output.data.cpu().detach().numpy())

def returnCAM(feature_conv, weight_softmax, idx):
    # 生成CAM图: 输入是feature_conv和weight_softmax 
    bz, nc, h, w = feature_conv.shape  
    # feature_conv和weight_softmax 点乘(.dot)得到cam
    cam = weight_softmax[idx].dot(feature_conv.reshape((nc, h*w))) 
    cam = cam.reshape(h, w)
    cam = cam - np.min(cam)
    cam_img = cam / np.max(cam)
    cam_img = np.uint8(255 * cam_img)
    # cam_img = Image.fromarray(cam_img)
    # cam_img = cam_img.resize((224,224))
    cam_img = cv2.resize(cam_img, (224,224))
    return cam_img


def heatmap(path,model):
    shutil.rmtree(os.path.join(os.getcwd(),'chest','static','heatmap'))
    os.makedirs(os.path.join(os.getcwd(),'chest','static','heatmap'))
    transform_test = transforms.Compose([
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize((0.4722708), (0.22180891))
    ])
    picture = Image.open(path)
    # test_pic = np.array(test_pic)
    test_pic = transform_test(picture)
    test_pic = torch.unsqueeze(test_pic,0)

    net = DenseNet()
    pretrained = torch.load(model, map_location='cpu')
    net.load_state_dict(pretrained['net'])
    net.eval()
    # print(net)
    classify=net.state_dict()['classifier.weight'].squeeze(3).squeeze(2).numpy()
    # print(classify)
    # for name, _ in net.named_modules():
    #     print(name)
    net._modules['features']._modules.get('relu5').register_forward_hook(hook_feature)
    output = net(test_pic)
    ans = torch.where(output>=0.5,1,0).tolist()[0]
    # print(features_blobs[0].shape)
    img = cv2.imread(path)
    img = cv2.resize(img,(896,896))
    for idx,output in enumerate(ans):
        if output==1:
            CAMs = returnCAM(features_blobs[0], classify, idx)
            heatmap = cv2.applyColorMap(CAMs, cv2.COLORMAP_JET)
            heatmap = cv2.resize(heatmap, (896,896))
            result = heatmap * 0.2 + img * 0.9
            cv2.imwrite(os.path.join(os.getcwd(),'chest','static','heatmap','heatmap'+str(idx+1)+'.jpg'), result)
    return ans
