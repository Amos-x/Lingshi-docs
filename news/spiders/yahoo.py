# -*- coding: utf-8 -*-
import scrapy
import re
from news.items import NewsItem,NewsContent
import datetime

class YahooSpider(scrapy.Spider):
    name = "yahoo"
    allowed_domains = ['yahoo.com','news.search.yahoo.com']
    urlPath = '/home/liuweihuang/yahooPicture'
    start_urls = ['http://https://www.yahoo.com/news//']
    custom_settings = {'USER_AGENT':None}

    def start_requests(self):
        print('开始运行yahoo...')
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
        item = NewsItem()
        try:
            result_list = response.css('ol.reg.searchCenterMiddle')
            for group in result_list:
                time = group.css('span.tri.fc-2nd.ml-10::text').extract_first()
                if self.time_judgement(time):
                    item['title'] = group.css('.title a::text').extract_first()
                    item['url'] = group.css('.title a::attr(href)').extract_first()
                    item['time'] = str(datetime.datetime.today())[:10]
                    item['content'] = group.css('.compText p::text').extract_first()
                    item['msite'] = 'yahoo'
                    item['goal_type'] = response.meta['goal']
                    yield item
                    yield scrapy.Request(item['url'], callback=self.parse, meta={'url': item['url']})
        except:
            print('YAHOO，错误，忽略错误项')
    # 爬取新闻内容
    def parse(self, response):
        try:
            contentElements = response.xpath(
                './/div[@id="Col1-0-ContentCanvas"]/article/div/p|.//div[@id="Col1-0-ContentCanvas"]/article/div/figure/div/img|.//div[@id="Col1-0-ContentCanvas"]/article/div/ul').extract()
            content = ""
            pPattern = '<p class='
            for contents in contentElements:
                if re.match(r'<img (.+?)>',contents):
                    content = content + '<p>'+ contents +'</p>'
                if re.match(pPattern, contents):
                    string = re.compile('content="(.*?)" data-reactid').findall(contents)
                    if len(string) == 0:
                        continue
                    content = content + " <p> " + string[-1] + " </p>"
            item = NewsContent()
            item['title'] = response.xpath('.//div/header[@class="canvas-header"]/h1/text()').extract_first()
            item['url'] = response.url
            item['source'] = response.xpath('.//span[@class="provider-link"]/a/text()').extract_first()
            item['content'] = content
            item['msite'] = 'yahoo'
            img = response.css('article img::attr(src)').extract()
            if img:
                item['img_urls'] = img[:int(len(img)/2)]
            else:
                item['img_urls'] = None
            item['file_urls'] = None
            yield item
        except:
            print('YAHOO,内容解析错误，忽略错误项')