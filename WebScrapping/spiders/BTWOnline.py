import scrapy
from ..items import WebscrappingItem
import spacy
from ..download_upload_blob_gcp import download_upload
import os
import gdown
from nltk.corpus import stopwords

class QuotesSpider(scrapy.Spider):
    name = "BTWOnline"

    def myHash(self, text: str):
        hash = 0
        for ch in text:
            hash = (hash * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
        return hash

    def start_requests(self):
        urls = ["https://www.btwonline.com/collections/sale?page=" + str(i) for i in range(1, 200)]
        current_directory = os.getcwd()
        # Go back two folders
        project_directory = os.path.abspath(os.path.join(current_directory, "..", "..", ".."))
        model_path = "spacy-model-best"
        if (os.path.exists(model_path) == False):
            gdown.download_folder(
                "https://drive.google.com/drive/folders/12-Z-WPVXvVwmu3g914ciuWDszfsjG0DT?usp=drive_link",
                quiet=True)
        self.nlp_ner = spacy.load(model_path)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        article_urls = response.xpath("//a[@class='product-link']/@href").extract()
        for article_url in article_urls:
            article_url = "https://www.btwonline.com" + article_url
            yield scrapy.Request(article_url, callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        items = WebscrappingItem()
        title = response.xpath("//h1[@class='title']/text()").extract_first().replace(r"\n","").strip()
        category = response.xpath('//div[@class="product attribute overview"]/div[@class="value"]/text()').extract()
        description = response.xpath("//div[contains(@class,'product-description')]/p/text()").extract_first()
        old_price = response.xpath(
            "//span[@class='was-price theme-money']/text()").extract_first()
        if old_price == None:
            old_price = 0
        final_price = response.xpath("//span[@class='current-price theme-money']/text()").extract_first()
        image_links = response.xpath(
            "//meta[@property='og:image:secure_url']/@content").extract()
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
        try:
            items["discount_d"] = round(((items["old_price_d"]-items["final_price_d"])/items["old_price_d"])*100)
        except Exception as e:
            items["discount_d"] = 0
        labels = []
        entities = []
        doc = self.nlp_ner(description)
        labels = [ent.label_ for ent in doc.ents]
        entities = [entity.text for entity in doc.ents]
        items["highlight"] = list(set([word for word in entities if word not in (stopwords.words('english'))]))
        arr = []
        arr.append(items)
        try:
            items["final_urls"] = download_upload(arr)
            yield items
        except Exception as e:
            print("Exception occured on calling download & upload function---" + str(e))

