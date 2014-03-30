#encoding:utf-8
import urllib2
import json
import requests
from datetime import datetime, timedelta

from django.conf import settings
from django.db.models.signals import post_save, post_delete

from models import Fruit


APPID = settings.WX_APPID
APPSECRET = settings.WX_APPSECRET


class _AccessToken(str):
    def __init__(self):
        super(_AccessToken, self).__init__()
        self.last_refresh = None
        self._token = ''

    def __str__(self):
        return self.token

    def __repr__(self):
        return self.__str__()

    @property
    def token(self):
        if not self._token:
            self._refresh()

        elif datetime.now() - self.last_refresh > timedelta(seconds=7130):
            self._refresh()

        return self._token

    def _refresh(self):
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' \
              % (APPID, APPSECRET)

        self.last_refresh = datetime.now()
        response_data = json.loads(urllib2.urlopen(url).read())

        try:
            self._token = response_data['access_token']
        except KeyError:
            self._token = ''


ACCESSON_TOKEN = _AccessToken()

menu_data = {
    "button": [
        {
            "name": "水果",
            "sub_button": [
                {
                    "type": "click",
                    "name": "Sh",
                    "key": "V1001_TODAY_SINGER"
                }
            ]
        },
        {
            "name": "订单",
            "sub_button": [
                {
                    "type": "click",
                    "name": "未发货订单",
                    "key": "ONTHEWAY",
                },
                {
                    "type": "click",
                    "name": "取消订单",
                    "key": "DEL",
                },
                {
                    "type": "click",
                    "name": "立即下单",
                    "key": "NORMAL",
                },
                {
                    "type": "click",
                    "name": "使用说明",
                    "key": "INTRO",
                }
            ]
        },
        {
            "name": "功能",
            "sub_button": [
                {
                    "type": "click",
                    "name": "关于我们",
                    "key": "ABOUT",
                },
                {
                    "type": "click",
                    "name": "收货信息",
                    "key": "INFO",
                },
                {
                    "type": "click",
                    "name": "发货时间",
                    "key": "TIME",
                }
            ]
        }]
}


def update_menu():
    menu_data = data
    requests.post('https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s' % ACCESSON_TOKEN,
                  data=json.dumps(menu_data, ensure_ascii=False, encoding='utf-8'))