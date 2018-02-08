# -*- coding: utf-8 -*-

import gevent
from gevent import monkey

monkey.patch_all()

import datetime
import time
import sys
import imagehash
from io import BytesIO

reload(sys)
sys.setdefaultencoding('utf-8')

import random
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import requests
import imghdr
import os
from selenium import webdriver
from selenium.webdriver import ActionChains
from PIL import Image
from ruokuai import RuoKuai
from kafka import KafkaProducer
from kafka import KafkaConsumer
from random import randint
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
import zbarlight


class Public():
    def check_qr(self, file_path):
        with open(file_path, 'rb') as image_file:
            image = Image.open(image_file)
            image.load()
        codes = zbarlight.scan_codes('qrcode', image)
        if codes == None:
            qr = 0
        else:
            qr = 1
        return qr

    def new_code(self, url, user_agent):
        file_path = os.path.dirname(os.path.abspath(__file__))
        cap = webdriver.DesiredCapabilities.PHANTOMJS
        cap['browserName'] = ''
        cap['phantomjs.page.settings.userAgent'] = user_agent
        cap['phantomjs.page.settings.resourceTimeout'] = '1000'
        driver = webdriver.PhantomJS(executable_path=r'/root/phantomjs-2.1.1-linux-x86_64/bin/phantomjs',
                                     desired_capabilities=cap)
        driver.set_window_size(1024, 768)
        driver.get(url)
        # for l in ['input', 'bt']:
        #     locator = (By.ID, l)
        #     WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located(locator))
        driver.get_screenshot_as_file(file_path + '/img_code/v4.png')
        im = Image.open(file_path + '/img_code/v4.png')
        x = 520
        y = 240
        w = 140
        h = 60
        box = (x, y, x + w, y + h)
        region = im.crop(box)
        region.save(file_path + "/img_code/v4_deal.png")
        rc = RuoKuai('ricksun', 'ricksun123', '80026', 'c45f40de84d049c288eea22c91ab3284')
        im = open(file_path + '/img_code/v4_deal.png', 'rb').read()
        code = rc.rk_create(im, '2040')
        print(code)
        code_text = code['Result']
        # print('please input:')
        # code_text = raw_input()
        input_one = driver.find_element_by_id('input')
        button_one = driver.find_element_by_id('bt')

        input_one.send_keys(code_text)
        actions = ActionChains(driver)
        actions.move_to_element(button_one)
        actions.click(button_one)
        actions.double_click(button_one)
        time.sleep(1)
        actions.perform()
        time.sleep(1)
        print(u'验证码完成')

    def get_proxy(self):
        req_json = requests.get("http://127.0.0.1/get_proxy").json()
        if req_json["Status"] == 0:
            return (False, "")
        else:
            proxies = {
                "http": "http://%s" % req_json["Data"],
                # "https": "https://121.232.151.49:8118",
            }
            return proxies

    def get_user_agent(self):
        oss = [
            'Windows NT 5.1',  # Windowsxp
            'Windows NT 5.1; WOW64',  # 64bitversion
            'Windows XP',
            'Windows XP; WOW64',  # 64bitversion
            'Windows NT 6.0',  # WindowsVista
            'Windows NT 6.0; WOW64',  # WindowsVistax64
            'Windows NT 6.1',  # Windows7
            'Windows NT 6.1; WOW64',  # Windows7 x64
            'Windows NT 6.2',  # Windows8
            'Windows NT 6.2; WOW64',  # Windows8x64
            'Windows NT 10.0',  # Windows10
            'Windows NT 10.0; WOW64',  # Windows10x64
            'Linux x86_64',
            'Linux i686',
            'Macintosh; U; Intel Mac OS X 10_%s_%s ; en-US' % (str(randint(0, 9)), str(randint(0, 9))),
            'Macintosh; Intel Mac OS X 10_%s_%s',
        ]
        styles = [
            "chrome",
            "firefox",
        ]

        style = random.choice(styles)
        os = random.choice(oss)
        if style == "chrome":
            version = "%s.0.%s.%s" % (str(randint(47, 53)), str(randint(1000, 4000)), str(randint(100, 400)))
            ret = 'Mozilla/5.0 (%s) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36' % (os, version)
        else:
            version = "%s.%s" % (str(randint(45, 49)), str(randint(0, 9)))
            ret = 'Mozilla/5.0 (%s) Gecko/20100101 Firefox/%s' % (os, version)
        return ret

    def kafka_connect(self):
        producer = KafkaProducer(bootstrap_servers="10.10.233.2, 10.10.213.218, 10.10.238.166")
        return producer

    # producer.send(topic, b'aaaa')
    # producer.flush()
    def get_kafka_producer(self):
        producer = KafkaProducer(bootstrap_servers="10.10.233.2, 10.10.213.218, 10.10.238.166")
        return producer

    # for m in consumer:
    # print m.value
    def get_kafka_consumer(self, topic, group_id):
        consumer = KafkaConsumer(topic, group_id=group_id,
                                 bootstrap_servers="10.10.233.2, 10.10.213.218, 10.10.238.166")
        return consumer

    def kafka_send(self, topic, something):
        try:
            self.kafka_producer.send("newcobub", bytes(something))
            self.kafka_producer.flush()
        except:
            self.__init__()
            self.kafka_producer.send("newcobub", bytes(something))
            self.kafka_producer.flush()

    def up_to_qiniu(self, url, name='0', file_path=os.path.dirname(os.path.abspath(__file__)), sys_num='0'):
        try:
            access_key = 'Heg2bTu0m2UlhtHJixAKMDld4O9DV4W_3bp8DmFV'
            secret_key = 'VuLbXbxV060ZQGls6FvCPvzbCespwESrvT48Tdas'
            q = Auth(access_key, secret_key)
            bucket_name = 'foto'
            localfile = file_path + '/qn_temp_jike_' + sys_num + '_' + name
            print(localfile)
            # 获取图片
            # url = 'https://cdn.ruguoapp.com/cf910f67dab80b6877cad09f1dce2018?imageView2/0/h/2000/interlace/1'
            try:
                req = requests.get(url, timeout=10)
            except:
                return ''
            # 判断分辨率
            open(localfile, 'wb').write(req.content)
            im = Image.open(localfile)
            w, h = im.size
            # print w
            # print h
            # 判断图片类型
            img_type = imghdr.what(localfile)
            # print img_type
            key = 'jk/%s@r_%sw_%sh.%s' % (url.split('?')[0].split('/')[-1], str(w), str(h), img_type)
            token = q.upload_token(bucket_name, key, 3600)
            ret, info = put_file(token, key, localfile)
            try:
                qr = self.check_qr(localfile)
            except:
                qr = '0'
            ret['qr'] = str(qr)
            return ret
            # print(info)
            # assert ret['key'] == key
            # assert ret['hash'] == etag(localfile)
        except Exception as e:
            print(e)
            return ''

    def wx_up_to_qiniu(self, url, name='0', file_path=os.path.dirname(os.path.abspath(__file__)), sys_num='0'):
        try:
            access_key = 'Heg2bTu0m2UlhtHJixAKMDld4O9DV4W_3bp8DmFV'
            secret_key = 'VuLbXbxV060ZQGls6FvCPvzbCespwESrvT48Tdas'
            q = Auth(access_key, secret_key)
            bucket_name = 'foto'
            localfile = file_path + '/qn_temp_weixin_' + sys_num + '_' + name
            print(localfile)
            # 获取图片
            # url = 'https://cdn.ruguoapp.com/cf910f67dab80b6877cad09f1dce2018?imageView2/0/h/2000/interlace/1'
            try:
                req = requests.get(url, timeout=10)
            except:
                return '', ''
            # 生成图片的hash值，图片去重标志
            image_hash = Image.open(BytesIO(req.content))
            pic_hash = str(imagehash.dhash(image_hash))
            # 判断分辨率
            open(localfile, 'wb').write(req.content)
            im = Image.open(localfile)
            w, h = im.size
            # print w
            # print h
            # 判断图片类型
            img_type = imghdr.what(localfile)
            # print img_type
            key = 'wx/%s@r_%sw_%sh.%s' % (url.split('/')[-2], str(w), str(h), img_type)
            token = q.upload_token(bucket_name, key, 3600)
            ret, info = put_file(token, key, localfile)
            try:
                qr = self.check_qr(localfile)
            except:
                qr = '0'
            ret['qr'] = str(qr)
            return ret, pic_hash
            # print(info)
            # assert ret['key'] == key
            # assert ret['hash'] == etag(localfile)
        except Exception as e:
            print(e)
            return '', ''

    gw_list = {
        '1': [
            '10.10.106.212',
            '10.10.108.103',
            '10.10.88.214',
            '10.10.81.20',
            '10.10.96.91',
            '10.10.90.3',
            '10.10.96.133',
            '10.10.90.68',
            '10.10.82.171',
            '10.10.87.161',
            '10.10.86.112',
            '10.10.91.34',
            '10.10.89.8',
            '10.10.96.26',
            '10.10.89.248',
            '10.10.91.75',
            '10.10.94.46',
            '10.10.96.239',
            '10.10.91.98',
            '10.10.83.56',
            '10.10.81.179',
            '10.10.90.32',
            '10.10.89.49',
            '10.10.93.141',
            '10.10.90.61',
            '10.10.94.49',
            '10.10.95.88',
            '10.10.94.55',
            '10.10.86.177',
            '10.10.90.93',
            '10.10.94.184',
            '10.10.94.141',
            '10.10.92.12',
            '10.10.81.49',
            '10.10.81.78',
            '10.10.93.145',
            '10.10.96.168',
            '10.10.95.243',
            '10.10.92.44',
            '10.10.91.183',
            '10.10.84.140',
            '10.10.85.102',
            '10.10.86.245',
            '10.10.88.222',
            '10.10.83.14',
            '10.10.81.239',
            '10.10.86.131',
            '10.10.94.177',
            '10.10.92.194',
            '10.10.82.182',
            '10.10.87.232',
            '10.10.94.239',
            '10.10.87.242',
            '10.10.96.198',
            '10.10.77.238',
            '10.10.71.5',
            '10.10.74.59',
            '10.10.67.62',
            '10.10.77.213',
            '10.10.70.175',
            '10.10.69.182',
            '10.10.71.138',
            '10.10.69.122',
            '10.10.80.128',
        ],
        '2':
            [
                '10.10.51.33',
                '10.10.49.13',
                '10.10.42.205',
                '10.10.18.172',
                '10.10.26.216',
                '10.10.8.75',
                '10.10.27.91',
                '10.10.43.55',
                '10.10.13.106',
                '10.10.62.35',
                '10.10.32.165',
                '10.10.43.96',
                '10.10.23.247',
                '10.10.59.169',
                '10.10.54.242',
                '10.10.42.66',
                '10.10.15.53',
                '10.10.20.65',
                '10.10.38.127',
                '10.10.61.118',
                '10.10.21.8',
                '10.10.13.59',
                '10.10.54.182',
                '10.10.61.186',
                '10.10.22.129',
                '10.10.23.139',
                '10.10.60.153',
                '10.10.55.146',
                '10.10.48.77',
                '10.10.25.26',
                '10.10.61.178',
                '10.10.33.64',
                '10.10.21.32',
                '10.10.53.177',
                '10.10.12.62',
                '10.10.31.129',
                '10.10.34.100',
                '10.10.35.122',
                '10.10.17.145',
                '10.10.62.43',
                '10.10.34.185',
                '10.10.11.128',
                '10.10.23.143',
                '10.10.11.109',
                '10.10.47.35',
                '10.10.64.19',
                '10.10.32.229',
                '10.10.20.41',
                '10.10.63.139',
                '10.10.62.88',
                '10.10.11.186',
                '10.10.4.203',
                '10.10.10.210',
                '10.10.25.44',
                '10.10.29.45',
                '10.10.10.113',
                '10.10.19.234',
                '10.10.2.110',
                '10.10.7.30',
                '10.10.5.103',
                '10.10.25.145',
                '10.10.1.67',
                '10.10.51.62',
                '10.10.45.205',
            ],
        '3':
            [
                '10.10.242.50',
                '10.10.245.11',
                '10.10.239.110',
                '10.10.233.147',
                '10.10.217.58',
                '10.10.247.100',
                '10.10.227.66',
                '10.10.223.203',
                '10.10.224.16',
                '10.10.217.26',
                '10.10.220.169',
                '10.10.242.117',
                '10.10.220.207',
                '10.10.244.18',
                '10.10.216.129',
                '10.10.217.85',
                '10.10.215.133',
                '10.10.234.89',
                '10.10.242.57',
                '10.10.217.101',
                '10.10.214.214',
                '10.10.212.239',
                '10.10.246.8',
                '10.10.242.107',
                '10.10.224.121',
                '10.10.249.242',
                '10.10.228.29',
                '10.10.244.60',
                '10.10.224.192',
                '10.10.243.69',
                '10.10.219.180',
                '10.10.234.163',
                '10.10.231.18',
                '10.10.231.37',
                '10.10.224.10',
                '10.10.245.206',
                '10.10.238.20',
                '10.10.237.185',
                '10.10.234.218',
                '10.10.246.87',
                '10.10.245.27',
                '10.10.226.152',
                '10.10.249.216',
                '10.10.213.208',
                '10.10.246.75',
                '10.10.243.117',
                '10.10.228.198',
                '10.10.212.163',
                '10.10.230.224',
                '10.10.241.118',
                '10.10.238.49',
                '10.10.247.252',
                '10.10.216.160',
                '10.10.232.152',
                '10.10.218.128',
                '10.10.217.247',
                '10.10.220.133',
                '10.10.238.213',
                '10.10.238.217',
                '10.10.217.175',
                '10.10.241.200',
                '10.10.248.52',
                '10.10.247.176',
                '10.10.243.59',
            ],
        '4':
            [
                '10.10.216.14',
                '10.10.226.9',
                '10.10.232.7',
                '10.10.220.79',
                '10.10.217.181',
                '10.10.222.96',
                '10.10.235.219',
                '10.10.242.113',
                '10.10.216.216',
                '10.10.240.204',
                '10.10.239.233',
                '10.10.229.168',
                '10.10.237.39',
                '10.10.222.56',
                '10.10.246.134',
                '10.10.229.20',
                '10.10.219.75',
                '10.10.223.185',
                '10.10.226.26',
                '10.10.223.162',
                '10.10.226.168',
                '10.10.217.172',
                '10.10.238.76',
                '10.10.221.158',
                '10.10.234.184',
                '10.10.242.26',
                '10.10.215.84',
                '10.10.216.141',
                '10.10.237.21',
                '10.10.226.112',
                '10.10.239.84',
                '10.10.246.73',
                '10.10.228.79',
                '10.10.245.91',
                '10.10.247.98',
                '10.10.216.252',
                '10.10.214.125',
                '10.10.212.58',
                '10.10.248.197',
                '10.10.230.144',
                '10.10.224.25',
                '10.10.242.213',
                '10.10.240.68',
                '10.10.246.45',
                '10.10.234.175',
                '10.10.241.55',
                '10.10.218.213',
                '10.10.222.14',
                '10.10.225.164',
                '10.10.246.247',
                '10.10.230.76',
                '10.10.216.157',
                '10.10.231.173',
                '10.10.244.164',
                '10.10.237.155',
                '10.10.242.172',
                '10.10.226.62',
                '10.10.225.131',
                '10.10.233.51',
                '10.10.243.193',
                '10.10.231.163',
                '10.10.221.109',
                '10.10.225.2',
                '10.10.226.59',
            ],
        '5':
            [
                '10.10.11.114',
                '10.10.33.136',
                '10.10.61.207',
                '10.10.37.218',
                '10.10.53.41',
                '10.10.30.234',
                '10.10.55.168',
                '10.10.44.182',
                '10.10.11.117',
                '10.10.61.188',
                '10.10.20.185',
                '10.10.23.248',
                '10.10.12.220',
                '10.10.47.159',
                '10.10.20.246',
                '10.10.48.63',
                '10.10.3.220',
                '10.10.26.136',
                '10.10.33.56',
                '10.10.23.206',
                '10.10.33.181',
                '10.10.16.222',
                '10.10.42.177',
                '10.10.26.34',
                '10.10.43.25',
                '10.10.63.23',
                '10.10.9.88',
                '10.10.40.232',
                '10.10.21.114',
                '10.10.30.64',
                '10.10.57.150',
                '10.10.58.239',
                '10.10.12.233',
                '10.10.10.133',
                '10.10.43.187',
                '10.10.56.107',
                '10.10.10.2',
                '10.10.17.153',
                '10.10.23.121',
                '10.10.9.89',
                '10.10.24.75',
                '10.10.37.60',
                '10.10.53.241',
                '10.10.53.53',
                '10.10.10.20',
                '10.10.48.143',
                '10.10.24.108',
                '10.10.32.151',
                '10.10.37.49',
                '10.10.38.151',
                '10.10.53.138',
                '10.10.46.153',
                '10.10.1.234',
                '10.10.41.121',
                '10.10.42.86',
                '10.10.3.102',
                '10.10.38.190',
                '10.10.42.50',
                '10.10.2.225',
                '10.10.32.64',
                '10.10.32.169',
                '10.10.8.222',
                '10.10.56.166',
                '10.10.5.108',
            ],
        '6': [
            '10.10.162.26',
            '10.10.179.164',
            '10.10.166.93',
            '10.10.178.220',
            '10.10.198.153',
            '10.10.194.93',
            '10.10.147.178',
            '10.10.155.78',
            '10.10.152.33',
            '10.10.185.25',
            '10.10.159.49',
            '10.10.168.146',
            '10.10.197.207',
            '10.10.175.106',
            '10.10.195.28',
            '10.10.198.242',
            '10.10.188.64',
            '10.10.198.231',
            '10.10.159.234',
            '10.10.197.116',
            '10.10.187.93',
            '10.10.146.157',
            '10.10.167.208',
            '10.10.149.182',
            '10.10.164.38',
            '10.10.161.17',
            '10.10.170.111',
            '10.10.146.238',
            '10.10.152.40',
            '10.10.168.37',
            '10.10.163.81',
            '10.10.177.23',
            '10.10.145.130',
            '10.10.148.21',
            '10.10.172.8',
            '10.10.176.51',
            
            '10.10.189.107',
            '10.10.141.222',
            '10.10.131.248',
            '10.10.119.187',
            '10.10.125.39',
            '10.10.127.131',
            '10.10.125.19',
            '10.10.128.60',
            '10.10.135.238',
            '10.10.132.115',
            '10.10.137.119',
            '10.10.144.220',
            '10.10.117.9',
            '10.10.123.194',
            '10.10.139.21',
            '10.10.128.180',
            '10.10.138.19',
            '10.10.119.204',
            '10.10.143.92',
            '10.10.130.143',
            '10.10.140.165',
            '10.10.125.219',
            '10.10.139.162',
            '10.10.119.223',
            '10.10.124.52',
            '10.10.121.33',
            '10.10.142.241',
        ],
        '7': [
            '10.10.144.109',
            '10.10.129.219',
            '10.10.132.186',
            '10.10.134.163',
            '10.10.129.60',
            '10.10.136.149',
            '10.10.135.204',
            '10.10.140.242',
            '10.10.126.80',
            '10.10.121.35',
            '10.10.138.143',
            '10.10.135.130',
            '10.10.140.31',
            '10.10.115.235',
            '10.10.129.101',
            '10.10.134.172',
            '10.10.129.246',
            '10.10.123.91',
            '10.10.120.149',
            '10.10.123.169',
            '10.10.139.164',
            '10.10.114.127',
            '10.10.144.184',
            '10.10.127.176',
            '10.10.133.49',
            '10.10.133.142',
            '10.10.126.245',
            '10.10.127.5',
            '10.10.115.147',
            '10.10.130.13',
            '10.10.131.82',
            '10.10.120.21',
            '10.10.139.80',
            '10.10.130.142',
            '10.10.115.40',
            '10.10.114.165',
            '10.10.116.211',
            '10.10.138.65',
            '10.10.128.5',
            '10.10.136.205',
            '10.10.124.246',
            '10.10.134.124',
            '10.10.128.156',
            '10.10.132.5',
            '10.10.133.42',
            '10.10.137.252',
            '10.10.117.108',
            '10.10.121.41',
            '10.10.131.28',
            '10.10.139.152',
            '10.10.127.2',
            '10.10.132.135',
            '10.10.142.4',
            '10.10.123.26',
            '10.10.125.209',
            '10.10.142.48',
            '10.10.143.252',
            '10.10.129.244',
            '10.10.143.91',
            '10.10.129.157',
            '10.10.118.30',
            '10.10.114.186',
            '10.10.144.45',
            '10.10.124.216',
        ],
        '8': [
            '10.10.137.167',
            '10.10.120.157',
            '10.10.144.206',
            '10.10.130.117',
            '10.10.121.8',
            '10.10.122.243',
            '10.10.117.193',
            '10.10.134.249',
            '10.10.127.71',
            '10.10.129.21',
            '10.10.119.208',
            '10.10.118.6',
            '10.10.125.196',
            '10.10.131.86',
            '10.10.122.101',
            '10.10.141.240',
            '10.10.131.32',
            '10.10.115.27',
            '10.10.128.100',
            '10.10.136.79',
            '10.10.128.72',
            '10.10.115.229',
            '10.10.129.171',
            '10.10.119.234',
            '10.10.136.181',
            '10.10.128.85',
            '10.10.114.104',
            '10.10.121.242',
            '10.10.114.130',
            '10.10.120.16',
            '10.10.130.23',
            '10.10.142.90',
            '10.10.142.20',
            '10.10.118.66',
            '10.10.133.104',
            '10.10.129.191',
            '10.10.124.169',
            '10.10.116.186',
            '10.10.139.89',
            '10.10.134.84',
            '10.10.126.5',
            '10.10.116.107',
            '10.10.142.166',
            '10.10.133.12',
            '10.10.127.218',
            '10.10.130.109',
            '10.10.120.58',
            '10.10.130.5',
            '10.10.123.32',
            '10.10.114.251',
            '10.10.115.213',
            '10.10.126.59',
            '10.10.129.201',
            '10.10.122.134',
            '10.10.134.202',
            '10.10.139.104',
            '10.10.115.206',
            '10.10.126.108',
            '10.10.144.83',
            '10.10.137.127',
            '10.10.144.170',
            '10.10.136.168',
            '10.10.116.23',
            '10.10.134.216',
        ],
        '9': [
            '10.10.126.238',
            '10.10.126.48',
            '10.10.137.199',
            '10.10.129.26',
            '10.10.127.97',
            '10.10.136.196',
            '10.10.142.80',
            '10.10.126.222',
            '10.10.123.50',
            '10.10.137.90',
            '10.10.128.239',
            '10.10.129.202',
            '10.10.136.192',
            '10.10.127.188',
            '10.10.120.243',
            '10.10.138.7',
            '10.10.129.45',
            '10.10.142.10',
            '10.10.134.83',
            '10.10.121.249',
            '10.10.121.22',
            '10.10.115.172',
            '10.10.130.216',
            '10.10.144.140',
            '10.10.116.78',
            '10.10.122.64',
            '10.10.143.32',
            '10.10.136.80',
            '10.10.131.124',
            '10.10.117.158',
            '10.10.133.200',
            '10.10.134.36',
            '10.10.139.27',
            '10.10.138.83',
            '10.10.122.67',
            '10.10.122.63',
            '10.10.116.75',
            '10.10.142.198',
            '10.10.136.106',
            '10.10.140.189',
            '10.10.119.202',
            '10.10.132.45',
            '10.10.126.19',
            '10.10.136.233',
            '10.10.121.30',
            '10.10.114.101',
            '10.10.123.174',
            '10.10.132.117',
            '10.10.127.87',
            '10.10.138.174',
            '10.10.116.46',
            '10.10.130.59',
            '10.10.101.153',
            '10.10.101.148',
            '10.10.111.150',
            '10.10.108.200',
            '10.10.97.211',
            '10.10.104.210',
            '10.10.105.125',
            '10.10.102.243',
            '10.10.108.243',
            '10.10.109.233',
            '10.10.111.199',
            '10.10.104.227',
        ],
        '10': [
            '10.10.109.188',
            '10.10.106.253',
            '10.10.105.114',
            '10.10.109.17',
            '10.10.101.54',
            '10.10.110.178',
            '10.10.107.199',
            '10.10.104.55',
            '10.10.99.163',
            '10.10.112.54',
            '10.10.105.119',
            '10.10.97.55',
            '10.10.106.52',
            '10.10.99.26',
            '10.10.99.173',
            '10.10.105.231',
            '10.10.101.164',
            '10.10.108.15',
            '10.10.105.161',
            '10.10.106.153',
            '10.10.109.150',
            '10.10.108.161',
            '10.10.105.168',
            '10.10.102.198',
            '10.10.108.84',
            '10.10.107.88',
            '10.10.100.126',
            '10.10.99.148',
            '10.10.108.176',
            '10.10.99.253',
            '10.10.111.222',
            '10.10.102.32',
            '10.10.102.76',
            '10.10.112.119',
            '10.10.99.179',
            '10.10.99.243',
            '10.10.102.59',
            '10.10.98.52',
            '10.10.100.7',
            '10.10.105.214',
            '10.10.104.46',
            '10.10.99.193',
            '10.10.101.138',
            '10.10.98.19',
            '10.10.108.111',
            '10.10.109.179',
            '10.10.103.124',
            '10.10.103.157',
            '10.10.97.38',
            '10.10.107.94',
            '10.10.108.210',
            '10.10.112.206',
            '10.10.100.195',
            '10.10.103.98',
            '10.10.100.251',
            '10.10.104.188',
            '10.10.98.107',
            '10.10.103.193',
            '10.10.107.13',
            '10.10.99.188',
            '10.10.112.217',
            '10.10.94.106',
            '10.10.86.8',
            '10.10.109.188',
        ],
        '11': [
            '10.10.65.10',
            '10.10.72.172',
            '10.10.73.160',
            '10.10.79.169',
            '10.10.80.58',
            '10.10.79.63',
            '10.10.69.76',
            '10.10.67.136',
            '10.10.77.98',
            '10.10.76.74',
            '10.10.76.211',
            '10.10.65.173',
            '10.10.79.70',
            '10.10.72.118',
            '10.10.73.34',
            '10.10.72.191',
            '10.10.70.89',
            '10.10.72.91',
            '10.10.69.13',
            '10.10.75.192',
            '10.10.80.95',
            '10.10.80.56',
            '10.10.80.162',
            '10.10.69.212',
            '10.10.78.195',
            '10.10.72.132',
            '10.10.67.181',
            '10.10.78.63',
            '10.10.80.33',
            '10.10.71.178',
            '10.10.67.47',
            '10.10.70.187',
            '10.10.78.26',
            '10.10.75.126',
            '10.10.24.4',
            '10.10.85.147',
            '10.10.35.65',
            '10.10.37.156',
            '10.10.61.177',
            '10.10.55.167',
            '10.10.54.34',
            '10.10.60.158',
            '10.10.15.77',
            '10.10.2.5',
            '10.10.27.232',
            '10.10.22.97',
            '10.10.42.231',
            '10.10.40.168',
            '10.10.2.64',
            '10.10.47.239',
            '10.10.4.63',
            '10.10.17.148',
            '10.10.60.75',
            '10.10.10.142',
            '10.10.40.37',
            '10.10.28.71',
            '10.10.42.148',
            '10.10.1.233',
            '10.10.37.119',
            '10.10.11.104',
            '10.10.64.13',
            '10.10.11.142',
            '10.10.15.50',
            '10.10.59.190',
        ],
        '12': [
            '10.10.54.73',
            '10.10.40.188',
            '10.10.12.171',
            '10.10.45.82',
            '10.10.22.98',
            '10.10.12.218',
            '10.10.64.251',
            '10.10.51.176',
            '10.10.242.248',
            '10.10.229.35',
            '10.10.237.171',
            '10.10.214.85',
            '10.10.228.62',
            '10.10.231.55',
            '10.10.219.103',
            '10.10.220.104',
            '10.10.220.150',
            '10.10.237.148',
            '10.10.248.164',
            '10.10.249.141',
            '10.10.239.146',
            '10.10.247.169',
            '10.10.230.252',
            '10.10.234.87',
            '10.10.233.209',
            '10.10.241.157',
            '10.10.249.40',
            '10.10.215.244',
            '10.10.229.189',
            '10.10.220.147',
            '10.10.249.142',
            '10.10.220.110',
            '10.10.235.220',
            '10.10.245.98',
            '10.10.223.154',
            '10.10.239.232',
            '10.10.236.130',
            '10.10.232.99',
            '10.10.237.154',
            '10.10.225.46',
            '10.10.243.78',
            '10.10.245.158',
            '10.10.219.247',
            '10.10.244.235',
            '10.10.242.27',
            '10.10.227.243',
            '10.10.232.128',
            '10.10.213.16',
            '10.10.231.114',
            '10.10.221.60',
            '10.10.240.226',
            '10.10.245.172',
            '10.10.214.44',
            '10.10.227.228',
            '10.10.217.55',
            '10.10.227.236',
            '10.10.227.43',
            '10.10.226.235',
            '10.10.238.204',
            '10.10.224.99',
            '10.10.246.171',
            '10.10.243.92',
            '10.10.239.188',
            '10.10.232.12',
        ],
        '13': [
            '10.10.212.201',
            '10.10.215.68',
            '10.10.229.216',
            '10.10.229.34',
            '10.10.226.198',
            '10.10.230.223',
            '10.10.240.3',
            '10.10.224.167',
            '10.10.240.118',
            '10.10.248.5',
            '10.10.221.119',
            '10.10.226.185',
            '10.10.241.126',
            '10.10.228.219',
            '10.10.245.4',
            '10.10.248.249',
            '10.10.9.180',
            '10.10.54.171',
            '10.10.41.96',
            '10.10.10.101',
            '10.10.13.50',
            '10.10.62.161',
            '10.10.1.192',
            '10.10.16.111',
            '10.10.3.166',
            '10.10.26.160',
            '10.10.26.209',
            '10.10.3.114',
            '10.10.64.43',
            '10.10.46.38',
            '10.10.1.18',
            '10.10.213.186',
            '10.10.230.139',
            '10.10.243.207',
            '10.10.228.218',
            '10.10.222.20',
            '10.10.246.54',
            '10.10.219.210',
            '10.10.246.106',
            '10.10.232.133',
            '10.10.228.201',
            '10.10.245.76',
            '10.10.219.144',
            '10.10.237.158',
            '10.10.222.115',
            '10.10.243.13',
            '10.10.240.241',
            '10.10.217.102',
            '10.10.212.154',
            '10.10.223.18',
            '10.10.219.101',
            '10.10.212.115',
            '10.10.125.73',
            '10.10.126.127',
            '10.10.130.183',
            '10.10.139.124',
            '10.10.126.176',
            '10.10.135.191',
            '10.10.124.117',
            '10.10.141.101',
            '10.10.122.210',
            '10.10.127.127',
            '10.10.140.138',
            '10.10.123.109',
        ],
        '14': [
            '10.10.135.232',
            '10.10.136.132',
            '10.10.124.176',
            '10.10.135.168',
            '10.10.134.223',
            '10.10.130.205',
            '10.10.140.185',
            '10.10.115.64',
            '10.10.136.153',
            '10.10.137.69',
            '10.10.133.46',
            '10.10.114.179',
            '10.10.127.82',
            '10.10.143.217',
            '10.10.129.12',
            '10.10.131.193',
            '10.10.117.96',
            '10.10.126.60',
            '10.10.130.240',
            '10.10.118.9',
            '10.10.130.225',
            '10.10.115.96',
            '10.10.130.72',
            '10.10.121.220',
            '10.10.121.57',
            '10.10.116.96',
            '10.10.125.76',
            '10.10.123.36',
            '10.10.126.161',
            '10.10.137.74',
            '10.10.121.73',
            '10.10.116.124',
            '10.10.144.248',
            '10.10.114.109',
            '10.10.116.79',
            '10.10.123.90',
            '10.10.137.246',
            '10.10.124.131',
            '10.10.130.79',
            '10.10.125.222',
            '10.10.139.77',
            '10.10.138.24',
            '10.10.141.72',
            '10.10.115.49',
            '10.10.113.10',
            '10.10.116.60',
            '10.10.143.221',
            '10.10.141.87',
            '10.10.142.197',
            '10.10.124.158',
            '10.10.117.86',
            '10.10.143.152',
            '10.10.125.62',
            '10.10.119.180',
            '10.10.133.187',
            '10.10.144.247',
            '10.10.116.187',
            '10.10.131.206',
            '10.10.128.242',
            '10.10.122.65',
            '10.10.123.129',
            '10.10.123.131',
            '10.10.132.9',
            '10.10.134.90',
        ],
        '15': [
            '10.10.143.235',
            '10.10.135.101',
            '10.10.134.79',
            '10.10.121.183',
            '10.10.126.23',
            '10.10.137.198',
            '10.10.123.83',
            '10.10.130.156',
            '10.10.126.213',
            '10.10.116.248',
            '10.10.121.139',
            '10.10.135.224',
            '10.10.126.53',
            '10.10.130.68',
            '10.10.124.249',
            '10.10.141.59',
            '10.10.131.183',
            '10.10.136.57',
            '10.10.132.53',
            '10.10.131.12',
            '10.10.127.171',
            '10.10.140.90',
            '10.10.116.204',
            '10.10.137.185',
            '10.10.142.129',
            '10.10.117.97',
            '10.10.132.19',
            '10.10.127.43',
            '10.10.118.106',
            '10.10.141.160',
            '10.10.137.187',
            '10.10.143.125',
            '10.10.112.203',
            '10.10.104.152',
            '10.10.109.107',
            '10.10.108.68',
            '10.10.108.23',
            '10.10.104.240',
            '10.10.104.185',
            '10.10.110.126',
            '10.10.99.19',
            '10.10.97.136',
            '10.10.98.162',
            '10.10.102.130',
            '10.10.105.64',
            '10.10.104.112',
            '10.10.110.171',
            '10.10.109.196',
            '10.10.105.104',
            '10.10.106.219',
            '10.10.102.238',
            '10.10.108.206',
            '10.10.104.208',
            '10.10.106.225',
            '10.10.109.38',
            '10.10.111.68',
            '10.10.107.86',
            '10.10.97.228',
            '10.10.107.139',
            '10.10.110.125',
            '10.10.101.67',
            '10.10.102.120',
            '10.10.103.21',
            '10.10.103.179',
            '10.10.101.34',
            '10.10.107.17',
            '10.10.98.79',
            '10.10.108.207',
        ],
    }

    # sys._getframe().f_lineno
    def change_gw(self, line_num, sys_num='1'):
        print('change gw %s' % str(line_num))
        gw_list_useful = self.gw_list[str(sys_num)]
        print('use gw sys_num %s' % sys_num)
        aa = os.popen("/sbin/route -n|grep '^0.0.0.0'|awk '{print $2}'")
        for a in aa:
            gw = a.strip()
        try:
            new = gw_list_useful[(gw_list_useful.index(gw) + 1) % 100]
        except:
            new = gw_list_useful[0]
        print(new, gw)
        try:
            bb = '/sbin/route add default gw %s && /sbin/route delete default gw %s ' % (new, gw)
            os.system(bb)

            print('%s to %s' % (new, gw))
            print('change gw sleep 20')
            # time.sleep(20)
        except Exception as e:
            print e
            print('change gw error')
            sys.exit()


if __name__ == "__main__":
    now = datetime.datetime.now()
    print("start at %s" % now.strftime("%Y-%m-%d %H:%M:%S"))
    p = Public()
    print p.get_proxy()
    print p.get_user_agent()