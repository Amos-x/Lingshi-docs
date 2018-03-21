# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
import re
import hashlib
from scrapy.exceptions import DropItem
import datetime
import pymysql


class ImageDownloadPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        """自定义文件名和存储结构"""
        sha = hashlib.sha1(request.url.encode('utf-8'))
        encrypts = sha.hexdigest()
        today = datetime.datetime.today()
        year = str(today.year)
        month = str(today.month)
        day = str(today.day)
        filename = u'{0}/{1}/{2}/{3}/{4}.png'.format(request.meta['msite'], year, month, day, encrypts)
        return filename

    def get_media_requests(self,item,info):
        if item['home_img_url']:
            yield scrapy.Request(item['home_img_url'].strip(),meta={'msite':item['msite']})
        if item['content_img_urls']:
            for img_url in item['content_img_urls']:
                yield scrapy.Request(img_url.strip(),meta={'msite':item['msite']})
            item['content_img_urls'] = ','.join(item['content_img_urls'])

    def item_completed(self, results, item, info):
        """
        得到图片地址，将地址赋值给对应item，并将内容中的图片链接替换成图片地址
        """
        try:
            img_paths = ['http://eip.hkmtl.com/images/'+ x['path'] for ok, x in results if ok]
            item['home_img_path'] = None
            item['content_img_paths'] = None
            if img_paths:
                item['content'] = re.sub(r'<img .*?>', '<img src="replace">', item['content'])
                if item['home_img_url']:
                    item['home_img_path'] = img_paths[0]
                    if item['content_img_urls']:
                        item['content_img_paths'] = ','.join(img_paths[1:])
                        for img_path in img_paths[1:]:
                            item['content'] = re.sub(r'<img src="replace">','<img src="'+img_path+'">',item['content'],1)
                else:
                    if item['content_img_urls']:
                        item['content_img_paths'] = ','.join(img_paths)
                        for img_path in img_paths:
                            item['content'] = re.sub(r'<img src="replace">', '<img src="' + img_path + '">',item['content'], 1)
        except Exception as e:
            print('图片管道错误')
            print(e)
            raise DropItem('ImagePipeline Error')
        return item


class ContentClean(object):
    def process_item(self,item,spider):
        content = item['content']
        item['content'] = re.sub(r'<script.*?</script>','',content)
        return item

class save_to_mysql(object):
    def __init__(self,mysql_host,mysql_username,mysql_password,mysql_db,mysql_port):
        self.host = mysql_host
        self.port = mysql_port
        self.username = mysql_username
        self.password = mysql_password
        self.db_name = mysql_db

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_username=crawler.settings.get('MYSQL_USERNAME'),
            mysql_password=crawler.settings.get('MYSQL_PASSWORD'),
            mysql_db=crawler.settings.get('MYSQL_DB'),
            mysql_port = crawler.settings.get('MYSQL_PORT')
        )

    def open_spider(self,spider):
        self.db = pymysql.connect(host=self.host,port=self.port,user=self.username,passwd=self.password,db=self.db_name,charset='utf8')
        self.cursor = self.db.cursor()

    def close_spider(self,spider):
        self.db.close()

    def process_item(self,item,spider):
        try:
            sql = 'insert into news_item(id,title,url,time,msite,source,classify,display,abstract,content,home_img_url,home_img_path,content_img_urls,content_img_paths,type) values(NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.cursor.execute(sql,(item['title'],item['url'],item['time'],item['msite'],item['source'],
                                     item['classify'],item['display'],item['abstract'],item['content'],
                                     item['home_img_url'],item['home_img_path'],item['content_img_urls'],
                                     item['content_img_paths'],item['news_type']))
            self.db.commit()
        except Exception as e:
            print(item)
            print(e)
            print('插入数据库错误')
        return item