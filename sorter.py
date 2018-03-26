from zxcs8 import *
from glob import glob


with open('武侠幻想.txt', 'r', encoding='UTF-8') as f:
	text = f.read()

s1 = from_json(text)