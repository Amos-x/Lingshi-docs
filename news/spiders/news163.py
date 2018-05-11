# -*- coding: utf-8 -*-
import scrapy
from news.items import AllItem
import re


class News163Spider(scrapy.Spider):
    name = 'news163'

    def start_requests(self):
        cj_url = 'http://money.163.com/'
        sz_url = 'http://gov.163.com/'
        yield scrapy.Request(cj_url,callback=self.cj_parse,dont_filter=True)
        yield scrapy.Request(sz_url, callback=self.sz_parse, dont_filter=True)

    def cj_parse(self,response):
        news = response.css('ul.topnews_nlist li h2 a,ul.topnews_nlist li h3 a')
        for i in news:
            title = i.css('::text').extract_first()
            content_url = i.css('::attr(href)').extract_first().strip()
            yield scrapy.Request(content_url,callback=self.parse,meta={'title':title,'news_type':'财经'})

    def sz_parse(self,response):
        news = response.css('ul.top_news_list li p a,ul.top_news_list li h2 a')
        for i in news:
            title = i.css('::text').extract_first()
            content_url = i.css('::attr(href)').extract_first().strip()
            yield scrapy.Request(content_url,callback=self.parse,meta={'title':title,'news_type':'时政'})

    def parse(self, response):
        item = AllItem()
        item['title'] = response.meta['title']
        item['url'] = response.url
        item['time'] = response.css('div.post_time_source::text').extract_first().strip()[:19]
        item['msite'] = '163'
        item['source'] = response.css('div.post_time_source a#ne_article_source::text').extract_first()
        item['classify'] = '{}头条热点'.format(response.meta['news_type'])
        item['news_type'] = response.meta['news_type']
        item['display'] = '1'
        content = response.css('div#endText p').extract()
        item['content'] = (''.join(content) if content else None)
        if item['content']:
            content_img_urls = response.css('div#endText p img::attr(src)').extract()
            item['content_img_urls'] = (content_img_urls if content_img_urls else None)
            item['home_img_url'] = (content_img_urls[0] if content_img_urls else None)
            item['abstract'] = re.sub(r'<.*?>','',item['content'])[:150] + '...'
            yield item
