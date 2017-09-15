# -*- coding: utf-8 -*-
import scrapy
import time
import json
from news.items import AllItem

class Im2makerSpider(scrapy.Spider):
    name = 'im2maker'
    url = 'http://www.im2maker.com/index.php?m=content&c=index&a=get_more'

    def start_requests(self):
        now = str(int(time.time()))
        yield scrapy.FormRequest(self.url,formdata={'last_time':now,'pages':'1','pagesize':'15'},
                                 callback=self.next_parse,dont_filter=True)

    def _time_judgment(self,str_time):
        now = time.localtime(time.time())
        date = time.strftime('%Y-%m-%d',now)
        if str_time == date:
            return True

    def next_parse(self,response):
        results = json.loads(response.text)
        for group in results:
            try:
                str_time = time.strftime('%Y-%m-%d',time.localtime(int(group['inputtime'])))
                if not self._time_judgment(str_time):
                    break
                item = AllItem()
                item['title'] = group['title']
                item['url'] = group['url']
                item['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(group['inputtime'])))
                item['source'] = '镁客网'
                item['msite'] = 'im2maker'
                item['classify'] = (group['keywords'] if group['keywords'] else None)
                item['display'] = '1'
                item['abstract'] = (group['description'] if group['description'] else None)
                item['home_img_url'] = (group['thumb'] if group['thumb'] else None)
                yield scrapy.Request(group['url'],callback=self.parse,meta={'item':item})
            except Exception as e:
                print(e)
                print('im2maker,Home-error')

    def parse(self, response):
        try:
            item = response.meta['item']
            content = response.css('div.text p').extract()
            if content:
                item['content'] = ''.join(content)
                content_img_urls = response.css('div.text p img::attr(src)').extract()
                item['content_img_urls'] = (content_img_urls if content_img_urls else None)
                yield item
        except Exception as e:
            print(e)
            print('im2maker,content-error')
