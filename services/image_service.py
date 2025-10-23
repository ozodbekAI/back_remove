import requests
import io
import base64
from PIL import Image, ImageDraw, ImageFont
from config import settings
from utils.logger import logger


class ImageService:
    @staticmethod
    def _ensure_bytes(image_data):
        if isinstance(image_data, bytes):
            return image_data
        elif isinstance(image_data, io.BytesIO):
            return image_data.getvalue()
        else:
            raise TypeError(f"Expected bytes, got {type(image_data)}")

    @staticmethod
    def remove_background(image_bytes: bytes) -> bytes:
        image_bytes = ImageService._ensure_bytes(image_bytes)

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openrouter_token}",
            "Content-Type": "application/json"
        }

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            payload = {
                "model": "google/gemini-2.5-flash-preview-image",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Delete background"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_str}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 0,
                "modalities": ["image", "text"] 
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            message = data.get("choices", [{}])[0].get("message", {})
            
            if message.get("images"):
                image_obj = message["images"][0]
                if image_obj.get("type") == "image_url":
                    image_url = image_obj["image_url"]["url"]
                    
                    if image_url.startswith("data:image/png;base64,"):
                        base64_data = image_url.split(",")[1]
                        result = base64.b64decode(base64_data)
                        return result
                    else:
                        raise ValueError("Invalid image URL format - expected data:image/png;base64,")
                else:
                    raise ValueError("Invalid image object type")
            else:
                content = message.get("content", "")
                if isinstance(content, str):
                    content = content.strip()
                    if content.startswith("data:image/"):
                        if ";base64," in content:
                            base64_data = content.split(";base64,")[1]
                            result = base64.b64decode(base64_data)
                            return result
                    elif content.startswith("http"):
                        img_response = requests.get(content, timeout=30)
                        img_response.raise_for_status()
                        return img_response.content
                    else:
                        try:
                            result = base64.b64decode(content)
                            return result
                        except:
                            pass
                
                raise ValueError("No image found in response - check model compatibility or prompt")

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except Exception as e:
            raise Exception(f"Failed to remove background: {e}")

    @staticmethod
    def add_watermarks(image_bytes: bytes) -> bytes:
        image_bytes = ImageService._ensure_bytes(image_bytes)
        logger.debug(f"add_watermarks: Input bytes size: {len(image_bytes)}")

        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        width, height = image.size
        logger.debug(f"Image size: {width}x{height}")

        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        font_size = max(13, min(29, min(width, height) // 45))
        logger.debug(f"Font size: {font_size}pt")

        font = None
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Regular
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\arial.ttf",
            "arial.ttf"
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                logger.debug(f"Loaded font: {font_path}")
                break
            except (OSError, IOError):
                continue
        
        if font is None:
            logger.warning("No TrueType font found, using default")
            try:
                font = ImageFont.load_default(size=font_size)
            except:
                font = ImageFont.load_default()

        text = "Обработка фото"

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        logger.debug(f"Text dimensions: {text_width}x{text_height}")


        horizontal_spacing = text_width * 1.2
        vertical_spacing = text_height * 1.5
        
        num_cols = int(width / horizontal_spacing) + 2
        num_rows = int(height / vertical_spacing) + 2
        
        positions = []
        
        total_grid_width = (num_cols - 1) * horizontal_spacing
        total_grid_height = (num_rows - 1) * vertical_spacing
        start_x = (width - total_grid_width) / 2
        start_y = (height - total_grid_height) / 2
        
        for row in range(num_rows):
            for col in range(num_cols):
                x = start_x + col * horizontal_spacing
                y = start_y + row * vertical_spacing
                positions.append((x, y))

        # stroke_width = max(1, font_size // 50)
        
        for x, y in positions:
            x, y = int(x), int(y)
            draw.text((x, y), text, font=font, fill=(0, 0, 0, 200),
                    stroke_width=0) 

        watermarked = Image.alpha_composite(image, overlay)
        
        buffered = io.BytesIO()
        watermarked.save(buffered, format="PNG")
        result = buffered.getvalue()
        
        logger.debug(f"add_watermarks: Added {len(positions)} grid watermarks ({num_rows} rows × {num_cols} cols). Output PNG size: {len(result)}")
        logger.info("Watermarks successfully added to image")
        
        return result