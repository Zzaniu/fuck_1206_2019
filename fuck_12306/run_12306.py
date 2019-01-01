#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Software    : nothing_project
# @File        : run_12306.py
# @Author      : zaniu (Zzaniu@126.com)
# @Date        : 2019/1/1 11:00 
# @Description :
import re

import requests
import time

import json
from urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


header = {
    'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'kyfw.12306.cn',
    'Referer': 'https://kyfw.12306.cn/otn/resources/login.html',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

image_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image64'
str_now_time = str(time.time()*1000).split('.')[0]
images_data = {
    'login_site': 'E',
    'module': 'login',
    'rand': 'sjrand',
    str_now_time: '',
    'callback': 'jQuery19106871271910086258_{}'.format(str_now_time),
    '_': 'str_now_time',
}
check_url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
str_now_time = str(time.time()*1000).split('.')[0]
check_data = {
    'callback': 'jQuery19106871271910086258_{}'.format(str_now_time),
    'answer': '48,35,19,128,193,105',
    'rand': 'sjrand',
    'login_site': 'E',
    '_': str_now_time,
}
login_url = ''


if __name__ == "__main__":
    image_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&1546318151296&callback=jQuery191024208348036332363_1546316975253&_=1546316975260'
    sessions = requests.session()
    response = sessions.get(url=image_url, headers=header, verify=False)  # verify 屏蔽证书
    response.encoding = 'utf8'
    if response.status_code == 200:
        print('response.text = ', response.text)
        image = re.search('"image":"([\s\S]+?)"', response.text)
        import base64
        # python解码data: image开头的图片地址
        img = base64.urlsafe_b64decode(image.group(1) + '=' * (4 - len(image.group(1)) % 4))  # 从URL中解析出图片
        with open('check_12306_images.jpg', 'wb') as f:
            f.write(img)
    else:
        print('下载图片失败, 状态码:{}'.format(response.status_code))
        print(response.text)
