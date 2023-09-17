#from reusable_components.download_upload_blob_gcp import download_upload
import logging

import scrapy
import requests
import zipfile
import io
import pysolr
import json
import requests
import facebook
import time
import random
class QuotesSpider(scrapy.Spider):
    name = "SocialMediaUpload"
    solr_username = 'admin'
    solr_password = 'NH4LLLw274ZZ'

    def publish_image_insta(self,image_url,caption):
        access_token = "EAALsyQ98bfIBOZBznC5fmcvMtkH6aBgRbZAAuvKcTs7HVYrXuZCgQ0TttpIYTGZC7OmZBvtlvb2phm9T5Ds5PQZB12nZA0Yln4c6jgVpQZBwo0EZCRliE4gy9weZCWlIyioElru4uigg6PG9qgZALhaVk1mZCiYlAxtO1VNXxJ5ErckIfPZB9xzQO25BJhh7s"
        post_url = "https://graph.facebook.com/v17.0/17841461451978477/media?access_token=bearer " + access_token
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": access_token
        }
        r = requests.post(post_url, data=payload)
        print(r.text)
        results = json.loads(r.text)
        if 'id' in results:
            creation_id = results['id']
            second_url = "https://graph.facebook.com/v17.0/17841461451978477/media_publish?access_token=" + access_token
            secondpayload = {
                "creation_id": creation_id,
                "access_token": access_token
            }
            requests.post(second_url, data=secondpayload)
            print(r.text)


    def publish_image_fb(self,image_url,caption):
        access_token = "EAAJ6EFGBzUkBO9otxBrZBJivK1tLKP8Cx6hEfONeVqfA2c8qxaxVM6aB9Ck2WZCZBKSMR1LzjTMhwopxbYPgCsVqFh46BP9i5WYByCfnP9Jyduo9xTK3xcRkJi2WZBmQGoX9ZCGlz5uZAc32zqYeyJmd7OZAGdlc9aVZByBnQTHtzp0gYjbP3FUZCNESQEKe4KH4ZD"
        id = '110556835472680'
        graph = facebook.GraphAPI(access_token=access_token)
        x = graph.put_object(id, 'photos', message=caption, url=image_url)
        print(x)

    def start_requests(self):
        # Create a connection to your Solr instance
        solr = pysolr.Solr('http://34.129.54.101/solr/stores',auth=(self.solr_username, self.solr_password))
        # Step 1: Fetch all document IDs
        params = {
            'q': 'discount_d:[20 TO 90]',  # The search query
            'rows': 1000,  # Number of rows (results) per page
            'start': 0,  # Starting offset for pagination
            'defType': 'edismax',
            'bq': ' Embroidered ',
        }

        response = solr.search(**params)  # Adjust rows as needed
        ids = []
        for doc in response:
            ids.append(doc['id'])

        # Convert IDs to a filter query string
        rand_lst = random.sample(ids, 50)
        id_filter_query = 'id:' + ' OR id:'.join(rand_lst)
        # Define other parameters if needed
        params = {
            'q': '*:*',  # Match all documents
            'fq': id_filter_query,
            'rows': len(rand_lst),  # Number of rows (results) to return
        }
        response = solr.search(**params)
        logging.info("solr docs:"+str(len(response)))
        for result in response:
            time.sleep(2)
            self.publish_image_insta(result['final_urls_ss'][0],"\nStore:"+result["store_s"]+"\nTitle:"+result["title_s"]+"\nLink:"+result["url_s"]+"\nPrice: Rs "+str(result["new_price_d"])+"\nDiscount:"+str(result["discount_d"])+"%")
            time.sleep(2)
            self.publish_image_fb(result['final_urls_ss'][0],"\nStore:"+result["store_s"]+"\nTitle:"+result["title_s"]+"\nLink:"+result["url_s"]+"\n Price: Rs "+str(result["new_price_d"])+"\nDiscount:"+str(result["discount_d"])+"%")




