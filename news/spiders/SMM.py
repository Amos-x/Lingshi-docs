# -*- coding: utf-8 -*-
import scrapy
from news.items import NewsItem,NewsContent
import time
import urllib.request
import json
import re

class SmmSpider(scrapy.Spider):
    name = 'SMM'
    allowed_domains = ['www.smm.cn','news.smm.cn']
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
                item = NewsItem()
                item['title'] = news['Title']
                item['url'] = self.serach_urlheaders + news['ID']
                item['time'] = news['Date']
                item['content'] = (news['Profile'] if news['Profile'] else None)
                item['msite'] = 'smm'
                item['goal_type'] = response.meta['goal']
                item['img_urls'] = [news['Thumb']]
                yield scrapy.Request(item['url'],callback=self.parse,meta={'source':news['Source'],'url':item['url'],'newsitem':item})
            except:
                print('SMM，Homepage Error')

    def parse(self, response):
        try:
            item = NewsContent()
            item['title'] = response.css('div.news-title h1::text').extract_first()
            item['url'] = response.meta['url']
            item['source'] = response.meta['source']
            content = response.xpath('//*[@id="content"]/div[3]/article/div/p|//*[@id="content"]/div[3]/article/div/table|//*[@id="content"]/div[3]/article/div/hr').extract()
            for x in range(len(content)):
                if content[x] == '<hr>':
                    content = content[:x]
                    break
            item['content'] = content
            item['msite'] = 'smm'
            img_urls = response.css('article p img::attr(src)').extract()
            if img_urls:
                item['img_urls'] = img_urls
            else:
                item['img_urls'] = None
            item['file_urls'] = None
            newsitem = response.meta['newsitem']
            yield newsitem
            yield item
        except Exception as e:
            print(e)
