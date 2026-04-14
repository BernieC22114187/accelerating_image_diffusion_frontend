from PIL import Image
import requests
import base64
import io

BACKEND_URL = "http://localhost:8000"   # change to your backend address


def _pil_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _to_pil(img) -> Image.Image:
    """Accept PIL Image or numpy array."""
    if isinstance(img, Image.Image):
        return img
    return Image.fromarray(img)


def _call_backend(payload: dict):
    """Call the backend and return (image, time_str)."""
    resp = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    img = Image.open(io.BytesIO(base64.b64decode(data["image"])))
    elapsed = data.get("generation_time_seconds")
    time_str = f"**{elapsed:.2f}s**" if elapsed is not None else "**—**"
    return img, time_str


def _call_backend_both(payload: dict):
    """Run accelerated then normal in one backend call.

    Returns (accel_img, accel_time_str, normal_img, normal_time_str).
    """
    resp = requests.post(f"{BACKEND_URL}/generate", json={**payload, "both": True}, timeout=300)
    resp.raise_for_status()
    data = resp.json()
    accel_img   = Image.open(io.BytesIO(base64.b64decode(data["accelerated_image"])))
    normal_img  = Image.open(io.BytesIO(base64.b64decode(data["normal_image"])))
    accel_str   = f"**{data['accelerated_time']:.2f}s**"
    normal_str  = f"**{data['normal_time']:.2f}s**"
    return accel_img, accel_str, normal_img, normal_str
