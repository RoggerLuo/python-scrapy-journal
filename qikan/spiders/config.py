from urllib import request, parse
import json
import requests
import os
import sys
import scrapy

apiAddress = 'http://47.99.79.11:8081'
proxyServer = "transfer.mogumiao.com:9001"
proxyAuth = "Basic " + 'dWlXQnlhUzZ5dnoxeFJESTpZdjc2R3hRbGVYNXlYaWR6'

class Config(object):
    pdf_url = '/opt/crawler/paper_python_crawler/qikan/document/pdf/'
    img_url = 'dev/null'#'/Users/RogersMac/WorkHtgk/qikan/qikan/document/img/'

def proxyRequest(url,meta,callback,headers={}):
    # proxy = {"http": "http://" + proxyServer, "https": "https://" + proxyServer}
    # meta["proxies"] = proxy 
    meta["proxy"] = proxyServer
    # headers["Proxy-Authorization"] = proxyAuth 
    headers["Authorization"] = proxyAuth     
    # if headers == False:
    #     return scrapy.Request(url=url,meta=meta,callback=callback)
    # else:
    return scrapy.Request(url=url,meta=meta,callback=callback,headers=headers)

def matchPaper(item):
    print('----------post matchPaper--------------------------------------------------')
    data = {
        'author': item['author'],
        'keyword': item['keyword'],
        'title': item['title'],
    }
    url = apiAddress + '/paper/matchpaper'
    data = json.dumps(data)
    req = request.Request(url)  # 'http://localhost:9911'
    req.add_header('Content-Type', 'application/json')
    data = data.encode('utf-8')
    with request.urlopen(req, data=data) as f:
        print('Status:', f.status, f.reason)
        for k, v in f.getheaders():
            print('%s: %s' % (k, v))
        value = f.read().decode('utf-8')
        print('matchPaperData:', value)
        return value


def savePaperPost(item, fileItem):  # 保存文章
    print('from spider download post------------------------------------------------------------')
    EmailArr = item['correspongdingauthorEmail'].split('||')
    email = ','.join(EmailArr)
    if len(EmailArr) == 2:
        email = email[:-1]

    keyword = item['keyword']
    if keyword == 'NULL':
        keyword = ''
    data = {
        "auditState": "WAIT",
        "author": item['author'],
        "correspondAuthorList": [
            {
                "email": email,
                "name": item['correspongdingauthor']
            }
        ],
        "doi": item['DOI'],

        "file": fileItem['mediaId'],
        "fileName": item['title'],
        "fileSize": fileItem['size'],

        "journalName": item['journalTitle'],
        "keyword": keyword,
        "origin": "COLLECT",
        "paperState": "SOLDOUT",
        "publishTime": item['publishTime'],
        "reelNumber": item['annualVolume'],
        "summary": item['abstract'],
        "title": item['title'],
    }
    print('------------------------------------------------------------')
    print(data)

    url = apiAddress + '/paper'
    data = json.dumps(data)
    req = request.Request(url)  # 'http://localhost:9911'
    req.add_header('Content-Type', 'application/json')
    data = data.encode('utf-8')

    with request.urlopen(req, data=data) as f:
        print('Status:', f.status, f.reason)
        for k, v in f.getheaders():
            print('%s: %s' % (k, v))
        print('Data:', f.read().decode('utf-8'))


def postItemWithPdf(item):
    def dwnld(response):
        file_path = Config().pdf_url + response.meta['filename']
        if matchPaper(item) == 'true':
            print('已存在重复文献，跳过')
            return

        with open(file_path, 'wb') as f:  # 上传pdf文件
            f.write(response.body)
            print(
                '----------postItemWithPdf--------------------------------------------------')
            file = {'file': open(file_path, 'rb')}
            r = requests.post(apiAddress + '/paper/pdf', files=file)
            dic = json.loads(r.text)
            savePaperPost(item, dic['data']['media'])  # 保存文献信息
            if(os.path.exists(file_path)):  # 判断文件是否存在
                os.remove(file_path)
                print('移除文件：%s' % file_path)

    return dwnld


def postInPipeline(item):
    if matchPaper(item) == 'true':
        print('已存在重复文献，跳过')
        return

    print('-post from pipeline-----------------------------------------------------------')
    correspongdingauthorEmail = item['correspongdingauthorEmail'].split('||')
    email = ','.join(correspongdingauthorEmail)
    keyword = item['keyword']
    if keyword == 'NULL':
        keyword = ''
    data = {
        "auditState": "WAIT",
        "author": item['author'],
        "correspondAuthorList": [
            {
                "email": email,
                "name": item['correspongdingauthor']
            }
        ],
        "doi": item['DOI'],

        # "file": fileItem['mediaId'],
        # "fileName": item['title'],
        # "fileSize": fileItem['size'],

        "journalName": item['journalTitle'],
        "keyword": keyword,
        "origin": "COLLECT",
        "paperState": "SOLDOUT",
        "publishTime": item['publishTime'],
        "reelNumber": item['annualVolume'],
        "summary": item['abstract'],
        "title": item['title'],
    }
    print('---pipeline post ---------------------------------------------------------')

    url = apiAddress + '/paper'
    data = json.dumps(data)
    req = request.Request(url)  # 'http://localhost:9911'
    req.add_header('Content-Type', 'application/json')
    data = data.encode('utf-8')

    with request.urlopen(req, data=data) as f:
        print('Status:', f.status, f.reason)
        for k, v in f.getheaders():
            print('%s: %s' % (k, v))
        print('Data:', f.read().decode('utf-8'))


def postItem(test):
    return '这个不能删'
