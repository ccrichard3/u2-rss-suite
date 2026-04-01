"""必填参数只有 COOKIES 和 API 相关参数
依赖: pip install requests lxml bs4 loguru pytz
"""

import gc
import os
import json
import re
import pytz
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from time import sleep, time
from typing import Dict, List, Union

from requests import get, ReadTimeout, ConnectTimeout
from bs4 import BeautifulSoup
from loguru import logger
import xml.etree.ElementTree as ET
from xml.dom import minidom
from email.utils import format_datetime
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer


# ================= 环境变量配置 =================
def _env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {'1', 'true', 'yes', 'on'}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except Exception:
        return default


def _env_list(name: str, default):
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else default
    except Exception:
        return [x.strip() for x in raw.split(',') if x.strip()]


def _normalize_cookie(raw: str) -> str:
    raw = (raw or '').strip()
    if raw.startswith('nexusphp_u2='):
        return raw.split('=', 1)[1]
    return raw


# ================= 基础配置 =================
COOKIE_VALUE = _normalize_cookie(os.getenv('U2_COOKIE', ''))
COOKIES = {'nexusphp_u2': COOKIE_VALUE} if COOKIE_VALUE else {'nexusphp_u2': ''}
INTERVAL = _env_int('INTERVAL', 120)  # 检查魔法的时间间隔(秒)
API_TOKEN = os.getenv('API_TOKEN', '').strip()
UID = _env_int('UID', 0)
PROXIES = {
    'http': os.getenv('HTTP_PROXY', '').strip(),
    'https': os.getenv('HTTPS_PROXY', '').strip(),
}

# ================= 过滤规则 =================
MAX_SEEDER_NUM = _env_int('MAX_SEEDER_NUM', 5)
DOWNLOAD_NON_FREE = _env_bool('DOWNLOAD_NON_FREE', False)
MIN_DAY = _env_int('MIN_DAY', 7)
DOWNLOAD_OLD = _env_bool('DOWNLOAD_OLD', True)
DOWNLOAD_NEW = _env_bool('DOWNLOAD_NEW', False)
MAGIC_SELF = _env_bool('MAGIC_SELF', False)
EFFECTIVE_DELAY = _env_int('EFFECTIVE_DELAY', 60)
DOWNLOAD_DEAD_TO = _env_bool('DOWNLOAD_DEAD_TO', False)
CHECK_PEERLIST = _env_bool('CHECK_PEERLIST', False)
DA_QIAO = _env_bool('DA_QIAO', True)
MIN_RE_DL_DAYS = _env_int('MIN_RE_DL_DAYS', 0)
CAT_FILTER = _env_list('CAT_FILTER', [])
SIZE_FILTER = _env_list('SIZE_FILTER', [0, -1])
NAME_FILTER = _env_list('NAME_FILTER', [])

# ================= RSS 配置 =================
RSS_MAX_ITEMS = _env_int('RSS_MAX_ITEMS', 20)
RSS_TITLE = os.getenv('RSS_TITLE', 'U2 CatchMagic')
RSS_LINK = os.getenv('RSS_LINK', 'https://u2.dmhy.org/')
RSS_DESCRIPTION = os.getenv('RSS_DESCRIPTION', 'Auto-generated RSS feed for Vertex.')
RSS_HTTP_BIND = os.getenv('RSS_HTTP_BIND', '0.0.0.0')
RSS_HTTP_PORT = _env_int('RSS_HTTP_PORT', 8787)

# ================= 系统路径 =================
DATA_DIR = os.getenv('DATA_DIR', '/app/data')
os.makedirs(DATA_DIR, exist_ok=True)
LOG_PATH = f'{DATA_DIR}/catch_magic.log'
DATA_PATH = f'{DATA_DIR}/catch_magic.data.txt'
RSS_PATH = f'{DATA_DIR}/rss.xml'

R_ARGS = {
    'cookies': COOKIES,
    'headers': {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36'},
    'timeout': 20,
    'proxies': PROXIES
}


class CatchMagic:
    pre_suf = [['时区', '，点击修改。'], ['時區', '，點擊修改。'], ['Current timezone is ', ', click to change.']]

    def __init__(self):
        self.checked = deque([], maxlen=200)
        self.magic_id_0 = None
        self.tid_add_time = {}
        self.rss_items = deque([], maxlen=RSS_MAX_ITEMS)
        self.rss_guids = deque([], maxlen=RSS_MAX_ITEMS)

        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                self.checked = deque(data.get('checked', []), maxlen=200)
                self.magic_id_0 = data.get('id_0')
                self.tid_add_time = data.get('add_time', {})
                self.rss_items = deque(data.get('rss_items', []), maxlen=RSS_MAX_ITEMS)
                self.rss_guids = deque(data.get('rss_guids', []), maxlen=RSS_MAX_ITEMS)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        self.first_time = True

    def info_from_u2(self):
        all_checked = True if self.first_time and not self.magic_id_0 else False
        index = 0
        id_0 = self.magic_id_0

        while True:
            soup = self.get_soup(f'https://u2.dmhy.org/promotion.php?action=list&page={index}')
            user_id = soup.find('table', {'id': 'info_block'}).a['href'][19:]

            for i, tr in filter(lambda tup: tup[0] > 0, enumerate(soup.find('table', {'width': '99%'}))):
                magic_id = int(tr.contents[0].string)
                if index == 0 and i == 1:
                    self.magic_id_0 = magic_id
                    if self.first_time and id_0 and magic_id - id_0 > 10 * INTERVAL:
                        all_checked = True
                if tr.contents[5].string in ['Expired', '已失效'] or magic_id == id_0:
                    all_checked = True
                    break

                if tr.contents[1].string in ['魔法', 'Magic', 'БР']:
                    if not tr.contents[3].a and tr.contents[3].string in ['所有人', 'Everyone', 'Для всех'] \
                            or MAGIC_SELF and tr.contents[3].a and tr.contents[3].a['href'][19:] == user_id:
                        if tr.contents[5].string not in ['Terminated', '终止', '終止', 'Прекращён']:
                            if tr.contents[2].a:
                                tid = int(tr.contents[2].a['href'][15:])
                                if magic_id not in self.checked:
                                    if self.first_time and all_checked:
                                        self.checked.append(magic_id)
                                    else:
                                        yield magic_id, tid
                                    continue

                if magic_id not in self.checked:
                    self.checked.append(magic_id)

            if all_checked:
                break
            else:
                index += 1

    def info_from_api(self):
        r_args = {'timeout': R_ARGS.get('timeout'), 'proxies': R_ARGS.get('proxies')}
        params = {'uid': UID, 'token': API_TOKEN, 'scope': 'public', 'maximum': 30}
        resp = get('https://u2.kysdm.com/api/v1/promotion', **r_args, params=params).json()
        pro_list = resp['data']['promotion']
        if MAGIC_SELF:
            params['scope'] = 'private'
            resp1 = get('https://u2.kysdm.com/api/v1/promotion', **r_args, params=params).json()
            pro_list.extend([pro_data for pro_data in resp1['data']['promotion'] if pro_data['for_user_id'] == UID])

        for pro_data in pro_list:
            magic_id = pro_data['promotion_id']
            tid = pro_data['torrent_id']
            if magic_id == self.magic_id_0:
                break
            if magic_id not in self.checked:
                if self.first_time and not self.magic_id_0:
                    self.checked.append(magic_id)
                else:
                    yield magic_id, tid
        self.magic_id_0 = pro_list[0]['promotion_id']

    def all_effective_magic(self):
        id_0 = self.magic_id_0

        if not API_TOKEN:
            yield from self.info_from_u2()
        else:
            try:
                yield from self.info_from_api()
            except Exception as e:
                logger.exception(e)
                yield from self.info_from_u2()

        if self.magic_id_0 != id_0:
            self.save_data()
        self.first_time = False

    def save_data(self):
        with open(DATA_PATH, 'w', encoding='utf-8') as fp:
            json.dump({
                'checked': list(self.checked),
                'id_0': self.magic_id_0,
                'add_time': self.tid_add_time,
                'rss_items': list(self.rss_items),
                'rss_guids': list(self.rss_guids),
            }, fp, ensure_ascii=False, default=str)

    def process_torrent(self, to_info):
        tid = to_info['dl_link'].split('&passkey')[0].split('id=')[1]

        if tid in self.tid_add_time:
            logger.info(f'Torrent {tid} | Already processed recently.')
            return

        if CHECK_PEERLIST and to_info.get('last_dl_time'):
            peer_list = self.get_soup(f'https://u2.dmhy.org/viewpeerlist.php?id={tid}')
            tables = peer_list.find_all('table')
            for table in tables or []:
                for tr in filter(lambda _tr: 'nowrap' in str(_tr), table):
                    if tr.get('bgcolor'):
                        logger.info(f"Torrent {tid} | You are already seeding/downloading this torrent.")
                        return

        # 添加到 RSS 供 Vertex 抓取，不再下载实体 .torrent
        self._append_rss_item(magic_id=to_info.get('magic_id', 0), tid=tid, to_name=to_info['to_name'], length=to_info.get("length", 0))
        self.write_rss()

        logger.info(f"Added to RSS: torrent {tid}, name {to_info['to_name']}")
        self.tid_add_time[tid] = time()

    def _append_rss_item(self, magic_id: int, tid: str, to_name: str, length: int = 0):
        guid = f'u2:magic:{magic_id}:tid:{tid}'
        if guid in self.rss_guids:
            return

        self.rss_items.appendleft({
            "title": f"[U2][Magic {magic_id}] {to_name} (tid={tid})",
            "link": f"https://u2.dmhy.org/details.php?id={tid}",
            "enclosure": f"https://u2.dmhy.org/download.php?id={tid}&https=1",
            "length": int(length) if length else 0,
            "guid": guid,
            "pubDate": datetime.now(pytz.timezone("Asia/Shanghai")),
            "description": f"magic_id={magic_id} tid={tid}",
        })
        self.rss_guids.appendleft(guid)

    def write_rss(self):
        rss = ET.Element("rss", {"version": "2.0"})
        channel = ET.SubElement(rss, "channel")

        ET.SubElement(channel, "title").text = RSS_TITLE
        ET.SubElement(channel, "link").text = RSS_LINK
        ET.SubElement(channel, "description").text = RSS_DESCRIPTION
        ET.SubElement(channel, "language").text = "zh-cn"
        ET.SubElement(channel, "ttl").text = "60"
        ET.SubElement(channel, "pubDate").text = format_datetime(datetime.now(pytz.timezone("Asia/Shanghai")))

        for it in list(self.rss_items):
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = it["title"]
            ET.SubElement(item, "link").text = it["link"]
            ET.SubElement(item, "description").text = it.get("description", "")

            enclosure = ET.SubElement(item, "enclosure")
            enclosure.set("url", it["enclosure"])
            enclosure.set("length", str(it.get("length", 0)))
            enclosure.set("type", "application/x-bittorrent")

            guid = ET.SubElement(item, "guid")
            guid.set("isPermaLink", "false")
            guid.text = it["guid"]

            pub_dt = it.get("pubDate")
            if isinstance(pub_dt, datetime):
                ET.SubElement(item, "pubDate").text = format_datetime(pub_dt)
            else:
                ET.SubElement(item, "pubDate").text = str(pub_dt or "")

        xml_bytes = ET.tostring(rss, encoding="utf-8", xml_declaration=True)
        pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ", encoding="utf-8")

        with open(RSS_PATH, "wb") as f:
            f.write(pretty)

    def start_rss_http(self):
        catch = self

        class Handler(BaseHTTPRequestHandler):
            def _send_rss_headers(self, content_length: int):
                self.send_response(200)
                self.send_header('Content-Type', 'text/xml; charset=utf-8')
                self.send_header('Content-Length', str(content_length))
                self.end_headers()

            def do_HEAD(self):
                if self.path.split("?", 1)[0] not in {"/", "/rss.xml"}:
                    self.send_response(404)
                    self.end_headers()
                    return
                try:
                    catch.write_rss()
                    with open(RSS_PATH, 'rb') as f:
                        self._send_rss_headers(len(f.read()))
                except Exception:
                    self.send_response(500)
                    self.end_headers()

            def do_GET(self):
                if self.path.split("?", 1)[0] not in {"/", "/rss.xml"}:
                    self.send_response(404)
                    self.end_headers()
                    return
                try:
                    catch.write_rss()
                    with open(RSS_PATH, 'rb') as f:
                        body = f.read()
                    self._send_rss_headers(len(body))
                    self.wfile.write(body)
                except Exception:
                    self.send_response(500)
                    self.end_headers()

            def log_message(self, format, *args):
                pass  # 静默 HTTP 访问日志

        server = HTTPServer((RSS_HTTP_BIND, RSS_HTTP_PORT), Handler)
        self.write_rss()
        t = Thread(target=server.serve_forever, daemon=True)
        t.start()
        logger.info(f'RSS HTTP server started on port {RSS_HTTP_PORT}')

    @classmethod
    def get_tz(cls, soup):
        tz_info = soup.find('a', {'href': 'usercp.php?action=tracker#timezone'})['title']
        tz = [tz_info[len(pre):-len(suf)].strip() for pre, suf in cls.pre_suf if tz_info.startswith(pre)][0]
        return pytz.timezone(tz)

    @staticmethod
    def timedelta(date, timezone):
        dt = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        return time() - timezone.localize(dt).timestamp()

    @staticmethod
    def get_pro(td):
        pro = {'ur': 1.0, 'dr': 1.0}
        pro_dict = {'free': {'dr': 0.0}, '2up': {'ur': 2.0}, '50pct': {'dr': 0.5}, '30pct': {'dr': 0.3}, 'custom': {}}
        for img in td.select('img') or []:
            if not [pro.update(data) for key, data in pro_dict.items() if key in img['class'][0]]:
                pro[{'arrowup': 'ur', 'arrowdown': 'dr'}[img['class'][0]]] = float(img.next.text[:-1].replace(',', '.'))
        return list(pro.values())

    @staticmethod
    def get_soup(url):
        magic_page = get(url, **R_ARGS).text
        if url != 'https://u2.dmhy.org/promotion.php?action=list&page=0':
            logger.debug(f'Checking page: {url}')
        return BeautifulSoup(magic_page.replace('\n', ''), 'lxml')

    def analyze_magic(self, magic_id, tid):
        soup = self.get_soup(f'https://u2.dmhy.org/details.php?id={tid}')
        aa = soup.select('a.index')
        if len(aa) < 2:
            logger.info(f'Torrent {tid} | deleted, passed')
            return
            
        to_info = {
            'to_name': aa[0].text[5:-8],
            'dl_link': f"https://u2.dmhy.org/{aa[1]['href']}",
            'magic_id': magic_id
        }

        if NAME_FILTER and any(st in soup.find('h1', {'align': 'center', 'id': 'top'}).text or st in to_info['to_name'] for st in NAME_FILTER):
            return

        if CAT_FILTER and soup.time.parent.contents[7].strip() not in CAT_FILTER:
            return

        if SIZE_FILTER and not (SIZE_FILTER[0] <= 0 and SIZE_FILTER[1] == -1):
            size_str = soup.time.parent.contents[5].strip().replace(',', '.').replace('Б', 'B')
            [num, unit] = size_str.split(' ')
            _pow = ['MiB', 'GiB', 'TiB', '喵', '寄', '烫', 'egamay', 'igagay', 'eratay'].index(unit) % 3
            gb = float(num) * 1024 ** (_pow - 1)
            to_info["length"] = int(gb * 1024**3)
            if gb < SIZE_FILTER[0] or SIZE_FILTER[1] != -1 and gb > SIZE_FILTER[1]:
                return

        if CHECK_PEERLIST or MIN_RE_DL_DAYS > 0:
            for tr in soup.find('table', {'width': '90%'}):
                if tr.td.text in ['My private torrent', '私人种子文件', '私人種子文件', 'Ваш личный торрент']:
                    time_str = tr.find_all('time')
                    to_info['last_dl_time'] = time() - self.timedelta(time_str[1].get('title') or time_str[1].text, self.get_tz(soup)) if time_str else None
            if MIN_RE_DL_DAYS > 0 and to_info.get('last_dl_time') and time() - to_info['last_dl_time'] < 86400 * MIN_RE_DL_DAYS:
                return

        delta = self.timedelta(soup.time.get('title') or soup.time.text, self.get_tz(soup))
        seeder_count = int(re.search(r'(\d+)', soup.find('div', {'id': 'peercount'}).b.text).group(1))
        magic_page_soup = None

        if delta < MIN_DAY * 86400:
            if DOWNLOAD_NEW and seeder_count <= MAX_SEEDER_NUM:
                if [self.get_pro(tr.contents[1])[1] for tr in soup.find('table', {'width': '90%'}) if tr.td.text in ['流量优惠', '流量優惠', 'Promotion', 'Тип раздачи (Бонусы)']][0] <= 0:
                    self.process_torrent(to_info)
            return
        elif not DOWNLOAD_OLD:
            return

        if not DOWNLOAD_NON_FREE:
            if [self.get_pro(tr.contents[1])[1] for tr in soup.find('table', {'width': '90%'}) if tr.td.text in ['流量优惠', '流量優惠', 'Promotion', 'Тип раздачи (Бонусы)']][0] > 0:
                magic_page_soup = self.get_soup(f'https://u2.dmhy.org/promotion.php?action=detail&id={magic_id}')
                tbody = magic_page_soup.find('table', {'width': '75%', 'cellpadding': 4}).tbody
                if self.get_pro(tbody.contents[6].contents[1])[1] == 0:
                    time_tag = tbody.contents[4].contents[1].time
                    delay = -self.timedelta(time_tag.get('title') or time_tag.text, self.get_tz(magic_page_soup))
                    if not (-1 < delay < EFFECTIVE_DELAY): return
                else:
                    return

        if seeder_count > 0 or DOWNLOAD_DEAD_TO:
            if seeder_count <= MAX_SEEDER_NUM:
                self.process_torrent(to_info)
            elif DA_QIAO:
                if not magic_page_soup:
                    magic_page_soup = self.get_soup(f'https://u2.dmhy.org/promotion.php?action=detail&id={magic_id}')
                comment = magic_page_soup.legend.parent.contents[1].text
                if '搭' in comment and '桥' in comment or '加' in comment and '速' in comment:
                    self.process_torrent(to_info)

    def run(self):
        id_0 = self.magic_id_0
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(self.analyze_magic, magic_id, tid): magic_id for magic_id, tid in self.all_effective_magic()}
            if futures:
                error = False
                for future in as_completed(futures):
                    try:
                        future.result()
                        self.checked.append(futures[future])
                    except Exception as er:
                        error = True
                        if isinstance(er, (ReadTimeout, ConnectTimeout)):
                            logger.error(er)
                        else:
                            logger.exception(er)
                if error:
                    self.magic_id_0 = id_0
                self.save_data()

@logger.catch()
def main_loop():
    logger.add(level='DEBUG', sink=LOG_PATH, rotation='2 MB')
    c = CatchMagic()
    c.start_rss_http()
    
    while True:
        try:
            c.run()
        except Exception as e:
            logger.error(f"Run Error: {e}")
        finally:
            gc.collect()
            sleep(INTERVAL)

if __name__ == '__main__':
    main_loop()
