import copy
import json
import os
import time
import threading

import requests

from orm.sport import Sport, DBSession, Friend

from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Hello:
    RANK_URL = 'https://quic.yundong.qq.com/pushsport/cgi/rank/friends?g_tk=579475239'
    COOKIES = {'uin': 'o2702746632',
               ' skey': os.getenv('skey'),
               ' p_uin': 'o2702746632',
               ' p_skey': 'hVfF0drVpaF40ob4yXATqrQFAYz1yaG*n26v-JRf2cI_',
               'xClientProtoVer': 'https_https1'}
    HANDLERS = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Le X620 Build/HEXCNFN5902812161S; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/49.0.2623.91 Mobile Safari/537.36 V1_AND_SQ_8.1.5_1258_YYB_D PA QQ/8.1.5.4215 NetType/WIFI WebP/0.4.1 Pixel/1080 StatusBarHeight/63 SimpleUISwitch/0',
        'Content-Type': 'application/x-www-form-urlencoded'}
    BODY_PATTERN = {
        'dcapiKey': 'user_rank',
        'l5apiKey': 'rank_friends',
        'params': '{{"cmd": 1, "pno": {pno}, "dtype": 1, "pnum": 20}}'
    }

    def __init__(self, care_flag=False, name: list = None):
        self.inform_callback = []
        self.friend_all = set()
        self.all_qq = dict()
        self.get_friend()
        self.care_flag = care_flag
        self.sport_rank = {}
        self._make_care = {_: False for _ in name}

        threading.Thread(target=self.clear_make_care).start()

    def inform(self, callback):
        if callback not in self.inform_callback:
            self.inform_callback.append(callback)

    def care(self):
        if not self.care_flag:
            return
        for name in self._make_care:
            if self._make_care[name]:
                continue
            if self.sport_rank.get(name, {}).get('points', 0) > 10:
                self._make_care[name] = True
                current_time = int(time.strftime("%H%M"))
                if current_time < 400:
                    msg = '亲爱的{name} 夜深了，快点睡觉'.format(name=name)
                else:
                    msg = '亲爱的{name} 早安'.format(name=name)
                [f(msg) for f in self.inform_callback]

    def clear_make_care(self):
        while True:
            if time.strftime('%H%M') == '0000':
                for name in self._make_care:
                    self._make_care[name] = False
                while time.strftime('%H%M') == '0000':
                    time.sleep(30)
            time.sleep(30)

    def get_sport_rank(self):
        pno = 1
        while True:
            body = copy.copy(self.BODY_PATTERN)
            body['params'] = self.BODY_PATTERN['params'].format(pno=pno)
            response = requests.post(url=self.RANK_URL, headers=self.HANDLERS, cookies=self.COOKIES,
                                     data=body, verify=False)
            res_dict = json.loads(response.text)
            if res_dict.get('code') == 0:
                rank_list = res_dict.get('data', {}).get('list', [])
                if not rank_list:
                    self.care()
                    return self.sport_rank
                for rank in rank_list:
                    self.sport_rank[rank.get('name')] = {'points': rank.get('points'),
                                                         'rank': rank.get('rank'),
                                                         'qq': rank.get('uin'),
                                                         'appname': rank.get('appname')
                                                         }
                pno += 1

    def save_to_mysql(self):
        session = DBSession()
        timestamp = int(time.time())
        for name, data in self.sport_rank.items():
            new_sport = Sport(
                friend_id=self.all_qq.get(data['qq']),
                points=data['points'],
                timestamp=timestamp
            )
            session.add(new_sport)
        session.commit()
        session.close()

    def get_friend(self):
        session = DBSession()
        query_all = session.query(Friend).all()
        self.friend_all = set((friend.qq, friend.nick_name) for friend in query_all)
        self.all_qq = {friend.qq: friend.id for friend in query_all}
        session.close()

    def add_friend(self):
        session = DBSession()
        current_friend_all = set((data['qq'], nick_name) for nick_name, data in self.sport_rank.items())
        new_friend = current_friend_all - self.friend_all
        for friend in new_friend:
            session.add(Friend(qq=friend[0],
                               nick_name=friend[1]
                               ))
        session.commit()
        session.close()


def main():
    hello = Hello(True, ['葛'])
    while True:
        hello.get_sport_rank()
        hello.add_friend()
        hello.get_friend()
        hello.save_to_mysql()
        time.sleep(3 * 60)


if __name__ == '__main__':
    main()
