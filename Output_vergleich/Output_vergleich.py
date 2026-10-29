import torch
from PIL import Image
import torchvision.transforms as T
import lpips
from skimage.metrics import structural_similarity as ssim
import numpy as np

#Bilder laden
def load_image(path):
    return Image.open(path).convert('RGB')


img_fp16 = load_image(r"C:\U_M\Studienarbeit\Grafiken\fp_16\landscape\generated_image(11).png") #landscape: (11), minecraft (12), futuristic (13)
img_fp32 = load_image(r"C:\U_M\Studienarbeit\Grafiken\fp_32\landscape\generated_image(2).png") #landscape: (2), minecraft (1), futuristic (4)
img_bf16 = load_image(r"C:\U_M\Studienarbeit\Grafiken\bf_16\landscape\generated_image(4).png") #landscape: (4), minecraft (8), futuristic (2)

#SSIM Berechnen (mit numpy / scikit-image)
def compute_ssim(img1, img2):
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    # channel_axis=2 für RGB
    ssim_value = ssim(arr1, arr2, channel_axis=2) 
    return ssim_value
ssim_fp16_fp32 = compute_ssim(img_fp16, img_fp32)
ssim_fp16_bf16 = compute_ssim(img_fp16, img_bf16)
ssim_fp32_bf16 = compute_ssim(img_fp32, img_bf16)

print(f"SSIM (FP32 vs FP16): {ssim_fp16_fp32:.4f}")
print(f"SSIM (FP32 vs BF16): {ssim_fp32_bf16:.4f}")
print(f"SSIM (FP16 vs BF16): {ssim_fp16_bf16:.4f}")

print (f"Durchschnitt der SSIM : {np.array([ssim_fp16_fp32, ssim_fp32_bf16, ssim_fp16_bf16]).mean():.4f}")


#LPIPS Berechnen (Torch-basiert)
# Modell laden (vgg)
loss_fn_vgg = lpips.LPIPS(net='vgg') 

transform = T.Compose([
    T.ToTensor(),
    T.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]) # LPIPS erwartet [-1, 1]
])

t_fp32 = transform(img_fp32).unsqueeze(0)
t_fp16 = transform(img_fp16).unsqueeze(0)
t_bf16 = transform(img_bf16).unsqueeze(0)

with torch.no_grad():
    lpips_fp16 = loss_fn_vgg(t_fp32, t_fp16).item()
    lpips_bf16 = loss_fn_vgg(t_fp32, t_bf16).item()
    lpips_16_vs_b16 = loss_fn_vgg(t_fp16, t_bf16).item()

print(f"LPIPS (FP32 vs FP16): {lpips_fp16:.4f}")
print(f"LPIPS (FP32 vs BF16): {lpips_bf16:.4f}")
print(f"LPIPS (FP16 vs BF16): {lpips_16_vs_b16:.4f}")

print (f"Durchschnitt der LPIPS : {np.array([lpips_fp16, lpips_bf16, lpips_16_vs_b16]).mean():.4f}")