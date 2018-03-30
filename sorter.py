from zxcs8 import *
from glob import glob
import os
import numpy as np


all_tag = glob('./tags/*.txt')
all_sort = glob('./sort/*.txt')
all_txt = all_tag + all_sort


def sort_score(score_list):
    score_list.sort(key=lambda tup: tup[1], reverse=True)


def sort_by_excellent(shelf, path):
    if 'tags' in path:
        if not os.path.isdir('./score/excellent/tags'):
            os.makedirs('./score/excellent/tags', exist_ok=True)
    elif 'sort' in path:
        if not os.path.isdir('./score/excellent/sort'):
            os.makedirs('./score/excellent/sort', exist_ok=True)

    excellent = []
    for book in shelf.content:
        excellent.append((book, int(shelf.content[book]['score1'])))
    sort_score(excellent)

    with open('./score/excellent/{}{}_excellent.txt'.format(path, shelf.name),
              'w', encoding='UTF-8') as f:
        f.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in excellent))


def sort_by_bad(shelf, path):
    if 'tags' in path:
        if not os.path.isdir('./score/bad/tags'):
            os.makedirs('./score/bad/tags', exist_ok=True)
    elif 'sort' in path:
        if not os.path.isdir('./score/bad/sort'):
            os.makedirs('./score/bad/sort', exist_ok=True)

    excellent = []
    for book in shelf.content:
        excellent.append((book, int(shelf.content[book]['score1'])))
    sort_score(excellent)

    with open('./score/bad/{}{}_bad.txt'.format(path, shelf.name),
              'w', encoding='UTF-8') as f:
        f.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in excellent))


def sort_by_ratio(shelf, path):
    if 'tags' in path:
        if not os.path.isdir('./score/ratio/tags'):
            os.makedirs('./score/ratio/tags', exist_ok=True)
    elif 'sort' in path:
        if not os.path.isdir('./score/ratio/sort'):
            os.makedirs('./score/ratio/sort', exist_ok=True)

    ratio = []
    for book in shelf.content:
        score = 0
        try:
            score = ((int(shelf.content[book]['score1']) +
                      int(shelf.content[book]['score2'])) /
                     (int(shelf.content[book]['score4']) +
                      int(shelf.content[book]['score5'])))
        except ZeroDivisionError:
            score = -1
        ratio.append((book, round(score, 3)))
    sort_score(ratio)

    with open('./score/ratio/{}{}_ratio.txt'.format(path, shelf.name),
              'w', encoding='UTF-8') as f:
        f.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in ratio))


def sort_by_votes(shelf, path):
    if 'tags' in path:
        if not os.path.isdir('./score/votes/tags'):
            os.makedirs('./score/votes/tags', exist_ok=True)
    elif 'sort' in path:
        if not os.path.isdir('./score/votes/sort'):
            os.makedirs('./score/votes/sort', exist_ok=True)

    votes = []
    for book in shelf.content:
        vote = (int(shelf.content[book]['score1']) +
                int(shelf.content[book]['score2']) +
                int(shelf.content[book]['score3']) +
                int(shelf.content[book]['score4']) +
                int(shelf.content[book]['score5']))
        votes.append((book, vote))
    sort_score(votes)

    with open('./score/votes/{}{}_votes.txt'.format(path, shelf.name),
              'w', encoding='UTF-8') as f:
        f.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in votes))


def sort_by_overall(shelf, path):
    if 'tags' in path:
        if not os.path.isdir('./score/overall/tags'):
            os.makedirs('./score/overall/tags', exist_ok=True)
    elif 'sort' in path:
        if not os.path.isdir('./score/overall/sort'):
            os.makedirs('./score/overall/sort', exist_ok=True)

    rank = []
    for book in shelf.content:
        vote = (int(shelf.content[book]['score1']) +
                int(shelf.content[book]['score2']) +
                int(shelf.content[book]['score3']) +
                int(shelf.content[book]['score4']) +
                int(shelf.content[book]['score5']))
        score = (2 * int(shelf.content[book]['score1']) +
                 int(shelf.content[book]['score2']) +
                 -1 * int(shelf.content[book]['score4']) +
                 -2 * int(shelf.content[book]['score5']))
        try:
            rank.append((book, round(score / vote, 3)))
        except ZeroDivisionError:
            rank.append((book, -1))

    sort_score(rank)

    with open('./score/overall/{}{}_overall.txt'.format(path, shelf.name),
              'w', encoding='UTF-8') as f:
        f.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in rank))


def sort_by_score(shelf, path):
    if 'tags' in path:
        if not os.path.isdir('./score/score/tags'):
            os.makedirs('./score/score/tags', exist_ok=True)
    elif 'sort' in path:
        if not os.path.isdir('./score/score/sort'):
            os.makedirs('./score/score/sort', exist_ok=True)

    rank = []
    for book in shelf.content:
        score = (2 * int(shelf.content[book]['score1']) +
                 int(shelf.content[book]['score2']) +
                 -1 * int(shelf.content[book]['score4']) +
                 -2 * int(shelf.content[book]['score5']))
        rank.append((book, score))
    sort_score(rank)

    with open('./score/score/{}{}_score.txt'.format(path, shelf.name),
              'w', encoding='UTF-8') as f:
        f.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in rank))


if __name__ == '__main__':
    for txt in all_tag:
        path = 'tags/'
        with open(txt, 'r', encoding='UTF-8') as f:
            text = f.read()
        shelf = from_json(text)
        sort_by_score(shelf, path)
        sort_by_overall(shelf, path)

    for txt in all_sort:
        path = 'sort/'
        with open(txt, 'r', encoding='UTF-8') as f:
            text = f.read()
        shelf = from_json(text)
        sort_by_score(shelf, path)
        sort_by_overall(shelf, path)
