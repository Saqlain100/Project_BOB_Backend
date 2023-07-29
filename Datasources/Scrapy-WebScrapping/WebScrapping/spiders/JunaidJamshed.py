import scrapy
from ..items import WebscrappingItem
import spacy
from ..download_upload_blob_gcp import download_upload
import os

class QuotesSpider(scrapy.Spider):
    name = "JunaidJamshed"

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
        self.nlp_ner = spacy.load(model_path)
        urls_men = ["https://www.junaidjamshed.com/mens/kameez-shalwar.html?p=" + str(i) for i in range(1, 100)]
        urls_untitched = ["https://www.junaidjamshed.com/womens/un-stitched.html?p=" + str(i) for i in range(1, 100)]
        urls = urls_untitched+urls_men
        for url in urls:
            item = ""
            yield scrapy.Request(url=url, callback=self.parse, meta={'item': item})

    def parse(self, response):
        item = response.meta['item']
        article_urls = response.xpath('//div[@class="product_image"]/a/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request(article_url, callback=self.parse_dir_contents,meta={'item': item})

    def parse_dir_contents(self, response):
        items = WebscrappingItem()
        title = response.xpath("//h1[@class='page-title']/span/text()").extract_first()
        description = ','.join(response.xpath("//td[@class='col data']/text()").extract()[0:5])
        old_price = response.xpath(
            "(//span[@class='pric'])[2]/text()").extract_first()
        if old_price == None:
            old_price = '0'
        final_price = response.xpath(
            "(//span[@class='price'])[1]/text()").extract_first()
        image_links = response.xpath("//div[@class='MagicToolboxSelectorsContainer']//a/@href").extract()
        items["id"] = self.myHash(response.url)
        items["store"] = self.name
        items["url"] = response.url
        items["title"] = title.replace(r"\n"," ").strip()
        items["category"] = ""
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
        items["highlight"] = [response.meta['item']] + description.split(",")
        items["highlight_labels"] = ["hard coded"]
        arr = []
        arr.append(items)
        try:
            items["final_urls"] = download_upload(arr)
            yield items
        except Exception as e:
            print("Exception occured on calling download & upload function---" + str(e))
