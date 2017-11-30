# -*- coding: utf-8 -*-
import scrapy
import time
from news.items import AllItem
import re

class PmcaffSpider(scrapy.Spider):
    name = 'pmcaff'
    url = 'http://www.pmcaff.com/site/selection'

    def start_requests(self):
        yield scrapy.Request(self.url,callback=self.article_list_parse,dont_filter=True)

    def _time_judgment(self,str_time):
        now = time.localtime(time.time())
        date = time.strftime('%Y-%m-%d',now)
        if str_time == date:
            return True

    def article_list_parse(self,response):
        try:
            article_list = response.css('ul.list-group li.list-group-item')
            for article in article_list:
                pub_time = article.css('span.pub-time::attr(title)').extract_first()
                # if not self._time_judgment(pub_time[:10]):
                #     break
                item = AllItem()
                item['title'] = article.css('h2.news-title a::text').extract_first()
                item['url'] = article.css('h2.news-title a::attr(href)').extract_first()
                item['time'] = pub_time
                item['msite'] = 'pmcaff'
                item['source'] = '互联网产品研究中心'
                item['classify'] = '产品经理'
                item['display'] = '1'
                item['home_img_url'] = article.css('div.pic-banner img::attr(src)').extract_first()
                yield scrapy.Request(item['url'],callback=self.parse,meta={'item':item})
        except Exception as e:
            print('index page error')
            print(e)

    def parse(self, response):
        try:
            item = response.meta['item']
            content = response.css('div.article-body article > *').extract()
            if content:
                item['content'] = ''.join(content)
                item['abstract'] = re.sub(r'<.*?>','',item['content'])[:150] + '...'
                content_img_urls = response.css('div.article-body article img::attr(src)').extract()
                item['content_img_urls'] = (content_img_urls if content_img_urls else None)
                yield item
        except Exception as e:
            print('content page error')
            print(e)