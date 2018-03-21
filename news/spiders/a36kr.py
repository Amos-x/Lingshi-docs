# -*- coding: utf-8 -*-
import scrapy
import time
import json
from news.items import AllItem
import re

class A36krSpider(scrapy.Spider):
    name = '36kr'
    # custom_settings = {'DOWNLOADER_MIDDLEWARES': {'news.middlewares.SeleniumMiddleware': 1}}
    url = 'http://36kr.com/api/info-flow/main_site/posts?b_id=&per_page=20&_='

    def start_requests(self):
        now = str(int(time.time()*1000))
        yield scrapy.Request(self.url+now,callback=self.next_parse,dont_filter=True)

    def _time_judgment(self,str_time):
        now = time.localtime(time.time())
        date = time.strftime('%Y-%m-%d',now)
        if str_time == date:
            return True

    def next_parse(self,response):
        results = json.loads(response.text)['data']['items']
        for group in results:
            try:
                str_time = group['updated_at'][:10]
                if not self._time_judgment(str_time):
                    break
                item = AllItem()
                item['title'] = group['title']
                item['url'] = 'http://36kr.com/p/' + str(group['id']) +'.html'
                item['time'] = group['updated_at']
                item['msite'] = '36kr'
                item['source'] = '36氪'
                item['news_type'] = '科技'
                classify = json.loads(group['extraction_tags'])
                tags = []
                for x in classify:
                    tags.append(x[0])
                item['classify'] = ' '.join(tags)
                item['display'] = '1'
                item['abstract'] = group['summary']
                item['home_img_url'] = group['cover']
                yield scrapy.Request(item['url'],callback=self.parse,meta={'item':item})
            except Exception as e:
                print(e)
                print('36kr,Home-error')

    def parse(self, response):
        try:
            item = response.meta['item']
            text = re.search(r'"content":"<p>.*</p>"',response.text)
            if text:
                content = json.loads('{' + text.group() + '}')
                item['content'] = content['content']
                content_img_urls = re.findall(r'<img.*?src="(.*?)".*?>',content['content'])
                item['content_img_urls'] = (content_img_urls if content_img_urls else None)
                yield item
        except Exception as e:
            print(e)
            print('36kr,Content-error')