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
    """Call the backend and return (image, time_str) or (None, error_str)."""
    resp = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    img = Image.open(io.BytesIO(base64.b64decode(data["image"])))
    elapsed = data.get("generation_time_seconds")
    time_str = f"**{elapsed:.2f}s**" if elapsed is not None else "**—**"
    return img, time_str
