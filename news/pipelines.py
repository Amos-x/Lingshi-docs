# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.files import FilesPipeline
from news.items import NewsContent,NewsItem
import re
import hashlib
from scrapy.exceptions import DropItem
import datetime
import pymysql


class save_to_mongo(object):
    def __init__(self,mongo_uri,mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DB')
        )

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self,spider):
        self.client.close()

    def process_item(self,item,spider):
        try:
            if type(item) == NewsItem:
                self.db['first'].update({'url': item['url']}, {'$set': dict(item)}, True)
            if type(item) == NewsContent:
                self.db['second'].insert(dict(item))
            return item
        except:
            print('insert datadb ERROR ')

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
        if type(item) == NewsContent:
            if item['img_urls']:
                for img_url in item['img_urls']:
                    yield scrapy.Request(img_url,meta={'msite':item['msite']})

    def item_completed(self, results, item, info):
        """得到图片地址，赋值给item"""
        try:
            img_paths = [x['path'] for ok, x in results if ok]
            if type(item) == NewsContent:
                item['img_paths'] = None
                if item['content']:
                    if type(item['content']) == list:
                        item['content'] = ''.join(item['content'])
            if img_paths:
                item['img_paths'] = ','.join(img_paths)
                for x in range(len(img_paths)):
                    item['content'] = re.sub(r'<img (.*?)>','<img src="'+img_paths[x] +'">',item['content'],1)
        except:
            raise DropItem('ImagePipeline Error')
        return item

class FileDownloadPipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None):
        """自定义文件名和存储结构"""
        sha = hashlib.sha1(request.url.encode('utf-8'))
        encrypts = sha.hexdigest()
        today = datetime.datetime.today()
        year = str(today.year)
        filename = u'{0}/{1}/{2}/.png'.format(request.meta['msite'], year, encrypts)
        return filename

    def get_media_requests(self,item,info):
        if type(item) == NewsContent:
            if item['file_urls']:
                for file_url in item['file_urls']:
                    yield scrapy.Request(file_url,meta={'msite':item['msite']})

    def item_completed(self, results, item, info):
        """得到图片地址，赋值给item"""
        try:
            file_paths = [x['path'] for ok, x in results if ok]
            if type(item) == NewsContent:
                if file_paths:
                    item['file_paths'] = ','.join(file_paths)
                else:
                    item['file_paths'] = None
        except:
            raise DropItem('FilePipeline Error')
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
        tb_names = {
            '铝': 'tb_al_cn','aluminum': 'tb_al_en',
            '债券': 'tb_bonds_cn','bonds': 'tb_bonds_en',
            '铜': 'tb_cu_cn','copper': 'tb_cu_en',
            '美元': 'tb_dollar_cn','dollar': 'tb_dollar_en',
            '黄金': 'tb_gold_cn','gold': 'tb_gold_en',
            '拆借': 'tb_lending','lending rates': 'tb_lending_rates',
            '矿': 'tb_mine_cn','mine': 'tb_mine_en',
            '原油': 'tb_oil_cn','crude oil': 'tb_oil_en',
            '铅': 'tb_pb_cn','plumbun': 'tb_pb_en',
            '锌': 'tb_zn_cn','zinc': 'tb_zn_en',
        }
        if type(item) == NewsItem:
            try:
                sql = 'insert into '+tb_names[item['goal_type']]+'(mTitle,mLink,mTime,mContent,mSite) values(%s,%s,%s,%s,%s)'
                self.cursor.execute(sql,(item['title'],item['url'],item['time'],item['content'],item['msite']))
                self.db.commit()
            except:
                pass
        if type(item) == NewsContent:
            try:
                sql = "insert into tb_detail(mTitle,mSource,mLink,mContent,mSite,mImage_urls,mImage_paths,mFile_urls,mFile_path) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                self.cursor.execute(sql,(item['title'],item['source'],item['url'],item['content'],item['msite'],item['img_urls'],item['img_paths'],item['file_urls'],item['file_paths']))
                self.db.commit()
            except:
                pass
        return item