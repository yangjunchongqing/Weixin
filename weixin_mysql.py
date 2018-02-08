# -*- coding: utf-8 -*-

import datetime
import time
import sys

import requests
import random
from lxml import etree
import pymysql
import re
import simplejson
import os
import hashlib

reload(sys)
sys.setdefaultencoding('utf-8')
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from public import Public
import traceback
import Queue
import traceback
import re


def get_articles(html):
    html = html.replace('\n', '').replace('\r', '').replace(' ', '')
    # 解析全部json的方法
    article_json = re.findall('varmsgList=(.*?);seajs', html)
    # 如果文章列表正确：
    try:
        article_info = simplejson.loads(article_json[0])
    # 如果文章列表错误：
    except:
        return []
        # print(html)
        # sys.exit()
    article_list = article_info['list']
    articles = []
    # 格式化每一篇文章
    for article_temp in article_list:
        article = {}
        cur_time = int(time.time())
        today_time = cur_time - cur_time % 86400 - 28800 - 86400
        app_msg_ext_info = article_temp['app_msg_ext_info']
        multi_app_msg_item_list = app_msg_ext_info['multi_app_msg_item_list']
        # 两个位置去文章列表内容信息
        try:
            article['datetime'] = article_temp['comm_msg_info']['datetime']
        except:
            article['datetime'] = 0
        article['author'] = app_msg_ext_info['author']
        article['title'] = app_msg_ext_info['title']
        article['cover'] = app_msg_ext_info['cover']
        article['content_url'] = app_msg_ext_info['content_url'].replace('amp;', '')
        article['digest'] = app_msg_ext_info['digest']
        article['fileid'] = app_msg_ext_info['fileid']
        if article['fileid'] == 0:
            mmdd55 = hashlib.md5()
            mmdd55.update(article['title'])
            article['fileid'] = mmdd55.hexdigest()
        # 判断文章日期，如果不是今日：
        # if int(article['datetime']) < int(1511020800):
        if int(article['datetime']) < int(today_time):
            print('%s %s:%s no' % (article['title'], str(int(article['datetime'])), str(today_time)))
            pass
        else:
            print('%s %s:%s yes' % (article['title'], str(int(article['datetime'])), str(today_time)))
            articles.append(article)

        if len(multi_app_msg_item_list) > 0:
            for multi_app_msg_item in multi_app_msg_item_list:
                article = {}
                try:
                    article['datetime'] = article_temp['comm_msg_info']['datetime']
                except:
                    article['datetime'] = 0
                article['author'] = multi_app_msg_item['author']
                article['title'] = multi_app_msg_item['title']
                article['cover'] = multi_app_msg_item['cover']
                article['content_url'] = multi_app_msg_item['content_url'].replace('amp;', '')
                article['digest'] = multi_app_msg_item['digest']
                article['fileid'] = multi_app_msg_item['fileid']
                if article['fileid'] == 0:
                    mmdd55 = hashlib.md5()
                    mmdd55.update(article['title'])
                    article['fileid'] = mmdd55.hexdigest()
                # 判断文章日期，如果不是今日：
                if int(article['datetime']) < int(today_time):
                    print('%s %s:%s no' % (article['title'], str(int(article['datetime'])), str(today_time)))
                    pass
                else:
                    print('%s %s:%s yes' % (article['title'], str(int(article['datetime'])), str(today_time)))
                    articles.append(article)
        else:
            pass
    return articles


def download_article(article, headers, sn, weixinhao, article_sort):
    fileid = article['fileid']
    # 处理文章链接
    if 'weixin.qq.com' not in article['content_url']:
        content_url = "https://mp.weixin.qq.com" + article['content_url']
    else:
        content_url = article['content_url']
    # 如果网路错误
    try:
        req = sn.get(content_url, headers=headers, verify=False, timeout=5)
    except:
        return 0
    if req.status_code == 200:
        html = req.content
        # 文章页如果验证码
        if u'验证码' in html:
            p.new_code(url, 'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14')
            p.change_gw(sys._getframe().f_lineno, sys_second)
            return 0
        # 文章页如果没有验证码
        else:
            selector = etree.HTML(html)
            main_content = selector.xpath('//div[@id="js_content"]')

            # 取正文
            try:
                main_content_html = etree.tostring(main_content[0], encoding='unicode', method="html")
            except:
                main_content_html = ''
            main_content_html = main_content_html.replace('"', '\\\"').replace("'", "\\\'")

            # 取原始链接
            origin_urls = selector.xpath('//div[@id="js_sg_bar"]/a[1]/@href')
            try:
                origin_url = origin_urls[0]
            except:
                origin_url = ''

            # 取详情
            author = article['author'].replace('"', '\\\"').replace("'", "\\\'")
            title = article['title'].replace('"', '\\\"').replace("'", "\\\'")
            cover = article['cover'].replace('"', '\\\"').replace("'", "\\\'")
            # content_url = article['content_url'].replace('"', '\\\"').replace("'", "\\\'")
            # content_url = 'https://mp.weixin.qq.com' + content_url
            digest = article['digest'].replace('"', '\\\"').replace("'", "\\\'")
            # fileid = article['fileid'].replace('"', '\\\"').replace("'", "\\\'")

            # 取正文图片
            try:
                # main_content_imgs = main_content[0].xpath('descendant::img/@data-src')
                main_content_imgs = re.findall(r'data-src="(http.*?)"', html.decode())
                main_content_imgss = ','.join(main_content_imgs)
            except:
                main_content_imgs = main_content_imgss = ''

            # 取文章发布时间
            datetimes = article['datetime']

            conn = pymysql.connect(
                host="10.10.38.201", port=3306, user="alb", passwd="H3KoTMEun9aia7NI", charset="utf8")
            cur = conn.cursor()
            sql = ('insert ignore `sns`.alb_article_index_origin '
                   '(`author`,`title`,`cover`,`content_url`,`digest`,`fileid`,`from`,`weixinhao_code`,`weixinhao_name`,'
                   '`content`,`pic`,`origin_url`,`datetime`,`qiniu_cover`,`qiniu_pic`,`sort`)'
                   'values ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","","","%s")') % (
                      author, title, cover, content_url, digest, str(fileid), web_type,
                      weixinhao[1], weixinhao[0],
                      main_content_html,
                      main_content_imgss, origin_url, str(datetimes), str(article_sort))
            print('%s download' % title)
            try:
                cur.execute(sql)
            except:
                file_object = open('error_sql', 'wb')
                file_object.write(sql)
                file_object.close()
                sys.exit()
            conn.commit()
            kafka_id = cur.lastrowid
            producer = p.get_kafka_producer()
            producer.send('alb_weixin_img_qiniu',
                          bytes(simplejson.dumps({'id': kafka_id, 'time': int(time.time()), 'source': 'weixin'})))
            producer.flush()
            cur.close()
            conn.close()
        return 1
    else:
        print('%s not 200 is %s' % (fileid, req.status_code))
        return 1


def worker():
    p = Public()
    q = Queue.Queue()
    # 微信号计数器
    weixinhao_n = 0
    # 遍历每个公众号

    for weixinhao in weixinhaos:
        q.put(weixinhao)
    while 1:
        if q.empty():
            break
        weixinhao = q.get()
        # weixinhao = (u'冷兔', 'lengtoo')
        weixinhao_name = weixinhao[0]
        weixinhao_code = weixinhao[1]
        alb_mapping_id = weixinhao[2]
        frequency = weixinhao[3]
        print('++++++++++++++++++++++++++++++++++++++++')
        print(weixinhao_n)
        print(weixinhao_name)
        print('++++++++++++++++++++++++++++++++++++++++')
        sql = 'insert `sns`.`alb_record` (`name`,`source`,`code`) values ("%s","%s","%s")' % (
            weixinhao_name, 'weixin', weixinhao_code)
        try:
            conn.ping()
        except:
            conn = pymysql.connect(host="10.10.38.201", port=3306, user="alb", passwd="H3KoTMEun9aia7NI",
                                   charset="utf8mb4")

        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        print 'next weixinhao sleep 20'
        time.sleep(15)
        weixinhao_n += 1
        # 生成随机数判断换不换网关
        # 关闭自动更换网关，切换ip
        # change_gw_code = random.randint(0, 10)
        # if change_gw_code < 3:
        #     p.change_gw(sys._getframe().f_lineno, sys_second)
        # 搜索公众号列表页，这一步是搜索搜狗
        search_url = url % weixinhao_code
        print(search_url)
        headers = {
            "Asccept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Host": "weixin.sogou.com",
            # "if-modified-since":"Thu, 01 Jan 1970 00:00:00 GMT",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "",
            'X-Forwarded-For': '%s.%s.%s.%s' % (
                random.randint(50, 250), random.randint(50, 250), random.randint(50, 250), random.randint(50, 250)),
            'CLIENT-IP': '%s.%s.%s.%s' % (
                random.randint(50, 250), random.randint(50, 250), random.randint(50, 250), random.randint(50, 250))
        }
        headers["User-Agent"] = p.get_user_agent()
        # 使用session ，从搜狗拿
        try:
            sn = requests.Session()
            sn.get("http://weixin.sogou.com/", headers=headers, timeout=3, verify=False)
        except Exception as e:
            print(e)
            traceback.print_exc()
            q.put(weixinhao)
            continue
        time.sleep(0.5)
        try:
            req = sn.get(search_url, headers=headers, timeout=3, verify=False)
        except Exception as e:
            print(e)
            traceback.print_exc()
            q.put(weixinhao)
            continue
        time.sleep(0.5)
        # 如果搜狗搜索正常：
        if req.status_code == 200:
            html = req.content
            # 如果页面是验证码：
            if u'验证码' in html:
                # 换网关：
                p.change_gw(sys._getframe().f_lineno, sys_second)
                # 微信号放回去
                q.put(weixinhao)
                # 如下返回for weixinhao in weixinhaos:
                continue
            # 如果页面没有验证码：
            else:
                selector = etree.HTML(html)
                # 获取公众号文章列表页account_urls，兼容两种格式
                account_urls = selector.xpath('//a[@uigs="main_toweixin_account_name_0"]/@href')
                if len(account_urls) == 0:
                    account_urls = selector.xpath('//a[@uigs="account_name_0"]/@href')
                # 如果获取到存在该微信号：
                if len(account_urls) > 0:
                    # 取到微信公众号文章列表
                    account_url = account_urls[0]
                    print account_url
                    headers['Host'] = 'mp.weixin.qq.com'
                    headers['Referer'] = search_url
                    try:
                        req = sn.get(account_url, headers=headers, timeout=5, verify=False)
                        if req.status_code == 200:
                            html = req.content
                            # 如果列表页出现验证码
                            if u'验证码' in html:
                                while 1:
                                    try:
                                        p.new_code(account_url,
                                                   'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14')
                                        break
                                    except Exception as e:
                                        print(e)
                                        print(traceback.print_exc())
                                        break
                                p.change_gw(sys._getframe().f_lineno, sys_second)
                                q.put(weixinhao)
                            # 如果列表页没有出现验证码
                            else:
                                # 获取所有文章的list
                                articles = get_articles(html)
                                # 如果可爬文章列表为空，增加抓取间隔
                                if len(articles) == 0:
                                    new_frequency = int(frequency) + 1
                                    if new_frequency > 15:
                                        new_frequency = 15
                                    now_timestamp = int(time.mktime(
                                        time.strptime(now.strftime("%Y-%m-%d 00:00:00"), "%Y-%m-%d %H:%M:%S")))
                                    next_crawl_timestamp = now_timestamp + (fbnc[new_frequency] * 86400)
                                    next_crawl_time = time.strftime("%Y-%m-%d 00:00:00",
                                                                    time.localtime(next_crawl_timestamp))
                                    last_crawl_time = time.strftime("%Y-%m-%d 00:00:00", time.localtime(now_timestamp))
                                    sql = 'update `sns`.`sns_out_user_mapping` set `frequency`="%s",`next_crawl_time`="%s",`last_crawl_time`="%s" where `id`="%s" ' % (
                                        str(new_frequency), next_crawl_time, last_crawl_time, alb_mapping_id)
                                else:
                                    # 计算下一次抓取时间
                                    new_frequency = int(frequency)
                                    now_timestamp = int(time.mktime(
                                        time.strptime(now.strftime("%Y-%m-%d 00:00:00"), "%Y-%m-%d %H:%M:%S")))
                                    next_crawl_timestamp = now_timestamp + (fbnc[new_frequency] * 86400)
                                    next_crawl_time = time.strftime("%Y-%m-%d 00:00:00",
                                                                    time.localtime(next_crawl_timestamp))
                                    last_crawl_time = time.strftime("%Y-%m-%d 00:00:00", time.localtime(now_timestamp))
                                    sql = 'update `sns`.`sns_out_user_mapping` set `next_crawl_time`="%s",`last_crawl_time`="%s" where `id`="%s" ' % (
                                        next_crawl_time, last_crawl_time, alb_mapping_id)
                                try:
                                    conn.ping()
                                except:
                                    conn = pymysql.connect(
                                        host="10.10.38.201", port=3306, user="alb", passwd="H3KoTMEun9aia7NI",
                                        charset="utf8")
                                cur = conn.cursor()
                                print(sql)
                                cur.execute(sql)
                                conn.commit()
                                cur.close()
                                article_title_temp = ''
                                # 开始抓取文章
                                article_sort = 0
                                for article in articles:
                                    article_sort += 1
                                    print('next article sleep 20')
                                    time.sleep(15)
                                    # 如果是不是相同文章
                                    print('%s %s' % (article_title_temp, article['title']))
                                    if article['title'] != article_title_temp:
                                        headers['Referer'] = account_url
                                        download_article_temp = download_article(article, headers, sn, weixinhao,
                                                                                 str(article_sort))
                                        # 如果获取文章错误：
                                        if download_article_temp == 0:
                                            # 把文章放回到文章列表
                                            articles.append(article)
                                        else:
                                            article_title_temp = article['title']
                                    # 如果是相同文章
                                    else:
                                        pass
                        else:
                            print('weixinhao article list status_code is error %s' % req.status_code)
                            p.change_gw(sys._getframe().f_lineno, sys_second)
                    except Exception as e:
                        print (e)
                        traceback.print_exc()
                        print('weixinhao article list http is error')
                        q.put(weixinhao)
                        # 跳回到for weixinhao in weixinhaos:
                        p.change_gw(sys._getframe().f_lineno, sys_second)
                # 如果微信号不存在：
                else:
                    print('the weixinhao is not exist %s' % weixinhao_code)
                    sql = 'update `sns`.`sns_out_user_mapping` set `status`="2" where `id`="%s" ' % alb_mapping_id
                    print(sql)
                    try:
                        conn.ping()
                    except:
                        conn = pymysql.connect(
                            host="10.10.38.201", port=3306, user="alb", passwd="H3KoTMEun9aia7NI", charset="utf8")
                    cur = conn.cursor()
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
        # 如果搜狗搜索不正常：换网关
        else:
            print('sogou not get weixincode %s' % str(req.status_code))
            p.change_gw(sys._getframe().f_lineno, sys_second)
            # 把这个未成功的微信号放回去
            q.put(weixinhao)


if __name__ == "__main__":
    now = datetime.datetime.now()
    print("start at %s" % now.strftime("%Y-%m-%d %H:%M:%S"))
    # 斐波那契数列
    fbnc = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597]
    try:
        sys_first = sys.argv[1]
        sys_second = sys.argv[2]
    except:
        sys_first = sys_second = '0'
    if sys_first.isdigit() and sys_second.isdigit():
        if int(sys_first) < int(sys_second):
            raise Exception('one > two')
    else:
        raise Exception('not int')
    p = Public()
    # 删除相同机器内的其他微信脚本
    ret_text_list = os.popen("ps aux --sort=start_time | grep weixin_mysql.py")
    pid_list = []
    for line in ret_text_list:
        pid_list.append(line)
    if len(pid_list) > 3:
        cmd_list = pid_list[0].split()
        pid_num = cmd_list[1]
        print pid_num
        os.system("kill -9 %s" % pid_num)
    print("killed at %s" % now.strftime("%Y-%m-%d %H:%M:%S"))

    file_path = os.path.dirname(os.path.abspath(__file__))
    # 数据库字段类型
    web_type = 'weixin'
    conn = pymysql.connect(host="10.10.38.201", port=3306, user="alb", passwd="H3KoTMEun9aia7NI", charset="utf8mb4")
    # 计算待爬取的数量
    # sql = 'select count(*) from sns.alb_account where source ="weixin" and status ="0"'
    sql = 'select count(*) from `sns`.`sns_out_user_mapping` where `platform_id` = "1" and status ="0" and (next_crawl_time<="%s" or next_crawl_time is NULL ) ' % now.strftime(
        "%Y-%m-%d %H:%M:%S")
    cur = conn.cursor()
    cur.execute(sql)
    count_num = cur.fetchall()
    total = count_num[0][0]
    # 获取所有的待爬去公众号
    one_cent = int(total) / int(sys_first)
    if sys_first == '0':
        sql = 'select `platform_nick`,`platform_acc`,`id`,`frequency` from sns.sns_out_user_mapping where platform_id ="1" and status ="0" and (next_crawl_time<="%s" or next_crawl_time is NULL )' % now.strftime(
            "%Y-%m-%d %H:%M:%S")
    elif sys_first == sys_second:
        sql = 'select `platform_nick`,`platform_acc`,`id`,`frequency` from sns.sns_out_user_mapping where platform_id ="1" and status ="0" and (next_crawl_time<="%s" or next_crawl_time is NULL ) limit %s,%s ' % (
            now.strftime("%Y-%m-%d %H:%M:%S"), one_cent * (int(sys_second) - 1), int(total))
    else:
        sql = 'select `platform_nick`,`platform_acc`,`id`,`frequency` from sns.sns_out_user_mapping where platform_id ="1" and status ="0" and (next_crawl_time<="%s" or next_crawl_time is NULL ) limit %s,%s ' % (
            now.strftime("%Y-%m-%d %H:%M:%S"), one_cent * (int(sys_second) - 1), one_cent)
    print(sql)
    time.sleep(5)
    cur = conn.cursor()
    cur.execute(sql)
    weixinhaos = list(cur.fetchall())
    cur.close()
    # 公众号乱序
    random.shuffle(weixinhaos)
    url = "http://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_="
    conn.commit()
    worker()
