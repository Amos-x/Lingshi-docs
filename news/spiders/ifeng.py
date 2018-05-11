# -*- coding: utf-8 -*-
import scrapy
from news.items import AllItem
import re


class IfengSpider(scrapy.Spider):
    name = 'ifeng'
    allowed_domains = ['finance.ifeng.com','news.ifeng.com']

    def start_requests(self):
        sz_url = 'http://news.ifeng.com/'
        cj_url = 'http://finance.ifeng.com/'
        yield scrapy.Request(sz_url,callback=self.sz_parse,dont_filter=True)
        yield scrapy.Request(cj_url,callback=self.cj_parse,dont_filter=True)

    def sz_parse(self,response):
        news = response.css('div.left_co1 div.tit h1 a,div.left_co1 div.tit p a,div.left_co1 div.tit h2 a')
        for i in news:
            title = i.css('::text').extract_first()
            content_url = i.css('::attr(href)').extract_first().strip()
            yield scrapy.Request(content_url,callback=self.parse,meta={'title':title,'news_type':'时政'})

    def cj_parse(self,response):
        news = response.css('div.box_01 h2 a,div.box_01 ul li a')
        for i in news:
            title = i.css('::text').extract_first()
            content_url = i.css('::attr(href)').extract_first()
            yield scrapy.Request(content_url,callback=self.parse,meta={'title':title,'news_type':'财经'})

    def parse(self, response):
        item = AllItem()
        item['title'] = response.meta['title']
        item['url'] = response.url
        item['msite'] = 'ifeng'
        item['classify'] = '{}头条热点'.format(response.meta['news_type'])
        item['news_type'] = response.meta['news_type']
        item['display'] = '1'

        web_type = response.css('html::attr(class)').extract_first()
        if web_type == 'no-js':
            item['time'] = response.css('div.yc_tit p span::text').extract_first()
            source = response.css('div.yc_tit p a::text').extract_first()
            item['source'] = (source.strip() if source else None)
            content = response.css('div#yc_con_txt p').extract()
            item['content'] = (''.join(content) if content else None)
            if item['content']:
                content_img_urls = response.css('div#yc_con_txt p img::attr(src)').extract()
                item['content_img_urls'] = (content_img_urls if content_img_urls else None)
                item['home_img_url'] = (content_img_urls[0] if content_img_urls else None)
                item['abstract'] = re.sub(r'<.*?>', '', item['content'])[:150] + '...'
                yield item
        elif not web_type:
            time = response.css('div#artical_sth p.p_time span.ss01::text').extract_first()
            item['time'] = (re.sub(r'[年月日]','-',time) if time else None)
            source = response.css('div#artical_sth p.p_time span.ss03 a::text').extract_first()
            item['source'] = (source.strip() if source else None)
            content = response.css('div#main_content p').extract()
            item['content'] = (''.join(content) if content else None)
            if item['content']:
                content_img_urls = response.css('div#main_content p img::attr(src)').extract()
                item['content_img_urls'] = (content_img_urls if content_img_urls else None)
                item['home_img_url'] = (content_img_urls[0] if content_img_urls else None)
                item['abstract'] = re.sub(r'<.*?>', '', item['content'])[:150] + '...'
                yield item

