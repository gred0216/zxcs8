from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import re
import os
import time
import json


class Book:
    def __init__(self, name, author, intro,
     score1, score2, score3, score4, score5, url, dllink):
        self.name = name
        self.author = author
        self.intro = intro
        self.score1 = score1
        self.score2 = score2
        self.score3 = score3
        self.score4 = score4
        self.score5 = score5
        self.url = url
        self.dllink = dllink

    def download(self):
        try:
            g = requests.get(self.dllink)
        except Exception as err:
            return 'Unexpected Error', err
        else:
            if not g.ok:
                return str(g.status_code) + 'error'
            else:
                dlsoup = BeautifulSoup(g.text)
                spans = [x.a for x in dlsoup.find_all('span')]
                dllinks = [y.get('href') for y in spans if y]
        for i in dllinks:
            dl = requests.get(i)
            if dl.ok:
                break
            elif i == dllinks[-1]:
                return 'file unavailable'
        if not os.path.isdir('./download/'):
            os.makedirs('./download/', exist_ok=True)
        with open('./download/' + self.name + '.rar', 'wb') as f:
            f.write(dl.content)
        print("download completed")


class Shelf:
    def __init__(self, url, name):
        self.url = url
        self.name = name
        self.content = []
        self.book_links = []
        self.failed_page = []

    def add_book(self, book):
        if book not in self.content:
            self.content.append(book)

    def delete_book(self, book):
        try:
            self.content.remove(book)
        except ValueError as err:
            return book.name + ' is not in the shelf'

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
                soup = BeautifulSoup(r.text)
                pages = soup.find(id='pagenavi')
                last_page = pages.find_all('a')[-1].get('href')
                last_page_num = int(re.search('page/([0-9]*)', last_page)[1])
                to_get = self.url + '/page/'
                for i in range(1, last_page_num + 1):
                    currect_page = to_get + str(i)
                    c = requests.get(currect_page)
                    if not c.ok:
                        self.failed_page.append(currect_page)
                    else:
                        soup2 = BeautifulSoup(c.text)
                        all_dt = soup2.find_all('dt')
                        for booklink in all_dt:
                            self.book_links.append(booklink.a.get('href'))
                    if not i % 10 or i == last_page_num:
                        print('running page %s/%s' % (i, last_page_num))

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
    browser = webdriver.Chrome('C:\Python\chromedriver.exe')
    browser.get(page_url)
    content = browser.find_element_by_id('content')
    content_h1 = content.find_element_by_css_selector('h1').text
    title = re.search('(.*?)作者：(.*)', content_h1)
    name, author = title.group(1), title.group(2)
    tag_p = browser.find_elements_by_tag_name('p')
    for p in tag_p:
        temp_text = re.match('【TX', p.text)
        if temp_text:
            break
    intro = re.findall('【内容简介】：\s(.*)', temp_text.string, flags=re.S)[0]
    mood0 = browser.find_element_by_id('moodinfo0').text
    mood1 = browser.find_element_by_id('moodinfo1').text
    mood2 = browser.find_element_by_id('moodinfo2').text
    mood3 = browser.find_element_by_id('moodinfo3').text
    mood4 = browser.find_element_by_id('moodinfo4').text
    down_2 = browser.find_element_by_class_name('down_2')
    dl_link = down_2.find_element_by_css_selector('a').get_attribute('href')
    browser.quit()
    return (name, author, intro,
     mood0, mood1, mood2, mood3, mood4, page_url, dl_link)


def create_book(info):
    return Book(info[0], info[1], info[2], info[3],
        info[4], info[5], info[6], info[7], info[8], info[9])


def create_category_shelf(category):
    return Shelf(category[0], category[1])


test = 'http://www.zxcs8.com/sort/40'
test2 = 'http://www.zxcs8.com/post/10927'
test3 = ('http://www.zxcs8.com/sort/26', '奇幻·玄幻')


print()
'''
s1 = create_category_shelf(test3)
s1.get_book_links()

for i in range(3):
    tmp = get_book_info(s1.book_links[i])
    s1.add_book(create_book(tmp))
'''
g1 = get_book_info(test2)
