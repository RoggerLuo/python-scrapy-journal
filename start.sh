#! /bin/bash
source /opt/sci-scrapy/crawler_env/bin/activate
cd /opt/crawler/paper_python_crawler
scrapy batchCrawl
