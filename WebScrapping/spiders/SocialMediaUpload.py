#from reusable_components.download_upload_blob_gcp import download_upload
import scrapy
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
        solr = pysolr.Solr('http://34.129.190.144/solr/stores',auth=(self.solr_username, self.solr_password))
        # Step 1: Fetch all document IDs
        query_all_ids = 'discount_d:[1 TO 90]'
        response = solr.search(query_all_ids, rows=50000)  # Adjust rows as needed
        all_document_ids = [doc['id'] for doc in response]
        # Step 2: Randomly select document IDs
        num_random_documents = 30  # Choose the number of random documents you want
        random_document_ids = random.sample(all_document_ids, num_random_documents)

        # Step 3: Fetch documents using chosen IDs
        query_random_documents = f'id:({" OR ".join(random_document_ids)})'
        random_documents = solr.search(query_random_documents)
        for result in random_documents:
            time.sleep(2)
            self.publish_image_insta(result['final_urls_ss'][0],"\nStore:"+result["store_s"]+"\nTitle:"+result["title_s"]+"\nLink:"+result["url_s"]+"\nPrice: Rs "+str(result["new_price_d"])+"\nDiscount:"+str(result["discount_d"])+"%")
            time.sleep(2)
            self.publish_image_fb(result['final_urls_ss'][0],"\nStore:"+result["store_s"]+"\nTitle:"+result["title_s"]+"\nLink:"+result["url_s"]+"\n Price: Rs "+str(result["new_price_d"])+"\nDiscount:"+str(result["discount_d"])+"%")




