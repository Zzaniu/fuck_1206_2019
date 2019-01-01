#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Software    : nothing_project
# @File        : fuck_login.py
# @Author      : zaniu (Zzaniu@126.com)
# @Date        : 2019/1/1 14:04 
# @Description :
import json
import os
import re
from time import sleep

from numpy import random
from urllib.parse import quote

import requests
import time
from urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


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
        self.session.get(url=index_url, verify=False)
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
        """识别验证码(最难点)"""
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


    def login(self):
        """模拟登陆"""
        check_code = None
        while True:
            callback_code = self.get_login_images()
            if callback_code:
                check_code = self.check_images_code(callback_code)
                if check_code:
                    break
            sleep_number = random.randint(0,3)
            print('校验失败，{}秒后继续获取验证码校验...'.format(sleep_number))
            sleep(sleep_number)
        login_url = "https://kyfw.12306.cn/passport/web/login"
        login_data = {
            'username': 'hugong2',
            'password': 'wenjunai93',
            'appid': 'otn',
            'answer': '{}'.format(check_code),
        }
        response = self.session.post(url=login_url, data=login_data, verify=False)
        print(response.text)


if __name__ == "__main__":
    s = FuckLogin()
    s.login()

