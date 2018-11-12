# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QikanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 文章题目
    title = scrapy.Field()
    # 作者
    author = scrapy.Field()
    # 通讯作者
    correspongdingauthor = scrapy.Field()
    # 通讯作者单位
    authorAffiliation = scrapy.Field()
    # 通讯作者邮箱
    correspongdingauthorEmail = scrapy.Field()
    # DOI号
    DOI = scrapy.Field()
    # 关键词
    keyword = scrapy.Field()
    # 摘要
    abstract = scrapy.Field()
    # pdf全文
    pdf = scrapy.Field()
    # 年卷期
    annualVolume = scrapy.Field()
    # 页码
    pageNumber = scrapy.Field()
    # 期刊名称
    journalTitle = scrapy.Field()
    # 图片地址
    imageUrlList = scrapy.Field()
    #出版时间
    publishTime = scrapy.Field()





