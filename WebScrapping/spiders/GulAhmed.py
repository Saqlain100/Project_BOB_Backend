import scrapy
from ..items import WebscrappingItem
import spacy
from ..download_upload_blob_gcp import download_upload
import os
import gdown
from datetime import datetime

class QuotesSpider(scrapy.Spider):
    name = "GulAhmed"

    def myHash(self, text: str):
        hash = 0
        for ch in text:
            hash = (hash * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
        return hash

    def start_requests(self):
        current_directory = os.getcwd()
        # Go back two folders
        project_directory = os.path.abspath(os.path.join(current_directory, "..", "..", ".."))
        model_path = "spacy-model-best"
        if (os.path.exists(model_path) == False):
            gdown.download_folder(
                "https://drive.google.com/drive/folders/12-Z-WPVXvVwmu3g914ciuWDszfsjG0DT?usp=drive_link",
                quiet=True)
        self.nlp_ner = spacy.load(model_path)
        urls_stitched = ["https://www.gulahmedshop.com/sale/unstitched?p=" + str(i) for i in range(1, 100)]
        urls_pret = ["https://www.gulahmedshop.com/sale/ideas-pret?p=" + str(i) for i in range(1, 100)]
        urls_men = ["https://www.gulahmedshop.com/sale/men?p=" + str(i) for i in range(1, 100)]
        urls_home = ["https://www.gulahmedshop.com/sale/home?p=" + str(i) for i in range(1, 100)]
        urls_accessories = ["https://www.gulahmedshop.com/sale/accessories?p=" + str(i) for i in range(1, 100)]
        sale = ["https://www.gulahmedshop.com/sale?p="+str(i) for i in range(1, 200)]
        urls = urls_pret+urls_stitched+urls_men+urls_home+urls_accessories
        for url in urls:
            item = ""
            yield scrapy.Request(url=url, callback=self.parse, meta={'item': item})

    def parse(self, response):
        item = response.meta['item']
        article_urls = response.xpath('//div[@class="product details product-item-details"]/a/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request(article_url, callback=self.parse_dir_contents,meta={'item': item})

    def parse_dir_contents(self, response):
        items = WebscrappingItem()
        title = response.xpath("//h1[@class='page-title']/span/text()").extract_first()
        print(title)
        category = response.xpath('//div[@class="product attribute overview"]/div[@class="value"]/text()').extract()
        description = ','.join(response.xpath("//div[@class='product attribute description']//text()").extract())
        old_price = response.xpath(
            "(//span[@class='price'])[2]/text()").extract_first()
        if old_price == None:
            old_price = 0
        final_price = response.xpath(
            "(//span[@class='price'])[1]/text()").extract_first()
        image_links = response.xpath("//div[@class='MagicToolboxSelectorsContainer']//a/@href").extract()
        items["id"] = self.myHash(response.url)
        items["store"] = self.name
        items["url"] = response.url
        items["title"] = title.replace(r"\n"," ").strip()
        items["category"] = category
        items["description"] = description.replace(r"\n","").strip()
        items["old_price"] = old_price.replace(r"\n"," ").strip()
        items["old_price_d"] = float(str(old_price).replace("PKR","").replace(",","").strip())
        items["final_price_d"] = float(str(final_price).replace("PKR","").replace(",","").strip())
        items["final_price"] = final_price.replace(r"\n"," ").strip()
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
        items["highlight"] = list(set(entities))
        current_date = datetime.now()
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
