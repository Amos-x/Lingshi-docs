# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class NewsItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    time = scrapy.Field()
    content = scrapy.Field()
    msite = scrapy.Field()
    goal_type = scrapy.Field()

class NewsContent(scrapy.Item):
    title = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    msite = scrapy.Field()
    img_urls = scrapy.Field()
    img_paths = scrapy.Field()
    file_urls = scrapy.Field()
    file_paths = scrapy.Field()