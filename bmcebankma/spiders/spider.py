import scrapy

from scrapy.loader import ItemLoader

from ..items import BmcebankmaItem
from itemloaders.processors import TakeFirst
base = 'https://www.bmcebank.ma/en/actualites-groupe?page={}'

class BmcebankmaSpider(scrapy.Spider):
	name = 'bmcebankma'
	page = 0
	start_urls = [base.format(page)]

	def parse(self, response):
		post_links = response.xpath('//div[@class="actu-body-bloc"]//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if post_links:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response):
		date_and_title = response.xpath('//div[@class="node-body-title content-head content-head-inner clearfix"]/h1/text()').get().split('-')
		title = date_and_title[1]
		description = response.xpath('//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		date = date_and_title[0]

		item = ItemLoader(item=BmcebankmaItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
