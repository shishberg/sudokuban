#!/usr/bin/python

import cgi, sys
from sudoku import Sudoku

def showForm():
    pass

def main():
    print 'Status: 200 OK'
    print 'Content-type: text/html\n'
    
    form = cgi.FieldStorage()
    if form.has_key('Solve'):
        solve(form)
    else:
        showForm()

if __name__ == '__main__':
    sys.exit(main())
