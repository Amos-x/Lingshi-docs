# -*- coding: utf-8 -*-
import scrapy
from news.items import AllItem
import time
import urllib.request
import json
import re


class SmmSpider(scrapy.Spider):
    name = 'SMM'
    serach_urlheaders = 'https://news.smm.cn/news/'

    def start_requests(self):
        print('start crawling SMM...')
        url = 'https://news.smm.cn/'
        yield scrapy.Request(url,callback=self.next_parse,dont_filter=True)

    def _time_judgment(self,str_time):
        now = time.localtime(time.time())
        date = time.strftime('%Y-%m-%d',now)
        if str_time == date:
            return True

    def next_parse(self,response):
        news_List = response.css('ul.news-body-cont-list li.news_item')
        for news in news_List:
            try:
                label = news.css('div.newslist-tool label::text').extract_first()
                date_time = label[-10:]
                if not self._time_judgment(date_time):
                    break
                item = AllItem()
                item['title'] = news.css('div.newslist-title h3::text').extract_first()
                item['url'] = news.css('div.newslist-title a::attr(href)').extract_first()
                item['time'] = date_time
                item['msite'] = 'smm'
                item['source'] = (label[:-11] if label[:-11] else 'SMM')
                item['news_type'] = '有色'
                item['classify'] = ' '.join(news.css('div.newslist-label a::text').extract())
                item['display'] = '1'
                item['home_img_url'] = news.css('div.newslist-img img::attr(src)').extract_first()
                yield scrapy.Request(item['url'],callback=self.parse,meta={'item':item})
            except Exception as e:
                print(e)
                print('SMM，Homepage Error')

    def parse(self, response):
        try:
            item = response.meta['item']
            abstract = response.css('div.news-body-content p.news-intro.news_intro::text').extract_first()
            item['abstract'] = (abstract if abstract else item['title'])
            content = response.css('div.news-body-content div.news-main p').extract()
            item['content'] = (''.join(content) if content else None)
            if item['content']:
                img_urls = response.css('div.news-body-content div.news-main img::attr(src)').extract()
                item['content_img_urls'] = (img_urls if img_urls else None)
                yield item
        except Exception as e:
            print(e)
            print('内容解析错误')
