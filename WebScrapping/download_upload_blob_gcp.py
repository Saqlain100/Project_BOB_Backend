from google.cloud import storage
import time
import requests
from PIL import Image
import os
from io import BytesIO
import requests
import zipfile
import io
import gdown

# Path to your service account key JSON file
credentials_path = "boutiqueofbrands.json"

def download_and_resize_image(url, file_path, width, height):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        with Image.open(BytesIO(response.content)) as image:
            # resized_image = image.resize((width, height))
            image.save(file_path)

def download_upload(json_docs):
    width = 400
    height = 370
    directory = 'Stores_Images'
    image_final_urls = []
    if (True):
        zip_url = "https://storage.googleapis.com/bob-bucket/boutiqueofbrands_security.zip"
        extract_dir = ''
        # Send an HTTP GET request to download the ZIP file
        response = requests.get(zip_url)
        if response.status_code == 200:
            # Create a BytesIO object to hold the downloaded data
            zip_data = io.BytesIO(response.content)
            # Extract the ZIP file
            with zipfile.ZipFile(zip_data, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"ZIP file downloaded and extracted to {extract_dir}")
    if not os.path.exists(directory):
        os.makedirs(directory)
    for json in json_docs:
        try:
            count = 0
            folder_path = json["store"]
            if not os.path.exists(directory+"\\" + folder_path):
                os.makedirs(directory+"\\" + folder_path)
            else:
                pass
            for image in json["image_links"]:
                count += 1
                file_name = str(json["id"]) + "_" + str(count) + ".png"
                filepath = directory+"\\" + folder_path + "\\" +file_name
                if json["store"] == "Khaadi":
                    image_url = image.replace("width=53&height=80", "width=500&height=500")
                elif json["store"] == "Bonanza":
                    image_url = image.replace("_120", "_500")
                elif json["store"] == "Beechtree":
                    image_url = image.replace("compact.jpg", "500x500.jpg")
                elif json["store"] == "SanaSafinaz":
                    image_url = image.split(".jpg")[0]+".jpg"
                else:
                    image_url = image
                try:
                    if ("https:" not in image_url and "http:" not in image_url):
                        image_url = "https:" + image_url
                    download_and_resize_image(image_url, filepath, width, height)
                    upload_path = upload(filepath,file_name)
                    image_final_urls.append(upload_path)
                except Exception as e:
                    time.sleep(3)
                    print(image_url, str(e))
        except Exception as e:
            print("Main exception-", str(e))
    return image_final_urls


def upload(filepath,file_name):
    # Create a client with explicit credentials
    client = storage.Client.from_service_account_json(credentials_path)
    bucket_name = 'bob-bucket'
    bucket = client.get_bucket(bucket_name)
    # Local file path of the image to upload
    # Destination folder path within the bucket
    folder_path = 'Images/'
    # Blob name with folder path included
    blob_name = folder_path + file_name
    # Upload the image file to the blob
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(filepath)
    os.remove(filepath)
    url = blob.public_url
    print(f'Public URL for the blob: {url}')
    return url
