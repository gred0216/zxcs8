# zxcs8
This is a crawler of [知軒藏書](http://www.zxcs8.com/map.html)

## Feature
* Create different category shelves from the site
* Create custom shelf
* Retrieve information of all books from the category
* Using scores of books from the site as filter and download books
* Search books by words
* Save the shelf and book data as json
* Use [gevent](http://www.gevent.org/) to crawl synchronously
* Logging
* Sorting
* Download top books by sorted overall ranking
* Auto extract rar files
* Convert the txt files to Traditional Chinese in UTF-8

### Sorting
There are five voting level, each level is given an score accordingly:

Excellent(仙草):2, Good(糧草):1, Fair(乾草):0, Poor(枯草):-1, Bad(毒草): -2

* Excellent: sorted by number of excellent votes

* Bad: sorted by number of bad votes

* Ratio: sorted by number of excellent and good votes divided by poor and bad votes

  If poor and bad votes are zero, the ratio is -1

* Votes: sorted by number of votes

* Score: sorted by total score

* Overall: sorted by average score + popular score
## TODO
* manually set filter rules(maybe not)
* Update per period(maybe per month)
