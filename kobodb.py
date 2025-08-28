#!/usr/bin/env python

# MIT License

# Copyright (c) 2025 ema

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sqlite3
import argparse
import os

class KoboException(Exception):
   pass

class Book:
   def __init__(self, rec):
      self.title = rec['Title']
      self.author = rec['Attribution']
      self.mime_type = rec['MimeType']
      self.read_status = self.__to_read_status(rec['ReadStatus'])
      self.filepath = rec['ContentID']
      self.last_read_date = rec['DateLastRead']
      self.percent_read = rec['___PercentRead']
      self.time_spent_reading_sec = (-1 if rec['TimeSpentReading'] == None else rec['TimeSpentReading'])
      self.filesize = rec['___FileSize']
      self.language = rec['Language']

   def __to_read_status(self, value):
      if value == 0:
         return 'not read'
      elif value == 1:
         return 'in progress'
      elif value == 2:
         return 'completed'
      else:
         return 'unknown'

class Bookmark:
   def __init__(self, rec):
      self.id = rec['BookmarkID']
      self.book_title = rec['Title']
      self.book_author = rec['Attribution']
      self.date_created = rec['DateCreated']
      self.date_modified = rec['DateModified']
      self.type = rec['Type']
      self.text = rec['Text']
      self.annotation = rec['Annotation']
      
class KoboDB:

   BOOK_NOT_READ = 0
   BOOK_IN_PROGRESS = 1
   BOOK_COMPLETED = 2

   def __init__(self, filename):
      self.filename = filename
      self.conn = None
      
   def connect(self):
      try:
         self.conn = sqlite3.connect('file:'+self.filename+'?mode=ro', uri=True)
         self.conn.row_factory = sqlite3.Row
      except Exception as e:
         raise KoboException('Error connecting database, {0}'.format(e))

   def close(self):
      if self.conn != None:
         self.conn.close()
         
   def get_version(self):
      try:
         cur = self.conn.cursor()
         res = cur.execute('SELECT version FROM dbversion')
         r = res.fetchone()
      except Exception as e:
         raise KoboException('Error getting version, {0}'.format(e))
      return r[0]

   def get_books(self, title = None, author = None, status = None):
      lb = []
      try:
         filter_str = '' if title == None else 'AND Title LIKE "%'+title+'%"'
         filter_str += '' if author == None else ' AND Attribution LIKE "%'+author+'%"'
         filter_str += '' if status == None else ' AND ReadStatus='+str(status)
         cur = self.conn.cursor()
         res = cur.execute('SELECT Title, Attribution, MimeType, ReadStatus, ContentID, DateLastRead, ___PercentRead, TimeSpentReading, ___FileSize, Language'
                           ' FROM content WHERE BookID is Null AND ContentType = 6 AND IsDownloaded in ("true",1) AND ContentID LIKE "file%"'
                           ' {0}'
                           ' ORDER BY Title'.format(filter_str))
         records = res.fetchall()
         for r in records:
            lb.append(Book(r))
      except Exception as e:
         raise KoboException('Error getting books, {0}'.format(e))
      return lb

   def get_bookmarks(self, title = None, author = None):
      lb = []
      try:
         cur = self.conn.cursor()
         res = cur.execute('SELECT BookmarkID, Title, Attribution , b.DateCreated, b.DateModified, Type, Text, Annotation'
                           ' FROM content c INNER JOIN Bookmark b ON c.ContentID = b.VolumeID')
         records = res.fetchall()
         for r in records:
            pass
            lb.append(Bookmark(r))
      except Exception as e:
         raise KoboException('Error getting bookmarks, {0}'.format(e))
      return lb

def seconds_to_str(secs):
   if secs < 0:
      return 'not available'
   hours = secs//3600
   minutes = (secs%3600)//60
   seconds = secs - 3600*hours - 60*minutes
   return '{}h {}min {}sec'.format(hours, minutes, seconds)
   
def to_str(field):
   return '-' if field == None else field
   
def print_book_info(book):
   print('Title: {}'.format(book.title))
   print('Author: {}'.format(book.author))
   print('Mime type: {}'.format(book.mime_type))
   print('language: {}'.format(book.language))
   print('File: {}'.format(book.filepath))
   print('Size: {} bytes'.format(book.filesize))
   print('Read status: {}'.format(book.read_status))
   print('Last read date: {}'.format(book.last_read_date))
   print('Percent read: {}%'.format(book.percent_read))
   print('Time spent reading: {}'.format(seconds_to_str(book.time_spent_reading_sec)))
   print('-'*80)
   
def print_bookmark(bm):
   print('Bookmark ID: {}'.format(bm.id))
   print('Type: {}'.format(bm.type))
   print('Book title: {}'.format(bm.book_title))
   print('Book author: {}'.format(bm.book_author))
   print('Date created: {}'.format(bm.date_created))
   print('Date modified: {}'.format(bm.date_modified))
   if bm.text != None and bm.text != '':
      print('Text: "{}"'.format(bm.text))
   if bm.annotation != None and bm.annotation != '':
      print('Annotation: "{}"'.format(bm.annotation))
   print('-'*80)

def export_books(books, filename):
   Columns = ['title','author','mime_type','language','filepath','filesize','read_status','last_read_date','percent_read']
   Separator = '\t'
   f = open(filename, 'w')
   f.write(Separator.join(Columns))
   f.write('\n')
   for b in books:
      data = [b.title,b.author,b.mime_type,b.language,b.filepath,str(b.filesize),b.read_status,b.last_read_date,str(b.percent_read)]
      data = map(to_str, data)
      f.write(Separator.join(data))
      f.write('\n')
   f.close()
   
def book_status(status):
   if status == 'read':
      return KoboDB.BOOK_COMPLETED
   elif status == 'unread':
      return KoboDB.BOOK_NOT_READ
   elif status == 'progress':
      return KoboDB.BOOK_IN_PROGRESS
   else:
      return None

def main():
   parser = argparse.ArgumentParser(description='Get information from a Kobo sqlite database. This is stored in <KOBO DRIVE:>\\.kobo\\KoboReader.sqlite on the device filesystem.')
   parser.add_argument('database', help='Kobo sqlite database file')
   group = parser.add_mutually_exclusive_group()
   group.add_argument('-v', '--version', help='show Kobo database version', action='store_true')
   group.add_argument('-l', '--list',  nargs='?', const='all', choices=['all', 'read', 'unread', 'progress'], help='list books stored in the database')
   group.add_argument('-e', '--export', help='export to TAB separated text file')
   group.add_argument('-b', '--bookmark', help='show bookmarks', action='store_true')
   group.add_argument('-t', '--title', help='show book(s) info')   
   group.add_argument('-a', '--author', help='show all the books of an author')   
   
   args = parser.parse_args()  
   
   db = KoboDB(args.database)

   try:
      db.connect()
      
      if args.version:
         print('DB Version: {0}'.format(db.get_version()))

      elif args.list:
         for i,b in enumerate(db.get_books(status=book_status(args.list))):
            print('{0}) {1} - {2}'.format(i+1, b.title, b.author))

      elif args.bookmark:
         for k in db.get_bookmarks():
            print_bookmark(k)
        
      elif args.title != None:
         for b in db.get_books(title=args.title):
            print_book_info(b)

      elif args.author != None:
         for i,b in enumerate(db.get_books(author=args.author)):
            print('{0}) {1} - {2}'.format(i+1, b.title, b.author))
            
      elif args.export != None:
         export_books(db.get_books(), args.export)
         print('database content exported to file {0}.'.format(args.export))
            
      else:
         parser.print_usage()
            
   except Exception as e:
      print(e)
      
   finally:
      db.close()

if __name__ == '__main__':
   main()