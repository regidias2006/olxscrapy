import scrapy
import json
import os
import sys

# Captura o valor passado como argumento de linha de comando
url = sys.argv[3]
user_max_pages = sys.argv[7]
user_max_value = sys.argv[5]

# Separa a string em chave e valor
chave, user_max_pages = user_max_pages.split("=")
chave, user_max_value = user_max_value.split("=")

import logging
logging.getLogger('scrapy').setLevel(logging.WARNING)

import warnings
from scrapy.exceptions import ScrapyDeprecationWarning
warnings.filterwarnings("ignore", category=UserWarning, module="scrapy")
warnings.filterwarnings("ignore", category=ScrapyDeprecationWarning, module="scrapy.utils.request")
warnings.filterwarnings("ignore", category=UserWarning, module="scrapy.utils.log")

class OLXSpider(scrapy.Spider):
    name = 'olx_spider'
    start_urls = []

    start_urls.append(url.replace("'", '')) #url.replace("'", '')

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2
    }
    max_pages = int(user_max_pages)
    current_page = 1

    def start_requests(self):
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'Accept-Language': 'en',
        }
        
        # Suprimir os logs
        sys.stdout = open(os.devnull, 'w')

        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse(self, response):
        if self.current_page > self.max_pages:
            return

        if response.status == 200:
            items = response.css('li[class^="sc-1fcmfeb-2"]')

            # Carrega os dados do arquivo output.json
            data = self.load_json()

            for item in items:
                # Extrair os detalhes do item
                item_id = item.css('a::attr(href)').get()
                if item_id:
                    item_id = item_id.split('/')[-1]
                title = item.css('h2::text').get()
                price = item.css('span[class^="m7nrfa"]::text').get()
                image_url = item.css('img::attr(src)').get()
                item_url = item.css('a::attr(href)').get()

                # Check if the price is less than R$ 300,00
                if price and float(price.replace('R$ ', '').replace('.', '')) <= float(user_max_value):
                    item_data = {
                        'id': item_id,
                        'title': title,
                        'price': price,
                        'image_url': image_url,
                        'item_url': response.urljoin(item_url) if item_url else None
                    }

                    # Verificar se o item já existe na primeira leitura do arquivo JSON
                    if self.item_exists(item_id, data):
                        continue

                    # Adicionar o item à lista de dados
                    data.append(item_data)

                    yield item_data

            # Salvar os dados no arquivo output.json
            self.save_json(data)

            # Extrair o link da próxima página
            next_page = response.css('a[data-lurker-detail="next_page"]::attr(href)').get()
            if next_page:
                self.current_page += 1
                yield response.follow(next_page, callback=self.parse, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                    'Accept-Language': 'en',
                })
        else:
            self.logger.error(f"Failed to open the page: {response.url}")

    def load_json(self):
        json_file = os.path.join(os.getcwd(), 'output.json')

        if os.path.exists(json_file):
            with open(json_file, 'r') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []

        return data

    def item_exists(self, item_id, existing_data):
        existing_ids = {item.get('id') for item in existing_data}
        return item_id in existing_ids

    def save_json(self, data):
        json_file = os.path.join(os.getcwd(), 'output.json')

        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)
