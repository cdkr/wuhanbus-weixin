#encoding:utf-8

import re
import hashlib
import time
import xml.etree.ElementTree as ET

from django.http import HttpResponse
from django.views.generic.base import View

import api

TOKEN = 'whbus'


class Weixin(View):
    def get(self, request):
        echostr = request.GET.get("echostr") if is_from_weixin(request) else 'error'
        return HttpResponse(echostr)

    def post(self, request):
        # if is_from_weixin(request):
        return _weixin(request)


def _weixin(request):
    msg = parse_msg(request.body)

    if msg['MsgType'] == 'event':
        if msg['Event'] == 'CLICK ':
            pass

    content = msg['Content']

    if re.match(r'^\d+', content):
        q = content
        lines = api.get_lines(q)

        s = ('\n' + '-' * 26 + '\n').join(
            line['name']
            + '\n\n'
            + line['stats'].replace(';', '\n')
            for line in lines)

        return response_text_msg(msg, s)

    else:
        q = content
        stats = api.get_stats(q)

        s = compress_stats(stats)

        return response_text_msg(msg, s)

        #return response_text_msg(msg, msg['Content'])


def compress_stats(stats):
    stats = [_compress_stat(stat) for stat in stats]

    return '\n'.join(stats)


def _compress_stat(stat):
    stat['line_names'] = stat['line_names'].replace(')', '').split(';')

    appeared_lines = []

    r = ''
    for numbers in stat['line_names']:
        k, v = numbers.split('(')
        if not k in appeared_lines:
            appeared_lines.append(k)
            r += '%s  %s\n' % (k.replace(u'路', ''), v)

    return '%s\n%s' % (stat['name'], r)


def is_from_weixin(request):
    data = request.GET

    signature = data.get("signature", None)
    timestamp = data.get("timestamp", None)
    nonce = data.get("nonce", None)
    token = TOKEN

    tmplist = [token, timestamp, nonce]
    tmplist.sort()
    tmpstr = "%s%s%s" % tuple(tmplist)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()

    return tmpstr == signature


def parse_msg(rawmsgstr):
    root = ET.fromstring(rawmsgstr)
    msg = {child.tag: child.text for child in root}
    return msg


HELP_INFO = \
    u'【下单】\n' \
    u'输入#编号 数量 编号 数量......\n比如#1 3个  2 4斤\n\n' \
    u'如果要送到其他地址在后面加上@收货信息\n\n' \
    u'如果要求在某个时间送货加上&时间\n' \
    u'比如#1 3个 @13012345678 C3-421 &明天下午'

TEXT_MSG_TPL = \
    u"""
    <xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    <FuncFlag>0</FuncFlag>
    </xml>
    """

IMG_TEXT_MAG_TPL = \
    u"""
    <xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>1</ArticleCount>
    <Articles>
    <item>
    <Title><![CDATA[%s]]></Title>
    <Description><![CDATA[%s]]></Description>
    <PicUrl><![CDATA[%s]]></PicUrl>
    </item>
    </Articles>
    </xml>
    """

WELCOME_MSG = \
    u"""
    欢迎关注武汉公交
    """


def response_text_msg(msg, content):
    s = TEXT_MSG_TPL % (msg['FromUserName'], msg['ToUserName'],
                        str(int(time.time())), content)
    return HttpResponse(s)


def response_text_img_msg(msg, title, description, picurl):
    s = IMG_TEXT_MAG_TPL % (msg['FromUserName'], msg['ToUserName'],
                            str(int(time.time())), title, description, picurl)
    return HttpResponse(s)