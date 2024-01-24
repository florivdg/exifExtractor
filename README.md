# exifExtractor

## Description
This project is a Python script that extracts metadata from images and generates captions using OpenAI's GPT-4 Vision API. It reads images from a specified folder, extracts EXIF data, generates a detailed description, title suggestions, and tags for each image, and writes this information to a JSON file.

## Getting Started

### Dependencies
* Python 3.12 or higher
* `PIL` (Pillow) for handling images and EXIF data extraction
* `openai` for interacting with the OpenAI API
* `dotenv` for loading environment variables

### Installing
1. Clone the repository to your local machine.
2. Install the required dependencies using pip:
```python
pip install pillow openai python-dotenv
```
3. Create a `.env` file in the root directory of the project and add your OpenAI API key:
```env
OPENAI_API_KEY=your_api_key_here
```

### Executing Program

1. Run the `main.py` script from the command line:
```bash
python main.py
```

2. When prompted, enter the path to the folder containing the images:
```bash
Enter folder path: /path/to/your/images
```

3. The script will process each image in the folder, extracting EXIF data and generating a description, title suggestions, and tags using the OpenAI API. This information will be written to a JSON file in the same folder, with the same name as the image file.

## Functionality
The main functionalities of the script are:
* `extract_exif_data(image_path)`: Extracts EXIF data from an image.
* `compose_exif_json(...)`: Composes a JSON object with the extracted EXIF data.
* `compose_image_json(...)`: Composes a JSON object with the image metadata and the generated description, title suggestions, and tags.
* `encode_image(image_path)`: Encodes an image to base64 format.
* `generate_image_caption(image_path)`: Generates a description, title suggestions, and tags for an image using the OpenAI API.
* `write_json_to_file(json_data, file_path)`: Writes a JSON object to a file.
* `read_images_from_folder(path)`: Reads images from a folder, processes each image, and writes the results to a JSON file.

## Example Output

```json
{
  "id": "2R9A1905",
  "title": [
    "Voices in Dusk",
    "Stand Against Intolerance",
    "Messages Against Hate",
    "Standing Together in Solidarity",
    "Twilight Rally for Change"
  ],
  "image": "./2R9A1905.jpg",
  "alt": "A diverse group of individuals are gathered in a twilight setting, participating in a protest. The crowd is dense and filled with various expressions of determination and focus. Several homemade signs are held aloft, with one prominently displayed in the center reading 'MY MOM TOLD ME NOT TO TALK TO NAZIS!' Other signs with messages are partially visible around it. The lighting suggests either dawn or dusk, and the urban setting provides a backdrop of buildings with the sky showing a gentle gradient from blue to orange.",
  "location": "Bayreuth, Germany",
  "date": "2024-01-22",
  "tags": ["protest", "crowd", "signs", "twilight", "activism"],
  "exif": {
    "camera": "Canon EOS R6m2",
    "lens": "RF35mm F1.8 MACRO IS STM",
    "aperture": "1.8",
    "iso": "4000",
    "focal_length": "35.0",
    "shutter_speed": "1/50"
  }
}
```