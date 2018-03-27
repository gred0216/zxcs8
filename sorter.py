from zxcs8 import *
from glob import glob
import os


def sort_score(score_list):
    score_list.sort(key=lambda tup: tup[1], reverse=True)


all_txt = glob('*.txt')
os.makedirs('./score/', exist_ok=True)

for txt in all_txt:
    with open(txt, 'r', encoding='UTF-8') as f:
        text = f.read()

    s1 = from_json(text)
    sc1, sc2, sc3, sc4, sc5 = [], [], [], [], []
    for book in s1.content:
        sc1.append((book, int(s1.content[book]['score1'])))
        sc2.append((book, int(s1.content[book]['score2'])))
        sc3.append((book, int(s1.content[book]['score3'])))
        sc4.append((book, int(s1.content[book]['score4'])))
        sc5.append((book, int(s1.content[book]['score5'])))

sort_score(sc1)
sort_score(sc2)
sort_score(sc3)
sort_score(sc4)
sort_score(sc5)

with open('./score/仙草.txt', 'w', encoding='UTF-8') as f1:
    f1.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in sc1))
with open('./score/糧草.txt', 'w', encoding='UTF-8') as f2:
    f2.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in sc2))
with open('./score/乾草.txt', 'w', encoding='UTF-8') as f3:
    f3.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in sc3))
with open('./score/枯草.txt', 'w', encoding='UTF-8') as f4:
    f4.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in sc4))
with open('./score/毒草.txt', 'w', encoding='UTF-8') as f5:
    f5.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in sc5))
