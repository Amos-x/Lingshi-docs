# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class AllItem(scrapy.Item):
    title = scrapy.Field()                          # 标题
    url = scrapy.Field()                            # 网址
    time = scrapy.Field()                           # 时间
    msite = scrapy.Field()                          # 网站名
    source = scrapy.Field()                         # 来源
    classify = scrapy.Field()                       # 分类
    display = scrapy.Field()                        # 是否展示
    abstract = scrapy.Field()                       # 摘要（150字纯文本）
    content = scrapy.Field()                        # 内容
    home_img_url = scrapy.Field()                   # 列表图片原网址
    home_img_path = scrapy.Field()                  # 列表图片保存地址
    content_img_urls = scrapy.Field()               # 内容图片原网址
    content_img_paths = scrapy.Field()              # 内容图片保存地址
    news_type = scrapy.Field()                      # 新闻大类型

