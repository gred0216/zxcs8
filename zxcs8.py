from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import re

def getmood(page):
	# get the voting evaluation of the book, donwload page link and title
	browser = webdriver.Chrome()
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
	browser.close()
	return (mood0,mood1,mood2,mood3,mood4,downlink,title)

tlink = 'http://www.zxcs8.com/sort/23'
r = requests.get(tlink)
soup = BeautifulSoup(r.text)
pages = soup.find(id='pagenavi')
current_page = pages.find('span').string
last_page = pages.find_all('a')[-1].get('href')
last_page_num = int(re.search('page/([0-9]*)',last_page)[1])
alldt = soup.find_all('dt')
books = []
for booklink in alldt:
	books.append(booklink.a.get('href'))
