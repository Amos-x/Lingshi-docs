# -*- coding: utf-8 -*-
import scrapy
from news.items import AllItem
import time

class WoshipmSpider(scrapy.Spider):
    name = 'woshipm'
    url = 'http://www.woshipm.com/'

    def start_requests(self):
        yield scrapy.Request(self.url,callback=self.topics_parse,dont_filter=True)

    def topics_parse(self,response):
        topics_list = response.css('ul.sub-menu li a')[:5]
        for topic in topics_list:
            topics_url = topic.css('::attr(href)').extract_first()
            classify = topic.css('::text').extract_first()
            yield scrapy.Request(topics_url,callback=self.topics_parse_two,dont_filter=True,meta={'classify':classify})

    def _time_judgment(self,str_time):
        now = time.localtime(time.time())
        date = time.strftime('%Y/%m/%d',now)
        if str_time == date:
            return True

    def topics_parse_two(self,response):
        try:
            postlist = response.css('div.home-post-list div.postlist-item')
            for postitem in postlist:
                str_time = postitem.css('div.stream-list-meta time::text').extract_first()
                if not self._time_judgment(str_time):
                    break
                item = AllItem()
                item['title'] = postitem.css('h2.post-title a::text').extract_first()
                item['url'] = postitem.css('h2.post-title a::attr(href)').extract_first()
                item['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                item['msite'] = 'woshipm'
                item['source'] = '人人都是产品经理'
                item['news_type'] = '产品'
                item['display'] = '1'
                item['classify'] = response.meta['classify']
                item['abstract'] = postitem.css('div.content p.des::text').extract_first()
                item['home_img_url'] = postitem.css('div.post-img img::attr(src)').extract_first()
                yield scrapy.Request(item['url'],callback=self.topics_parse_three,meta={'item':item})
        except Exception as e:
            print('index page error:')
            print(e)

    def topics_parse_three(self, response):
        try :
            item = response.meta['item']
            content = response.css('article div.grap > *').extract()
            if content:
                item['content'] = ''.join(content)
                content_img_urls = response.css('article div.grap img::attr(src)').extract()
                item['content_img_urls'] = (content_img_urls if content_img_urls else None)
                yield item
        except Exception as e:
            print('content page error：')
            print(e)
