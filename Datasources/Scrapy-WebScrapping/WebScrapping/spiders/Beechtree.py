import scrapy
from ..items import WebscrappingItem
import spacy
from ..download_upload_blob_gcp import download_upload
import os

class QuotesSpider(scrapy.Spider):
    name = "Beechtree"

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
        urls_stitched = ["https://beechtree.pk/collections/sale-unstitched/?page=" + str(i) for i in range(1, 200)]
        urls_pret = ["https://beechtree.pk/collections/sale-pret?page=" + str(i) for i in range(1, 200)]
        urls_pant = ["https://beechtree.pk/collections/sale-pants?page=" + str(i) for i in range(1, 200)]
        urls_absolute = ["https://beechtree.pk/collections/sale-absolute?page=" + str(i) for i in range(1, 200)]
        urls_lux = ["https://beechtree.pk/collections/sale-luxury-pret?page=" + str(i) for i in range(1, 200)]
        urls_teens = ["https://beechtree.pk/collections/sale-forever-teens?page=" + str(i) for i in range(1, 200)]
        urls_out = ["https://beechtree.pk/collections/sale-outer-wear?page=" + str(i) for i in range(1, 200)]
        urls_winter = ["https://beechtree.pk/collections/sale-winter?page=" + str(i) for i in range(1, 200)]
        urls_summer = ["https://beechtree.pk/collections/sale-summer?page=" + str(i) for i in range(1, 200)]
        urls_footwear = ["https://beechtree.pk/collections/sale-accessories-footwear?page=" + str(i) for i in range(1, 200)]
        urls_scarves = ["https://beechtree.pk/collections/sale-accessories-scarves22?page=" + str(i) for i in
                         range(1, 200)]
        urls_frag = ["https://beechtree.pk/collections/sale-accessories-scarves22?page=" + str(i) for i in
                        range(1, 200)]
        sale = ["https://beechtree.pk/search?q=sale&page=" + str(i) for i in
                        range(1, 500)]
        urls = urls_frag+urls_scarves+urls_footwear+urls_summer+urls_winter+urls_out+urls_teens+urls_lux+urls_absolute+urls_pant+urls_pret+urls_stitched+sale
        for url in urls:
            item = ""
            yield scrapy.Request(url=url, callback=self.parse, meta={'item': item})

    def parse(self, response):
        item = response.meta['item']
        article_urls = response.xpath("//div[contains(@class,'grid-view-item product-card')]/a/@href").extract()
        for article_url in article_urls:
            yield scrapy.Request("https://beechtree.pk/"+article_url, callback=self.parse_dir_contents,meta={'item': item})

    def parse_dir_contents(self, response):
        items = WebscrappingItem()
        title = response.xpath("//h2[@class='product-single__title']/text()").extract_first()
        print(title)
        category = response.xpath('//div[@class="product attribute overview"]/div[@class="value"]/text()').extract()
        description = ','.join(response.xpath("//div[@class='product-single__description rte']/ul/li/text()").extract())
        if description.strip() == "":
            description = ','.join(response.xpath("//div[@class='product-single__description rte']/p//text()").getall())
        old_price = response.xpath(
            "//div[@class='product-container']//s[@class='price-item price-item--regular']//span[contains(@class,'money')]/text()").extract_first()
        if old_price == None:
            old_price = 0
        final_price = response.xpath(
            "//div[@class='product-container']//span[@class='price-item price-item--sale']//span[contains(@class,'money')]/text()").extract_first()
        image_links = response.xpath(
            "//div[@class='thumbImg']/img/@src").extract()
        items["id"] = self.myHash(response.url)
        items["store"] = self.name
        items["url"] = response.url
        items["title"] = title
        items["category"] = category
        items["description"] = description
        items["old_price"] = old_price
        items["old_price_d"] = float(str(old_price).replace("PKR","").replace(",","").strip())
        items["final_price_d"] = float(str(final_price).replace("PKR","").replace(",","").strip())
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
        items["highlight"] = [response.meta['item']] + entities
        items["highlight_labels"] = ["url_label"] + labels
        arr = []
        arr.append(items)
        try:
            items["final_urls"] = download_upload(arr)
            yield items
        except Exception as e:
            print("Exception occured on calling download & upload function---" + str(e))

