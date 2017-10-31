# -*- coding: utf-8 -*-
import scrapy
import time
from news.items import AllItem
from urllib.request import urljoin
import re

class PeoplehouseSpider(scrapy.Spider):
    name = 'peoplehouse'
    url = 'http://house.people.com.cn/GB/194441/index1.html'

    def start_requests(self):
        yield scrapy.Request(self.url,callback=self.next_parse,dont_filter=True)

    def _time_judgment(self,str_time):
        now = time.localtime(time.time())
        date = time.strftime('%Y-%m-%d',now)
        if str_time == date:
            return True

    def next_parse(self,response):
        try:
            datalist = response.css('div.fl.p2j_list ul.list_14 li')
            for group in datalist:
                strtime = group.css('i::text').extract_first()[:10]
                if not self._time_judgment(strtime):
                    break
                item = AllItem()
                item['title'] = group.css('a::text').extract_first()
                item['url'] = urljoin(self.url,group.css('a::attr(href)').extract_first())
                item['time'] = group.css('i::text').extract_first()
                item['msite'] = 'house.people'
                item['classify'] = '房地产'
                item['display'] = 1
                item['home_img_url'] = None
                yield scrapy.Request(item['url'],callback=self.parse,meta={'item':item})
        except Exception as e:
            print(e,' Home error')

    def parse(self, response):
        try:
            item = response.meta['item']
            item['source'] = response.css('div.box01 div.fl a::text').extract_first()
            content = response.css('div#rwb_zw p')
            if content:
                item['content'] = ''.join(content.extract())
                abstract = content.css('p::text').extract()
                item['abstract'] = ''.join(abstract)[:150].strip()
                content_img_urls = content.css('img::attr(src)').extract()
                if content_img_urls:
                    item['content_img_urls'] = [urljoin(response.url,img_url) for img_url in content_img_urls]
                else:
                    item['content_img_urls'] = None
                yield item
        except Exception as e:
            print(e,' content error')
