import scrapy
import logging
import requests
import zipfile
import io
from ..items import WebscrappingItem
from scrapy_splash import SplashRequest


class QuotesSpider(scrapy.Spider):
    counter = 0
    name = "SanaSafinaz"

    def myHash(self, text: str):
        hash = 0
        for ch in text:
            hash = (hash * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
        return hash

    def start_requests(self):
        self.start_date = datetime.now()

        urls_ready = ["https://www.sanasafinaz.com/pk/sale/ready-to-wear.html?p=" + str(i) for i in range(1, 10)]
        urls_unstitched = ["https://www.sanasafinaz.com/pk/sale/unstitched-fabric.html?p=" + str(i) for i in range(1, 10)]
        urls_pant = ["https://www.sanasafinaz.com/pk/sale/accessories.html?p=" + str(i) for i in range(1, 10)]
        urls = [
            'https://www.sanasafinaz.com/pk/sale/ready-to-wear.html?p=1&product_list_limit=60', 'https://www.sanasafinaz.com/pk/sale/ready-to-wear.html?p=6&product_list_limit=60',
            'https://www.sanasafinaz.com/pk/sale/ready-to-wear.html?p=2&product_list_limit=60', 'https://www.sanasafinaz.com/pk/sale/ready-to-wear.html?p=7&product_list_limit=60',
            'https://www.sanasafinaz.com/pk/sale/ready-to-wear.html?p=3&product_list_limit=60', 'https://www.sanasafinaz.com/pk/sale/ready-to-wear.html?p=8&product_list_limit=60',
            'https://www.sanasafinaz.com/pk/sale/ready-to-wear.html?p=4&product_list_limit=60', 'https://www.sanasafinaz.com/pk/sale/ready-to-wear.html?p=9&product_list_limit=60',
            'https://www.sanasafinaz.com/pk/sale/ready-to-wear.html?p=5&product_list_limit=60', 'https://www.sanasafinaz.com/pk/sale/ready-to-wear.html?p=10&product_list_limit=60'
        ]
        for url in urls:
            yield SplashRequest(url=url, callback=self.parse)

    def parse(self, response):
        article_urls = response.xpath("//div[@class='product-item-info']/a/@href").extract()
        for article_url in article_urls:
            article_url = article_url
            yield SplashRequest(article_url, callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        items = WebscrappingItem()
        items["body"] = response.text
        logging.info(items["body"])
        title = response.xpath("//h1[@class='page-title']/span/text()").extract_first()
        category = response.xpath('//div[@class="product attribute overview"]/div[@class="value"]/text()').extract()
        description = response.xpath("//div[@class='product attribute overview']/text()").extract_first()
        old_price = response.xpath(
            "//span[@class='old-price']//span[@class='price']/text()").extract_first()
        if old_price == None:
            old_price = 0
        final_price = response.xpath("//span[@class='special-price']//span[@class='price']/text()").extract_first()
        image_links = response.xpath(
            "//div[@class='mcs-item']/a").extract()
        items["id"] = self.myHash(response.url)
        items["store"] = self.name
        items["url"] = response.url
        items["title"] = title
        items["category"] = category
        items["description"] = description
        items["old_price"] = old_price
        items["old_price_d"] = float(str(old_price).replace("PKR","").replace(",","").strip(" "))
        items["final_price_d"] = float(str(final_price).replace("PKR", "").replace(",","").strip(" "))
        items["final_price"] = final_price
        items["image_links"] = image_links
        yield items
