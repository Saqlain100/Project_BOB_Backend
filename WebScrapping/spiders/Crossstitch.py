import scrapy
from ..items import WebscrappingItem
import spacy
from ..download_upload_blob_gcp import download_upload
import os
import gdown
from datetime import datetime,timedelta
from bs4 import BeautifulSoup

class QuotesSpider(scrapy.Spider):
    counter = 0
    name = "Crossstitch"

    def myHash(self, text: str):
        hash = 0
        for ch in text:
            hash = (hash * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
        return hash

    def start_requests(self):
        self.start_date = datetime.now()
        urls = ["https://crossstitch.pk/collections/sale?page=" + str(i) for i in range(1, 500)]
        current_directory = os.getcwd()
        # Go back two folders
        project_directory = os.path.abspath(os.path.join(current_directory, "..", "..", ".."))
        model_path = "spacy-model-best"
        if (os.path.exists(model_path) == False):
            gdown.download_folder(
                "https://drive.google.com/drive/folders/1TUDGfH2gJYD-gFAKjYGT0d0cqUwmANxA?usp=sharing",
                quiet=True)
        self.nlp_ner = spacy.load(model_path)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        article_urls = response.xpath("//div[@class='grid-view-item product-card']/a/@href").extract()
        for article_url in article_urls:
            article_url = "https://crossstitch.pk" + article_url
            yield scrapy.Request(article_url, callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        items = WebscrappingItem()
        title = response.xpath("//h1[@class='product-single__title']/text()").extract_first().replace(r"\n","").strip()
        category = response.xpath('//div[@class="product attribute overview"]/div[@class="value"]/text()').extract()
        description = ",".join(response.xpath("//div[@class='fulldescription']//text()").extract())
        old_price = response.xpath(
            "//div[@class='product-single__meta']//s[@class='price-item price-item--regular']//span[@class='money']/text()").extract_first()
        if old_price == None:
            old_price = 0
        final_price = response.xpath("//div[@class='product-single__meta']//span[@class='price-item price-item--sale']//span[@class='money']/text()").extract_first()
        image_links = response.xpath(
            "//meta[@property='og:image']/@content").extract()
        items["id"] = self.myHash(response.url)
        items["store"] = self.name
        items["url"] = response.url
        items["title"] = title
        items["category"] = category
        items["description"] = description.replace(r"\n"," ").strip()
        items["old_price"] = old_price
        items["old_price_d"] = float(str(old_price).replace("Rs.","").replace(",","").strip(" "))
        items["final_price_d"] = float(str(final_price).replace("Rs.", "").replace(",","").strip(" "))
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

