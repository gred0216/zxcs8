from zxcs8 import *
from glob import glob
import os
import math
import rarfile
from chardet.universaldetector import UniversalDetector
from itertools import islice
from ast import literal_eval


all_tag = glob('./tags/*.txt')
all_sort = glob('./sort/*.txt')

if os.path.isfile('downloaded.txt'):
    with open('downloaded.txt', 'r', encoding='UTF-8') as f:
        downloaded = literal_eval(f.read())
else:
    downloaded = set()


def set_log():
    logger = logging.getLogger('zxcs8')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

    # filehandler write to sorter.log under current working directory
    fh = logging.FileHandler('sorter.log', encoding='UTF-8')
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)

    # streamhandler only print out log warning or above
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.WARNING)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


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
    '''
    Overall ranking
    '''
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
            rank.append((book_name, 0))

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
        if not os.path.isdir('./score/%s' % rank_type):
            os.makedirs('./score/%s' % rank_type)

    with open('./score/{}/{}/{}_{}.txt'.format(
        rank_type, path, name, rank_type),
            'w', encoding='UTF-8') as f:
        f.write('\n'.join('{}:{}'.format(tup[0], tup[1]) for tup in rank))
    logger.info('{} sorting result of {} saved'.format(rank_type, name))


def download_top(shelf, rank, num, download_path):
    '''
    Download top N books from a shelf sorted by different ranking
    If one book was downloaded before, it will be skipped.
    '''
    global downloaded
    book_num = shelf.get_book_num()
    if book_num < num:
        logger.warning('Only {} book(s) in the Shelf {}'
                       .format(book_num, shelf.name))
        num = book_num
    i = 0
    while i < num:
        is_downloaded = False
        while not is_downloaded:
            for d_book, d_shelf in downloaded:
                if rank[i][0] == d_book:
                    num += 1
                    logger.warning(('Book {} is already downloaded in {}.'
                                    ' Skipping this book.'
                                    .format(rank[i][0], d_shelf.name)))
                    is_downloaded = True
                    break
            if not is_downloaded:
                shelf.content[rank[i][0]].download(path=download_path)
                downloaded.add((rank[i][0], shelf.name))
                is_downloaded = True
        i += 1
    logger.info(('Successfully downloaded top {} books of Shelf {}'
                 .format(num, shelf.name)))


def extract_all_rar():
    '''
    Extract txt from every rar and delete rar file under download folder.
    Need unrar.exe in PATH or working directory
    '''
    rar = glob('./download/**/*.rar', recursive=True)
    for item in rar:
        rf = rarfile.RarFile(item)
        for f in rf.infolist():
            if '.txt' in f.filename:
                rf.extract(f, path=os.path.dirname(item))
        os.remove(item)
        logger.info('Successfully extract {}'.format(item))
    logger.info('All rar extracted')


def convert_to_tc():
    '''
    Convert txt file and path name to traditional Chinese.
    File and folder will be renamed.
    '''
    detector = UniversalDetector()
    txt = glob('./download/**/*.txt', recursive=True)
    for i in txt:
        # Detect the txt encoding
        detector.reset()
        with open(i, 'rb') as b:
            lines = list(islice(b, 50, 55))
        for line in lines:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        if detector.result['confidence'] <= 0.5:
            logger.warning('Detetor is unable to detect encoding of {}. '
                           'Using utf-16-le'.format(convert_to_zhtw(i)))
            encoding = 'utf-16-le'
        else:
            encoding = detector.result['encoding']

        # Convert to traditional Chinese
        with open(i, 'r+', encoding=encoding, errors='ignore') as f:
            text = f.read()
            new_text = convert_to_zhtw(text)
        with open(i, 'w', encoding='UTF-8') as f:
            f.write(new_text)
        if i != convert_to_zhtw(i):
            os.renames(i, convert_to_zhtw(i))
        logger.info('{} converted to Traditional Chinese'
                    .format(os.path.basename(convert_to_zhtw(i))))
    logger.info('All txt converted to Traditional Chinese')


def main_shelf():
    main_shelf = Shelf()
    main_shelf.name = 'main'
    path = ''
    for i in all_tag:
        with open(i, 'r', encoding='UTF-8') as f:
            text = f.read()
        shelf = from_json(text)
        main_shelf.content.update(shelf.content)
    for i in all_sort:
        with open(i, 'r', encoding='UTF-8') as f:
            text = f.read()
        shelf = from_json(text)
        main_shelf.content.update(shelf.content)

    overall = sort_by_overall(main_shelf)
    save_score(*(overall + (path,)))
    main_json = main_shelf.to_json()
    with open('main.txt', 'w', encoding='UTF-8') as f:
        f.write(main_json)
    return main_shelf, overall


def main():
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

    extract_all_rar()
    convert_to_tc()

    with open('downloaded.txt', 'w', encoding='UTF-8') as f:
        f.write(repr(downloaded))

    logger.info('stop logging')
    logging.shutdown()


if __name__ == '__main__':

    logger = set_log()
    logger.info('start logging')

    shelf, rank = main_shelf()
    download_top(shelf, rank[2], 100, 'main')
    extract_all_rar()
    convert_to_tc()

    logger.info('stop logging')
    logging.shutdown()

    # main()
