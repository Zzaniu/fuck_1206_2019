#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Software    : nothing_project
# @File        : fuck_login.py
# @Author      : zaniu (Zzaniu@126.com)
# @Date        : 2019/1/1 14:04 
# @Description : 元旦闲着没事写的代码，目的是想自己抢票~~~
import datetime
import json
import os
import re
from time import sleep

from numpy import random
from urllib.parse import quote, unquote

import requests
import time
from urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from fuck_12306 import settings


image_code_dict = {
    '1': '38,49',
    '2': '106,48',
    '3': '188,49',
    '4': '257,49',
    '5': '44,121',
    '6': '107,115',
    '7': '188,123',
    '8': '257,122',
}


class FuckLogin(object):
    def __init__(self):
        self.session = requests.session()
        self.CookieDir = '12306cookie'

    def save_cookie(self):
        with open(self.CookieDir, "w") as output:
            cookies = self.session.cookies.get_dict()
            print('cookies = ', self.session.cookies.get_dict())
            json.dump(cookies, output)
        print("已在目录下生成cookie文件")

    def get_cookie(self):
        """获取cookie"""
        if os.path.exists(self.CookieDir):
            with open(self.CookieDir, "r") as f:
                cookie = json.load(f)
                return cookie
        else:
            if os.path.exists(self.CookieDir):
                os.remove(self.CookieDir)
            return self.get_login_images()

    def get_login_images(self):
        """下载12306验证码"""
        index_url = 'https://kyfw.12306.cn/otn/resources/login.html'
        header = {
            'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'kyfw.12306.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.session.headers.update(header)
        self.session.get(url=index_url, verify=False)  # 访问12306首页，这一步应该是可以省略的，这里先不删除了，以后再整理
        self.save_cookie()
        self.session.headers.update({'Referer': 'https://kyfw.12306.cn/otn/resources/login.html'})
        _str_now_time = str(time.time() * 1000).split('.')[0]
        str_now_time = str(int(_str_now_time) - 1200000)
        image_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&{0}&callback=jQuery19107746992860815924_{1}&_={2}'.format(_str_now_time, str_now_time, str_now_time)
        self.session.headers.update(header)
        response = self.session.get(url=image_url, verify=False)  # verify 屏蔽证书
        print('session.cookies.get_dict() = ', self.session.cookies.get_dict())
        response.encoding = 'utf8'
        if response.status_code == 200:
            self.save_cookie()
            print('response.text = ', response.text)
            image = re.search('(jQuery\d+?_\d+)[\s\S]+?"image":"([\s\S]+?)"', response.text)
            callback = image.group(1)
            print('callback = ', callback)
            import base64
            # python解码data: image开头的图片地址
            img = base64.urlsafe_b64decode(image.group(2) + '=' * (4 - len(image.group(1)) % 4))  # 从URL中解析出图片
            with open('check_12306_images.jpg', 'wb') as f:
                f.write(img)
            return callback
        else:
            print('下载图片失败, 状态码:{}'.format(response.status_code))
            print(response.text)

    def known_images(self):
        """识别12306验证码(难点),可考虑打码或者百度识图，AI就不想了。。。"""
        pass

    def check_images_code(self, callback):
        """发送验证码校验"""
        header = {
            'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/resources/login.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-Cache-Control': 'no-cache-With',
            'Pragma': 'no-cache',
        }
        _time = str(int(callback.split('_')[1])+1)
        check_code = input("请输入验证码: ")
        _code = []
        for code in check_code.split(','):
            _code.append(image_code_dict.get(code))
        _code = ','.join(_code)
        check_code = quote(_code)
        print('check_code = ', check_code)
        check_images_url = "https://kyfw.12306.cn/passport/captcha/captcha-check?callback={0}&answer={1}&rand=sjrand&login_site=E&_={2}".format(callback, check_code, _time, )
        print('check_images_url = ', check_images_url)
        self.session.headers.update(header)
        response = self.session.get(url=check_images_url, verify=False, cookies=self.get_cookie())
        print('response_check = ', response.text)
        if response.text.find('失败') > -1:
            return False
        else:
            return _code

    def check_user(self):
        """验证账号密码"""
        check_code = None
        while True:
            callback_code = self.get_login_images()
            if callback_code:
                check_code = self.check_images_code(callback_code)
                if check_code:
                    break
            sleep_number = random.randint(0, 3)
            print('校验失败，{}秒后继续获取验证码校验...'.format(sleep_number))
            sleep(sleep_number)
        login_url = "https://kyfw.12306.cn/passport/web/login"
        login_data = {
            'username': settings.USERNAME,
            'password': settings.PASSWD,
            'appid': 'otn',
            'answer': '{}'.format(check_code),
        }
        response = self.session.post(url=login_url, data=login_data, verify=False)
        if response.text.find('登录成功') > -1:
            self.save_cookie()
            print('response.text = ', response.text)
            print('账户验证成功')
            return True
        else:
            print('账户验证失败')
            return False

    def get_login_cookie(self):
        """登录动作，获取cookie"""
        url = 'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin'
        header = {
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://kyfw.12306.cn/otn/resources/login.html',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        response = self.session.get(url=url, headers=header, cookies=self.get_cookie())
        if response.status_code == 200:
            self.save_cookie()
            print('登录动作执行成功')
        else:
            print('登录动作执行失败')

    def check_uamtk(self):
        url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        header = {
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://kyfw.12306.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        data = {'appid': 'otn'}
        response = self.session.post(url=url, headers=header, data=data, cookies=self.get_cookie())
        print('response = ', response.text)
        res = response.json()
        if res.get('result_code') == 0:
            self.save_cookie()
            print('uamtk 验证通过')
            return res.get('newapptk')
        else:
            print('uamtk 验证失败')

    def check_uamauthclient(self, tk):
        """验证uamauthclient"""
        url = 'https://kyfw.12306.cn/otn/uamauthclient'
        header = {
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': '*/*',
            'Origin': 'https://kyfw.12306.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        data = {'tk': tk}
        response = self.session.post(url=url, headers=header, data=data, cookies=self.get_cookie())
        print(response.text)
        res = response.json()
        if res.get('result_code') == 0:
            self.save_cookie()
            print('tk 验证通过')
        else:
            print('tk 验证失败')

    def login(self):
        """模拟登录，包括一整套动作"""
        while True:
            try:
                if self.check_user():
                    self.get_login_cookie()
                    s.check_uamauthclient(self.check_uamtk())
                    print('登录成功')
                    break
            except:
                sleep_time = random.randint(1, 3)
                print('登录失败，{}秒后继续登录'.format(sleep_time))
                sleep(sleep_time)

    def _get_train_ticket_sz_xh(self):
        """写死了深圳到新化，因为我只买深圳-新化,需要别的地方可以传参城市或者写在settings里面"""
        header = {
            'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/resources/login.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-Cache-Control': 'no-cache-With',
            'Pragma': 'no-cache',
        }
        query_url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={0}&leftTicketDTO.from_station=SZQ&leftTicketDTO.to_station=EHQ&purpose_codes=ADULT'.format(settings.GO_DATE)
        response = self.session.get(url=query_url, headers=header, verify=False, cookies=self.get_cookie())
        return response

    def get_train_tocket_sz_xh(self):
        try:
            response = self._get_train_ticket_sz_xh()
            res = response.json()
            if res.get('status'):
                print('{0}深圳-新化列车查询成功, 当前时间{1}'.format(settings.GO_DATE, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                print('info: {}'.format(res))
                return res.get('data').get('result')
        except:
            print('查询失败...data: {}'.format(response.text))
            return False

    def prase_data(self, datas):
        data = {}
        for i in datas:
            tmp_list = i.split('|')
            data[tmp_list[3]] = {
                'secretStr': tmp_list[0],
                '无座': tmp_list[26],
                '硬座': tmp_list[29],
                '硬卧': tmp_list[28],
                '软卧': tmp_list[23],
                '二等座': tmp_list[30],
                '一等座': tmp_list[31],
                'train_location': tmp_list[15].strip(),
                'stationTrainCode': tmp_list[3].strip(),
                'toStationTelecode': tmp_list[7].strip(),
                'fromStationTelecode': tmp_list[6].strip(),
                'train_no': tmp_list[2].strip().replace(' ', ''),
                'leftTicket': tmp_list[12].strip(),
            }
        print(data)
        return data

    def get_train_ticket_xh_sz(self):
        """写死了深圳到新化，因为我只买新化-深圳"""
        pass

    def check_login(self):
        """验证是否已经登录"""
        url = 'https://kyfw.12306.cn/otn/login/checkUser'
        header = {
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Origin': 'https://kyfw.12306.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'If-Modified-Since': '0',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        data = {'_json_att': ''}
        response = self.session.post(url=url, headers=header, data=data, cookies=self.get_cookie())
        print(response.text)
        res = response.json()
        return res.get("data").get("flag")

    def send_order(self, datas):
        """发送订单信息"""
        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        header = {
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': '*/*',
            'Origin': 'https://kyfw.12306.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        data = {
            'secretStr': unquote(datas['K9006'].get('secretStr')),
            'train_date': settings.GO_DATE,
            'back_train_date': datetime.date.today().strftime('%Y-%m-%d'),
            'tour_flag': 'dc',
            'purpose_codes': 'ADULT',
            'query_from_station_name': '深圳',
            'query_from_station_name': '新化',
            'undefined': '',
        }
        response = self.session.post(url=url, headers=header, data=data, cookies=self.get_cookie())
        print('order = ', response.text)

    def to_initdc(self):
        """跳转至initDc,提取globalRepeatSubmitToken和key_check_isChange"""
        url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        header = {
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Origin': 'https://kyfw.12306.cn',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        data = {'_json_att': ''}
        response = self.session.post(url=url, headers=header, data=data, cookies=self.get_cookie())
        print('initDc = ', response.text)
        globalRepeatSubmitToken = re.findall(r"globalRepeatSubmitToken\s+=\s+'(\w+)'", response.text)
        key_check_isChange = re.findall(r"'key_check_isChange'\s*:\s*'(\w+)'", response.text)
        return globalRepeatSubmitToken[0], key_check_isChange[0]

    def get_passengers(self, token):
        """获取乘客"""
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        header = {
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'Content-Length': '63',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': '*/*',
            'Origin': 'https://kyfw.12306.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        data = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        response = self.session.post(url=url, headers=header, data=data, cookies=self.get_cookie())
        if response.json().get('status'):
            print('获取乘车人信息成功')
            print(response.json())
        else:
            print('获取乘车人信息失败')

    def check_passengers(self, token):
        """乘车人确认"""
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        header = {
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://kyfw.12306.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        data = {
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': '3,0,1,{0},1,{1},15575971869,N'.format(settings.USER_NAME, settings.ID_CARD),  # 没有电话的话直接空着就行
            'oldPassengerStr': '曾文君,1,432524199305022536,1_',
            'tour_flag': 'dc',
            'randCode': '',
            'whatsSelect': '1',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        response = self.session.post(url=url, headers=header, data=data, cookies=self.get_cookie())
        res = response.json()
        if res.get('status') and not res.get('data').get('errMsg'):
            print('乘车人确认成功')
            print(response.text)
        else:
            print('乘车人确认失败, info = {}'.format(response.text))
            raise Exception('大爷的')

    def send_queue(self, token, datas):
        """准备排队"""
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        header = {
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://kyfw.12306.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        data = {
            'train_date': '{0} {1} 00:00:00 GMT+0800 (中国标准时间)'.format(datetime.date.today().strftime('%a %b'), datetime.datetime.strptime(settings.GO_DATE, '%Y-%m-%d').strftime('%d %Y')),
            'leftTicket': datas.get('leftTicket'),
            'train_location': datas.get('train_location'),
            'stationTrainCode': datas.get('stationTrainCode'),
            'toStationTelecode': datas.get('toStationTelecode'),
            'fromStationTelecode': datas.get('fromStationTelecode'),
            'train_no': datas.get('train_no'),
            'REPEAT_SUBMIT_TOKEN': token,
            'seatType': '3',
            'purpose_codes': '00',
            '_json_att': '',
        }
        response = self.session.post(url=url, headers=header, data=data, cookies=self.get_cookie())
        if response.json().get('status'):
            print('排队准备完毕')
            print(response.json())
        else:
            print('排队准备失败')
            print(response.text)
            raise Exception('大爷的')

    def confirm_buy_trains(self, token, train_date, datas):
        """确认购买"""
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        header = {
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://kyfw.12306.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        data = {
            'oldPassengerStr': '{},1,{},1_'.format(settings.USER_NAME, settings.ID_CARD),
            'train_location': 'QZ',
            'dwAll': 'N',
            'leftTicketStr': datas.get('leftTicket'),
            'key_check_isChange': train_date,
            'REPEAT_SUBMIT_TOKEN': token,
            'passengerTicketStr': '3,0,1,{0},1,{1},,N'.format(settings.USER_NAME, settings.ID_CARD),
            'whatsSelect': '1',
            'seatDetailType': '000',
            'roomType': '00',
            'purpose_codes': '00',
            'randCode': '',
            '_json_att': '',
            'choose_seats': '',
        }
        response = self.session.post(url=url, headers=header, data=data, cookies=self.get_cookie())
        res = response.json()
        if response.json().get('data').get('submitStatus'):
            print('订单已确认，已进入排队状态')
            print(response.text)
        else:
            print('订单确认失败， info = {}'.format(response.text))
            raise Exception('大爷的')

    def get_queue_status(self, token):
        """获取排队状态"""
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime'
        header = {
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Referer': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        data = {
            'random': str(time.time()*1000).split('.')[0],
            'tourFlag': 'dc',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        response = self.session.get(url=url, headers=header, params=data, cookies=self.get_cookie())
        res = response.json()
        status = res.get('status')
        _eid = res.get('data').get('orderId')
        if status and _eid:
            print('--已成功下单, eid = {}'.format(_eid))
            return _eid
        print('昂，还在排队，5S后继续查询')
        return False

    def get_order_info(self, token, orderid):
        """获取火车票订单信息"""
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
        header = {
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://kyfw.12306.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        data = {
            'orderSequence_no': orderid,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token,
        }
        response = self.session.post(url=url, headers=header, data=data, cookies=self.get_cookie())
        res = response.json()
        if res.get('data').get('submitStatus'):
            print('购票成功~~~')
            return True
        else:
            print('购票失败...')
            return False


if __name__ == "__main__":
    # a = 'mFuCr%2F%2F7cxyYOPc%2BGAEyht2RuTfCfDlq7iwAoXimMtYyQAQXSGQox9kC2xU%3D'
    # print(unquote(a))
    if 1:
        s = FuckLogin()
        s.login()
        info = s.prase_data(s.get_train_tocket_sz_xh())
        print(s.check_login())
        s.send_order(info)
        token, isChange = s.to_initdc()
        s.get_passengers(token)
        s.check_passengers(token)
        s.send_queue(token, info.get(settings.TRAINS_NO))
        s.confirm_buy_trains(token, isChange, info.get(settings.TRAINS_NO))
        while True:
            _eid = s.get_queue_status(token)
            print('_eid = ', _eid)
            if _eid:
                print('跳出循环')
                break
            print('还在排队，5S后继续检查')
            sleep(5)
        s.get_order_info(token, _eid)
        # s.confirm_buy_trains(token, isChange)
        # while 1:
        #     data = s.get_train_tocket_sz_xh()
        #     if data:
        #         s.prase_data(data)
        #     sleep(random.randint(3, 5))  # 一开始这里是2S，然后我账号被封了...

