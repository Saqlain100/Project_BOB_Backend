from google.cloud import storage
import time
import requests
from PIL import Image
import os
from io import BytesIO
import gdown

# Path to your service account key JSON file
credentials_path = "ContainerSecurity/boutiqueofbrands-a4ba1b0d7277.json"

def download_and_resize_image(url, file_path, width, height):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        with Image.open(BytesIO(response.content)) as image:
            # resized_image = image.resize((width, height))
            image.save(file_path)

def download_upload(json_docs):
    width = 500
    height = 500
    directory = 'Stores_Images'
    image_final_urls = []
    if (os.path.exists(credentials_path)==False):
        gdown.download_folder("https://drive.google.com/drive/folders/14VLco9UxzXP1I9fgVP1-1YkZu8774GmB?usp=sharing",
                              quiet=True)
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
