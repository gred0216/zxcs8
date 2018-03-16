from zxcs8 import *
import logging


def main():
    logging.basicConfig(filename='scrawler.log',
                        format='%(asctime)s %(message)s',
                        level=logging.INFO
                        )
    logging.info("scrawler start")
    s1 = Shelf('http://www.zxcs8.com/tag/%E6%AD%A6%E4%BE%A0%E5%B9%BB%E6%83%B3', '武侠幻想')
    s1.get_book_links()
    s1.add_all_book()
    s1.download_all_by_rule()

    logging.info("scrawler stop")


if __name__ == '__main__':
    main()
