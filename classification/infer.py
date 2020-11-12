import os
import sys
import random
import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
from torchvision.transforms import transforms
import argparse
import cv2
import numpy as np


seed = 1234
random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False


checkpoint_path = "model_196000.pth"

CATEGORIES2LABELS = {
    0: "bg",
    1: "text",
    2: "title",
    3: "list",
    4: "table",
    5: "figure"
}


def get_instance_segmentation_model(num_classes):
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256

    model.roi_heads.mask_predictor = MaskRCNNPredictor(
        in_features_mask,
        hidden_layer,
        num_classes
    )
    return model


def infer_image(image_path):
    num_classes = 6

    # Get model and send to GPU
    model = get_instance_segmentation_model(num_classes)
    model.cuda()

    # Assure model exists and prepare it
    assert os.path.exists(checkpoint_path)
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    model.load_state_dict(checkpoint['model'])
    model.eval()

    # Ensure that image exists
    assert os.path.exists(image_path)

    # Transform image
    image = cv2.imread(image_path)
    rat = 1300 / image.shape[0]
    image = cv2.resize(image, None, fx=rat, fy=rat)

    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor()
    ])
    image = transform(image)

    # Classify document elements
    with torch.no_grad():
        prediction = model([image.cuda()])

    return prediction

# TODO: Refactor
def infer_image_with_mask(image_path, output_folder):
    num_classes = 6

    # Get model and send to GPU
    model = get_instance_segmentation_model(num_classes)
    model.cuda()

    # Assure model exists and prepare it
    assert os.path.exists(checkpoint_path)
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    model.load_state_dict(checkpoint['model'])
    model.eval()

    # Ensure that image exists
    assert os.path.exists(image_path)

    # Transform image
    image = cv2.imread(image_path)
    rat = 1300 / image.shape[0]
    image = cv2.resize(image, None, fx=rat, fy=rat)

    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor()
    ])
    image = transform(image)

    # Classify document elements
    with torch.no_grad():
        prediction = model([image.cuda()])

    image = torch.squeeze(image, 0).permute(1, 2, 0).mul(255).numpy().astype(np.uint8)

    for pred in prediction:
        for idx, mask in enumerate(pred['masks']):
            if pred['scores'][idx].item() < 0.7:
                continue

            m = mask[0].mul(255).byte().cpu().numpy()
            box = list(map(int, pred["boxes"][idx].tolist()))
            label = CATEGORIES2LABELS[pred["labels"][idx].item()]

            score = pred["scores"][idx].item()

            image = overlay_ann(image, m, box, label, score)

    cv2.imwrite(output_folder + "{}".format(os.path.basename(image_path)), image)

### Colouring utilities ###
# TODO: Make colours consistent

def show(img, name="disp", width=1000):
    """
    name: name of window, should be name of img
    img: source of img, should in type ndarray
    """
    cv2.namedWindow(name, cv2.WINDOW_GUI_EXPANDED)
    cv2.resizeWindow(name, width, 1000)
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def overlay_mask(image, mask, alpha=0.5):
    c = (np.random.random((1, 3)) * 153 + 102).tolist()[0]
 
    mask = np.dstack([mask.astype(np.uint8)] * 3)
    mask = cv2.threshold(mask, 127.5, 255, cv2.THRESH_BINARY)[1]
    inv_mask = 255 - mask

    overlay = image.copy()
    overlay = np.minimum(overlay, inv_mask) 

    color_mask = (mask.astype(np.bool) * c).astype(np.uint8)
    overlay = np.maximum(overlay, color_mask).astype(np.uint8) 

    image = cv2.addWeighted(image, alpha, overlay, 1 - alpha, 0)
    return image

def overlay_ann(image, mask, box, label, score, alpha=0.5):
    c = np.random.random((1, 3))
    mask_color = (c * 153 + 102).tolist()[0]
    text_color = (c * 183 + 72).tolist()[0]
 
    mask = np.dstack([mask.astype(np.uint8)] * 3)
    mask = cv2.threshold(mask, 127.5, 255, cv2.THRESH_BINARY)[1]
    inv_mask = 255 - mask

    overlay = image.copy()
    overlay = np.minimum(overlay, inv_mask) 

    color_mask = (mask.astype(np.bool) * mask_color).astype(np.uint8)
        
    overlay = np.maximum(overlay, color_mask).astype(np.uint8) 

    image = cv2.addWeighted(image, alpha, overlay, 1 - alpha, 0)

    # draw on color mask
    cv2.rectangle(
        image,
        (box[0], box[1]),
        (box[2], box[3]),
        mask_color, 1
    )

    (label_size_width, label_size_height), base_line = \
        cv2.getTextSize(
            "{}".format(label),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.3, 1
        )

    cv2.rectangle(
        image,
        (box[0], box[1] + 10),
        (box[0] + label_size_width, box[1] + 10 - label_size_height),
        (223, 128, 255),
        cv2.FILLED
    )

    cv2.putText(
        image,
        "{}: {:.3f}".format(label, score),
        (box[0], box[1] + 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.3, (0, 0, 0), 1
    )
 
    return image


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("output", type=str)
    args = parser.parse_args()

    infer_image_with_mask(args.input, args.output)
    exit()