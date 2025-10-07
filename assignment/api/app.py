
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from redis import Redis
from rq import Queue
from rq.job import Job
import os, uuid
from tasks import gen_image_task, gen_local_image_task
import requests
import logging

from models.models import ImageRequest, ImageStatusResponse, LocalImageRequest

load_dotenv(override=True)  # take environment variables
logging.getLogger('uvicorn.error')

STORAGE_DIR = os.environ.get("IMAGE_STORAGE_DIR", "./images")

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_QUEUE_TIMEOUT = int(os.environ.get("REDIS_QUEUE_TIMEOUT", 3600))  # seconds
API_KEY = os.getenv("STABILITY_KEY")
STABILITY_URL = os.getenv("STABILITY_URL")
STABLE_DIFFUSION_URL = os.getenv("STABLE_DIFFUSION_URL")

assert STABILITY_URL is not None, "STABILITY_URL environment variable is not set"
assert API_KEY is not None, "STABILITY_KEY environment variable is not set"

os.makedirs(STORAGE_DIR, exist_ok=True)

redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
q = Queue("images", connection=redis_conn)

app = FastAPI(title="Image Generator Service")

@app.post("/images", response_model=ImageStatusResponse)
async def create_image(req: ImageRequest):
    image_id = str(uuid.uuid4())

    # enqueue job with job_id=image_id so we can poll by ID
    job = q.enqueue(gen_image_task, req.prompt, image_id, job_id=image_id, negative_prompt=req.negative_prompt, job_timeout=REDIS_QUEUE_TIMEOUT)

    return ImageStatusResponse(image_id=image_id, status="queued")

@app.get("/image/{image_id}")
async def get_image(image_id: str):
    file_path = os.path.join(STORAGE_DIR, f"{image_id}.png")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")

    # still generating or failed?
    try:
        job = Job.fetch(image_id, connection=redis_conn)
    except:
        raise HTTPException(status_code=404, detail="Image not found")

    status = job.get_status()  # queued, started, finished, failed
    if status == "failed":
        raise HTTPException(status_code=500, detail="Image generation failed")

    return {"image_id": image_id, "status": status}

@app.get("/status/{image_id}", response_model=ImageStatusResponse)
async def get_status(image_id: str):
    """
    Dedicated endpoint for job status polling.
    """
    file_path = os.path.join(STORAGE_DIR, f"{image_id}.png")
    if os.path.exists(file_path):
        return ImageStatusResponse(image_id=image_id, status="finished")

    try:
        job = Job.fetch(image_id, connection=redis_conn)
        status = job.get_status()  # queued | started | finished | failed
    except:
        raise HTTPException(status_code=404, detail="Image not found")

    return ImageStatusResponse(image_id=image_id, status=status)

@app.get("/local/models")
async def list_models():
    """
    List available Stable Diffusion models from the SD container.
    """
    try:
        resp = requests.get(f"{STABLE_DIFFUSION_URL}/sdapi/v1/sd-models")
        resp.raise_for_status()
        models = resp.json()  # [{'title': 'model_name', 'model_name': '…', ...}, ...]
        return {"models": models}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error contacting Stable Diffusion API: {e}")

@app.post("/local/images")
async def create_image(req: LocalImageRequest):
    image_id = str(uuid.uuid4())

    # enqueue job with job_id=image_id so we can poll by ID
    job = q.enqueue(gen_local_image_task, req.prompt, image_id, req.model, req.steps, req.cfg_scale, req.width, req.height, req.sampler_name, req.n_iter, job_id=image_id,
                    negative_prompt=req.negative_prompt,
                    job_timeout=REDIS_QUEUE_TIMEOUT)  # longer timeout for local SD

    return ImageStatusResponse(image_id=image_id, status="queued")

@app.get("/local/sampler_names")
async def get_sampler_names():
    """
    Get available sampler names from the SD container.
    """
    try:
        resp = requests.get(f"{STABLE_DIFFUSION_URL}/sdapi/v1/samplers")
        resp.raise_for_status()
        samplers = resp.json()
        return {"samplers": samplers}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error contacting Stable Diffusion API: {e}")
