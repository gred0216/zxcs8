from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import re
import os
import time


class Book:
    def __init__(self, name, s1, s2, s3, s4, s5, link):
        self.name = name
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.s4 = s4
        self.s5 = s5
        self.link = link

    def download(self):
        try:
            g = requests.get(self.link)
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


def get_sort_link():
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


def get_book_info(page):
    # retrieve the voting evaluation of the book, donwload page link and title
    browser = webdriver.Chrome('C:\Python\chromedriver.exe')
    browser.get(page)
    contents = browser.find_element_by_id('content')
    title = contents.find_element_by_css_selector('h1').text
    mood0 = browser.find_element_by_id('moodinfo0').text
    mood1 = browser.find_element_by_id('moodinfo1').text
    mood2 = browser.find_element_by_id('moodinfo2').text
    mood3 = browser.find_element_by_id('moodinfo3').text
    mood4 = browser.find_element_by_id('moodinfo4').text
    downhref = browser.find_element_by_class_name('down_2')
    downlink = downhref.find_element_by_css_selector('a').get_attribute('href')
    browser.quit()
    return (title, mood0, mood1, mood2, mood3, mood4, downlink)


def create_book(info):
    return Book(info[0], info[1], info[2], info[3], info[4], info[5], info[6])


def create_category_shelf(category):
    return Shelf(category[0], category[1])


test = 'http://www.zxcs8.com/sort/40'
test2 = 'http://www.zxcs8.com/post/10927'
test3 = ('http://www.zxcs8.com/sort/26', '奇幻·玄幻')


print()
s1 = create_category_shelf(test3)
l1 = s1.get_book_links()
for link in s1.book_links:
    if not s1.book_links.index(link) % 50 or link is s1.book_links[-1]:
        print('running book %s/%s'
        % (s1.book_links.index(link), s1.get_book_num()))
    info = get_book_info(link)
    tb = create_book(info)
    s1.add_book(tb)
    time.sleep(3)
print()

for book in s1.content:
    if book.s1 > book.s5 and book.s1 / book.s5 > 3:
        book.download()
