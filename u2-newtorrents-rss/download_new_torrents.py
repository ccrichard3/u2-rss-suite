
# python 版本 3.8 及以上，依赖: requests beautifulsoup4 lxml loguru pytz
import os
import re
import ast
import json
import argparse
import pytz
import xml.etree.ElementTree as ET
from xml.dom import minidom
from email.utils import format_datetime
from collections import deque
from pathlib import Path
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

from datetime import datetime as dt, datetime
from functools import wraps
from time import sleep, time
from bs4 import BeautifulSoup
from loguru import logger
from requests import get


# *************************环境变量配置************************
def _env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {'1', 'true', 'yes', 'on'}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except Exception:
        return default


def _normalize_cookie(raw: str) -> str:
    raw = (raw or '').strip()
    if raw.startswith('nexusphp_u2='):
        return raw.split('=', 1)[1]
    return raw


# *************************必填配置************************
cookies = {'nexusphp_u2': _normalize_cookie(os.getenv('U2_COOKIE', ''))}
passkey = os.getenv('U2_PASSKEY', '').strip()
save_path = os.getenv('SAVE_PATH', '/app/data/compat-watchdir')  # 仅保留兼容字段，不再写入 .torrent
download_location = os.getenv('DOWNLOAD_LOCATION', '/downloads')

# ************************可修改配置***********************
proxies = {
    'http': os.getenv('HTTP_PROXY', '').strip(),
    'https': os.getenv('HTTPS_PROXY', '').strip(),
}
headers = {
    'authority': 'u2.dmhy.org',
    'accept-encoding': 'gzip, deflate',
    'accept-language': 'zh-CN,zh;q=0.8',
    'referer': 'https://u2.dmhy.org/index.php',
    'user-agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62')
}
interval = _env_int('INTERVAL', 300)
mgdb = False
download_sticky = _env_bool('DOWNLOAD_STICKY', True)
download_no_seeder_sticky = _env_bool('DOWNLOAD_NO_SEEDER_STICKY', True)
download_no_free_sticky = _env_bool('DOWNLOAD_NO_FREE_STICKY', False)
download_no_free_non_sticky = _env_bool('DOWNLOAD_NO_FREE_NON_STICKY', False)
eval_all_keys = _env_bool('EVAL_ALL_KEYS', False)

skip_existing_on_first_run = _env_bool('SKIP_EXISTING_ON_FIRST_RUN', True)
RSS_MAX_ITEMS = _env_int('RSS_MAX_ITEMS', 50)
RSS_TITLE = os.getenv('RSS_TITLE', 'U2 New Torrents')
RSS_LINK = os.getenv('RSS_LINK', 'https://u2.dmhy.org/')
RSS_DESCRIPTION = os.getenv('RSS_DESCRIPTION', 'Auto-generated RSS feed for new torrents.')
RSS_HTTP_BIND = os.getenv('RSS_HTTP_BIND', '0.0.0.0')
RSS_HTTP_PORT = _env_int('RSS_HTTP_PORT', 8788)
STATE_DIR = os.getenv('DATA_DIR', '/app/data')
Path(STATE_DIR).mkdir(parents=True, exist_ok=True)
STATE_PATH = f'{STATE_DIR}/state.json'
RSS_PATH = f'{STATE_DIR}/rss.xml'
LOG_PATH = f'{STATE_DIR}/service.log'

logger.remove()
logger.add(level='DEBUG', sink=LOG_PATH, rotation='2 MB')

checked = deque([], maxlen=300)
added = deque([], maxlen=800)
rss_items = deque([], maxlen=RSS_MAX_ITEMS)
rss_guids = deque([], maxlen=RSS_MAX_ITEMS)

def normalize_cookies():
    val = cookies.get('nexusphp_u2')
    if isinstance(val, str) and val.startswith('nexusphp_u2='):
        cookies['nexusphp_u2'] = val.split('=', 1)[1]


def ensure_runtime_dirs():
    Path(STATE_DIR).mkdir(parents=True, exist_ok=True)
    if not Path(RSS_PATH).exists():
        write_rss()


def load_state():
    global checked, added, rss_items, rss_guids
    p = Path(STATE_PATH)
    if not p.exists():
        return
    try:
        data = json.loads(p.read_text())
        checked = deque(data.get('checked', []), maxlen=300)
        added = deque(data.get('added', []), maxlen=800)
        rss_items = deque(data.get('rss_items', []), maxlen=RSS_MAX_ITEMS)
        rss_guids = deque(data.get('rss_guids', []), maxlen=RSS_MAX_ITEMS)
    except Exception as e:
        logger.error(f'load_state failed: {e}')


def save_state():
    ensure_runtime_dirs()
    Path(STATE_PATH).write_text(json.dumps({
        'checked': list(checked),
        'added': list(added),
        'rss_items': list(rss_items),
        'rss_guids': list(rss_guids),
    }, ensure_ascii=False, default=str))


def append_rss_item(tid: int, title: str, size_bytes: int = 0):
    guid = f'u2:new:{tid}'
    if guid in rss_guids:
        return
    rss_items.appendleft({
        'title': f'[U2][NEW] {title} (tid={tid})',
        'link': f'https://u2.dmhy.org/details.php?id={tid}',
        'enclosure': f'https://u2.dmhy.org/download.php?id={tid}&https=1',
        'length': int(size_bytes) if size_bytes else 0,
        'guid': guid,
        'pubDate': datetime.now(pytz.timezone('Asia/Shanghai')),
        'description': f'tid={tid}',
    })
    rss_guids.appendleft(guid)


def write_rss():
    Path(STATE_DIR).mkdir(parents=True, exist_ok=True)
    rss = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = RSS_TITLE
    ET.SubElement(channel, 'link').text = RSS_LINK
    ET.SubElement(channel, 'description').text = RSS_DESCRIPTION
    ET.SubElement(channel, 'language').text = 'zh-cn'
    ET.SubElement(channel, 'ttl').text = '60'
    ET.SubElement(channel, 'pubDate').text = format_datetime(datetime.now(pytz.timezone('Asia/Shanghai')))

    for it in list(rss_items):
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = it['title']
        ET.SubElement(item, 'link').text = it['link']
        ET.SubElement(item, 'description').text = it.get('description', '')
        enclosure = ET.SubElement(item, 'enclosure')
        enclosure.set('url', it['enclosure'])
        enclosure.set('length', str(it.get('length', 0)))
        enclosure.set('type', 'application/x-bittorrent')
        guid = ET.SubElement(item, 'guid')
        guid.set('isPermaLink', 'false')
        guid.text = it['guid']
        pub_dt = it.get('pubDate')
        if isinstance(pub_dt, datetime):
            ET.SubElement(item, 'pubDate').text = format_datetime(pub_dt)
        else:
            ET.SubElement(item, 'pubDate').text = str(pub_dt or '')

    xml_bytes = ET.tostring(rss, encoding='utf-8', xml_declaration=True)
    pretty = minidom.parseString(xml_bytes).toprettyxml(indent='  ', encoding='utf-8')
    with open(RSS_PATH, 'wb') as f:
        f.write(pretty)


def start_rss_http():
    class Handler(BaseHTTPRequestHandler):
        def _send_rss_headers(self, content_length: int):
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml; charset=utf-8')
            self.send_header('Content-Length', str(content_length))
            self.end_headers()

        def do_HEAD(self):
            if self.path.split('?', 1)[0] not in {'/', '/rss.xml'}:
                self.send_response(404)
                self.end_headers()
                return
            try:
                write_rss()
                body = Path(RSS_PATH).read_bytes()
                self._send_rss_headers(len(body))
            except Exception:
                self.send_response(500)
                self.end_headers()

        def do_GET(self):
            if self.path.split('?', 1)[0] not in {'/', '/rss.xml'}:
                self.send_response(404)
                self.end_headers()
                return
            try:
                write_rss()
                body = Path(RSS_PATH).read_bytes()
                self._send_rss_headers(len(body))
                self.wfile.write(body)
            except Exception:
                self.send_response(500)
                self.end_headers()

        def log_message(self, format, *args):
            pass

    server = HTTPServer((RSS_HTTP_BIND, RSS_HTTP_PORT), Handler)
    write_rss()
    t = Thread(target=server.serve_forever, daemon=True)
    t.start()
    logger.info(f'RSS HTTP server started on port {RSS_HTTP_PORT}')


def get_url(url):
    try:
        html = get(url, cookies=cookies, headers=headers, proxies=proxies, timeout=20)
        if html.status_code < 400:
            if url != 'https://u2.dmhy.org/torrents.php':
                logger.info(f'download page {url}')
            return html.text
        logger.error(f'get_url failed {url}, status={html.status_code}')
    except Exception as e:
        logger.error(e)
    return ''


normalize_cookies()
detail_key_dict = {
        'filename': ['下载', '下載', 'Download', 'Скачивание'],
        'author': ['发布人', '發佈人', '發布人', 'Uploader', 'Загрузил'],
        'hash': ['种子信息', '種子訊息', 'Torrent Info', 'Информация о торренте'],
        'description': ['描述', '描述', 'Description', 'Описание'],
        'progress': ['活力度', 'Health', 'Целостность'],
        'geoips': ['同伴', 'Peers', 'Всего Участников']
    }


class U2Web:
    def __init__(self):
        self.keys = [key[1:] for key, obj in type(self).__dict__.items()
                     if isinstance(obj, property) and key.startswith('_')]
        self.info = {}
        self.tr = None
        self.tr1 = None
        self.trs = None
        self.d_url = None
        self.t_url = None
        self.table1 = []
        self.tz = ''
        self.passkey = passkey

    def __getattr__(self, item):
        if item in self.keys:
            return getattr(self, f'_{item}')
        else:
            raise KeyError(f'Key {item} is not supported. These are all supported keys: {self.keys}')

    def torrent_page(self):
        page = get_url('https://u2.dmhy.org/torrents.php')
        soup = BeautifulSoup(page.replace('\n', ''), 'lxml')
        tz_info = soup.find('a', {'href': 'usercp.php?action=tracker#timezone'})['title']
        pre_suf = [['时区', '，点击修改。'], ['時區', '，點擊修改。'], ['Current timezone is ', ', click to change.']]
        self.tz = [tz_info[len(pre):][:-len(suf)].strip() for pre, suf in pre_suf if tz_info.startswith(pre)][0]

        table = soup.select('table.torrents')[0]
        for self.tr in table.contents[1:]:
            self.info = {}
            if self.tid not in added:  # 过滤已经添加的种子
                self.trs = str(self.tr)
                yield self.tr

    def _seeding(self):  # 是否正在做种
        return bool('seedhlc_current' in self.trs)

    def _leeching(self):  # 是否正在下载
        return bool('leechhlc_current' in self.trs)

    def _sticky(self):  # 是否顶置
        return bool('sticky' in self.trs)

    '''
    def _hot(self):  # 是否热门
        return bool(self.tr.select('span.hot'))
    '''

    def _incomplete(self):  # 是否曾经未完成
        return bool('incomplete' in self.trs)

    def _completed(self):  # 是否曾经完成
        return bool('snatchhlc_finish' in self.trs)

    def _auxseed(self):  # 是否曾经辅种
        return bool('snatchhlc_auxseed' in self.trs)

    def _tid(self):  # 种子 id
        return int(self.tr.contents[1].a['href'][15:-6])

    def _title(self):  # 标题
        return self.tr.contents[1].a.text

    def _small_descripton(self):  # 副标题
        tooltip = self.tr.find('span', {'class': 'tooltip'})
        return tooltip.text if tooltip else None

    def _seeder_num(self):  # 做种数
        return int(self.tr.contents[5].string)

    def _leecher_num(self):  # 下载数
        return int(self.tr.contents[6].contents[0].string)

    def _completes(self):  # 完成数
        return int(self.tr.contents[7].string)

    def _date(self):  # 发布日期(字符串)
        return self.tr.contents[3].time.get('title') or self.tr.contents[3].time.get_text(' ')

    def _size(self):  # 体积(字符串)
        return self.tr.contents[4].get_text(' ')

    def _promotion(self):  # 上传下载比率
        pro = {'ur': 1.0, 'dr': 1.0}
        pro_dic = {'free': {'dr': 0.0}, 'twoup': {'ur': 2.0}, 'halfdown': {'dr': 0.5}, 'thirtypercent': {'dr': 0.3}}
        if self.tr.get('class'):
            [pro.update(data) for key, data in pro_dic.items() if key in self.tr['class'][0]]
        td = self.tr.tr and self.tr.select('tr')[1].td or self.tr.select('td')[1]
        pro_dic_1 = {'free': {'dr': 0.0}, '2up': {'ur': 2.0}, '50pct': {'dr': 0.5}, '30pct': {'dr': 0.3}, 'custom': {}}
        for img in td.select('img') or []:
            if not [pro.update(data) for key, data in pro_dic_1.items() if key in img['class'][0]]:
                pro[{'arrowup': 'ur', 'arrowdown': 'dr'}[img['class'][0]]] = float(img.next.text[:-1].replace(',', '.'))
        for span in td.select('span') or []:
            [pro.update(data) for key, data in pro_dic.items() if key in (span.get('class') and span['class'][0] or '')]
        return list(pro.values())

    def _torrentsign(self):  # 种子签名
        if 'torrentsign' in self.trs:
            return self.tr.select('span.torrentsign')[0].text

    def _pro_end_date(self):  # 优惠结束时间
        if self.tr.contents[1].time:
            return self.tr.contents[1].time.get('title') or self.tr.contents[1].time.text

    def _ani_link(self):  # anidb 链接
        td = self.tr.select('tr')[1].contents[1]
        if td.string:
            return td.a['href']

    def _rating(self):  # anidb 评分
        num = self.tr.select('tr')[1].contents[1].string
        if num not in (None, ' - '):
            return float(num)

    def detail_page(self):  # 详情页很多地方结构的不固定，可能用正则表达式可能会好点？
        if self.tid not in checked:
            self.d_url = self.t_url
            soup = BeautifulSoup(get_url(self.d_url).replace('\n', ''), 'lxml')
            self.passkey = soup.select('a.index')[1]['href'].split('&passkey=')[1][:-8]
            self.table1 = soup.find('table', {'width': '90%'})
            checked.append(self.info['tid'])
            write_list('checked')
        for self.tr1 in self.table1:
            yield self.tr1

    def _filename(self):  # 种子内容文件名
        return self.tr1.a.text[5:-8]

    def _author(self):  # 发布者 uid
        if not any(a in str(self.tr1) for a in ['匿名', 'torrentsign', 'Anonymous', 'Анонимно']):
            return self.tr1.s and self.tr1.s.text or self.tr1.a['href'][19:]

    '''
    def _descrption(self):  # 详细描述
        return self.tr1.bdo.text
    '''

    def _hash(self):  # info_hash
        return self.tr1.tr.contents[-2].contents[1].strip()

    def _progress(self):  # (包括做种者在内的) 平均进度
        if not any(st in str(self.tr1) for st in ['没有流量', '沒有流量', 'No Traffic', 'Не зафиксировано']):
            return int(self.tr1.b.previous_element.strip()[1:-2])

    def _geoips(self):  # 做种者的地理位置信息
        if int(re.search(r'(\d+)', self.tr1.b.text).group(1)) > 0:
            peerlist = get_url(f'https://u2.dmhy.org/viewpeerlist.php?id={self.tid}')
            table = BeautifulSoup(peerlist.replace('\n', ' '), 'lxml').table
            ips = []
            for tr in filter(lambda _tr: 'nowrap' in str(_tr), table):
                ip = {}
                for i, span in enumerate(tr.contents[0]):
                    if i == 0:
                        ip['user'] = tr.i and str(tr.i) or tr.bdo.text  # 用户名
                    else:
                        ip[span['class'][1]] = span['title']
                ips.append(ip)
            return ips

    @property
    def secs(self):  # 发布时间到现在的间隔(s)，不是 property
        tm = dt.strptime(self.date, '%Y-%m-%d %H:%M:%S')
        return int(time() - pytz.timezone(self.tz).localize(tm).timestamp())

    @property
    def gbs(self):  # 种子体积(gb)，不是 property
        [num, unit] = self.size.split(' ')
        _pow = ['MiB', 'GiB', 'TiB', '喵', '寄', '烫', 'MiБ', 'GiБ', 'TiБ', 'egamay', 'igagay', 'eratay'].index(unit) % 3
        return float(num.replace(',', '.')) * 1024 ** (_pow - 1)

    def select_torrent(self):
        """
        选择种子，符合条件返回 True。有些值可能为空
        规则自己写吧，反正应该很好懂，看这个逻辑也不是很方便能用配置描述....
        """
        if not self.seeding and not self.leeching:  # 过滤下载中和做种中的种子
            if self.sticky:  # 顶置种子
                if download_sticky:
                    if not download_no_free_sticky and self.promotion[1] > 0:
                        return
                    if self.seeder_num > 0:  # 做种数大于 0 ，直接下载
                        return True
                    if download_no_seeder_sticky:
                        return
                    if self.leecher_num > 5:
                        if self.progress is not None and self.progress > 0:
                            # 做种数小于于 0 ，检查下载者进度，如果平均进度全为 0 不下载
                            return True
            else:
                if not download_no_free_non_sticky and self.promotion[1] > 0:
                    return
                if self.secs < 2 * interval:  # 发布不久，直接下载
                    return True
                if self.seeder_num < 10 or self.leecher_num > 20:  # 根据做种数和下载数判断是否要下载
                    if self.progress is not None and self.progress < 30:  # 检查平均进度
                        return True


    def rss(self, run_once=False):
        first_cycle = True if len(added) == 0 else False
        while True:
            try:
                page_tids = []
                matched_tids = []
                for self.tr in self.torrent_page():
                    page_tids.append(self.tid)
                    if first_cycle and skip_existing_on_first_run and len(added) == 0:
                        continue
                    if self.tid in added:
                        continue
                    if self.select_torrent():
                        size_bytes = 0
                        try:
                            size_bytes = int(self.gbs * 1024 ** 3)
                        except Exception:
                            pass
                        append_rss_item(self.tid, self.title, size_bytes)
                        matched_tids.append(self.tid)
                        added.append(self.tid)
                        if eval_all_keys:
                            for _key in self.keys:
                                getattr(self, _key)
                        for key in list(self.info.keys()):
                            if not self.info[key]:
                                del self.info[key]
                        if mgdb:
                            col.insert_one(self.info)
                        else:
                            logger.debug(f'-----------  torrent info  ----------\n{self.info}')
                        logger.info(f'Added to RSS: torrent {self.tid}, name {self.title}')

                if first_cycle and skip_existing_on_first_run and len(added) == 0 and page_tids:
                    for tid in page_tids:
                        added.append(tid)
                    logger.info(f'Initialized baseline with {len(page_tids)} current torrents; future new torrents will be added to RSS.')

                save_state()
                write_rss()

                if matched_tids:
                    logger.info(f'Cycle completed, matched {len(matched_tids)} torrents: {matched_tids[:10]}')
            except Exception as e:
                logger.exception(e)
            finally:
                first_cycle = False
                if run_once:
                    break
                sleep(interval)


    def value(func):
        @property
        @wraps(func)
        def wrapper(self):
            name = func.__name__[1:]
            if name not in self.info:  # sel.info 中没有这个 key，说明之前没有获取
                if name in detail_key_dict:  # key 只有详细页才有
                    self.t_url = f'https://u2.dmhy.org/details.php?id={self.tid}&hit=1'
                    if self.tid in checked and self.d_url != self.t_url:
                        # 已经检查过一次，并且详情页不在内存中，返回 None
                        self.info[name] = None
                    else:
                        for self.tr1 in self.detail_page():
                            if any(word in self.tr1.td.text for word in detail_key_dict[name]):
                                self.info[name] = func(self)
                                break
                            else:
                                self.info[name] = None
                else:
                    self.info[name] = func(self)
            return self.info.get(name)
        return wrapper

    for name in list(vars()):
        obj = vars()[name]
        if hasattr(type(obj), '__get__') and not hasattr(type(obj), '__set__'):
            if name.startswith('_') and not (name.startswith('__') and name.endswith('__')):
                vars()[name] = value(obj)

    del value, name, obj




def main():
    parser = argparse.ArgumentParser(description='Expose U2 new torrents as RSS for Vertex')
    parser.add_argument('--once', action='store_true', help='run one cycle and exit')
    args = parser.parse_args()

    ensure_runtime_dirs()
    load_state()
    start_rss_http()

    if mgdb:
        import pymongo
        dbclient = pymongo.MongoClient('mongodb://localhost:27017/')
        base = dbclient['U2']
        col = base['torrent_info']

    u2 = U2Web()
    u2.rss(run_once=args.once)


if __name__ == '__main__':
    main()
