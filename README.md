# zxcs8
This is a crawler of [知軒藏書](http://www.zxcs8.com/map.html). 

## Feature
* Create different category shelves from the site.
* Create custom shelf
* Retrieve information of all books from the category.
* Using scores of books from the site as filter and download books.
* Search books by words.
* Save the shelf and book as json.
* Use [gevent](http://www.gevent.org/) to crawl synchronously.
* Logging.
* Sorting.

### Sorting
* Excellent: sorted by number of excellent votes(仙草)

* Bad: sorted by number of bad votes(毒草)

* Ratio: sorted by number of excellent and good votes divided by poor and bad votes((仙草+糧草)/(枯草+毒草))

If poor and bad votes are zero, the ratio is -1.

## TODO
* manually set filter rules
* download books from sorted result
