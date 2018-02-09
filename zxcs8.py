from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import re
import os

def get_book_links(sortlink):
	# retrieve all book link from the category
	try:
		r = requests.get(sortlink)
	except Exception as err:
		return 'Unexpected Error', err
	else:
		soup = BeautifulSoup(r.text)
		if not soup.ok:
			return str(soup.status_code) + ' error'
		else:
			pages = soup.find(id='pagenavi')
			last_page = pages.find_all('a')[-1].get('href')
			book_links = []
			failed_page =[]
			last_page_num = int(re.search('page/([0-9]*)',last_page)[1])
			to_get = sortlink + '/page/'
			for i in range(1,last_page_num+1):
				currect_page = to_get + str(i)
				c = requests.get(currect_page)
				if not c.ok:
					failed_page.append(currect_page)
				else:
					soup2 = BeautifulSoup(c.text)
					all_dt = soup2.find_all('dt')
					for booklink in all_dt:
						books.append(booklink.a.get('href'))
			return book_links, failed_page

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
		except Exception as err:
			return 'Unexpected Error', err
		else:
			if not g.ok:
				return str(g.status_code) + 'error'
			else:
				dlsoup = BeautifulSoup(g.text)
				spans = [ x.a for x in dlsoup.find_all('span') ]
				dllinks = [y.get('href') for y in spans if y]				
		for i in dllinks:
			dl = requests.get(i)			
			if dl.ok:
				break
			elif i == dllinks[-1]:
				return 'file unavailable'
		os.makedirs('./download/',exist_ok=True)
		with open('./download/'+self.name+'.rar','wb') as f:
			f.write(dl.content)

main_shelf = []

def create_book(info):
	return Book(info[0],info[1],info[2],info[3],info[4],info[5],info[6])

def add_book(book,shelf):
	if book not in shelf:
		shelf.append(book)
	
def delete_book(book,shelf):
	try:
		shelf.remove(book)
	except ValueError as err:
		return book.name + ' is not in the shelf'

def create_category_shelf(category):
	infos = get_book_links(category[0])[0]
	category[1]
	for links in infos[0]:
		pass










test = 'http://www.zxcs8.com/sort/40'	
test2 = 'http://www.zxcs8.com/post/10927'
# links = get_book_links(test)
print()

