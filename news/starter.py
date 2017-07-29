
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from news.spiders.SMM import SmmSpider
from news.spiders.pbc import PbcSpider
from news.spiders.XINHUA import XinhuaSpider
from news.spiders.cnbcSpider import CnbcspiderSpider
from news.spiders.miitSpider import MiitspiderSpider
from news.spiders.ndrcSpider import NdrcspiderSpider
from news.spiders.yahoo import YahooSpider
import time

statt_time = time.time()
process = CrawlerProcess(get_project_settings())
process.crawl(SmmSpider)
process.crawl(XinhuaSpider)
process.crawl(PbcSpider)
process.crawl(CnbcspiderSpider)
process.crawl(MiitspiderSpider)
process.crawl(NdrcspiderSpider)
process.crawl(YahooSpider)
process.start()
end_time = time.time()
use_time = end_time - statt_time
print('爬取结束，睡眠一个周期,共用时%s' %use_time)