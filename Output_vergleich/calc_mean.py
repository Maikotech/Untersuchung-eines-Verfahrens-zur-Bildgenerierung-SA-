import numpy as np

werte_clipscore_fp32 = [0.3020116090774536,
0.241691455245018,
0.3003799021244049
]
mean_wert_cs_fp32 = np.mean(werte_clipscore_fp32)

print("Mean value cs fp32:", mean_wert_cs_fp32)


werte_clipscore_bf16 = [0.28489845991134644,
0.242447167634964,
0.2973809838294983
]
mean_wert_cs_bf16 = np.mean(werte_clipscore_bf16)

print("Mean value cs bf16:", mean_wert_cs_bf16)

ssim_werte_fp16 = [0.3849, 0.3991, 0.0936, 
                   0.1166, 0.3420, 0.3426]
ssim_werte_bf16 = [0.4206, 0.3991,
                    0.0810, 0.1166, 
                    0.3664, 0.3426,]
ssim_werte_fp32 = [0.3849, 0.4206,
                   0.0936, 0.0810,
                   0.3420, 0.3664]

mean_ssim_fp16 = np.mean(ssim_werte_fp16)
mean_ssim_bf16 = np.mean(ssim_werte_bf16)
mean_ssim_fp32 = np.mean(ssim_werte_fp32)

lpips_werte_fp16 = [0.7577, 0.7217, 0.8309, 0.7774, 0.7216, 0.7138]
lpips_werte_bf16 = [0.6855, 0.7217, 0.7555, 0.7774, 0.6941, 0.7138]
lpips_werte_fp32 = [0.7577, 0.6855, 0.8309, 0.7555, 0.7216, 0.6941]

mean_lpips_fp16 = np.mean(lpips_werte_fp16)
mean_lpips_bf16 = np.mean(lpips_werte_bf16)
mean_lpips_fp32 = np.mean(lpips_werte_fp32)


print("Mean SSIM fp16:", mean_ssim_fp16)
print("Mean SSIM bf16:", mean_ssim_bf16)
print("Mean SSIM fp32:", mean_ssim_fp32)

print("Mean LPIPS fp16:", mean_lpips_fp16)
print("Mean LPIPS bf16:", mean_lpips_bf16)
print("Mean LPIPS fp32:", mean_lpips_fp32)