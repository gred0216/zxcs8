import requests
from bs4 import BeautifulSoup
import re
import os
import time
import json
import zhconv
from collections import namedtuple
import gevent
from gevent import monkey
from shutil import copyfileobj


class Book(dict):
    '''Book is a dictionary that stores information of book.'''

    def __init__(self, info):
        '''Create a new Book instance

        Args:
            info(dict): A dict contains book information
        '''
        self['name'] = info.get('name')  # book name
        self['author'] = info.get('author')  # Author
        self['intro'] = info.get('intro')  # Introduction
        self['score1'] = info.get('score1')  # 仙草 excellent
        self['score2'] = info.get('score2')  # 粮草 good
        self['score3'] = info.get('score3')  # 干草 fair
        self['score4'] = info.get('score4')  # 枯草 poor
        self['score5'] = info.get('score5')  # 毒草 bad
        self['size'] = info.get('size')  # compressed file size
        self['url'] = info.get('url')  # website page of the book
        self['dllink'] = info.get('dllink')  # download page of the book

    def download(self):
        '''Download the book.

        The file will be in 'download' folder under current working directory.

        Returns:
            return if exception occured.

        '''
        try:
            g = requests.get(self['dllink'])
        except Exception as e:
            return 'Unexpected Error', e
        else:
            if not g.ok:
                return str(g.status_code) + 'error'
            else:
                dlsoup = BeautifulSoup(g.text)
                spans = [x.a for x in dlsoup.find_all('span')]
                filelinks = [y.get('href') for y in spans if y]

        for i in filelinks:
            dl = requests.get(i, stream=True)
            filename_extension = re.search('\d/.*?(\..*)', i)[1]
            if dl.ok:
                break
            elif i == filelinks[-1]:
                return 'file unavailable'

        if not os.path.isdir('./download/'):
            os.makedirs('./download/')
        with open('./download/' + self['name'] +
                  filename_extension, 'wb') as f:
            copyfileobj(dl.raw, f)
        print("Book '" + self.name + "' download completed")

    def to_json(self):
        '''Generate JSON of the book.

        Returns:
            str: The return JSON string
        '''
        return json.dumps(self)

    def check_rules(self, rules):
        '''check the filter of book scores'''
        passed = True
        A = int(self['score1'])
        B = int(self['score2'])
        C = int(self['score3'])
        D = int(self['score4'])
        E = int(self['score5'])
        while passed:
            for rule in rules:
                passed = passed and eval(rule)
            break
        return passed


class Shelf:
    '''
    A set of books with same categories or search result.
    Books are stored in self.content.
    '''

    def __init__(self, url='', name='', shelftype='category'):
        self.url = url
        self.name = name
        self.content = {}
        self.book_links = []
        self.failed_page = []
        self.shelftype = shelftype
        if url and self.shelftype == 'category':
            self.pages = self.url + '/page/'
        elif url and self.shelftype == 'search':
            self.pages = self.url + '&page='
        else:
            self.pages = ''

    def add_book(self, book):
        if book['name'] not in self.content:
            self.content[book['name']] = book

    def delete_book(self, book):
        if book['name'] in self.content:
            del self.content[book['name']]
        else:
            return book['name'] + ' is not in the shelf'

    def get_book_link(self, page):
        currect_page = self.pages + str(page)
        c = requests.get(currect_page)
        if not c.ok:
            self.failed_page.append(currect_page)
        else:
            soup2 = BeautifulSoup(c.text)
            all_dt = soup2.find_all('dt')
            for booklink in all_dt:
                self.book_links.append(booklink.a.get('href'))
        time.sleep(3)

    def get_book_links(self):
        # retrieve every book's link from the shelf
        try:
            r = requests.get(self.url)
        except Exception as err:
            return 'Unexpected Error', err
        else:
            if not r.ok:
                return str(r.status_code) + ' error'
            else:
                soup = BeautifulSoup(r.text)
                pages = soup.find(id='pagenavi')
                if pages.contents:
                    last_page = [i for i in pages.contents if i != ' ']
                    last_page = last_page[-1].get('href')
                    last_page_num = int(re.search('page.(\d+)', last_page)[1])
                else:
                    last_page_num = 1
                jobs = ([gevent.spawn(self.get_book_link, page)
                         for page in range(1, last_page_num + 1)])
                gevent.joinall(jobs)

    def get_book_num(self):
        return len(self.content)

    def create_book_from_link(self, i):
        info = get_book_info(self.book_links[i])
        if not info:
            self.failed_page.append(self.book_links[i])
        else:
            tb = create_book(info)
            self.add_book(tb)
            time.sleep(3)

    def add_all_book(self):
        # create every book from links and add to the shelf then clear links
        jobs = ([gevent.spawn(self.create_book_from_link, i)
                 for i in range(len(self.book_links))])
        gevent.joinall(jobs)
        self.book_links.clear()

    def download_by_rule(self, book):
        if book.check_rules(myrule):
            book.download()

    def download_all_by_rule(self):
        jobs = ([gevent.spawn(self.download_by_rule, book[1])
                 for book in self.content.items()])
        gevent.joinall(jobs)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def search(text):
    # Search by text and return a shelf
    search_url = 'http://www.zxcs8.com/index.php?keyword='
    search_text = convert_to_zhcn(text)
    search_page = search_url + search_text
    name = '搜索 "%s" 的结果' % text
    s = requests.get(search_page)
    soup5 = BeautifulSoup(s.text)
    if soup5.find(class_='none'):
        return 'Sorry, no results matching your criteria were found'
    else:
        return Shelf(search_page, name, 'search')


def get_book_info(page_url):
    # retrieve the information of the book
    result = {}
    if 'zxcs' not in page_url:
        return result
    result['url'] = page_url
    book_score = ('http://www.zxcs8.com/content/plugins/'
                  'cgz_xinqing/cgz_xinqing_action.php?action=show&id=')
    book_id = re.search('post/(\d*)', page_url).groups()[0]
    retry = 3
    while retry:
        try:
            r = requests.get(page_url, timeout=10)
        except Exception as e:
            retry -= 1
            print(e, 'Exception occured. Retrying in 3 seconds.'
                  ' Retries left: %d' % retry)
            if retry != 0:
                time.sleep(3)
            else:
                print('No more retry!')
                return None
            continue
        break
    soup4 = BeautifulSoup(r.text)
    id_content = soup4.find('div', id='content')
    title = re.search('(.*?)作者：(.*)', id_content.h1.text)
    result['name'] = title.group(1)
    result['author'] = title.group(2)
    tag_p = soup4.find_all('p')
    for p in tag_p:
        temp_text = re.search('【TX', p.text)
        if temp_text:
            temp_text = temp_text.string.replace('\u3000', '')
            break
    res = re.search('【TXT大小】：(.*?)【内容简介】：(.*)', temp_text, flags=re.S)
    result['size'], result['intro'] = res.group(1), res.group(2)
    result['dllink'] = soup4.find(class_='down_2').a.get('href')

    scores = requests.get(book_score + book_id).text
    scores = scores.split(',')
    result['score1'] = scores[0]
    result['score2'] = scores[1]
    result['score3'] = scores[2]
    result['score4'] = scores[3]
    result['score5'] = scores[4]

    return result


def create_book(info):
    return Book(info)


def create_category_shelf(category):
    return Shelf(category[0], category[1])


def convert_to_zhtw(word):
    # Convert string to traditional Chinese
    return zhconv.convert(word, 'zh-tw')


def convert_to_zhcn(word):
    # Convert string to simplified Chinese
    return zhconv.convert(word, 'zh-cn')


def from_json(json_object):
    # Read json object and convert to Book or Shelf
    if 'content' not in json_object and 'author' in json_object:
        return Book(json.loads(json_object))
    elif 'book_links' in json_object:
        pat = '(.*?)("content": {)(.*?)("failed_page".*)'
        re_result = re.findall(pat, json_object, flags=re.S)[0]
        no_content = re_result[0] + re_result[3]
        books = re.findall('{.*?}', re_result[2], flags=re.S)
        shelf_info = json.loads(no_content, object_hook=lambda d: namedtuple
                                ('temp_class', d.keys())(*d.values()))
        temp_shelf = Shelf(shelf_info.url, shelf_info.name)
        temp_shelf.book_links = shelf_info.book_links
        temp_shelf.failed_page = shelf_info.failed_page
        for book in books:
            print(book)
            temp_shelf.add_book(from_json(book))
        return temp_shelf
    else:
        return 'Unrecognizable JSON object!'


monkey.patch_all()

test = 'http://www.zxcs8.com/sort/40'
test2 = 'http://www.zxcs8.com/post/10927'
test3 = ('http://www.zxcs8.com/sort/26', '奇幻·玄幻')
test4 = 'http://www.zxcs8.com/post/10920'

print()

g1 = {'url': 'http://www.zxcs8.com/post/10927',
      'name': '《重生之小玩家》（校对版全本）',
      'author': '吹个大气球9',
      'intro': ('世事如棋，有人身在局中当棋子，有人手握棋子做玩家。\n'
                '大玩家摆弄苍生，小玩家自得富贵。\n'
                '秦风活过一世再重来，睁开眼，便要从棋子变玩家。\n'
                '然则大玩家不好当，姑且，就做个小玩家，富贵一生吧。'),
      'score1': '118',
      'score2': '7',
      'score3': '9',
      'score4': '9',
      'score5': '127',
      'dllink': 'http://www.zxcs8.com/download.php?id=10927'}
g2 = {'url': 'http://www.zxcs8.com/post/10920',
      'name': '《白银之轮》（校对版全本）',
      'author': '悲剧山伯爵',
      'intro': ('蝇王撒的奇妙作死之旅……\n一位顶级灾神的成长史)\n'
                '这里有新派黑科技+古典主义魔法，灾神+宇宙人，'
                '东洲妖怪+皇家菠萝，共济会喵星人+光照会汪星人，'
                '甜党+咸党，触手魔女+地狱罪族，蒸汽飞艇+黑科技飞碟，'
                '黑科技装甲+受孕指环，数百款不同风格的亡灵，近万种口味各异的蝇妖精供您选择。\n'
                '锡兰是个充满安宁与祥和的美好世界，每天都有充满正能量的事情上演。\n'
                '三观端正，积极向上……'),
      'score1': '225',
      'score2': '27',
      'score3': '10',
      'score4': '13',
      'score5': '135',
      'dllink': 'http://www.zxcs8.com/download.php?id=10920'}

b1 = Book(g1)
b2 = Book(g2)
s1 = Shelf()
s1.add_book(b1)
s1.add_book(b2)

myrule = ['A>E', 'A+B>D+E', 'A-E>A/2']


s2 = create_category_shelf(test3)

test5 = 'http://www.zxcs8.com/index.php?keyword=5'
test6 = 'http://www.zxcs8.com/tag/%E5%8F%A6%E7%B1%BB%E5%B9%BB%E6%83%B3'
test7 = 'http://www.zxcs8.com/index.php?keyword=异界'

s3 = Shelf(test6, 'test6')
s4 = search('3')
