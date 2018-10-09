from zxcs8 import *
from glob import glob
from crawler import get_category, create_shelf
import sorter


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


def update_book_score(book):
    '''
    Update the scores of a book.

    Arg:
        book: zxcs8.book
    '''
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


def update_shelf(shelf_path):
    '''
    Update every book score in the shelf.
    If there is any new book, add it to the shelf.

    Arg:
        shelf_path: directory of the shelf json file
    '''
    with open(shelf_path, 'r', encoding='UTF-8') as f:
        shelf = from_json(f.read())
    book_list = list(shelf.content.keys())

    # Check if there is any new book
    page = 1
    while page:
        currect_page = shelf.pages + str(page)
        check_sleep_time()
        retry = 5

        while retry:
            try:
                r1 = requests.get(currect_page)
            except requests.exceptions.ConnectionError:
                retry -= 1
                if retry != 0:
                    logger.error(('ConnectionError on %s. '
                                  'Retrying in 1 minute. '
                                  'Retries left: %d'
                                  % (currect_page, retry)))
                    time.sleep(3)
                else:
                    logger.error(('Unable to get book links from %s'
                                  ': ConnectTimeout' % currect_page))
                    return None
                continue
            except requests.exceptions.ConnectTimeout:
                retry -= 1
                if retry != 0:
                    logger.error(('ConnectTimeout on %s. '
                                  'Retrying in 3 seconds. '
                                  'Retries left: %d'
                                  % (currect_page, retry)))
                    time.sleep(3)
                else:
                    logger.error(('Unable to get book links from %s'
                                  ': ConnectTimeout' % currect_page))
                    return None
                continue
            break

        reset_last_retrieve()

        if not r1.ok:
            self.failed_page.append(currect_page)
            logger.error('Unable to get book links of %s: %d error' %
                         (currect_page, r1.status_code))
        else:
            soup = BeautifulSoup(r1.text)
            all_dt = soup.find_all('dt')
            links = []
            for booklink in all_dt:
                bookname = re.findall('(.*?)作者', booklink.text)[0]
                if bookname not in book_list:
                    links.append(booklink.a.get('href'))
                else:
                    page = -1
                    break

            while links:
                jobs = []
                for i in range(3):
                    try:
                        jobs.append(gevent.spawn(shelf._create_book_from_link,
                                                 links.pop()))
                    except IndexError:
                        break
                gevent.joinall(jobs)
            logger.info('Successfully updated ' + currect_page)
            time.sleep(1)

        page += 1

    # Update book score
    while book_list:
        jobs = []
        for i in range(5):
            try:
                book = shelf.content[book_list.pop()]
                jobs.append(gevent.spawn(update_book_score, book))
            except IndexError:
                break
        gevent.joinall(jobs)
        time.sleep(1)

    with open(shelf_path, 'w', encoding='UTF-8') as f:
        f.write(shelf.to_json())

    logger.info('Successfully updated ' + shelf.name)


def update_shelf_list():
    old_sort = [os.path.splitext(os.path.basename(x))[0] for x in all_sort]
    tag, sort = get_category()

    for i in sort:
        if i not in old_sort:
            sort_shelf = create_shelf(i, tag[i])
            shelf_json = sort_shelf.to_json()
            with open('./sort/%s.txt' % i, 'w', encoding='UTF-8') as f:
                f.write(shelf_json)
    for i in old_sort:
        if i not in sort:
            os.makedirs('./old/sort', exist_ok=True)
            os.rename('./sort/%s.txt' % i, './old/sort/%s.txt' % i)



def main():
    logger = set_log()
    logger.info('start logging')

    for tag in all_tag:
        update_shelf(tag)

    for sort in all_sort:
        update_shelf(sort)

    sorter.main()

    logger = set_log()
    logger.info('stop logging')


if __name__ == '__main__':
    update_shelf_list()
    '''
    logger = set_log()
    logger.info('start logging')

    for txt in all_test:
        update_shelf(txt)

    logger.info('stop logging')
    '''
