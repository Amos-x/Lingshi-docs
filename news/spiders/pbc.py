# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from news.items import NewsItem,NewsContent
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class PbcSpider(scrapy.Spider):
    name = "pbc"
    # allowed_domains = [".pbc.gov.cn"]
    keywords = ['铜', '铝', '铅', '锌', '债券', '拆借', '美元', '黄金', '原油', '矿', 'copper', 'mine', 'lending rates', 'bonds']

    def __init__(self):
        scrapy.Spider.__init__(self)
        service_args = ['--disk-cache=true']
        self.browser = webdriver.PhantomJS(service_args=service_args)
        self.wait = WebDriverWait(self.browser, 10)
        self.browser.maximize_window()

    def _get_input_window(self):
        self.input_window = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.serch_text')))
        self.button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.serch_submit')))

    def _time_judgment(self,str_time):
        now = time.localtime(time.time())
        date = time.strftime('%Y-%m-%d',now)
        if str_time == date:
            return True

    def spider_close(self):
        self.browser.quit()

    def start_requests(self):
        yield scrapy.Request('http://wzdig.pbc.gov.cn:8080/dig/ui/search.action',callback=self.parse,dont_filter=True)

    def parse(self, response):
        print('satrt crawling pbc...')
        for keyword in self.keywords:
            try:
                self.browser.get(response.url)
                self._get_input_window()
                self.input_window.clear()
                self.input_window.send_keys(keyword)
                self.button.click()
                html = self.browser.page_source
                soup = BeautifulSoup(html, 'lxml')
                cen_list = soup.select('div.cen_list ul')
                for group in cen_list:
                    str_time = group.select('li')[0].get_text().strip()[-10:]
                    if not self._time_judgment(str_time):
                        break
                    item = NewsItem()
                    item['title'] = group.select('h3 a')[0].get_text()
                    item['url'] = group.select('h3 a')[0].get('href')
                    item['time'] = str_time
                    item['content'] = group.select('p')[0].get_text()
                    item['msite'] = 'pbc'
                    item['goal_type'] = keyword
                    item['img_urls'] = None
                    yield scrapy.Request(item['url'], callback=self.last_parse,meta={'newsitem':item})
            except:
                print('PBC,Homepage Error')

    def last_parse(self, response):
        try:
            item2 = NewsContent()
            if 'html' in response.url:
                self.browser.get(response.url)
                html2 = self.browser.page_source
                if html2:
                    soup = BeautifulSoup(html2, 'lxml')
                    if 'pbc.gov.cn' in response.url:
                        item2['title'] = soup.title.get_text().strip()
                        source = soup.select('span#laiyuan')
                        if source:
                            item2['source'] = '中国人民银行' + source[0].get_text()
                        else:
                            item2['source'] = '中国人民银行'
                        item2['url'] = response.url
                        item2['msite'] = 'pbc'
                        content = soup.select('p')
                        if content:
                            item2['content'] = [str(p) for p in content[0].parent.select('p')]
                        else:
                            item2['content'] = None
                        img = soup.select('div#zoom p img')
                        if img:
                            item2['img_urls'] = [image.get('src') for image in img]
                        else:
                            item2['img_urls'] = None
                        file = soup.select('div#zoom p a')
                        if file:
                            item2['file_urls'] = ['/'.join(response.url.split('/')[:3]) + x.get('href') for x in file if x.get('href')]
                        else:
                            item2['file_urls'] = None
                        newsitem = response.meta['newsitem']
                        yield newsitem
                        yield item2
        except:
            print('PBC,Content Error')

