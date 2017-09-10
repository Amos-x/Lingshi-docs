# -*- coding: utf-8 -*-
import scrapy
from news.items import AllItem
import time
import urllib.request
import json
import re

class SmmSpider(scrapy.Spider):
    name = 'SMM'
    start_urls = ['http://www.smm.cn/']
    serach_urlheaders = 'https://news.smm.cn/news/'

    def start_requests(self):
        keywords =['铜','铝','铅','锌']
        print('start crawling SMM...')
        for keyword in keywords:
            key_encode = urllib.request.quote('要闻/'+keyword)
            url = 'https://platform.smm.cn/newscenter/news/list/'+key_encode+'/1?page_limit=30'
            yield scrapy.Request(url,callback=self.next_parse,dont_filter=True,meta={'goal':keyword})

    def _time_judgment(self,str_time):
        now = time.localtime(time.time())
        date = time.strftime('%Y-%m-%d',now)
        if str_time == date:
            return True

    def next_parse(self,response):
        news_List = json.loads(response.text)['data']
        for news in news_List:
            try:
                if not self._time_judgment(news['Date']):
                    break
                item = AllItem()
                item['title'] = news['Title']
                item['url'] = self.serach_urlheaders + news['ID']
                item['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(news['UpdateTime']))
                item['msite'] = 'smm'
                item['source'] = (news['Source'] if news['Source'] else '上海有色网')
                item['classify'] = response.meta['goal']
                item['display'] = '1'
                item['abstract'] = (news['Profile'] if news['Profile'] else None)
                item['home_img_url'] = (news['Thumb'] if news['Thumb'] else None)
                yield scrapy.Request(item['url'],callback=self.parse,meta={'item':item})
            except Exception as e:
                print(e)
                print('SMM，Homepage Error')

    def parse(self, response):
        try:
            item = response.meta['item']
            content = response.xpath('//*[@id="content"]/div[3]/article/div/p|//*[@id="content"]/div[3]/article/div/table|//*[@id="content"]/div[3]/article/div/hr').extract()
            for x in range(len(content)):
                if content[x] == '<hr>':
                    content = content[:x]
                    break
            item['content'] = (''.join(content) if content else None)
            if item['content']:
                if not item['abstract']:
                    item['abstract'] = re.sub(r'<.*?>','',item['content'][:300]).strip()
                img_urls = response.css('article p img::attr(src)').extract()
                item['content_img_urls'] = (img_urls if img_urls else None)
                yield item
        except Exception as e:
            print(e)
            print('内容解析错误')
