import scrapy

from judicial_crawler.items import JudicialCrawlerItem
from scrapy.spiders import CrawlSpider
from scrapy.http import Request

entrance_url = "http://jirs.judicial.gov.tw/FJUD/FJUDQRY01_1.aspx" # no need any referer
list_url = "http://jirs.judicial.gov.tw/FJUD/FJUDQRY02_1.aspx" # need entrance url as referer
detail_url = "http://jirs.judicial.gov.tw/FJUD/FJUDQRY03_1.aspx" # need list url as referer
print_url = "http://jirs.judicial.gov.tw/FJUD/PrintFJUD03_0.aspx" # need detail url as referer

# "http://jirs.judicial.gov.tw/FJUD/FJUDQRY03_1.aspx?id=1&v_court=TPS+%e6%9c%80%e9%ab%98%e6%b3%95%e9%99%a2&v_sys=M&jud_year=&jud_case=&jud_no=&jud_no_end=&jud_title=&keyword=&sdate=20150101&edate=20160101&page=1&searchkw=&jmain=&cw=0",
# "http://jirs.judicial.gov.tw/FJUD/FJUDQRY03_1.aspx?id=201&v_court=TPS+%e6%9c%80%e9%ab%98%e6%b3%95%e9%99%a2&v_sys=M&jud_year=&jud_case=&jud_no=&jud_no_end=&jud_title=&keyword=&sdate=20150101&edate=20160101&page=11&searchkw=&jmain=&cw=0",
# "http://jirs.judicial.gov.tw/FJUD/FJUDQRY02_1.aspx?&v_court=TPS+%E6%9C%80%E9%AB%98%E6%B3%95%E9%99%A2&v_sys=M&jud_year=&jud_case=&jud_no=&jud_no_end=&jud_title=&keyword=&sdate=20150101&edate=20160101&page=2&searchkw=&jmain=&cw=0",

# id: the id in the query result (required in detail)
# v_court: 法院名稱 the court name (required in list)
# v_sys: 裁判類別 the law system (required in list)
# jud_year: 判決字號 年份 the year of the judgement
# jud_case: 判決字號 常用字別 the case name of the judgement
# jud_no: 判決字號 第一欄位 (第？) the first number of the judgement
# jud_no_end: 判決字號 第二欄位 ( - ？號) the second number of the judgement
# jud_title: 判決案由 the title of the judgement
# keyword: 全文檢索語詞 the full-text search keyword
# sdate: 判決日期 開始日期 the start date of the query, format: YYYYMMDD
# edate: 判決日期 開始日期 the start date of the query, format: YYYYMMDD
# page: 檢索結果分頁 the page of the query result
# searchkw: unknown
# jmain: 裁判主文 the main section search keyword
# cw: unknown

class FJUD_Crawler(CrawlSpider):
    name = "FJUD_Crawler"
    allowed_domains = ["jirs.judicial.gov.tw"]

    def start_requests(self):
        start_urls = [
            "http://jirs.judicial.gov.tw/FJUD/PrintFJUD03_0.aspx?jrecno=104%2c%E5%8F%B0%E6%8A%97%2c937%2c20151224&v_court=TPS+%E6%9C%80%E9%AB%98%E6%B3%95%E9%99%A2&v_sys=M&jyear=104&jcase=%E5%8F%B0%E6%8A%97&jno=937&jdate=1041224&jcheck="
        ]
        requests = []
        for item in start_urls:
          requests.append(Request(url=item, headers={'Referer':detail_url}))
        return requests

    def parse(self, response):
        item = JudicialCrawlerItem()
        item['url'] = response.url
        item['html'] = response.body
        yield item