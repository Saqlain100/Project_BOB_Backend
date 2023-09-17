#from reusable_components.download_upload_blob_gcp import download_upload
import scrapy
import requests
import json
import pysolr
import logging


class QuotesSpider(scrapy.Spider):
    name = "Notify"

    def start_requests(self):
        url = "https://app.zyte.com/api/v2/projects/677411/spiders?archived=&ordering=name&search=&page_size=200&page=1&apikey=4d522088b1414984a4c5bad9372052b2"
        # Send an HTTP GET request to the URL
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Print the response content (the data returned by the API)
            res_list = json.loads(response.text)['results']
            spiders = [item['name'] for item in res_list]
            solr_username = 'admin'
            solr_password = 'NH4LLLw274ZZ'
            solr = pysolr.Solr('http://34.129.54.101/solr/stores',auth=(solr_username, solr_password),verify=False)
            # Define your Solr query parameters to get all facets
            query_params = {
                'facet': 'on',
                'facet.field': 'store_s',  # The asterisk (*) retrieves facets for all fields
                'facet.limit': -1,  # Setting limit to -1 gets all facet values
                'facet.mincount': 1,
            }
            results = solr.search('*:*', **query_params)
            # Retrieve and print the facet information
            facets = results.facets['facet_fields']['store_s'][::2]
            # Find elements in list1 that are not in list2
            missing_elements = [element for element in spiders if element not in facets]
            logging.info("Missing stores are "+str(missing_elements))




