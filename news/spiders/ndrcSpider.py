# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import FormRequest
from scrapy.http import HtmlResponse
from news.items import NewsContent,NewsItem
from urllib.parse import urljoin
import datetime


class NdrcspiderSpider(scrapy.Spider):
    name = 'ndrcSpider'
    allowed_domains = ['"www.ndrc.gov.cn/#"']
    searchKey = ['铜', '铝', '铅', '锌', '债券', '拆借', '美元', '黄金', '原油', '矿', 'COPPER', 'mine', 'lending rates', 'bonds']

    def start_requests(self):
        print('start crawling ndrc...')
        today = str(datetime.datetime.today())[:10]
        url='http://www.ndrc.gov.cn/fgwSearch/searchResult.jsp'
        for key in self.searchKey:
            yield FormRequest(url=url,
                              formdata={'sword': key, 'type': '1', 'from': today,'to': today, 'order': '-DOCRELTIME', 'page': '1'},
                              dont_filter=True,
                              meta={'key': key,'page':1,'date': today},
                              callback=self.parse_list)


    def time_judgement(self,str_time):
        today = str(datetime.datetime.today())[:10]
        if str_time == today:
            return True

    #爬取一级新闻列表内容
    def parse_list(self, response):
        page = response.meta['page']  #当前搜索结果的所显示的页面数
        key=response.meta['key']  #当前页面的关键字
        today_date = response.meta['date']  #获取当天日期
        result_list = response.css('.list_04')
        if result_list:
            for result in result_list:
                try:
                    time = response.css('font.dateShow::text').extract_first()[3:-1]
                    if not self.time_judgement(time):
                        break
                    title = result.xpath('string(./dt/a)').extract()[0]
                    content = result.xpath('string(./dd[@class="txt"]/p[position() = 1]/a)').extract()[0]
                    link = result.xpath('./dd[@class="txt"]/p[position() = 2]/a/text()').extract()[0]
                    item = NewsItem()
                    item['title'] = self.replaceCharEntity(title[4:].strip()).replace(" ","")
                    item['content'] = self.replaceCharEntity(content.strip()).replace(" ","")
                    item['url'] = link.strip()
                    item['time'] = time.replace("- (", "").replace(")", "").strip() # 需要对日期进行修改
                    item['goal_type'] = key  # goal就是所要查找的关键词
                    item['msite'] = 'ndrc'
                    yield item
                    yield scrapy.Request(url=item['url'],
                                         callback=self.parse_content,
                                         meta={'title':item['title']})
                except:
                    print('NDRC,Homepage Error')
            # 进行换页,回调
            lat_time = result_list[-1].css('font.dateShow').extract_first()
            if self.time_judgement(lat_time):
                yield FormRequest(url='http://www.ndrc.gov.cn/fgwSearch/searchResult.jsp',
                          formdata={'sword': key, 'type': '1', 'from': today_date ,'to': today_date, 'order': '-DOCRELTIME', 'page': str(page+1)},
                          dont_filter=True, callback=self.parse_list, meta={'key': key, 'page': page+1,'date':today_date})
    #抓取新闻具体内容
    def parse_content(self, response):
        try:
            mTitle = response.meta['title']
            mSource = '国家发展和改革委员会'
            response = HtmlResponse(response.url, encoding='utf-8', body=response.body)
            if len(response.xpath('//div[@class="txt_title1 tleft"]//text()').extract()):
                mTitle = response.xpath('//div[@class="txt_title1 tleft"]//text()').extract()[0].strip()
            elif len(response.xpath('//div[@class="txt_title1"]//text()').extract()):
                mTitle = response.xpath('//div[@class="txt_title1"]//text()').extract()[0].strip()

            if len(response.xpath('//div[@id="dSourceText"]//text()').extract()):
                mSource = response.xpath('//div[@id="dSourceText"]//text()').extract()[0].strip()

            article = response.xpath('//div[@id="zoom"]|//td[@id="zoom"]').extract()
            if article:
                article = article[0]
                content = self.dispose(article).strip()
                item = NewsContent()
                item['title'] = mTitle
                item['source'] = mSource
                item['content'] = content
                item['img_urls'] = [urljoin(response.url,url) for url in response.css('#zoom img::attr(src)').extract()]
                item['file_urls'] = None
                item['url'] = response.url
                yield item
        except:
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
        delete_tag_begin = re.compile('<(div|DIV|a|FONT)[^>]*>')  # 去除标签开头
        delete_tag_end = re.compile('<(\/div|\/DIV|\/a)>')  # 去除标签结尾
        # 去除标签内的属性
        clear_tag = re.compile(
            '<(p|font|h1|h2|h3|h4|strong|dd|dt|dl|form|li|ul|hr|span|tr|td|tbody|table)(\s+)([^>])*>')
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



