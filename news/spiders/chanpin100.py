# -*- coding: utf-8 -*-
import scrapy
from urllib.request import urljoin
from news.items import AllItem
import time

class Chanpin100Spider(scrapy.Spider):
    name = 'chanpin100'
    url = 'http://www.chanpin100.com/'

    def start_requests(self):
        yield scrapy.Request(self.url,dont_filter=True,callback=self.section_parse)

    def section_parse(self,response):
        section_list = response.css('section.category ul.list li')[:5]
        for section in section_list:
            section_url = urljoin(response.url,section.css('a::attr(href)').extract_first())
            section_name = section.css('a::text').extract_first()
            yield scrapy.Request(section_url,callback=self.article_list_parse,meta={'section_name':section_name},dont_filter=True)

    def article_list_parse(self,response):
        try:
            article_list = response.css('div.article-list div.data-container div.item')
            for article in article_list:
                article_time = article.css('ul.article-info li.date::text').extract_first()
                if '天' in article_time:
                    break
                item = AllItem()
                item['title'] = article.css('h4.media-heading a::text').extract_first()
                item['url'] = urljoin(response.url,article.css('h4.media-heading a::attr(href)').extract_first())
                item['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                item['msite'] = 'chanpin100'
                item['source'] = '产品壹佰'
                item['classify'] = response.meta['section_name']
                item['display'] = '1'
                item['abstract'] = article.css('p.article-summary::text').extract_first().strip()
                item['home_img_url'] = article.css('div.cover-container img::attr(data-original)').extract_first()
                yield scrapy.Request(item['url'],callback=self.parse,meta={'item':item})
        except Exception as e:
            print('index page error')
            print(e)

    def parse(self, response):
        try:
            item = response.meta['item']
            content = response.css('div.article-content-container > *').extract()
            if content:
                item['content'] = ''.join(content)
                content_img_urls = response.css('div.article-content-container img::attr(src)').extract()
                item['content_img_urls'] = (content_img_urls if content_img_urls else None)
                yield item
        except Exception as e:
            print('content page error')
            print('e')