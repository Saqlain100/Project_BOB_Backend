# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WebscrappingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    store = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    category = scrapy.Field()
    description = scrapy.Field()
    old_price = scrapy.Field()
    old_price_d = scrapy.Field()
    final_price_d = scrapy.Field()
    discount_d = scrapy.Field()
    final_price = scrapy.Field()
    image_links = scrapy.Field()
    highlight = scrapy.Field()
    final_urls=scrapy.Field()
    updated_date_dt=scrapy.Field()
    body = scrapy.Field()

