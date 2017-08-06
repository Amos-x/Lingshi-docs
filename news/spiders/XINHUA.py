# -*- coding: utf-8 -*-
import scrapy
import urllib.request
import json
from news.items import NewsContent,NewsItem
import time
import re
from bs4 import BeautifulSoup
from urllib.request import urljoin

class XinhuaSpider(scrapy.Spider):
    name = 'XINHUA'
    # allowed_domains = ['www.news.cn']
    start_urls = ['http://www.news.cn/']

    keywords = ['债券','拆借','美元','黄金','原油']
    url = 'http://so.news.cn/getNews?keyword=%E9%BB%84%E9%87%91&curPage=1&sortField=0&searchFields=1'
    def start_requests(self):
        print('start crawling XINHUA...')
        for keyword in self.keywords:
            keyword_encode = urllib.request.quote(keyword)
            url = 'http://so.news.cn/getNews?keyword='+keyword_encode+'&curPage=1&sortField=0&searchFields=1'
            yield scrapy.Request(url,callback=self.next_parse,dont_filter=True,meta={'goal':keyword,'page':1})


    def _timejudgement(self,str_time):
        now = time.localtime(time.time())
        today = time.strftime('%Y-%m-%d',now)
        if str_time ==today:
            return True

    def next_parse(self,response):
        data = json.loads(response.text)['content']['results']
        item = NewsItem()
        for group in data:
            try:
                str_time = group['pubtime'][:10]
                if not self._timejudgement(str_time):
                    break
                item['title'] = re.sub(r"[<>/='a-z]", '', group['title']).replace(' ', '')
                item['url'] = group['url']
                item['time'] = str_time
                item['msite'] = 'xinhua'
                item['img_urls'] = None
                if group['des']:
                    item['content'] = re.sub(r"[<>/='a-z]",'',group['des']).replace(' ','')
                item['goal_type'] = response.meta['goal']
                sitename = group['sitename']
                yield scrapy.Request(group['url'],callback=self.parse,meta={'s_n':sitename})
                yield item
            except:
                print('XINHUA,Homepage Error')
                pass
        last_date = data[-1]['pubtime'][:10]
        if self._timejudgement(last_date):
            page_num = response.meta['page'] + 1
            page = 'curPage'+str(page_num)
            url = re.sub('curPage=\d',page,response.url)
            yield scrapy.Request(url,callback=self.next_parse,meta={'keyword':response.meta['goal'],'page':page_num})

    def parse(self, response):
        try:
            item = NewsContent()
            soup = BeautifulSoup(response.text,'lxml')
            item['title'] = soup.title.get_text().strip()
            item['source'] = ''.join(response.css('em::text').extract()).strip()
            if not item['source']:
                item['source'] = '新华网'+response.meta['s_n']
            item['url'] = response.url
            item['msite'] = 'xinhua'
            item['content'] = [str(a) for a in soup.select('p')[0].parent.select('p')]
            img_id = [i.get('src') for i in soup.select('p')[0].parent.select('p img')]
            if img_id:
                item['img_urls'] = [urljoin(response.url,x) for x in img_id if not 'http' in x]
            else:
                item['img_urls'] = None
            item['file_urls'] = None
            yield item
        except:
            print('XINHUA，Content Error')