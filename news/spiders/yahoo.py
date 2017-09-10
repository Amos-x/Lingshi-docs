# -*- coding: utf-8 -*-
import scrapy
import re
from news.items import AllItem
import datetime

class YahooSpider(scrapy.Spider):
    name = "yahoo"
    allowed_domains = ['yahoo.com','news.search.yahoo.com']
    urlPath = '/home/liuweihuang/yahooPicture'
    start_urls = ['http://https://www.yahoo.com/news//']
    custom_settings = {'USER_AGENT':None}

    def start_requests(self):
        print('satrt crawling yahoo...')
        keywords = ['copper', 'bonds', 'mine', 'lending rates']
        pages = ['0','11','21','31','41','51','61','71','81','91']
        for keyword in keywords:
            for page in pages:
                url = 'https://news.search.yahoo.com/search;_ylt=AwrC1CgYaXFZmwUAkQTQtDMD;_ylu=X3oDMTEzajVvczlrBGNvbG8DYmYxBHBvcwMxBHZ0aWQDBHNlYwNwYWdpbmF0aW9u?p='+keyword+'&pz=10&bct=0&b='+page
                yield scrapy.Request(url, callback=self.next_parse, dont_filter=True ,meta={'goal': keyword,'page':page})

    def time_judgement(self,str_time):
        time_list = str_time.split()
        if time_list[1] == 'hours':
            return True

    # 爬取新闻列表
    def next_parse(self, response):
        try:
            result_list = response.css('ol.reg.searchCenterMiddle li')
            for group in result_list:
                time = group.css('span.tri.fc-2nd.ml-10::text').extract_first()
                if self.time_judgement(time):
                    item = AllItem()
                    item['title'] = group.css('.title a::text').extract_first()
                    item['url'] = group.css('.title a::attr(href)').extract_first()
                    item['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item['abstract'] = group.css('.compText p::text').extract_first()
                    item['msite'] = 'yahoo'
                    item['classify'] = response.meta['goal']
                    item['source'] = group.css('.compTitle div .cite::text').extract_first()
                    item['display'] = '1'
                    item['home_img_url'] = group.css('img.s-img::attr(data-src)').extract_first()
                    if 'yahoo.com/news' in item['url']:
                        yield scrapy.Request(item['url'], callback=self.parse, meta={'item':item})
        except:
            print('YAHOO，Homepage Error')
    # 爬取新闻内容
    def parse(self, response):
        try:
            item = response.meta['item']
            # contentElements = response.xpath(
            #     './/div[@id="Col1-0-ContentCanvas"]/article/div/p|.//div[@id="Col1-0-ContentCanvas"]/article/div/figure/div/img|.//div[@id="Col1-0-ContentCanvas"]/article/div/ul').extract()
            # content = ""
            # pPattern = '<p class='
            # for contents in contentElements:
            #     if re.match(r'<img (.+?)>',contents):
            #         content = content + '<p>'+ contents +'</p>'
            #     if re.match(pPattern, contents):
            #         string = re.compile('content="(.*?)" data-reactid').findall(contents)
            #         if len(string) == 0:
            #             continue
            #         content = content + " <p> " + string[-1] + " </p>"
            content = response.css('div#Col1-0-ContentCanvas article p').extract()
            item['content'] = ''.join(content)
            content_img_urls = response.css('div#Col1-0-ContentCanvas article img::attr(src)').extract()
            item['content_img_urls'] = (content_img_urls if content_img_urls else None)
            # if img:
            #     item['img_urls'] = img[:int(len(img)/2)]
            # else:
            #     item['img_urls'] = None
            if item['content']:
                yield item
        except:
            print('YAHOO,Content Error')