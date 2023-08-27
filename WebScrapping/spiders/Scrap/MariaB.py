import scrapy
from ..items import WebscrappingItem
import spacy

class QuotesSpider(scrapy.Spider):
    counter = 0
    name = "MariaB"

    def myHash(self, text: str):
        hash = 0
        for ch in text:
            hash = (hash * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
        return hash

    def start_requests(self):
        self.start_date = datetime.now()

        urls = ["https://www.mariab.pk/collections/all-sale?page=" + str(i) for i in range(1, 20)]
        model_path = r"D:\Work\BoutiqueOfBrands\BOB_Backend\Datasources\WebScrapping\WebScrapping\model-best"
        self.nlp_ner = spacy.load(model_path)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        article_urls = response.xpath('//div[@class="grid-product__content"]/a/@href').extract()
        for article_url in article_urls:
            yield scrapy.Request("https://www.mariab.pk"+article_url, callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        items = WebscrappingItem()
        title = response.xpath('//h1[contains(@class,"product-single__title")]/text()').extract_first()
        category = response.xpath('//div[@class="product attribute overview"]/div[@class="value"]/text()').extract()
        description = ",".join(response.xpath('//div[@class="product-block"]/div[@class="rte"]//text()').extract())
        old_price = response.xpath(
            '//span[@class="product__price product__price--compare"]/text()').extract_first()
        if old_price == None:
            old_price = 0
        final_price = response.xpath(
            '//span[@class="asasas product__price final-price on-sale"]/text()').extract_first()
        image_links = response.xpath(
            '//div[@class="product__thumb-item"]//a/@src').extract()

        items["id"] = self.myHash(response.url)
        items["store"] = self.name
        items["url"] = response.url
        items["title"] = title
        items["category"] = category
        items["description"] = description
        items["old_price"] = old_price
        items["old_price_d"] = float(str(old_price).replace(",", "").replace("PKR", "").strip())
        items["final_price_d"] = float(str(final_price).replace(",", "").replace("PKR", "").strip())
        items["final_price"] = final_price
        items["image_links"] = image_links
        labels = []
        entities = []
        doc = self.nlp_ner(description)
        labels = [ent.label_ for ent in doc.ents]
        entities = [entity.text for entity in doc.ents]
        items["highlight"] = entities
        items["highlight_labels"] = labels
        yield items
