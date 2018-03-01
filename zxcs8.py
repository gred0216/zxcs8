from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import re
import os
import time
import json
import zhconv
from collections import namedtuple
import multiprocessing as mp


class Book(dict):
    def __init__(self, info):
        self['name'] = info.get('name')
        self['author'] = info.get('author')
        self['intro'] = info.get('intro')
        self['score1'] = info.get('score1')
        self['score2'] = info.get('score2')
        self['score3'] = info.get('score3')
        self['score4'] = info.get('score4')
        self['score5'] = info.get('score5')
        self['url'] = info.get('url')
        self['dllink'] = info.get('dllink')

    def download(self):
        try:
            g = requests.get(self['dllink'])
        except Exception as err:
            return 'Unexpected Error', err
        else:
            if not g.ok:
                return str(g.status_code) + 'error'
            else:
                dlsoup = BeautifulSoup(g.text)
                spans = [x.a for x in dlsoup.find_all('span')]
                filelinks = [y.get('href') for y in spans if y]
        for i in filelinks:
            dl = requests.get(i)
            if dl.ok:
                break
            elif i == filelinks[-1]:
                return 'file unavailable'
        if not os.path.isdir('./download/'):
            os.makedirs('./download/', exist_ok=True)
        with open('./download/' + self['name'] + '.rar', 'wb') as f:
            f.write(dl.content)
        print("download completed")

    def to_json(self):
        return json.dumps(self)

    def check_rules(self, rules):
        check_rule = True
        A = int(self['score1'])
        B = int(self['score2'])
        C = int(self['score3'])
        D = int(self['score4'])
        E = int(self['score5'])
        for rule in rules:
            check_rule = check_rule and eval(rule)
        return check_rule


class Shelf:
    def __init__(self, url='', name=''):
        self.url = url
        self.name = name
        self.content = {}
        self.book_links = []
        self.failed_page = []
        if url:
            self.pages = url + '/page/'
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
        currect_page = self.pages + page
        c = requests.get(currect_page)
        if not c.ok:
            self.failed_page.append(currect_page)
        else:
            soup2 = BeautifulSoup(c.text)
            all_dt = soup2.find_all('dt')
            for booklink in all_dt:
                self.book_links.append(booklink.a.get('href'))

    def get_book_links(self):
        # retrieve all book link from the category
        try:
            r = requests.get(self.url)
        except Exception as err:
            return 'Unexpected Error', err
        else:
            if not r.ok:
                return str(r.status_code) + ' error'
            else:
                mypool = mp.Pool()
                soup = BeautifulSoup(r.text)
                pages = soup.find(id='pagenavi')
                last_page = pages.find_all('a')[-1].get('href')
                last_page_num = int(re.search('page/([0-9]*)', last_page)[1])
                mypool.map(self.get_book_link, range(1, last_page_num + 1))

    def get_book_num(self):
        return len(self.content)

    def add_all_book(self):
        # add all books in the category to the shelf
        for link in self.book_links:
            if not self.book_links.index(link) % 50:
                print('running book %s/%s'
                      % (self.book_links.index(link), len(self.link)))
            info = get_book_info(link)
            tb = create_book(info)
            self.add_book(tb)
            time.sleep(3)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


def get_category():
    base = 'http://www.zxcs8.com/sort/'
    sort_results = []
    error = []
    for i in range(1, 100):
        try:
            r = requests.get(base + str(i))
        except Exception as err:
            error.append(err)
            print('Unexpected Error', err)
        else:
            if not r.ok:
                error.append('page %s %s error' % (i, r.status_code))
            else:
                soup3 = BeautifulSoup(r.text)
                category = soup3.find(id='ptop')
                name = category.find_all('a')[1].text
                sort_results.append((r.url, name))
    return sort_results, error


def search_tag():
    pass


def get_book_info(page_url):
    # retrieve the voting evaluation of the book, donwload page link and title
    result = {}
    result['url'] = page_url
    browser = webdriver.Chrome()
    browser.get(page_url)
    content = browser.find_element_by_id('content')
    content_h1 = content.find_element_by_css_selector('h1').text
    title = re.search('(.*?)作者：(.*)', content_h1)
    result['name'] = title.group(1)
    result['author'] = title.group(2)

    tag_p = browser.find_elements_by_tag_name('p')
    for p in tag_p:
        temp_text = re.match('【TX', p.text)
        if temp_text:
            break
    result['intro'] = re.findall('【内容简介】：\s(.*)',
                                 temp_text.string, flags=re.S)[0]
    result['score1'] = browser.find_element_by_id('moodinfo0').text
    result['score2'] = browser.find_element_by_id('moodinfo1').text
    result['score3'] = browser.find_element_by_id('moodinfo2').text
    result['score4'] = browser.find_element_by_id('moodinfo3').text
    result['score5'] = browser.find_element_by_id('moodinfo4').text

    down_2 = browser.find_element_by_class_name('down_2')
    result['dllink'] = (down_2.find_element_by_css_selector('a').
                        get_attribute('href'))

    browser.quit()
    return result


def create_book(info):
    return Book(info)


def create_category_shelf(category):
    return Shelf(category[0], category[1])


def convert_to_zhtw(word):
    return zhconv.convert(word, 'zh-tw')


def convert_to_zhcn(word):
    return zhconv.convert(word, 'zh-cn')


def from_json(json_object):
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

myrule = ['A>E', 'A+B>D+E', 'A/E>1.5']

s2 = create_category_shelf(test3)
