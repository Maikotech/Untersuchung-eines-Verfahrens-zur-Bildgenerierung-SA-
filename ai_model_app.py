import torch
import numpy as np
import io
import base64
from PIL import Image
# from transformers import DPTFeatureExtractor, DPTForDepthEstimation
from diffusers import ControlNetModel, StableDiffusionXLControlNetPipeline, AutoencoderKL, StableDiffusionControlNetPipeline, StableDiffusion3ControlNetPipeline, SD3ControlNetModel
from flask import Flask, request, jsonify

app = Flask(__name__)

# Stable Diffusion XL ControlNet Pipeline
controlnet = ControlNetModel.from_pretrained(
    "diffusers/controlnet-depth-sdxl-1.0-small",
    local_files_only=True,
    variant="fp16",
    use_safetensors=True,
    torch_dtype=torch.float16,
).to("cuda")
vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", local_files_only=True, torch_dtype=torch.float32).to("cuda")
pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    controlnet=controlnet,
    local_files_only=True,
    vae=vae,
    variant="fp16",
    use_safetensors=True,
    torch_dtype=torch.float16,
).to("cuda")


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'Server is alive'}), 200

@app.route('/predict', methods=['POST'])
def predict():
    print("Received /predict request")
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image_file = request.files['image']
    depth_map = Image.open(image_file.stream).convert('L')
    depth_map = np.array(depth_map)  # Convert to numpy array for processing
    depth_map = depth_map[:, :, None]
    depth_map = np.concatenate([depth_map, depth_map, depth_map], axis=2)
    print(depth_map.shape)
    input_tensor = Image.fromarray(depth_map)

    prompt = request.form.get('prompt')
    print("Prompt: ", prompt)
    negative_prompt = "blurry, low quality, low resolution,  distorted, deformed, unrealistic depth, cropped, warped geometry, cartoon, anime, sketch, text, watermark, logo, signature, unrealistic shapes"
    gen_image = pipe(prompt=prompt, image=input_tensor, guess_mode=False, controlnet_conditioning_scale=0.7, negative_prompt=negative_prompt, num_inference_steps=20).images[0]

    buffered = io.BytesIO()
    gen_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return jsonify({'result': img_str})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
