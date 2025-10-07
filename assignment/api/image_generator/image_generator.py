from .stability_api import StabilityApiGenerator
from .sd_api import StableDiffusionApiGenerator
import os

class ImageGenerator:
    negative_prompt = ("photo, painting, cartoon, realistic, portrait, face, colored, 3d, naked, realism, real, hair, "
                       "closeup, closeup shot, lowres, text, error, cropped, worst quality, low quality, "
                       "jpeg artifacts,"
                       "ugly, duplicate, morbid, mutilated, out of frame, extra fingers, mutated hands, poorly drawn "
                       "hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, "
                       "bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, "
                       "missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, "
                       "long neck, username, watermark, signature")

    image_prompt_template = "{user_input} comical sketch on paper technical details, highly detailed, high resolution"

    def __init__(self, api_key, host, engine="stable-diffusion-xl-1024-v1-0"):
        self.stability_api = StabilityApiGenerator(api_key, engine=engine, host=host)

    def generate_image(self, text: str, negative_prompt: str = negative_prompt):
        image_prompt = self.image_prompt_template.format(user_input=text)
        return self.stability_api.generate_image(image_prompt, negative_prompt)

class LocalImageGenerator:
    negative_prompt = ("photo, painting, cartoon, realistic, portrait, face, colored, 3d, naked, realism, real, hair, "
                       "closeup, closeup shot, lowres, text, error, cropped, worst quality, low quality, "
                       "jpeg artifacts,"
                       "ugly, duplicate, morbid, mutilated, out of frame, extra fingers, mutated hands, poorly drawn "
                       "hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, "
                       "bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, "
                       "missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, "
                       "long neck, username, watermark, signature")

    image_prompt_template = "{user_input} comical sketch on paper technical details, highly detailed, high resolution"

    def __init__(self, host, model, steps, cfg_scale, width, height, sampler_name, n_iter):
        self.host = host
        self.model = model
        self.steps = steps
        self.cfg_scale = cfg_scale
        self.width = width
        self.height = height
        self.sampler_name = sampler_name
        self.n_iter = n_iter
        self.stability_api = StableDiffusionApiGenerator(host=host, steps=steps, cfg_scale=cfg_scale, width=width, height=height, sampler_name=sampler_name, n_iter=n_iter)

    def generate_image(self, text: str, negative_prompt: str = negative_prompt):
        image_prompt = self.image_prompt_template.format(user_input=text)
        return self.stability_api.generate_image(image_prompt, negative_prompt)
