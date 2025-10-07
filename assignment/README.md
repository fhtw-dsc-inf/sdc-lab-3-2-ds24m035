## Project Overview - FastAPI | Streamlit | Redis | Docker | Stablediffusion

This project provides an **asynchronous image generation service** with a web frontend. Users can generate images using either a **local Stable Diffusion container** or the **Stability AI API**.

It is built with:

* **FastAPI** – Backend API handling image generation requests, queueing, and status tracking.
* **RQ + Redis** – Queue system for asynchronous image generation jobs.
* **Streamlit** – GUI frontend to interact with both local and remote image generation endpoints.
* **Stable Diffusion WebUI (optional)** – Local image generation engine running in Docker.

### How it works

1. **Submitting a request:**

   * The frontend or API POSTs a prompt to FastAPI.
   * FastAPI creates a unique `image_id` and enqueues the job in Redis.

2. **Processing the job:**

   * A background RQ worker listens to the queue.
   * The worker generates the image either via:

     * Local Stable Diffusion container (`/local/images` endpoint), or
     * Stability API (`/images` endpoint).

3. **Retrieving results:**

   * Users can poll the job status (`/status/{image_id}`).
   * When finished, the image can be downloaded via `/image/{image_id}`.

4. **Local SD model management:**

   * `/local/models` – lists available local SD models.
   * `/local/sampler_names` – lists available samplers for local generation.

### Docker Compose Services

* **Redis:** Message broker and job queue backend.
* **FastAPI:** Handles job creation, status tracking, and image storage.
* **Frontend (Streamlit):** User interface to submit prompts and view results.
* **Download Service (optional):** Prepares models for local SD.
* **Stable Diffusion WebUI (optional):** Local SD container for generating images.

**All-in-one image:** Both FastAPI and Streamlit share the same Docker image to simplify dependencies.

---

### Usage

1. **Start services**

```bash
docker compose up -d redis fastapi frontend
# optionally add local SD:
docker compose --profile stablediffusion up -d
```

2. **Open GUI:**
   Visit [http://localhost:8501](http://localhost:8501) to use the Streamlit frontend.

3. **Submit image generation requests:**

* **Remote (Stability API):** Enter a prompt in the “Stability AI” section.
* **Local SD:** Select a model and sampler, then submit a prompt in the “Local SD” section.

4. **Check job status:**

* Poll via GUI or FastAPI endpoint:

```http
GET /status/{image_id}
```

5. **Download finished images:**

```http
GET /image/{image_id}
```

6. **List available local models and samplers:**

```http
GET /local/models
GET /local/sampler_names
```
