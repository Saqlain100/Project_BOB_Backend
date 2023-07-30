import scrapy
from ..items import WebscrappingItem
from scrapy_splash import SplashRequest

class QuotesSpider(scrapy.Spider):
    name = "Crossstitch"

    def myHash(self, text: str):
        hash = 0
        for ch in text:
            hash = (hash * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
        return hash

    def start_requests(self):

        urls = [
            'https://crossstitch.pk/collections/sale?page=1', 'https://crossstitch.pk/collections/sale?page=6',
            'https://crossstitch.pk/collections/sale?page=2', 'https://crossstitch.pk/collections/sale?page=7',
            'https://crossstitch.pk/collections/sale?page=3', 'https://crossstitch.pk/collections/sale?page=8',
            'https://crossstitch.pk/collections/sale?page=4', 'https://crossstitch.pk/collections/sale?page=9',
            'https://crossstitch.pk/collections/sale?page=5', 'https://crossstitch.pk/collections/sale?page=10'
        ]
        for url in urls:
            yield SplashRequest(url=url, callback=self.parse)

    def parse(self, response):

        article_urls = response.xpath("//div[@class='spf-product-card__inner']/a/@href").extract()
        for article_url in article_urls:
            yield SplashRequest("https://crossstitch.pk/"+article_url, callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        items = WebscrappingItem()
        title = response.xpath("//h1[@class='product-single__title']/text()").extract_first()
        print(title)
        category = response.xpath('//div[@class="product attribute overview"]/div[@class="value"]/text()').extract()
        description = ','.join(response.xpath("//div[@class='fulldescription']/ul/li/text()").extract())
        old_price = response.xpath(
            "//div[@class='product-single__meta']//s[@class='price-item price-item--regular']//span[contains(@class,'money')]/text()").extract_first()
        if old_price == None:
            old_price = 0
        final_price = response.xpath(
            "//div[@class='product-single__meta']//span[@class='price-item price-item--sale']//span[contains(@class,'money')]/text()").extract_first()
        image_links = response.xpath(
            "//div[contains(@class,'MagicToolboxSelectorsContainer')]/a/@src").extract()
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
        yield items
