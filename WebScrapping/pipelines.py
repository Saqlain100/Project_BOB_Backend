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
        self.solr = pysolr.Solr('http://34.129.54.101/solr/stores/update?commit=true', auth=(solr_username,solr_password), always_commit=True,verify=False)



    def process_item(self,item, spider):
        docs = self.solr.search(q=f"id:{item['id']}", rows=1).docs
        likes = 0
        loves = 0
        views = 0
        if len(docs) > 0:
            likes = docs["likes_i"][0]
            loves = docs["loves_i"][0]
            views = docs["views_i"][0]
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
             "final_urls_txt": item["final_urls"],
             "updated_date_dt": item["updated_date_dt"],
             "save_d": item["save_d"],
             "likes_i":likes,
             "loves_i":loves,
             "views_i":views,
             "joined_t":str(item["id"])+"!!!"+item["final_urls"][0]+"!!!"+str(item["discount_d"])+"!!!"+str(item["final_price_d"])
             }])
        return item
