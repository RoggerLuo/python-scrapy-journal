# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#####################################存到mysql中
from sqlalchemy import create_engine,Column,Integer,String,Table,MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import os
from PIL import Image
# from .settings import IMAGES_STORE as image_store
from .spiders.config import postInPipeline

class ArticleTemplate():
    id = Column(Integer, primary_key=True)

    # 文章题目
    title = Column(String(500))
    # 作者
    author = Column( String(300))
    # 通讯作者
    correspongdingauthor = Column(String(300))
    # 通讯作者单位
    authorAffiliation = Column( String(1000))
    # # 第一作者邮箱
    # firstauthorEmail = Column( String(100))
    # 通讯作者邮箱
    correspongdingauthorEmail = Column( String(300))
    # DOI号
    DOI = Column( String(100))
    # 关键词
    keyword = Column( String(300))
    # 摘要
    abstract = Column( String(13000))
    # pdf全文
    pdf = Column( String(300))
    # 年卷期
    annualVolume = Column( String(100))
    # 页码
    pageNumber = Column( String(100))
    # 期刊名称
    journalTitle = Column( String(300))
    # 图片地址
    imageUrlList = Column( String(300))
    # 出版时间
    publishTime = Column(String(100))

    def __init__(self, **items):
        for key in items:
            if hasattr(self,key):
                setattr(self,key,items[key])
                # setattr(self,'id',int(round(time.time()*1000000)))

class QikanPipeline(object):
    def __init__(self):
        self.engine = create_engine('mysql://root:htgk2015!root@192.168.1.11:3306/paper_article?charset=utf8', echo=False)
        self.session = sessionmaker(bind=self.engine)
        self.sess = self.session()
        Base = declarative_base()
        # self.Nokind = type('article_nokind', (Base, ArticleTemplate), {'__tablename__': 'article_nokind'})
        self.Article = type('article_article', (Base, ArticleTemplate), {'__tablename__': 'article_article'})

    def process_item(self, item, spider):
        postInPipeline(item)

        # if spider.name not in self.engine.table_names():
        #     self.Article.metadata.create_all(self.engine)

        # if not self.sess.query(self.Article).filter_by(title=item['title']).all():
        #     self.sess.add(self.Article(**item))
        #     self.sess.commit()

        #     if len(item['pdf']) < 15:
        #         print('---------save paper---from pipeline--------------------------------------------------')
        # else:
        #     print('------检测到重复 from pipeline--------------------------------------------------')

        return item


    def close_spider(self, spider):
        self.sess.close()

