# -*- coding: utf-8 -*-
import scrapy
import urllib.request
import json
from news.items import AllItem
import time
import re
from bs4 import BeautifulSoup
from urllib.request import urljoin

class XinhuaSpider(scrapy.Spider):
    name = 'XINHUA'
    start_urls = ['http://www.news.cn/']

    keywords = ['有色金属','债券','拆借','美元','黄金','原油']
    url = 'http://so.news.cn/getNews?keyword=%E9%BB%84%E9%87%91&curPage=1&sortField=0&searchFields=1'
    def start_requests(self):
        print('start crawling XINHUA...')
        for keyword in self.keywords:
            keyword_encode = urllib.request.quote(keyword)
            url = 'http://so.news.cn/getNews?keyword='+keyword_encode+'&curPage=1&sortField=0&searchFields=1'
            yield scrapy.Request(url,callback=self.next_parse,dont_filter=True)


    def _timejudgement(self,str_time):
        now = time.localtime(time.time())
        today = time.strftime('%Y-%m-%d',now)
        if str_time ==today:
            return True

    def next_parse(self,response):
        result = json.loads(response.text)['content']
        data = result['results']
        keyword = result['keyword']
        for group in data:
            try:
                str_time = group['pubtime'][:10]
                if not self._timejudgement(str_time):
                    break
                item = AllItem()
                item['title'] = re.sub(r"[<>/='a-z]", '', group['title']).replace(' ', '')
                item['url'] = group['url']
                item['time'] = group['pubtime']
                item['classify'] = keyword
                item['msite'] = 'xinhua'
                item['display'] = '1'
                item['source'] =  ('新华网'+group['sitename'] if '频道' in group['sitename'] else group['sitename'])
                item['home_img_url'] = ('http://tpic.home.news.cn/xhCloudNewsPic/'+group['imgUrl'] if group['imgUrl'] else None)
                if group['des']:
                    item['abstract'] = re.sub(r"[<>/='a-z]",'',group['des']).replace(' ','')
                else:
                    item['abstract'] = None
                yield scrapy.Request(group['url'],callback=self.parse,meta={'item':item})
            except Exception as e:
                print(e)
                print('XINHUA,Homepage Error')
                pass
        last_date = data[-1]['pubtime'][:10]
        if self._timejudgement(last_date):
            page_num = int(result['curPage']) + 1
            page = 'curPage='+str(page_num)
            url = re.sub('curPage=\d',page,response.url)
            yield scrapy.Request(url,callback=self.next_parse,dont_filter=True)

    def parse(self, response):
        try:
            item = response.meta['item']
            soup = BeautifulSoup(response.text,'lxml')
            content = [str(a) for a in soup.select('p')[0].parent.select('p')]
            item['content'] = ''.join(content)
            img_id = [i.get('src') for i in soup.select('p')[0].parent.select('p img')]
            if img_id:
                item['content_img_urls'] = [urljoin(response.url,x) for x in img_id if not 'http' in x]
            else:
                item['content_img_urls'] = None
            if item['content']:
                if not item['abstract']:
                    item['abstract'] = re.sub(r'<.*?>','',item['content'][:300]).strip()
                yield item
        except:
            print('XINHUA，Content Error')