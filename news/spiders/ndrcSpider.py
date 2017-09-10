# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import FormRequest
from scrapy.http import HtmlResponse
from news.items import AllItem
from urllib.parse import urljoin
import math
import datetime


class NdrcspiderSpider(scrapy.Spider):
    name = 'ndrcSpider'
    searchKey = ['有色金属','铜', '铝', '铅', '锌', '债券', '拆借', '美元', '黄金', '原油', '矿']
    fromday = datetime.datetime.now().strftime('%Y.%m.%d')  #日期必须匹配%Y.%m.%d，不能为%Y-%m-%d
    today = datetime.datetime.now().strftime('%Y.%m.%d')    #日期必须匹配%Y.%m.%d，不能为%Y-%m-%d
    url = 'http://www.ndrc.gov.cn/fgwSearch/searchResult.jsp'

    def start_requests(self):
        print('start crawling ndrc...')
        for keyword in self.searchKey:
            yield FormRequest(url=self.url,
                              formdata={'sword': keyword, 'type': '1', 'from': '','to': '',
                                        'order': '-DOCRELTIME','pageSize':'20'},
                              dont_filter=True,
                              meta={'keyword': keyword,'page':1},
                              callback=self.parse_list)

    def _time_judgment(self, str_time):
        now = datetime.datetime.now().strftime('%Y.%m.%d')
        if str_time == now:
            return True

    def parse_list(self, response):
        result_list = response.css('dl.list_04')
        if result_list:
            for result in result_list:
                try:
                    time = result.css('font.dateShow::text').extract_first()
                    str_time = re.sub(r'[-() ]','',time)
                    if not self._time_judgment(str_time):
                        break
                    item = AllItem()
                    item['title'] = re.sub(r'<.*?>','',result.css('dt a::attr(title)').extract_first())
                    item['url'] = result.css('dt a::attr(href)').extract_first()
                    item['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item['classify'] = response.meta['keyword']
                    item['source'] = '国家发展和改革委员会'
                    item['display'] = '1'
                    item['msite'] = 'ndrc'
                    abstract = ''.join(result.css('dd.txt p')[0].css('a::text').extract()).strip()
                    item['abstract'] = re.sub(r'<.*?>','',abstract)
                    item['home_img_url'] = None
                    yield scrapy.Request(url=item['url'],
                                         callback=self.parse_content,
                                         meta={'item':item})
                except Exception as e:
                    print(e)
                    print('NDRC,Homepage Error')

    #抓取新闻具体内容
    def parse_content(self, response):
        try:
            item = response.meta['item']
            # response = HtmlResponse(response.url, encoding='utf-8', body=response.body)
            # if len(response.xpath('//div[@class="txt_title1 tleft"]//text()').extract()):
            #     mTitle = response.xpath('//div[@class="txt_title1 tleft"]//text()').extract()[0].strip()
            # elif len(response.xpath('//div[@class="txt_title1"]//text()').extract()):
            #     mTitle = response.xpath('//div[@class="txt_title1"]//text()').extract()[0].strip()
            #
            # if len(response.xpath('//div[@id="dSourceText"]//text()').extract()):
            #     mSource = response.xpath('//div[@id="dSourceText"]//text()').extract()[0].strip()

            # article = response.xpath('//div[@id="zoom"]|//td[@id="zoom"]').extract()
            article = response.css('#zoom p').extract()
            if article:
                # article = article[0]
                # content = self.dispose(article).strip()
                item['content'] = ''.join(article)
                content_img_urls = [urljoin(response.url,url) for url in response.css('#zoom img::attr(src)').extract()]
                item['content_img_urls'] = (content_img_urls if content_img_urls else None)
                yield item

        except Exception as e:
            print(e)
            print('NDRC，Content Error')

    #去除html中特殊的符号
    def replaceCharEntity(self,htmlstr):
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }
        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()  # entity全称，如>
            key = sz.group('name')  # 去除&;后entity,如>为gt
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                # 以空串代替
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

    #正则表达式去除标签和内容
    def dispose(self,content):  # content是爬去的正文内容,是字符串类型
        # 正则表达式
        # re.compile() 可以把正则表达式编译成一个正则表达式对象.
        delete_tag_begin = re.compile('<\s*(div|DIV|a|span)(\s*)[^>]*>')  # 去除标签开头
        delete_tag_end = re.compile('<\s*(\/div|\/DIV|\/a|\/span)\s*>')  # 去除标签结尾
        # 去除标签内的属性
        clear_tag = re.compile(
            '<\s*(p|font|FONT|h1|h2|h3|h4|h5|h6|strong|dd|dt|dl|form|li|ul|hr|tr|tt|td|th|thead|tbody|table|tfoot|b|br|i|u|time)(\s+)([^>])*>')
        # 去除<style>标签和内容
        delete_detail = re.compile('<\s*(style|script)([^>])*>([\s\S]*)<\s*/(style|script)([^>])*>')
        # 去除注释里面的内容
        delete_note = re.compile('<!--([\s\S]*?)-->')
        # 用正则表达式匹配清洗数据
        content = delete_detail.sub("", content)
        content = delete_tag_begin.sub("", content)
        content = delete_tag_end.sub("", content)
        content = clear_tag.sub('<' + r'\1' + '>', content)  # 清楚属性,只保留标签
        content = delete_note.sub("", content)
        # 清洗html里特殊的符号
        content = self.replaceCharEntity(content)
        # 替换文本中出现的空格
        content = content.replace(" ", "")

        return content  # 返回正文



