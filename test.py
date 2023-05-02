from densenet import DenseNet
from torchvision import transforms
from PIL import Image
import numpy as np
import torch

def test_pic(path):
    transform_test = transforms.Compose([
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize((0.4722708), (0.22180891))
    ])
    test_pic = Image.open(path)
    # test_pic = np.array(test_pic)
    test_pic = transform_test(test_pic)
    test_pic = torch.unsqueeze(test_pic,0)

    net = DenseNet()
    pretrained = torch.load("/Users/xuchengtian/code/chest-diseases-classification-web/27-11-54-24-epoch2.pth")
    net.load_state_dict(pretrained['net'])
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    net.to(device)
    output = net(test_pic)
    ans = torch.where(output>=0.5,1,0)
    return ans.tolist()[0]

