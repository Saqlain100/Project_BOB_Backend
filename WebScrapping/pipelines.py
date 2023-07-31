# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pysolr


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class WebscrappingPipeline:

    solr = None
    def __init__(self):
        solr_username = 'admin'
        solr_password = 'NH4LLLw274ZZ'
        self.solr = pysolr.Solr('http://34.129.190.144/solr/stores/update?commit=true', auth=(solr_username,solr_password), always_commit=True,verify=False)



    def process_item(self,item, spider):

        self.solr.add([
            {"store_t": item["store"],
             "store_s": item["store"],
             "url_s": item["url"],
             "id": item["id"],
             "title_t": item["title"],
             "title_s": item["title"],
             "description_t": item["description"],
             "description_s": item["description"],
             "old_price_t": item["old_price"],
             "old_price_s": item["old_price"],
             "old_price_d": item["old_price_d"],
             "new_price_t": item["final_price"],
             "new_price_s": item["final_price"],
             "new_price_d": item["final_price_d"],
             "discount_d": item["discount_d"],
             "image_links_ss": item["image_links"],
             "image_links_txt": item["image_links"],
             "highlight_txt": item["highlight"],
             "final_urls_ss":item["final_urls"],
             "final_urls_txt": item["final_urls"]
             }])
        return item
