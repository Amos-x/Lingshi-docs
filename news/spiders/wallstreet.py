# -*- coding: utf-8 -*-
import scrapy
from news.items import AllItem
import json
import time

class WallstreetSpider(scrapy.Spider):
    name = 'wallstreet'

    def start_requests(self):
        url = 'https://api-prod.wallstreetcn.com/apiv1/content/articles?category=global&limit=30&platform=wscn-platform'
        yield scrapy.Request(url,callback=self.next_parse,dont_filter=True)

    def _time_judgment(self,str_time):
        now = time.localtime(time.time())
        date = time.strftime('%Y-%m-%d',now)
        if str_time == date:
            return True

    def next_parse(self,response):
        data = json.loads(response.text)['data']['items']
        try:
            for group in data:
                str_time = time.strftime('%Y-%m-%d',time.localtime(group['display_time']))
                if not self._time_judgment(str_time):
                    break
                item = AllItem()
                item['title'] = group['title']
                item['url'] = group['uri']
                item['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(group['display_time']))
                item['msite'] = 'wallstreetcn'
                item['source'] = '华尔街见闻 作者：'+ group['author']['display_name']
                classify = group['categories']
                item['classify'] = (' '.join(classify) if classify else None)
                item['display'] = '1'
                item['abstract'] = group['content_short']
                item['home_img_url'] = group['image_uri']
                yield scrapy.Request(url=group['uri'],callback=self.parse,meta={'item':item})
        except Exception as e:
            print('Home page Error: ')
            print(e)

    def parse(self, response):
        try:
            item = response.meta['item']
            text = None
            if 'wallstreetcn.com/articles' in response.url:
                text = response.css('div.node-article-content ')
            if 'awtmt.com/articles' in response.url:
                text = response.css('div.article-detail-text.image-zoom ')
            if 'wallstreetcn.com/premium' in response.url:
                text = response.css('div.pa-main__content ')
            if 'weexcn.com/articles' in response.url:
                text = response.css('div.article__content__text ')
            if text:
                item['content'] = ''.join(text.extract())
                content_img_urls = text.css('img::attr(src)').extract()
                item['content_img_urls'] = (content_img_urls if content_img_urls else None)
                yield item
        except Exception as e:
            print('content error')
            print(e)