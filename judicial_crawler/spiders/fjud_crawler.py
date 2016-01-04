import scrapy
import urlparse
import time
import logging

from judicial_crawler.items import JudicialCrawlerItem
from scrapy.spiders import CrawlSpider
from scrapy.http import Request

entrance_url = "http://jirs.judicial.gov.tw/FJUD/FJUDQRY01_1.aspx" # no need any referer
list_url = "http://jirs.judicial.gov.tw/FJUD/FJUDQRY02_1.aspx" # need list url as referer
detail_url = "http://jirs.judicial.gov.tw/FJUD/FJUDQRY03_1.aspx" # need list url as referer
print_url = "http://jirs.judicial.gov.tw/FJUD/PrintFJUD03_0.aspx" # need detail url as referer
history_url = "http://jirs.judicial.gov.tw/FJUD/HISTORYSELF.aspx" # no need any referer

# 裁判書查詢 結果列表
list_url_example = "http://jirs.judicial.gov.tw/FJUD/FJUDQRY02_1.aspx?&v_court=TPS+%E6%9C%80%E9%AB%98%E6%B3%95%E9%99%A2&v_sys=M&jud_year=&jud_case=&jud_no=&jud_no_end=&jud_title=&keyword=&sdate=20150101&edate=20160101&page=2&searchkw=&jmain=&cw=0"
list_url_query = list_url + "?&v_court={v_court}&v_sys={v_sys}&jud_year=&jud_case=&jud_no=&jud_no_end=&jud_title=&keyword=&sdate={sdate}&edate={edate}&page=&searchkw=&jmain=&cw=0"
# query need: v_court, v_sys, sdate, edate

# 裁判書 詳細內容
detail_url_example = "http://jirs.judicial.gov.tw/FJUD/FJUDQRY03_1.aspx?id=1&v_court=TPS+%e6%9c%80%e9%ab%98%e6%b3%95%e9%99%a2&v_sys=M&jud_year=&jud_case=&jud_no=&jud_no_end=&jud_title=&keyword=&sdate=20150101&edate=20160101&page=1&searchkw=&jmain=&cw=0"
detail_url_query = detail_url + "?id={id}&v_court={v_court}&v_sys={v_sys}&jud_year=&jud_case=&jud_no=&jud_no_end=&jud_title=&keyword=&sdate={sdate}&edate={edate}&page=&searchkw=&jmain=&cw=0"

# id: 檢索結果編號 the judgement id of the query result (required in detail)
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

# 友善列印
print_url_example = "http://jirs.judicial.gov.tw/FJUD/PrintFJUD03_0.aspx?jrecno=104%2c%E5%8F%B0%E6%8A%97%2c937%2c20151224&v_court=TPS+%E6%9C%80%E9%AB%98%E6%B3%95%E9%99%A2&v_sys=M&jyear=104&jcase=%E5%8F%B0%E6%8A%97&jno=937&jdate=1041224&jcheck="

# jrecno: 裁判字號 + 裁判日期, format: 104,台抗,937,20151224 (required)
# v_court: same as above (required)
# v_sys: same as above (required)
# jyear: the year of the judgement (related to the html title)
# jcase: 判決字號 常用字別 (related to the html title)
# jno: 判決字號 第一欄位 (related to the html title)
# jdate: 判決日期 the date of the judgement
# jcheck: unknown

# 歷審裁判
history_url_example = "http://jirs.judicial.gov.tw/FJUD/HISTORYSELF.aspx?SwitchFrom=1&selectedOwner=H&selectedCrmyy=104&selectedCrmid=%E5%8F%B0%E9%9D%9E&selectedCrmno=000275&selectedCrtid=TPS"

# SwitchFrom: unknown
# selectedOwner: unknown
# selectedCrmyy: the year of the judgement
# selectedCrmid: 判決字號 常用字別
# selectedCrmno: 判決字號 第一欄位
# selectedCrtid: 法院名稱 英文簡寫

# 法院級別，S:最高院 H:高院 D:地院 A:最高行政 B:高等行政 P:公懲會
courts = ["TPC 司法院－刑事補償", "TPU 司法院－訴願決定", "TPJ 司法院職務法庭", "TPS 最高法院", "TPA 最高行政法院", "TPP 公務員懲戒委員會", "TPH 臺灣高等法院", "TPH 臺灣高等法院－訴願決定", "TPB 臺北高等行政法院", "TCB 臺中高等行政法院", "KSB 高雄高等行政法院", "IPC 智慧財產法院", "TCH 臺灣高等法院 臺中分院", "TNH 臺灣高等法院 臺南分院", "KSH 臺灣高等法院 高雄分院", "HLH 臺灣高等法院 花蓮分院", "TPD 臺灣臺北地方法院", "SLD 臺灣士林地方法院", "PCD 臺灣新北地方法院", "ILD 臺灣宜蘭地方法院", "KLD 臺灣基隆地方法院", "TYD 臺灣桃園地方法院", "SCD 臺灣新竹地方法院", "MLD 臺灣苗栗地方法院", "TCD 臺灣臺中地方法院", "CHD 臺灣彰化地方法院", "NTD 臺灣南投地方法院", "ULD 臺灣雲林地方法院", "CYD 臺灣嘉義地方法院", "TND 臺灣臺南地方法院", "KSD 臺灣高雄地方法院", "HLD 臺灣花蓮地方法院", "TTD 臺灣臺東地方法院", "PTD 臺灣屏東地方法院", "PHD 臺灣澎湖地方法院", "KMH 福建高等法院金門分院", "KMD 福建金門地方法院", "LCD 福建連江地方法院", "KSY 臺灣高雄少年及家事法院"]
# M:刑事 V:民事 A:行政 P:公懲 S:訴願
systems = ['M', 'V', 'A', 'P', 'S']

# default start date and end date
sdate = '19860101' # 民國 85 年 1 月 1 日 (依照公告資料庫收錄範圍之最早時間)
edate = time.strftime("%Y%m%d")

class FJUD_Crawler(CrawlSpider):
    name = "FJUD_Crawler"
    allowed_domains = ["jirs.judicial.gov.tw"]

    def __init__(self, _sdate=sdate, _edate=edate):
        sdate = _sdate
        edate = _edate
        logging.info(_sdate)
        logging.info(_edate)

    def start_requests(self):
        start_urls = [
            # entrance_url,
            # list_url_example,
            # detail_url_example,
            # print_url_example,
            # history_url_example
        ]
        for system in systems:
            for court in courts:
                start_urls.append(list_url_query.format(v_court=court, v_sys=system, sdate=sdate, edate=edate))

        requests = []
        for item in start_urls:
            # fake the referer base on the request url
            referer = ''
            if item.startswith(list_url) or item.startswith(detail_url):
                referer = list_url
            elif item.startswith(print_url):
                referer = detail_url
            requests.append(Request(url=item, headers={'Referer':referer}))
        return requests

    def parse(self, response):
        # fetch list first to get total data count
        if response.url.startswith(list_url):
            match = response.xpath('string(//body)').re(ur"本次查詢結果共(\d+)筆|共\s*(\d+)\s*筆")
            if len(match) > 0 and match[0].isdigit():
                count = int(match[0])
                logging.info(count);
                parsed = urlparse.urlparse(response.url).query
                query = urlparse.parse_qs(parsed)
                for index in range(1, count):
                    yield scrapy.Request(detail_url_query.format(id=index, v_court=query['v_court'][0], v_sys=query['v_sys'][0], sdate=query['sdate'][0], edate=query['edate'][0]), self.parse)
        elif response.url.startswith(detail_url):
            item = JudicialCrawlerItem()
            item['url'] = response.url
            item['html'] = response.body
            yield item