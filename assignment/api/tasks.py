import os
from image_generator import ImageGenerator, LocalImageGenerator
from dotenv import load_dotenv
import requests

load_dotenv(override=True)
STORAGE_DIR = os.environ.get("IMAGE_STORAGE_DIR", "./images")
API_KEY = os.getenv("STABILITY_KEY")
STABILITY_URL = os.getenv("STABILITY_URL")
STABLE_DIFFUSION_URL = os.getenv("STABLE_DIFFUSION_URL")

os.makedirs(STORAGE_DIR, exist_ok=True)

def gen_image_task(prompt: str, image_id: str, negative_prompt: str = "") -> str:
    image_gen = ImageGenerator(API_KEY, STABILITY_URL)

    print(f"Task started for {image_id}")
    img_bytes = image_gen.generate_image(prompt, negative_prompt=negative_prompt if negative_prompt else ImageGenerator.negative_prompt)
    file_path = os.path.join(STORAGE_DIR, f"{image_id}.png")
    with open(file_path, "wb") as f:
        f.write(img_bytes)
    print(f"Task finished for {image_id}")
    return file_path

def gen_local_image_task(prompt: str, image_id: str, model: str, steps: int, cfg_scale: float, width: int, height: int, sampler_name: str, n_iter: int, negative_prompt: str = "") -> str:
    local_image_gen = LocalImageGenerator(STABLE_DIFFUSION_URL, model, steps, cfg_scale, width, height, sampler_name, n_iter)
    print(f"Task started for {image_id} with model {model}")
    img_bytes = local_image_gen.generate_image(prompt, negative_prompt=negative_prompt if negative_prompt else LocalImageGenerator.negative_prompt)
    file_path = os.path.join(STORAGE_DIR, f"{image_id}.png")
    with open(file_path, "wb") as f:
        f.write(img_bytes)
    print(f"Task finished for {image_id}")
    return file_path
