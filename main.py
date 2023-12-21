import os
from PIL import Image, ExifTags


def extract_exif_data(image_path):
    with Image.open(image_path) as img:
        exif_data = img.getexif()
        exif_ifd = exif_data.get_ifd(ExifTags.IFD.Exif)
        if exif_data is not None:
            # Extracting specific fields
            camera = exif_data.get(272)  # Tag for Camera
            lens_type = exif_ifd.get(42036)  # Tag for LensMake
            aperture = exif_ifd.get(33437)  # Tag for FNumber
            iso = exif_ifd.get(34855)  # Tag for ISOSpeedRatings
            focal_length = exif_ifd.get(37386)  # Tag for FocalLength
            datetime_original = exif_ifd.get(36867)  # Tag for DateTimeOriginal
            return camera, lens_type, aperture, iso, focal_length, datetime_original
        else:
            return None, None, None, None, None


def read_images_from_folder(path):
    for file_name in os.listdir(path):
        if file_name.lower().endswith('.jpg'):
            image_path = os.path.join(path, file_name)
            camera, lens_type, aperture, iso, focal_length, datetime_original = extract_exif_data(image_path)
            print(f"Image: {file_name}")
            print(f"  Camera: {camera}")
            print(f"  Lens Type: {lens_type}")
            print(f"  Aperture: {aperture}")
            print(f"  ISO: {iso}")
            print(f"  Focal Length: {focal_length}")
            print(f"  Date Time Original: {datetime_original}")
            print("----------")


folder_path = '/Users/flori/Sites/flori-dev/src/content/grid'
read_images_from_folder(folder_path)
