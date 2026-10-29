import torch
import numpy as np
import io
import base64
from PIL import Image
# from transformers import DPTFeatureExtractor, DPTForDepthEstimation
from diffusers import ControlNetModel, StableDiffusionXLControlNetPipeline, AutoencoderKL, StableDiffusionControlNetPipeline, StableDiffusion3ControlNetPipeline, SD3ControlNetModel
from flask import Flask, request, jsonify
import time


app = Flask(__name__)

# Stable Diffusion XL ControlNet Pipeline
controlnet = ControlNetModel.from_pretrained(
    "diffusers/controlnet-depth-sdxl-1.0-small",
    local_files_only=True,
    variant="fp16",
    use_safetensors=True,
    torch_dtype=torch.float32
).to("cuda")
vae = AutoencoderKL.from_pretrained(
    "madebyollin/sdxl-vae-fp16-fix", 
    local_files_only=True, 
    torch_dtype=torch.float32
    ).to("cuda")
pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    controlnet=controlnet,
    local_files_only=True,
    vae=vae,
    variant="fp16",
    use_safetensors=True,
    torch_dtype=torch.float32
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


    # Inferenzzeit Messung
    torch.cuda.synchronize("cuda")
    start_ns = time.perf_counter_ns()
    
    # Bildgenerierung
    gen_image = pipe(
        prompt=prompt, image=input_tensor, guess_mode=False, 
        controlnet_conditioning_scale=0.7, negative_prompt=negative_prompt, 
        num_inference_steps=20).images[0]
    torch.cuda.synchronize("cuda")
    inference_time = (time.perf_counter_ns() - start_ns) / 1_000_000
    end_ns = time.perf_counter_ns()
    print(f"Inference Time: {inference_time} ms")

    buffered = io.BytesIO()
    gen_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return jsonify({'result': img_str})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

"""
Prompts (Schnittstelle aus der UI):
- "A futuristic vision of the world of tomorrow, blending advanced technology with striking architecture, seamless integration of nature and innovation, atmosphere of progress and wonder, highly detailed, cinematic, ultra-realistic, concept art style."
- "high-quality pixel art, retro video game environment, 2D sprite-based graphics, pixelated edges, limited color palette, flat colors, tile-based level design, simple geometric shapes, crisp pixels, 16-bit aesthetic"
- "Ultra-realistic natural landscape from aerial view, highly detailed textures, mountains, fields, lakes, forests, historic buildings. Natural colors, cinematic lighting, realistic shadows, photorealistic, wide perspective."

"""