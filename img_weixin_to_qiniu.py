# -*- coding: utf-8 -*-
# 
import gevent
from gevent import monkey

monkey.patch_all()

import datetime
import time
import sys
import gevent
from gevent import monkey
from gevent.queue import Queue

monkey.patch_all()

reload(sys)
sys.setdefaultencoding('utf-8')
from public import Public
import simplejson
import pymysql
import os
import hashlib


def worker(i):
    p = Public()
    consumer = p.get_kafka_consumer(topic, 'img1')
    conn = pymysql.connect(host="10.10.38.201", port=3306, user="alb", passwd="H3KoTMEun9aia7NI", charset="utf8mb4")
    for m in consumer:
        c_value = simplejson.loads(m.value)
        c_id = c_value['id']
        c_source = c_value['source']
        usefull = 1
        if c_id != 0:
            if c_source == 'weixin':
                print('weixin', c_id)
                host = 'http://f.yhres.com/'
                sql = ('select id,cover,content,pic '
                       'from sns.alb_article_index_origin '
                       'where id="%s" and `status` = "0" ') % c_id
                try:
                    conn.ping()
                except:
                    conn = pymysql.connect(host="10.10.38.201", port=3306, user="alb", passwd="H3KoTMEun9aia7NI",
                                           charset="utf8mb4")
                cur = conn.cursor()
                cur.execute(sql)
                res = cur.fetchall()
                cur.close()
                # 查出有结果
                if len(res) > 0:
                    r = res[0]
                    id = r[0]
                    cover = r[1]
                    content = r[2]
                    picss = r[3]
                    new_picss = new_cover = ''
                    pic_hash_list = []
                    # 有封面或者有图
                    if cover != '' or picss != '':
                        if cover != '':
                            img_name, pic_hash = p.wx_up_to_qiniu(cover, str(i), file_path, sys_num)
                            if img_name == '':
                                usefull = 0
                            try:
                                qr = img_name['qr']
                            except:
                                qr = '1'
                            try:
                                new_cover = host + str(img_name['key']) + '?qr=' + qr
                            except:
                                new_cover = ''
                            md5 = hashlib.md5()
                            md5.update(new_cover.split("?qr=")[0])
                            url_md5 = md5.hexdigest()
                            pic_hash_list.append((new_cover.split("?qr=")[0], pic_hash, url_md5))
                        else:
                            new_cover = ''

                        pics = picss.split(',')
                        new_pics = []
                        for pic in pics:
                            if pic == '':
                                continue
                            img_name, pic_hash = p.wx_up_to_qiniu(pic, str(i), file_path, sys_num)
                            if img_name == '':
                                usefull = 0
                                break
                            print(img_name)
                            try:
                                qr = img_name['qr']
                            except:
                                qr = '0'
                            new_pic = host + str(img_name['key'])
                            content = content.replace(pic, new_pic)
                            md5 = hashlib.md5()
                            md5.update(new_pic)
                            url_md5 = md5.hexdigest()
                            pic_hash_list.append((new_pic, pic_hash, url_md5))
                            new_pic = new_pic + '?qr=' + qr
                            new_pics.append(new_pic)
                            pics = picss.split(',')
                        new_picss = ','.join(new_pics)
                        content = content.replace('data-src', 'src')
                        content = content.replace("'", "\\\'").replace('"', '\\\"')
                        if usefull == 1:
                            sql = 'update `sns`.`alb_article_index_origin` set `status`="3",content="%s",qiniu_cover="%s",qiniu_pic="%s" where `id`="%s" ' % (
                                content, new_cover, new_picss, str(id))
                            for hash_i in pic_hash_list:
                                sql_h = 'insert ignore `sns`.`alb_pic_hash` (pic_url, pic_hash, url_md5) ' \
                                      'values ("%s", "%s", "%s")' % (hash_i[0], hash_i[1], hash_i[2])
                                try:
                                    conn.ping()
                                except:
                                    conn = pymysql.connect(host="10.10.38.201", port=3306, user="alb",
                                                           passwd="H3KoTMEun9aia7NI",
                                                           charset="utf8mb4")
                                cur = conn.cursor()
                                cur.execute(sql_h)
                                conn.commit()
                                cur.close()
                                conn.close()

                        else:
                            sql = 'update `sns`.`alb_article_index_origin` set `status`="2" where `id`="%s" ' % (
                                str(id))
                    # 无图的
                    else:
                        usefull = 1
                        sql = 'update `sns`.`alb_article_index_origin` set `status`="3" where `id`="%s" ' % (str(id))
                # 查出无结果
                else:
                    usefull = 0
                    pass
            # 类型错误
            else:
                pass

            try:
                conn.ping()
            except:
                conn = pymysql.connect(host="10.10.38.201", port=3306, user="alb", passwd="H3KoTMEun9aia7NI",
                                       charset="utf8mb4")
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            cur.close()
            if usefull == 1:
                producer = p.get_kafka_producer()
                producer.send('alb_clean',
                              bytes(simplejson.dumps({'id': c_id, 'time': int(time.time()), 'source': c_source})))
                producer.flush()
    conn.close()


if __name__ == "__main__":
    now = datetime.datetime.now()
    print("start at %s" % now.strftime("%Y-%m-%d %H:%M:%S"))
    try:
        sys_num = str(sys.argv[1])
        print('start sys_num %s' % sys_num)
    except:
        print('no sys_num')
        sys.exit()
    file_path = os.path.dirname(os.path.abspath(__file__))
    topic = 'alb_weixin_img_qiniu'
    threads_num = 20
    threads = []
    for i in xrange(threads_num):
        threads.append(gevent.spawn(worker, i))
    gevent.joinall(threads)
    print('game over')
