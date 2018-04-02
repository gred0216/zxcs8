from zxcs8 import *
from glob import glob
import os
import math


all_tag = glob('./tags/*.txt')
all_sort = glob('./sort/*.txt')
logger = logging.getLogger('zxcs8')


def sort_score(score_list):
    score_list.sort(key=lambda tup: tup[1], reverse=True)


def save_sort_by_excellent(shelf):
    rank = []
    for book in shelf.content:
        rank.append((book, int(shelf.content[book]['score1'])))
    sort_score(rank)

    return('excellent', shelf.name, rank,)


def save_sort_by_bad(shelf):
    rank = []
    for book in shelf.content:
        rank.append((book, int(shelf.content[book]['score5'])))
    sort_score(rank)

    return('bad', shelf.name, rank,)


def save_sort_by_ratio(shelf):
    rank = []
    for book in shelf.content:
        ratio = 0
        try:
            ratio = ((int(shelf.content[book]['score1']) +
                      int(shelf.content[book]['score2'])) /
                     (int(shelf.content[book]['score4']) +
                      int(shelf.content[book]['score5'])))
        except ZeroDivisionError:
            ratio = -1
        rank.append((book, round(ratio, 3)))
    sort_score(rank)

    return('ratio', shelf.name, rank,)


def sort_by_votes(shelf):
    rank = []
    for book in shelf.content:
        vote = (int(shelf.content[book]['score1']) +
                int(shelf.content[book]['score2']) +
                int(shelf.content[book]['score3']) +
                int(shelf.content[book]['score4']) +
                int(shelf.content[book]['score5']))
        rank.append((book, vote))
    sort_score(rank)

    return('votes', shelf.name, rank,)


def sort_by_overall(shelf):
    rank = []
    for book in shelf.content:
        # book_name = re.search('《.*》', book)[0]
        book_name = book

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
            rank.append((book_name,
                         round(score / vote + math.log(vote, 1000), 3)))
        except ZeroDivisionError:
            rank.append((book_name, -1))

    sort_score(rank)

    return('overall', shelf.name, rank,)


def sort_by_score(shelf):
    rank = []
    for book in shelf.content:
        score = (2 * int(shelf.content[book]['score1']) +
                 int(shelf.content[book]['score2']) +
                 -1 * int(shelf.content[book]['score4']) +
                 -2 * int(shelf.content[book]['score5']))
        rank.append((book, score))
    sort_score(rank)

    return('score', shelf.name, rank,)


def save_score(rank_type, name, rank, path):
    if 'tags' in path:
        if not os.path.isdir('./score/%s/tags' % rank_type):
            os.makedirs('./score/%s/tags' % rank_type)
    elif 'sort' in path:
        if not os.path.isdir('./score/%s/sort' % rank_type):
            os.makedirs('./score/%s/sort' % rank_type)
    else:
        if not os.path.isdir('./score/%s/other' % rank_type):
            os.makedirs('./score/%s/other' % rank_type)

    with open('./score/{}/{}/{}_{}.txt'.format(
        rank_type, path, name, rank_type),
            'w', encoding='UTF-8') as f:
        f.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in rank))
    logger.info('{} sorting result of {} saved'.format(rank_type, name))


def download_top(shelf, rank, num, download_path):
    book_num = shelf.get_book_num()
    if book_num < num:
        logger.warning('Only {} book(s) in the Shelf {}'
                       .format(book_num, shelf.name))
        num = book_num
    for i in range(num):
        shelf.content[rank[i][0]].download(path=download_path)
    logger.info(('Successfully downloaded top {} books of Shelf {}'
                 .format(num, shelf.name)))


if __name__ == '__main__':
    logger = set_log()
    logger.info('start logging')

    for txt in all_tag:
        path = 'tags'
        with open(txt, 'r', encoding='UTF-8') as f:
            text = f.read()
        shelf = from_json(text)
        overall = sort_by_overall(shelf)
        save_score(*(overall + (path,)))
        download_top(shelf, overall[2], 3, '{}/{}'.format(path, shelf.name))

    for txt in all_sort:
        path = 'sort'
        with open(txt, 'r', encoding='UTF-8') as f:
            text = f.read()
        shelf = from_json(text)
        overall = sort_by_overall(shelf)
        save_score(*(overall + (path,)))
        download_top(shelf, overall[2], 3, '{}/{}'.format(path, shelf.name))

    logger.info('stop logging')
    logging.shutdown()
