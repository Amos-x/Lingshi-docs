# -*- coding: utf-8 -*-
import scrapy
from news.items import AllItem
import time
import re

class QqhouseSpider(scrapy.Spider):
    name = 'qqhouse'

    def start_requests(self):
        url = 'http://fs.house.qq.com/l/fzjgdxw/more.htm'
        yield scrapy.Request(url,callback=self.next_parse,dont_filter=True)

    def _time_judgment(self,str_time):
        now = time.localtime(time.time())
        date = time.strftime('%m-%d-',now)
        if str_time == date:
            return True

    def next_parse(self,response):
        try:
            data = response.css('div.leftList ul.list01 li')
            for group in data:
                s_time = group.css('span::text').extract_first()[:6]
                strtime = re.sub('[月日]','-',s_time)
                if not self._time_judgment(strtime):
                    break
                item = AllItem()
                item['title'] = group.css('a::text').extract_first()
                item['url'] = group.css('a::attr(href)').extract_first()
                item['time'] = time.strftime('%Y-%m-%d',time.localtime(time.time()))
                item['msite'] = 'qq.house'
                item['news_type'] = '地产'
                item['classify'] = '房地产'
                item['display'] = 1
                item['home_img_url'] = None
                yield scrapy.Request(item['url'],callback=self.parse,meta={'item':item})
        except Exception as e:
            print(e,' Home page error')


    def parse(self, response):
        try:
            item = response.meta['item']
            item['source'] = response.css('span.a_source a::text').extract_first()
            abstract = response.css('div#Cnt-Main-Article-QQ p.titdd-Article ').extract_first()
            item['abstract'] = re.sub(r"<.+?>",'',abstract)
            content = response.css('div#Cnt-Main-Article-QQ p')
            if content:
                item['content'] = ''.join(content.extract()[1:])
                content_img_urls = content.css('img::attr(src)').extract()
                item['content_img_urls'] = (content_img_urls if content_img_urls else None)
                yield item
        except Exception as e:
            print(e,' content error')


