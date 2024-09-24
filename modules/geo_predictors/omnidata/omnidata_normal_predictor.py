import torch
import torch.nn.functional as F
from torchvision import transforms

import PIL
from PIL import Image

from modules.geo_predictors.geo_predictor import GeoPredictor
from .modules.unet import UNet
from .modules.midas.dpt_depth import DPTDepthModel
from .transforms import get_transform


class OmnidataNormalPredictor(GeoPredictor):
    def __init__(self):
        super().__init__()
        self.img_size = 384
        ckpt_path = './checkpoints/omnidata_dpt_normal_v2.ckpt'
        self.model = DPTDepthModel(backbone='vitb_rn50_384', num_channels=3)
        self.model.to(torch.device('cpu'))
        checkpoint = torch.load(ckpt_path, map_location=torch.device('cpu'))
        if 'state_dict' in checkpoint:
            state_dict = {}
            for k, v in checkpoint['state_dict'].items():
                state_dict[k[6:]] = v
        else:
            state_dict = checkpoint

        self.model.load_state_dict(state_dict)
        self.trans_totensor = transforms.Compose([transforms.Resize(self.img_size, interpolation=Image.BILINEAR),
                                                  transforms.CenterCrop(self.img_size),
                                                  transforms.Normalize(mean=0.5, std=0.5)])

    def predict_normal(self, img):
        self.model.to(torch.device('cuda'))
        img_tensor = self.trans_totensor(img)
        output = self.model(img_tensor)
        self.model.to(torch.device('cpu'))
        output = F.interpolate(output, size=(512, 512), mode='bicubic')
        return output
