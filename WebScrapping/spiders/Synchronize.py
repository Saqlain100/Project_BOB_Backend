#from reusable_components.download_upload_blob_gcp import download_upload
import scrapy
from datetime import datetime
from google.cloud import storage
import os
import gdown
import datetime
import pysolr

class QuotesSpider(scrapy.Spider):
    name = "Synchronize"
    # Path to your service account key JSON file
    credentials_path = "ContainerSecurity/boutiqueofbrands-a4ba1b0d7277.json"
    solr_username = 'admin'
    solr_password = 'NH4LLLw274ZZ'

    def delete_documents_by_query(self,solr_url, field_name, days_threshold):
        # Calculate the date threshold (7 days ago from today)
        threshold_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_threshold)
        threshold_date_str = threshold_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        # Construct the query
        query = f"{field_name}:[* TO {threshold_date_str}]"
        # Create a connection to the Solr server
        solr = pysolr.Solr(solr_url, auth=(self.solr_username, self.solr_password), always_commit=True, verify=False)
        # Send the delete request to Solr
        solr.delete(q=query)
        # Commit the changes
        solr.commit()
        print("Deletion successful.")

    def delete_old_objects(self,bucket_name, folder_path, days_threshold):
        if (os.path.exists(self.credentials_path) == False):
            gdown.download_folder(
                "https://drive.google.com/drive/folders/14VLco9UxzXP1I9fgVP1-1YkZu8774GmB?usp=sharing",
                quiet=True)
        # Create a client with explicit credentials
        client = storage.Client.from_service_account_json(self.credentials_path)
        bucket = client.get_bucket(bucket_name)
        # Calculate the date threshold (7 days ago from today)
        threshold_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_threshold)
        # Convert the threshold_date to offset-naive by removing the timezone information
        threshold_date = threshold_date.replace(tzinfo=None)
        # List objects in the folder
        blobs = list(bucket.list_blobs(prefix=folder_path))
        print(len(blobs))
        # Filter objects by last modification date
        objects_to_delete = [blob for blob in blobs if blob.updated.replace(tzinfo=None) < threshold_date]
        # Delete the old objects
        for obj in objects_to_delete:
            obj.delete()
            print(f"Deleted object: {obj.name}")

    def start_requests(self):
        self.delete_documents_by_query('http://34.129.190.144/solr/stores/update?commit=true', 'updated_date_dt', 7)
        self.delete_old_objects('bob-bucket', 'Images', 8)



