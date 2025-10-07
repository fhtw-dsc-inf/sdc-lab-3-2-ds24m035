import streamlit as st
import requests
import time
from dotenv import load_dotenv
import os

load_dotenv(override=True)

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

st.title("🖼️ Image Generator GUI")

tab1, tab2 = st.tabs(["Stability API (cloud)", "Local Stable Diffusion"])

# --- Stability API tab ---
with tab1:
    st.header("Generate via Stability API")

    prompt = st.text_area("Prompt", "A fantasy landscape, trending on artstation", key="prompt1")
    negative = st.text_area("Negative Prompt", "", key="negative1")

    if st.button("Generate via Stability API"):
        # send to FastAPI
        resp = requests.post(
            f"{FASTAPI_URL}/images",
            json={"prompt": prompt, "negative_prompt": negative}
        )
        resp.raise_for_status()
        data = resp.json()
        image_id = data["image_id"]
        st.write("Job queued. ID:", image_id)

        with st.spinner("Waiting for image..."):
            while True:
                status_resp = requests.get(f"{FASTAPI_URL}/status/{image_id}")
                status_resp.raise_for_status()
                status = status_resp.json()["status"]
                if status == "finished":
                    break
                elif status == "failed":
                    st.error("Image generation failed.")
                    st.stop()
                time.sleep(2)

        # get the image
        try:
            img_resp = requests.get(f"{FASTAPI_URL}/image/{image_id}")
            img_resp.raise_for_status()
            st.image(img_resp.content)
        except requests.RequestException as e:
            st.error(f"Error fetching image: {e}")

# --- Local Stable Diffusion tab ---
with tab2:
    st.header("Generate via Local Stable Diffusion")

    # fetch available models and samplers
    models_resp = requests.get(f"{FASTAPI_URL}/local/models")
    samplers_resp = requests.get(f"{FASTAPI_URL}/local/sampler_names")

    models = models_resp.json().get("models", [])
    samplers = samplers_resp.json().get("samplers", [])

    model_titles = [m["title"] for m in models] if isinstance(models, list) else []
    sampler_names = [s["name"] for s in samplers] if isinstance(samplers, list) else []

    prompt_local = st.text_area("Prompt", "A futuristic cityscape", key="prompt2")
    negative_local = st.text_area("Negative Prompt", "", key="negative2")
    model_selected = st.selectbox("Model", model_titles)
    sampler_selected = st.selectbox("Sampler", sampler_names)
    steps = st.number_input("Steps", min_value=1, max_value=150, value=30)
    cfg_scale = st.number_input("CFG Scale", min_value=1.0, max_value=20.0, value=8.0)
    width = st.number_input("Width", min_value=64, max_value=2048, value=512, step=64)
    height = st.number_input("Height", min_value=64, max_value=2048, value=512, step=64)
    n_iter = st.number_input("Number of images", min_value=1, max_value=4, value=1)

    if st.button("Generate via Local SD"):
        payload = {
            "prompt": prompt_local,
            "negative_prompt": negative_local,
            "model": model_selected,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "sampler_name": sampler_selected,
            "n_iter": n_iter,
        }
        resp = requests.post(f"{FASTAPI_URL}/local/images", json=payload)
        resp.raise_for_status()
        data = resp.json()
        image_id = data["image_id"]
        st.write("Job queued. ID:", image_id)

        with st.spinner("Waiting for image..."):
            while True:
                status_resp = requests.get(f"{FASTAPI_URL}/status/{image_id}")
                status_resp.raise_for_status()
                status = status_resp.json()["status"]
                if status == "finished":
                    break
                elif status == "failed":
                    st.error("Image generation failed.")
                    st.stop()
                time.sleep(2)

        img_resp = requests.get(f"{FASTAPI_URL}/image/{image_id}")
        img_resp.raise_for_status()
        st.image(img_resp.content)
