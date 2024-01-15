import json
import os
from PIL import Image, ExifTags


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


def compose_image_json(image_path: str, exif: dict[str, str], datetime_original: str):
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
        'alt': '',
        'date': taken_on,
        'tags': [],
        'exif': exif
    }

    return image


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
            image_data = compose_image_json(image_path, exif, datetime_original)

            print(image_data)

            # Write image data to JSON file
            json_file_path = os.path.join(path, file_name.split('.')[0] + '-test.json')
            write_json_to_file(image_data, json_file_path)


folder_path = '/Users/flori/Sites/flori-dev/src/content/grid'
read_images_from_folder(folder_path)
