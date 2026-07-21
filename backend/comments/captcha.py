import base64
import io
import random
import string
import uuid

from django.core.cache import cache
from PIL import Image, ImageDraw, ImageFont


def generate_captcha():
    captcha_id = str(uuid.uuid4())

    characters = string.ascii_letters + string.digits

    captcha_value = "".join(
        random.choices(characters, k=6)
    )

    cache.set(
        f"captcha:{captcha_id}",
        captcha_value,
        timeout=300,
    )

    image = Image.new(
        "RGB",
        (180, 60),
        "white",
    )

    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default(size=22)

    draw.text(
        (20, 20),
        captcha_value,
        font=font,
        fill="black",
    )

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="PNG",
    )

    image_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return {
        "captcha_id": captcha_id,
        "image": f"data:image/png;base64,{image_base64}",
        "captcha_value": captcha_value, #TODO only for testing
    }
