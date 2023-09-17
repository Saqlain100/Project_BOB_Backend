import scrapy
import requests
import zipfile
import io
from ..items import WebscrappingItem
import spacy
from ..download_upload_blob_gcp import download_upload
import os
import gdown
from datetime import datetime,timedelta
from bs4 import BeautifulSoup
class QuotesSpider(scrapy.Spider):
    counter = 0
    name = "Ethnic"

    def myHash(self, text: str):
        hash = 0
        for ch in text:
            hash = (hash * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
        return hash

    def start_requests(self):
        self.start_date = datetime.now()

        urls = ["https://ethnic.pk/collections/sale?page="+str(i) for i in range(1,200)]
        current_directory = os.getcwd()
        # Go back two folders
        project_directory = os.path.abspath(os.path.join(current_directory, "..", "..", ".."))
        model_path = "spacy-model-best"
        if (os.path.exists(model_path) == False):
            zip_url = "https://storage.googleapis.com/bob-bucket/spacy-model-best.zip"
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
            else:
                print(f"Failed to download ZIP file. Status code: {response.status_code}")
        self.nlp_ner = spacy.load(model_path)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        article_urls = response.xpath('//a[@class="product-grid-image"]/@href').extract()
        for article_url in article_urls:
            article_url = "https://ethnic.pk" + article_url
            yield scrapy.Request(article_url, callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        items = WebscrappingItem()
        title = response.xpath('//p[@class="head"]/span/text()').extract_first()
        category = response.xpath('//div[@class="product attribute overview"]/div[@class="value"]/text()').extract()
        description = response.xpath('//div[@class="new-product-grid-col1-container"]').extract_first().split("<br>")[1]
        old_price = response.xpath(
            '(//div[@class="prices"]//span[@class="money"]/text())[1]').extract_first()
        if old_price == None:
            old_price = 0
        final_price = response.xpath('(//div[@class="prices"]//span[@class="money"]/text())[2]').extract_first()
        image_links = response.xpath(
            '//div[contains(@class,"pro-imgs2-wrap")]/img[contains(@src,"products")]/@src').extract()
        items["id"] = self.myHash(response.url)
        items["store"] = self.name
        items["url"] = response.url
        items["title"] = title
        items["category"] = category
        items["description"] = description.replace(r"\n"," ").strip()
        items["old_price"] = old_price
        items["old_price_d"] = float(str(old_price).replace("PKR","").replace(",","").strip(" "))
        items["final_price_d"] = float(str(final_price).replace("PKR", "").replace(",","").strip(" "))
        items["final_price"] = final_price
        items["image_links"] = image_links
        soup = BeautifulSoup(response.text, "html.parser")
        items["body"] = soup.get_text()
        try:
            items["discount_d"] = round(((items["old_price_d"]-items["final_price_d"])/items["old_price_d"])*100)
            items["save_d"] = round(items["old_price_d"] - items["final_price_d"])
        except Exception as e:
            items["discount_d"] = 0
        labels = []
        entities = []
        doc = self.nlp_ner(description)
        labels = [ent.label_ for ent in doc.ents]
        entities = [entity.text for entity in doc.ents]
        items["highlight"] = list(set(entities))
        self.counter += 1
        current_date = self.start_date - timedelta(seconds=self.counter)
        # Format the date according to the Solr date format
        solr_date_format = "%Y-%m-%dT%H:%M:%SZ"
        solr_formatted_date = current_date.strftime(solr_date_format)
        items["updated_date_dt"] = solr_formatted_date
        arr = []
        arr.append(items)
        try:
            items["final_urls"] = download_upload(arr)
            yield items
        except Exception as e:
            print("Exception occured on calling download & upload function---" + str(e))

