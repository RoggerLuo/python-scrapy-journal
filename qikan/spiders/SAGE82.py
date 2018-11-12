# -*- coding: utf-8 -*-
import scrapy
from qikan.items import QikanItem
import re
import time
from .config import Config,postItemWithPdf,postItem



class Sage82Spider(scrapy.Spider):
    name = 'SAGE82'
    # url = input('请输入网址：')
    start_urls = ['http://journals.sagepub.com/toc/aan/current']
    base_url = 'http://journals.sagepub.com/toc/aan/current'

    def parse(self, response):
        # 文章url
        hrefs = response.xpath("//div[@class='art_title linkable']/a[@class='ref nowrap']/@href").extract()
        volume = response.xpath("//div[@class='pager issueBookNavPager']/span[@class='journalNavCenterTd']/div[@class='journalNavTitle']/text()").extract()[0]

        for i in range(len(hrefs)):
            yield scrapy.Request(url=self.base_url + hrefs[i],meta={'annualVolume':volume}, callback=self.parse2)

    def parse2(self, response):
        item = QikanItem()
        # 文章题目
        item['title'] = ''
        titles = response.xpath("//div[@class='hlFld-Title']//div[@class='publicationContentTitle']//h1").extract()
        pat = re.compile('<[^>]+>', re.S)
        for title in titles:
            item['title'] = item['title'] + pat.sub('', title).strip()
        # item['title'] = response.xpath("//div[@class='hlFld-Title']//div[@class='publicationContentTitle']//h1/text()").extract()[0].strip()
        # # titles = response.xpath("//h2[@class='citation__title']/text()").extract()
        # pat = re.compile('<[^>]+>', re.S)
        # 作者
        item['author'] = ''
        # 通讯作者
        # 通讯作者单位
        aus = []
        if response.xpath("//div[@class='header']/a[@class='entryAuthor']").extract():
            authors = response.xpath("//div[@class='header']/a[@class='entryAuthor']").extract()
            for author in authors:
                item['author'] = item['author'] + pat.sub('', author).strip() + ","
        else:
            item['author'] = 'NULL'


        if response.xpath("//div[@class='hlFld-ContribAuthor']/span[@class='NLM_contrib-group']/div[@class='artice-info-affiliation']/text()").extract():
            item['authorAffiliation'] = response.xpath("//div[@class='hlFld-ContribAuthor']/span[@class='NLM_contrib-group']/div[@class='artice-info-affiliation']/text()").extract()[0]
        elif response.xpath("//div[@class='hlFld-ContribAuthor']/div[@class='artice-info-affiliation'][1]/text()").extract():
            item['authorAffiliation'] = response.xpath("//div[@class='hlFld-ContribAuthor']/div[@class='artice-info-affiliation'][1]/text()").extract()[0]
        elif response.xpath("//div[@class='artice-notes']//corresp//text()").extract():
            item['authorAffiliation'] = response.xpath("//div[@class='artice-notes']//corresp//text()").extract()[0].replace('Email:','')
        else:
            item['authorAffiliation'] = 'NULL'
        item['authorAffiliation'] = item['authorAffiliation'].replace('\n','').replace('\r','').replace('\t','').replace('                ',' ')
        # print(item['authorAffiliation'])

        item['correspongdingauthorEmail'] = ''
        if response.xpath("//a[@class='email']/span[@class='nobrWithWbr']").extract():
            correspongdingauthorEmails = response.xpath("//a[@class='email']/span[@class='nobrWithWbr']").extract()
            for correspongdingauthorEmail in correspongdingauthorEmails:
                item['correspongdingauthorEmail'] = item['correspongdingauthorEmail'] + pat.sub('', correspongdingauthorEmail).strip() + '||'
        else:
            item['correspongdingauthorEmail'] = 'NULL'

        # item['correspongdingauthorEmail'] = response.xpath("//a[@class='email']/span[@class='nobrWithWbr']").extract()
        if response.xpath("//div[@class='hlFld-ContribAuthor']/span[@class='contribDegrees'][1]/div[@class='authorLayer']/div[@class='header']/a[@class='entryAuthor']/text()").extract():
            item['correspongdingauthor'] = response.xpath("//div[@class='hlFld-ContribAuthor']/span[@class='contribDegrees'][1]/div[@class='authorLayer']/div[@class='header']/a[@class='entryAuthor']/text()").extract()[0] + '||'
        else:
            item['correspongdingauthor'] = 'NULL'
        #         # DOI号
        if item['correspongdingauthor'] == 'NULL':
            item['correspongdingauthor'] = 'NULL'
        elif item['correspongdingauthor'] != '':
            correspongdingau = item['correspongdingauthor'].split("||")
            correspongdingEm = item['correspongdingauthorEmail'].split("||")
            item['correspongdingauthor'] = ''
            for i in range(len(correspongdingau)):
                if correspongdingau[i] != '':
                    item['correspongdingauthor'] += '(' + correspongdingau[i] + ',' + correspongdingEm[i] + '),'
        else:
            item['correspongdingauthor'] = 'NULL'
        # print(item['correspongdingauthor'])

        item['DOI'] = response.xpath("//div[@class='widget-body body body-none  body-compact-all']/div[@class='doiWidgetContainer']/a[@class='doiWidgetLink']/text()").extract()[0]
        #         # print(item['DOI'])
        #         # 没有关键词

        item['keyword'] = ''
        if response.xpath("//div[@class='hlFld-KeywordText']/kwd-group/a[@class='attributes']/text()").extract():
            keywords = response.xpath("//div[@class='hlFld-KeywordText']/kwd-group/a[@class='attributes']/text()").extract()
            for keyword in keywords:
                item['keyword'] = item['keyword'] + keyword + ','
        else:
            item['keyword'] = 'NULL'

        #         # 摘要

        item['abstract'] = ''
        pat = re.compile('<[^>]+>', re.S)
        if response.xpath("//div[@class='hlFld-Abstract']//div[@class='abstractSection abstractInFull']//p"):
            coninfos = response.xpath("//div[@class='hlFld-Abstract']//div[@class='abstractSection abstractInFull']//p").extract()
            for coninfo in coninfos:
                item['abstract'] = item['abstract'] + pat.sub('', coninfo).strip() + '<br>'


        else:
            item['abstract'] = 'NULL'
        item['abstract'] = item['abstract'].replace('\n', '')
        # print(item['abstract'])
        header = {
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3013.3 Safari/537.36'
        }

        if response.xpath("//div[@class='rightMobileMenuButton articleToolsButton PDFTool pdf-access redButton smallButton']/a/@href").extract():
            pdf = response.xpath("//div[@class='rightMobileMenuButton articleToolsButton PDFTool pdf-access redButton smallButton']/a/@href").extract()[0]
            item['pdf'] = self.base_url + pdf
            yield scrapy.Request(url=self.base_url + pdf, meta={'filename': pdf.split('/')[-1] + '.pdf'}, headers=header,
                                 callback=postItemWithPdf(item)
)
        else:
            item['pdf'] = 'NULL'
            postItem(item)



        # print(item['pdf'])
        # 卷，期，年
        item['annualVolume'] = response.meta['annualVolume'].strip()
        # item['annualVolume'] = response.xpath("//div[@class='Article information']/div[1]/text()").extract()[0].strip()
        # item['annualVolume'] = pat.sub('', annualVolume).strip()

        # print(item['annualVolume'])
        # 页码
        item['pageNumber'] = 'NULL'
        # print(pageNumber)
        # ru2 = re.compile(r'pp (.*)')
        # # 页码
        # item['pageNumber'] = ru2.search(pageNumber).group(1)
        # print(item['pageNumber'])
        # 期刊名
        item['journalTitle'] = pat.sub('',response.xpath("//div[@id='e3c018c7-8573-4acd-93ae-0ff4b1f3baf3']/div[@class='wrapped ']").extract()[0]).strip()
        # print(item['journalTitle'])
        # 有些期刊目录有一张图片
        item['imageUrlList'] = 'NULL'
        # 12 July 2018
        item['publishTime'] = response.xpath("//span[@class='publicationContentEpubDate dates']/text()").extract()[1].strip()
        # 改成2018-07-12
        temp = time.strptime(item['publishTime'], "%B %d, %Y")
        item['publishTime'] = time.strftime("%Y-%m-%d", temp)
        # print(item['publishTime'])
        yield item

    # # 下载pdf
    def downloadpdf(self, response):
        file_path = Config().pdf_url + response.meta['filename']
        with open(file_path, 'wb') as f:
            f.write(response.body)

    # #下载图片
    def downloadimg(self, response):
        file_path = Config().img_url + response.meta['filename']
        with open(file_path, 'wb') as f:
            f.write(response.body)

