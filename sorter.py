from zxcs8 import *
from glob import glob
import operator


with open('历史传记.txt', 'r', encoding='UTF-8') as f:
    text = f.read()

s1 = from_json(text)
scores = {}

s1, s2, s3, s4, s5 = (), (), (), (), ()

for book in s1.content:
    scores[book] = {}
    for key, value in s1.content[book].items():
        if 'score' in key:
            scores[book][key] = int(value)

for book in scores:
    sorted_book = sorted(scores[book].items(), key=operator.itemgetter(1))
    sort2 = sorted(scores[book].items(), key=operator.itemgetter(0))
    print(sorted_book)
    print()
    print(sort2)
