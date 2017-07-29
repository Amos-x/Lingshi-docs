# -*- coding: utf-8 -*-
import json
import scrapy
import datetime
from scrapy import Selector
from news.items import NewsItem, NewsContent
import requests


class CnbcspiderSpider(scrapy.Spider):
    name = 'cnbcSpider'

    def start_requests(self):
        print('start crawking cnbc...')
        keywords =['dollar','lending rates','bonds','cpooer']
        for keyword in keywords:
            url = ('http://search.cnbc.com/rs/search/view.html?partnerId=2000&keywords='
                   + keyword + '&sort=date&source=CNBC.com,Today&pubtime=7&pubfreq=d&page=1')
            yield scrapy.Request(url,callback=self.next_parse,dont_filter=True,meta={'goal':keyword,'page':1})

    def next_parse(self,response):
        item = NewsItem()
        searchResultCards = response.xpath('//div[@class="SearchResultCard"]')
        for result in searchResultCards:
            try:
                mLink = result.xpath('./h3/a/@href').extract()[0]
                if 'video' in mLink:
                    continue
                item['url'] = mLink
                item['title'] = result.xpath('./h3//text()').extract()[0]
                item['time'] = datetime.datetime.now().strftime('%Y-%m-%d')
                item['content'] = result.xpath('./p//text()').extract()[0]
                item['goal_type'] = response.meta['goal']
                item['msite'] = 'cnbc'
                source = result.css('span.source').extract_first()[8:]
                yield item
                yield scrapy.Request(mLink, callback=self.parse, meta={'mLink': mLink,'source':source})
            except:
                print('CNBC，Homepage Error')
        #翻页
        if searchResultCards:
            url = response.url[0:-1] + str(response.meta['page']+1)
            yield scrapy.Request(url,callback=self.next_parse,meta={'goal':response.meta['goal'],'page':response.meta['page']+1})

    def parse(self, response):
        try:
            item = NewsContent()
            item['url'] = response.meta['mLink']
            item['title'] = response.xpath('//h1[@class="title"]//text()').extract()[0]
            item['source'] = response.meta['source']
            item['img_urls'] = response.xpath('//div[@id="article_body"]//img/@src').extract()
            item['msite'] = 'cnbc'
            item['file_urls'] = None
            # 获取表格数据
            tableList = response.xpath('//div[@id="article_body"]//table')
            if len(tableList) > 0:  #判断是否需要表格
                reqList = []
                trDataList = response.xpath('//tbody/tr/@data-table-chart-symbol').extract()
                for i in trDataList:
                    flag = 0
                    for j in reqList:
                        if i == j:
                            flag = 1
                            break
                    if flag == 0:
                        reqList.append(i)
                tempUrl = "http://quote.cnbc.com/quote-html-webservice/quote.htm?partnerId=2&requestMethod=quick&exthrs=1&noform=1&fund=1&output=jsonp&symbols="
                for i in reqList:
                    tempUrl += i
                    if i != reqList[-1]:
                        tempUrl += '|'
                tempUrl += "&callback=quoteHandler1"
                res = requests.get(tempUrl)
                results = json.loads(res.text[14:-1])['QuickQuoteResult']['QuickQuote']
                item['content'] = self._parse_text(response, results)
                yield item
            else:
                item['content'] = self._parse_text(response=response)
                yield item
        except:
            print('CNBC,Content Error')

    def _parse_text(self,response,results=None):
        """解析正文"""
        try:
            mContent = []
            contentList = response.xpath(
                '//div[@id="article_deck"]//h4 | //div[@id="article_deck"]//p | //div[@id="article_body"]//p | //div[@id="article_body"]//table | //div[@id="article_body"]//h4 | //div[@id="article_body"]//img').extract()
            for i in contentList:
                if i[1] == 'h':
                    mContent.append("<h4>" + Selector(text=i).xpath('//text()').extract()[0] + "</h4>")
                elif i[1] == 'p':
                    strTemp = '<p>'
                    pStr = Selector(text=i).xpath('//text()').extract()
                    for i in pStr:
                        if i != '*':
                            strTemp += i
                        else:
                            break
                    mContent.append(strTemp + "</p>")
                elif i[1] == 't':
                    strTemp = '<table><thead><tr>'
                    strTemp += '<th>Symbol</th><th>Price</th><th>Change</th><th>%Change</th></tr></thead><tbody>'
                    trList = Selector(text=i).xpath('//tbody/tr/td[1]//text()').extract()
                    for j in trList:
                        strTemp += '<tr><td>' + j + '</td>'
                        for k in results:
                            if j == k['shortName']:
                                strTemp += '<td>' + k['last'] + '</td>'
                                strTemp += '<td>' + k['change'] + '</td>'
                                strTemp += '<td>' + k['change_pct'] + '</td>'
                                break
                        strTemp += '</tr>'
                    strTemp += '</tbody></table>'
                    mContent.append(strTemp)
                elif i[1] == 'i':
                    imgSrc = Selector(text=i).xpath('//img/@src').extract()[0]
                    mContent.append('<p><img src=' + imgSrc + '></p>')
            return mContent
        except:
            print('CNBC,content function Error')





