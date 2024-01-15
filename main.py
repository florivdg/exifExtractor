import base64
import json
import os

from PIL import Image, ExifTags
from dotenv import load_dotenv
import openai
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
            exposure_time = exif_ifd.get(33434)  # Tag for ExposureTime
            shutter_speed = f"1/{str(1 / exposure_time)}"
            datetime_original = str(exif_ifd.get(36867))  # Tag for DateTimeOriginal
            return camera, lens_type, aperture, iso, focal_length, shutter_speed, datetime_original
        else:
            return None, None, None, None, None, None


def compose_exif_json(camera: str,
                      lens_type: str,
                      aperture: str,
                      iso: str,
                      focal_length: str,
                      shutter_speed: str) -> dict[str, str]:
    exif = {
        'camera': camera,
        'lens': lens_type,
        'aperture': aperture,
        'iso': iso,
        'focal_length': focal_length,
        'shutter_speed': shutter_speed
    }

    return exif


def compose_image_json(image_path: str, exif: dict[str, str], datetime_original: str, description: dict[str, str]):
    # Get filename
    filename = os.path.basename(image_path)

    # Get ID based on filename
    image_id = filename.split('.')[0]

    # Convert date from YYYY:MM:DD HH:MM:SS to YYYY-MM-DD
    datetime_original = datetime_original.replace(':', '-')
    taken_on = datetime_original.split(' ')[0]

    image = {
        'id': image_id,
        'title': description['title_ideas'],
        'image': './{f}'.format(f=filename),
        'alt': description['description'],
        'location': '',
        'date': taken_on,
        'tags': description['tags'],
        'exif': exif
    }

    return image


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def generate_image_caption(image_path: str) -> dict[str, str] or None:
    # Log message to console
    print(f'Using GPT-4 Vision API for describing {image_path} ...')

    # Encode image
    base64_image = encode_image(image_path)

    prompt = ("Create an accurate and detailed description of this image that would also work as an alt text. Also "
              "come up with 5 title suggestions for this image. At last suggest 5 tags that suit the image "
              "description. These tags should be single words only. Identify the main subject or theme and make sure "
              "to put the according tag first. Return the description, the title suggestions and "
              "tags as JSON without any extra notes or information. Return a JSON string that can be parsed. Do not "
              "use markdown code blocks. Use the following JSON format: \n\n\"\"\"{\"title_ideas\": [\"\", \"\", "
              "\"\", \"\", \"\"],\"description\": \"\",\"tags\": [\"\", \"\", \"\", \"\", \"\"]}\"\"\"")

    # Create payload
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
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

    try:
        # Create chat completion
        chat_completion = client.chat.completions.create(model='gpt-4-vision-preview',
                                                         messages=messages,
                                                         max_tokens=2048)
        # Get description results from chat completion
        description = chat_completion.choices[0].message.content

        # Parse into object
        json_description = json.loads(description)

        return json_description

    except openai.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
    except openai.RateLimitError:
        print("A 429 status code was received; we should back off a bit.")
    except openai.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)

    return None


def write_json_to_file(json_data: dict[str, str], file_path: str):
    json_str = json.dumps(json_data)
    with open(file_path, 'w') as json_file:
        json_file.write(json_str)


def read_images_from_folder(path):
    for file_name in os.listdir(path):
        if file_name.lower().endswith('.jpg'):
            # Check for existing JSON file, and skip if it exists
            json_file_path = os.path.join(path, file_name.split('.')[0] + '.json')
            image_path = os.path.join(path, file_name)
            camera, lens_type, aperture, iso, focal_length, shutter_speed, datetime_original = extract_exif_data(image_path)
            exif = compose_exif_json(camera, lens_type, aperture, iso, focal_length, shutter_speed)

            print(exif)

            if os.path.exists(json_file_path):
                print(f'JSON file for {file_name} already exists. Skipping ...')
                continue

            description = generate_image_caption(image_path)
            if description is None:
                print(f'No description for {file_name} could be generated. Skipping ...')
                continue

            image_data = compose_image_json(image_path, exif, datetime_original, description)

            # Write image data to JSON file
            json_file_path = os.path.join(path, file_name.split('.')[0] + '-test.json')
            write_json_to_file(image_data, json_file_path)


folder_path = '/Users/flori/Sites/flori-dev/src/content/grid'
read_images_from_folder(folder_path)
