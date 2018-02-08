from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import re
import os

def get_book_links(sortlink):
	# retrieve all book link from the category
	r = requests.get(sortlink)
	to_get = sortlink + '/page/'
	soup = BeautifulSoup(r.text)
	pages = soup.find(id='pagenavi')
	last_page = pages.find_all('a')[-1].get('href')
	books = []
	last_page_num = int(re.search('page/([0-9]*)',last_page)[1])
	for i in range(1,last_page_num+1):
		currect_page = to_get + str(i)
		c = requests.get(currect_page)
		soup2 = BeautifulSoup(c.text)
		alldt = soup2.find_all('dt')
		for booklink in alldt:
			books.append(booklink.a.get('href'))
	return books

def get_book_info(page):
	# retrieve the voting evaluation of the book, donwload page link and title
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
	return (title,mood0,mood1,mood2,mood3,mood4,downlink)

class Book:
	def __init__(self,name,s1,s2,s3,s4,s5,link):
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
		except:
			return 'link error'
		else:
			if not g.ok:
				return str(g.status_code) + 'error'
			else:
				dlsoup = BeautifulSoup(g.text)
				spans = [ x.a for x in dlsoup.find_all('span') ]
				dllinks = [y.get('href') for y in spans if y]				
		for i in dllinks:
			dl = requests.get(i)
			save = False
			if dl.ok:
				break
			elif i == dllinks[-1]:
				return 'file unavailable'
		os.makedirs('./download/',exist_ok=True)
		with open('./download/'+self.name+'.rar','wb') as f:
			f.write(dl.content)







test = 'http://www.zxcs8.com/sort/40'	
test2 = 'http://www.zxcs8.com/post/10927'
# links = get_book_links(test)
print()

