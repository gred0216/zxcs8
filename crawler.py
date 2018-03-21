from zxcs8 import *
import logging


def main():
    logger = set_log()
    logger.info('scrawler start')
    tags, sort = get_category()

    os.makedirs('./tags/', exist_ok=True)
    for name, link in tags.items():
        temp_shelf = Shelf(link, name)
        temp_shelf.get_book_links()
        temp_shelf.add_all_book()
        shelf_json = temp_shelf.to_json()

        with open('./tags/%s.txt' % name, 'w', encoding='UTF-8') as f:
            f.write(shelf_json)

    os.makedirs('./sort/', exist_ok=True)
    for name, link in sort.items():
        temp_shelf = Shelf(link, name)
        temp_shelf.get_book_links()
        temp_shelf.add_all_book()
        shelf_json = temp_shelf.to_json()

        with open('./sort/%s.txt' % name, 'w', encoding='UTF-8') as f:
            f.write(shelf_json)

    logger.info('scrawler stop')
    logger.shutdown()


def set_log():
    logger = logging.getLogger('zxcs8')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

    # filehandler write to scrawler.log under current working directory
    fh = logging.FileHandler('scrawler.log', encoding='UTF-8')
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)

    # streamhandler only print out log warning or above
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.WARNING)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def get_category():
    r = requests.get('http://www.zxcs8.com/map.html')
    r.encoding = 'UTF-8'
    if r.ok:
        soup = BeautifulSoup(r.text)
    tag_a = soup.find(id='tags').find_all('a')
    tags = {}
    for i in tag_a:
        text = re.match('(.*)\(', i.text)[1]
        href = i.get('href')
        tags[text] = href

    sort_a = soup.find(id='sort').find_all('a')
    sort = {}
    for i in sort_a:
        if i.img:
            continue
        text = re.match('(.*)\(', i.text)[1]
        href = i.get('href')
        sort[text] = href

    return tags, sort


if __name__ == '__main__':

    logger = set_log()
    logger.info('logger start')
    test = 'http://www.zxcs8.com/sort/38'
    s1 = Shelf(test, 'test2')
    s1.get_book_links()
    s1.add_all_book()

    with open('./test2.txt', 'w', encoding='UTF-8') as f:
        f.write(s1.to_json())

    logger.info('logger stop')
    logger.shutdown()
