from zxcs8 import *
from glob import glob


all_tag = glob('./tags/*.txt', recursive=True)
all_sort = glob('./sort/*.txt', recursive=True)
all_test = glob('./test/**/*.txt', recursive=True)
book_score = ('http://www.zxcs8.com/content/plugins/'
              'cgz_xinqing/cgz_xinqing_action.php?action=show&id=')


def set_log():
    logger = logging.getLogger('zxcs8')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

    # filehandler write to sorter.log under current working directory
    fh = logging.FileHandler('updater.log', encoding='UTF-8')
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)

    # streamhandler only print out log warning or above
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.WARNING)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def update_book(book):
    score = book_score + re.search('post/(\d*)', book['url']).groups()[0]

    retry = 5

    while retry:
        try:
            scores = requests.get(score, headers=headers, timeout=30).text
        except requests.exceptions.ConnectionError:
            retry -= 1
            if retry != 0:
                logger.error(('ConnectionError on %s. '
                              'Retrying in 1 minute. Retries left: %d'
                              % (book_score, retry)))
                time.sleep(60)
                continue
            else:
                logger.error(('Unable to get book score from %s'
                              ': ConnectionError' % book_score))
                return None
        except requests.exceptions.ConnectTimeout:
            retry -= 1
            if retry != 0:
                logger.error(('ConnectTimeout on %s. '
                              'Retrying in 3 seconds. '
                              'Retries left: %d' % (book_score, retry)))
                time.sleep(3)
                continue
            else:
                logger.error(('Unable to get book score from %s'
                              ': ConnectTimeout' % book_score))
                return None
        break

    reset_last_retrieve()

    scores = scores.split(',')
    book['score1'] = scores[0]
    book['score2'] = scores[1]
    book['score3'] = scores[2]
    book['score4'] = scores[3]
    book['score5'] = scores[4]

    logger.info('Successfully updated {}'.format(book['name']))


def main():
    logger = set_log()
    logger.info('start logging')

    for tag in all_tag:
        with open(tag, 'r', encoding='UTF-8') as f:
            shelf = from_json(f.read())
        book_list = list(shelf.content.keys())
        while book_list:
            jobs = []
            for i in range(5):
                try:
                    book = shelf.content[book_list.pop()]
                    jobs.append(gevent.spawn(update_book, book))
                except IndexError:
                    break
            gevent.joinall(jobs)
            time.sleep(3)
        with open(tag, 'w', encoding='UTF-8') as f:
            f.write(shelf.to_json())

    for sort in all_sort:
        with open(sort, 'r', encoding='UTF-8') as f:
            shelf = from_json(f.read())
        book_list = list(shelf.content.keys())
        while book_list:
            jobs = []
            for i in range(5):
                try:
                    book = shelf.content[book_list.pop()]
                    jobs.append(gevent.spawn(update_book, book))
                except IndexError:
                    break
            gevent.joinall(jobs)
            time.sleep(1)
        with open(sort, 'w', encoding='UTF-8') as f:
            f.write(shelf.to_json())

    logger.info('stop logging')


if __name__ == '__main__':
    main()
    '''
    logger = set_log()
    logger.info('start logging')

    for txt in all_test:
        with open(txt, 'r', encoding='UTF-8') as f:
            shelf = from_json(f.read())
        book_list = list(shelf.content.keys())
        while book_list:
            jobs = []
            for i in range(5):
                book = shelf.content[book_list.pop()]
                jobs.append(gevent.spawn(update_book, book))
            gevent.joinall(jobs)
            time.sleep(3)
    with open(txt, 'w', encoding='UTF-8') as f:
        f.write(shelf.to_json())
    '''

    logger.info('stop logging')
