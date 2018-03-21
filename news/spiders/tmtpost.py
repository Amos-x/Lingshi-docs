# -*- coding: utf-8 -*-
import json
import scrapy
import time

from news.items import AllItem

class TmtpostSpider(scrapy.Spider):
    name = 'tmtpost'
    url = 'http://www.tmtpost.com/ajax/common/get?url=%2Fv1%2Flists%2Fhome&data=offset%3D%26limit%3D15%26post_fields%3Dtags%3Baccess%26tag_special_background_image_size%3D%5B%22640_256%22%5D%26auction_background_image_size%3D%5B%22640_256%22%5D%26ad_image_size%3D%5B%22640_256%22%5D%26focus_post_image_size%3D%5B%22640_256%22%5D%26homepage_universal_article_group_image_size%3D%5B%22210_240%22%5D%26special_column_post_image_size%3D%5B%22210_240%22%5D%26homepage_tag_group_image_size%3D%5B%22210_240%22%5D%26homepage_author_group_image_size%3D%5B%22210_240%22%5D%26thumb_image_size%3D%5B%22200_150%22%5D'

    def start_requests(self):
        yield scrapy.Request(self.url,callback=self.next_parse,dont_filter=True,headers={'X-Requested-With':'XMLHttpRequest'})

    def _time_judgment(self,str_time):
        now = time.localtime(time.time())
        date = time.strftime('%Y-%m-%d',now)
        if str_time == date:
            return True

    def next_parse(self,response):
        try:
            results = json.loads(response.text)['data']
            for group in results:
                if 'time_published' in group.keys():
                    item = AllItem()
                    str_time = time.strftime('%Y-%m-%d',time.localtime(int(group['time_published'])))
                    # if not self._time_judgment(str_time):
                    #     continue
                    item['title'] = group['title']
                    item['url'] = group['short_url']
                    item['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(group['time_published'])))
                    item['msite'] = 'tmtpost'
                    item['source'] = group['authors'][0]['username']
                    item['news_type'] = '科技'
                    tags = []
                    for x in group['tags']:
                        tags.append(x['tag'])
                    item['classify'] = (' '.join(tags) if tags else None)
                    item['display'] = '1'
                    item['abstract'] = group['summary']
                    item['home_img_url'] = group['thumb_image']['200_150'][0]['url']
                    yield scrapy.Request(item['url'],callback=self.parse,meta={'item':item})
        except Exception as e:
            print(e)
            print('tmtpost,Home-error')

    def parse(self, response):
        try:
            item = response.meta['item']
            content = response.css('article div.inner > *').extract()
            if content:
                item['content'] = ''.join(content[:-4])
                content_img_urls = response.css('article div.inner img::attr(src)').extract()
                item['content_img_urls'] = (content_img_urls[:-1] if content_img_urls[:-1] else None)
                yield item
        except Exception as e:
            print(e)
            print('tmtpost,content-error')
