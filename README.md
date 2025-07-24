# kobodb
A simple python script to browse the content of a Kobo e-reader database.
# Description
This is a simple python script that shows the content of a Kobo e-reader by querying the database stored in the device filesystem. The database filename is `.kobo/KoboReader.sqlite`
  
# Usage
Use `python kobodb.py -h` for help and command line options:

```
usage: kobodb.py [-h] [-v | -l [{all,read,unread,progress}] | -b | -t TITLE | -a AUTHOR] database

Get information from a Kobo sqlite database. This is stored in <KOBO DRIVE:>\.kobo\KoboReader.sqlite on the device filesystem.

positional arguments:
  database              Kobo sqlite database file

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show Kobo database version
  -l [{all,read,unread,progress}], --list [{all,read,unread,progress}]
                        list books stored in the database
  -b, --bookmark        show bookmarks
  -t TITLE, --title TITLE
                        show book(s) info
  -a AUTHOR, --author AUTHOR
                        show all the books of an author
```

## Examples
Get the sqlite database version: `python kobodb.py KoboReader.sqlite -v`

Get the list of all books: `python kobodb.py KoboReader.sqlite -l all`

Get the list of read books: `python kobodb.py KoboReader.sqlite -l read`

Get the list of books started but not completed: `python kobodb.py KoboReader.sqlite -l progress`

Get the list of unread books: `python kobodb.py KoboReader.sqlite -l unread`

Show the bookmarks: `python kobodb.py KoboReader.sqlite -b`

Show books information (return all the items matching the specified title): `python kobodb.py KoboReader.sqlite -t TITLE`

Show all the books of an author: `python kobodb.py KoboReader.sqlite -a AUTHOR`

# License
This code is licensed under MIT.
