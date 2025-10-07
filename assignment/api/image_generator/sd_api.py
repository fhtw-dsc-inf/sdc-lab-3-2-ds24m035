import requests
import base64
import warnings
from typing import Optional
import logging

logger = logging.getLogger('uvicorn.error')

class StableDiffusionApiGenerator:
    """
    Local Stable Diffusion generator using the web API exposed by a local container,
    e.g. AUTOMATIC1111's web UI at http://stable-diffusion:7860.
    """

    def __init__(self, host: str, steps: int, cfg_scale: float, width: int, height: int, sampler_name: str, n_iter: int):
        self.host = host.rstrip("/")
        self.steps = steps
        self.cfg_scale = cfg_scale
        self.width = width
        self.height = height
        self.sampler_name = sampler_name
        self.n_iter = n_iter

    def __stability_request(self, prompt: str, negative_prompt: Optional[str] = ""):
        """
        Send a POST to the local container's txt2img endpoint.
        """
        url = f"{self.host.strip()}/sdapi/v1/txt2img"

        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": self.steps,
            "cfg_scale": self.cfg_scale,
            "width": self.width,
            "height": self.height,
            "sampler_name": self.sampler_name,
            "n_iter": self.n_iter,
        }

        logger.error(f"Sending request to {url} with payload: {payload}")

        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

    def generate_image(self, prompt: str, negative_prompt: str = "") -> bytes:
        """
        Generate an image and return raw PNG bytes.
        """
        data = self.__stability_request(prompt, negative_prompt)

        if "images" not in data:
            warnings.warn("Local Stable Diffusion returned no images")
            return b""

        # Local SD returns base64-encoded images
        img_b64 = data["images"][0]
        return base64.b64decode(img_b64)
