#!/usr/bin/env python
# encoding: utf-8

"""
@file: weibo.py
@time: 2018/6/24 12:42
@desc: 获取指定用户所有微博
@author: hongquanpro@126.com
"""

import requests
from pyquery import PyQuery

headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/u/2145291155',
    'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'),
    'X-Requested-With': 'XMLHttpRequest',
}


def get_page(user_id=None, page=1):
    if user_id is None or user_id == '':
        raise ValueError('The value of user_id is None!')
    url = ('https://m.weibo.cn/api/container/getIndex?type=uid&value=%s'
           '&containerid=107603%s&page=%d' % (user_id, user_id, page))
    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            # 文章详情
            weibo_info = 'https://m.weibo.cn/statuses/extend?id=4243312196576582'
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)
        return None


def parse_page(cards=None):
    if isinstance(cards, dict):
        data = cards.get('data', None)
        if data is not None:
            card_list = data.get('cards', None)
            if card_list is not None:
                for card in card_list:
                    blog = card.get('mblog', None)
                    if blog is not None:
                        print('Post at %s from %s' % (blog.get('created_at', 'unknown'), blog.get('source', 'unknown')))
                        print('%s' % (PyQuery(blog.get('text', '')).text()))
                        print('Click to see full. https://m.weibo.cn/status/%s' % blog['id'])
                        print('-' * 57)
                    else:
                        print('Resolve page failed. The key `mblog` not found')
                        exit()
            else:
                print('Resolve page failed. The key `cards` not found')
                exit()
        else:
            print('Resolve page failed. The key `data` not found')
            exit()
    else:
        raise ValueError('Parse Card Error. The `card` parameter isn\'t dict type')
        exit()


def get_user_info(user_id=None):
    if user_id is None or user_id == '':
        raise ValueError('The value of user_id is None!')
    url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=100505%s' % (user_id, user_id)
    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Request Error', e.args)


def init(user_id=None):
    # 获取用户信息
    result = get_user_info(user_id=user_id)
    if result['ok']:
        user_info = result['data']['userInfo']
        print('[ID:%s]%s' % (user_info['id'], user_info['screen_name']))
        print('Follow:%s | Fans:%s' % (user_info['follow_count'], user_info['followers_count']))
        if user_info.get('verified', False):
            print('certification: %s' % user_info['verified_reason'])
        # 获取微博相关信息
        print('=' * 25 + ' weibo ' + '=' * 25)
        weibo = get_page(user_info['id'])
        if weibo is not None:
            if weibo.get('data', None) is not None:
                data = weibo['data']
                if data.get('cardlistInfo', None) is not None:
                    card_list = data['cardlistInfo']
                    if card_list.get('total', None) is not None:
                        # 获取总页数
                        total_page = card_list['total']
                        total_page = int(total_page / 10 + (1 if total_page % 10 > 0 else 0))
                        # 遍历微博
                        for i in range(1, total_page + 1):
                            wb = get_page(user_info['id'], i)
                            parse_page(wb)
                    else:
                        print('Resolve data failed. The key `total` not found')
                else:
                    print('Resolve data failed. The key `cardlistInfo` not found')
            else:
                print('Resolve data failed. The key `data` not found')
        else:
            print('Fetch weibo content failed')
    else:
        print('Fetch user info Failed. ok code = %s' % result['ok'])


if __name__ == '__main__':
    init(user_id='2145291155')
