import scrapy
from ..items import WebscrappingItem
import spacy
from ..download_upload_blob_gcp import download_upload
import os
import requests
import json

class QuotesSpider(scrapy.Spider):
    name = "Sapphire"
    def myHash(self, text: str):
        hash = 0
        for ch in text:
            hash = (hash * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
        return hash

    def start_requests(self):
        urls = []
        token_url = "https://pk.sapphireonline.pk/pages/search-results-page?q=sale&page=1"
        res = requests.get(token_url)
        api_token = res.text.split("//searchserverapi.com/widgets/shopify/init.js?a=")[1].split("\"")[0]
        urls.append("https://searchserverapi.com/getresults?q=sale&maxResults=3000&api_key="+api_token)
        current_directory = os.getcwd()
        # Go back two folders
        project_directory = os.path.abspath(os.path.join(current_directory, "..", "..", ".."))
        model_path = "spacy-model-best"
        self.nlp_ner = spacy.load(model_path)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        jsonresponse = json.loads(response.text)
        article_urls = jsonresponse["items"]
        for article_url in article_urls:
            yield scrapy.Request("https://pk.sapphireonline.pk"+article_url['link'], callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        items = WebscrappingItem()
        title = response.xpath('//h1[contains(@class,product_title)]/text()').extract_first()
        category = response.xpath('//h1[@class="product_title entry-title"]/text()').extract()
        description = ','.join(response.xpath('//section[@id="content1"]//p/text()').extract())
        old_price = float(response.xpath('//del//span[@class="money"]/text()').extract_first().replace("Rs.", ""))
        final_price = float(response.xpath('//ins//span[@class="money"]/text()').extract_first().replace("Rs.", ""))
        image_links = response.xpath('//img[contains(@src,"products")]/@src').extract()
        items["id"] = self.myHash(response.url)
        items["store"] = self.name
        items["url"] = response.url
        items["title"] = title
        items["category"] = category
        items["description"] = description.replace(r"\n"," ").strip()
        items["old_price"] = old_price
        items["final_price"] = final_price
        items["image_links"] = image_links
        try:
            items["discount_d"] = round(((items["old_price_d"]-items["final_price_d"])/items["old_price_d"])*100)
        except Exception as e:
            items["discount_d"] = 0
        doc = self.nlp_ner(description)
        labels = []
        entities = []
        labels = [ent.label_ for ent in doc.ents]
        entities = [entity.text for entity in doc.ents]
        items["highlight"] = entities
        items["highlight_labels"] = labels
        arr = []
        arr.append(items)
        try:
            items["final_urls"] = download_upload(arr)
            yield items
        except Exception as e:
            print("Exception occured on calling download & upload function---" + str(e))
