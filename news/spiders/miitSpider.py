# -*- coding: utf-8 -*-
import re
import scrapy
import time
from scrapy import FormRequest
from news.items import AllItem
import json
from urllib.request import urljoin


class MiitspiderSpider(scrapy.Spider):
    name = 'miitSpider'
    start_urls = 'http://searchweb.miit.gov.cn/search/search'

    def start_requests(self):
        print('start crawling miit...')
        keywords = ['铜', '铝', '铅', '锌', '债券', '拆借', '美元', '黄金', '原油', '矿','有色金属']
        for keyword in keywords:
            yield FormRequest(url=self.start_urls,
                              formdata={'pageSize': '10', 'pageNow': '1', 'sortFlag': '-1', 'sortKey': 'showTime',
                                        'sortType': '1', 'urls': 'http://www.miit.gov.cn/', 'fullText': keyword},
                              dont_filter=True,
                              meta={'goal': keyword},
                              callback=self.next_parse)

    def _time_judgment(self,str_time):
        now = time.localtime(time.time())
        date = time.strftime('%Y-%m-%d',now)
        if str_time == date:
            return True

    def next_parse(self, response):
        new_list = json.loads(response.text)['array']
        page_now = int(json.loads(response.text)['pageNow'])
        for news in new_list:
            try:
                if not self._time_judgment(news['showTime']):
                    break
                item = AllItem()
                item['title'] = news['name']
                item['url'] = news['url']
                item['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                item['abstract'] = re.sub(r'<.*?>','',news['summaries'])
                item['msite'] = 'miit'
                item['classify'] = response.meta['goal']
                item['display'] = '1'
                item['home_img_url'] = None
                yield scrapy.Request(news['url'],callback=self.parse,meta={'item':item})
            except:
                print('MIIT,Homepage Error')
        if self._time_judgment(new_list[-1]['showTime']):
            yield FormRequest(url=self.start_urls,dont_filter=True,
                              formdata={'pageSize': '10', 'pageNow': str(page_now + 1), 'sortFlag': '-1', 'sortKey': 'showTime',
                                        'sortType': '1', 'urls': 'http://www.miit.gov.cn/', 'fullText': response.meta['keyword']},
                              callback=self.next_parse)
                              
    def parse(self, response):
        try:
            item = response.meta['item']
            # content = response.text
            # title = response.xpath('/html/head/title/text()').extract()[0]
            # pattern = re.compile(
            #     r'<!--start component 文档组件[\((](new|正文|文件发布正文)[\))]-->([\s\S]*?)<!--end component 文档组件[\((](new|正文|文件发布正文)[\))]-->')
            # moudle = pattern.findall(content)
            # content = self.dispose("".join(moudle[len(moudle) - 1][1])).strip()
            # content = content.replace(title, "")
            # ioprint = re.compile('<a.*?onclick.*?【打印】<\/a>')
            # ioclose = re.compile('<a.*?onclick.*?【关闭】<\/a>')
            # content = re.sub(ioprint, "", content)
            # content = re.sub(ioclose, "", content)
            # doc_pattern = re.compile('<a.*?href="(.*?)">.*?<\/a>')
            # file_urls = doc_pattern.findall(content)
            # if "【打印】" or "【关闭】" in content:
            #     content = content.replace("【打印】", "")
            #     content = content.replace("【关闭】", "")
            # content = "<p>" + content + "</p>"
            try:
                source = response.css('div.cinfo.center span::text').extract()[1][4:]
            except:
                source = None
            item['source'] = (source if source else "工信部")
            content = response.css('div.ccontent.center p').extract()
            if not content:
                return
            item['content'] = ''.join(content)
            content_img_urls = response.css('div.ccontent.center p img::attr(src)').extract()
            if content_img_urls:
                item['content_img_urls'] = [urljoin(response.url,img_url) for img_url in content_img_urls]
            else:
                item['content_img_urls'] = None
            # if file_urls:
            #     files = []
            #     for x in file_urls:
            #         if ''.join(x.split('/')[:2]) =='....':
            #               files.append(x)
            #     item['file_urls'] = [urljoin(response.url,file_url) for file_url in files]
            # else:
            #     item['file_urls'] = None
            yield item
        except Exception as e:
            print(e)
            print('MIIT,Content Error')

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

    '''
    def dispose(self,article):  # article是爬去的正文内容,是字符串类型
        # 正则表达式
        # re.compile() 可以把正则表达式编译成一个正则表达式对象.
        delete_tag_begin = re.compile('<(div|DIV|a|FONT)[^>]*>')  # 去除标签开头
        delete_tag_end = re.compile('<(\/div|\/DIV|\/a|\/FONT)>')  # 去除标签结尾
        # 去除标签内的属性
        clear_tag = re.compile(
            '<(p|font|h1|h2|h3|h4|strong|dd|dt|dl|form|li|ul|hr|span|tr|td|tbody|table)(\s+)([^>])*>')
        # 去除<style>标签和内容
        delete_detail = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>')
        delete_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>')
        # delete_detail = re.compile('<\s*(style|script)([^>])*>([\s\S]*)<\s*/(style|script)([^>])*>')
        delete_note = re.compile('<!--([\s\S]*?)-->')
        # 用正则表达式匹配清洗数据
        content_delete_content = delete_detail.sub("", article)
        content_delete_tag_begin = delete_tag_begin.sub("", content_delete_content)
        content_delete_tag_end = delete_tag_end.sub("", content_delete_tag_begin)
        content_claer_tag = clear_tag.sub('<' + r'\1' + '>', content_delete_tag_end)  # 清楚属性,只保留标签
        content_delete_note = delete_note.sub("", content_claer_tag)
        # 清洗html里特殊的符号
        
        
        content_delete_note = self.replaceCharEntity(content_delete_note)
        content_delete_note = delete_script.sub("", content_delete_note)
        return content_delete_note  # 返回正文 
    '''
    def dispose(self,article):  # article是爬去的正文内容,是字符串类型
        # 正则表达式
        # re.compile() 可以把正则表达式编译成一个正则表达式对象.
        delete_tag_begin = re.compile('<(div|DIV|FONT)[^>]*>')  # 去除标签开头
        delete_tag_end = re.compile('<(\/div|\/DIV|\/FONT)>')  # 去除标签结尾
        # 去除标签内的属性
        clear_tag = re.compile(
            '<(p|font|h1|h2|h3|h4|strong|dd|dt|dl|form|li|ul|hr|span|tr|td|tbody|table)(\s+)([^>])*>')
        # 去除<style>标签和内容
        delete_detail = re.compile('<\s*(style|script)([^>])*>([\s\S]*?)<\s*/(style|script)([^>])*>')
        delete_note = re.compile('<!--([\s\S]*?)-->')
        # 用正则表达式匹配清洗数据
        content_delete_content = delete_detail.sub("", article)
        content_delete_tag_begin = delete_tag_begin.sub("", content_delete_content)
        content_delete_tag_end = delete_tag_end.sub("", content_delete_tag_begin)
        content_claer_tag = clear_tag.sub('<' + r'\1' + '>', content_delete_tag_end)  # 清楚属性,只保留标签
        content_delete_note = delete_note.sub("", content_claer_tag)
        # 清洗html里特殊的符号
        '''
        content_delete_content.replace('&nbsp;', ' ')
        content_delete_content.replace('&gt;', '>')
        content_delete_content.replace('&lt;', '<')
        '''
        content_delete_note = self.replaceCharEntity(content_delete_note)
        return content_delete_note  # 返回正文




