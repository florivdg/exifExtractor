import base64
import json
import os

from PIL import Image, ExifTags
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # take environment variables from .env.

# Instantiate an OpenAI API client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def extract_exif_data(image_path):
    with Image.open(image_path) as img:
        exif_data = img.getexif()
        exif_ifd = exif_data.get_ifd(ExifTags.IFD.Exif)
        if exif_data is not None:
            # Extracting specific fields
            camera = str(exif_data.get(272))  # Tag for Camera
            lens_type = str(exif_ifd.get(42036))  # Tag for LensMake
            aperture = str(exif_ifd.get(33437))  # Tag for FNumber
            iso = str(exif_ifd.get(34855))  # Tag for ISOSpeedRatings
            focal_length = str(exif_ifd.get(37386))  # Tag for FocalLength
            datetime_original = str(exif_ifd.get(36867))  # Tag for DateTimeOriginal
            return camera, lens_type, aperture, iso, focal_length, datetime_original
        else:
            return None, None, None, None, None


def compose_exif_json(camera: str,
                      lens_type: str,
                      aperture: str,
                      iso: str,
                      focal_length: str) -> dict[str, str]:
    exif = {
        'camera': camera,
        'lens': lens_type,
        'aperture': aperture,
        'iso': iso,
        'focal_length': focal_length
    }

    return exif


def compose_image_json(image_path: str, exif: dict[str, str], datetime_original: str, description: str):
    # Get filename
    filename = os.path.basename(image_path)

    # Get ID based on filename
    image_id = filename.split('.')[0]

    # Convert date from YYYY:MM:DD HH:MM:SS to YYYY-MM-DD
    datetime_original = datetime_original.replace(':', '-')
    taken_on = datetime_original.split(' ')[0]

    image = {
        'id': image_id,
        'title': '',
        'image': './{f}'.format(f=filename),
        'alt': description,
        'date': taken_on,
        'tags': [],
        'exif': exif
    }

    return image


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def generate_image_caption(image_path: str) -> str:
    # Encode image
    base64_image = encode_image(image_path)

    # Create payload
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Create a good and detailed description of this image that would also work as an alt "
                            "text for this image."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]

    # Create chat completion
    chat_completion = client.chat.completions.create(model='gpt-4-vision-preview', messages=messages, max_tokens=1024)

    # Get description from chat completion
    description = chat_completion.choices[0].message.content

    return description


def write_json_to_file(json_data: dict[str, str], file_path: str):
    json_str = json.dumps(json_data)
    with open(file_path, 'w') as json_file:
        json_file.write(json_str)


def read_images_from_folder(path):
    for file_name in os.listdir(path):
        if file_name.lower().endswith('.jpg'):
            # Check for existing JSON file, and skip if it exists
            json_file_path = os.path.join(path, file_name.split('.')[0] + '-test.json')
            if os.path.exists(json_file_path):
                continue

            image_path = os.path.join(path, file_name)
            camera, lens_type, aperture, iso, focal_length, datetime_original = extract_exif_data(image_path)
            exif = compose_exif_json(camera, lens_type, aperture, iso, focal_length)
            description = generate_image_caption(image_path)
            image_data = compose_image_json(image_path, exif, datetime_original, description)

            print(image_data)

            # Write image data to JSON file
            json_file_path = os.path.join(path, file_name.split('.')[0] + '-test.json')
            write_json_to_file(image_data, json_file_path)


folder_path = '/Users/flori/Sites/flori-dev/src/content/grid'
read_images_from_folder(folder_path)
