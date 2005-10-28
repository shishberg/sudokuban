#!/usr/local/bin/python

import cgi, sys
from sudoku import Sudoku

def showForm(form = None):
    print '<form method=post>'
    
    print '<table align=center border=0 cellspacing=4 cellpadding=0 bgcolor=#7f7f7f>'
    for row in range(0, 3):
        print '<tr>'
        for col in range(0, 3):
            print '<td>'
            print '<table border=0 cellpadding=0 cellspacing=1 bgcolor=#000000>'
            for row2 in range(0, 3):
                print '<tr>'
                for col2 in range(0, 3):
                    x = col * 3 + col2
                    y = row * 3 + row2
                    key = 'num%d%d' % (x, y)
                    if form and form.has_key(key):
                        print '<td><input type=text size=1 maxlength=1 name=%s value=%s></td>' % (key, form[key].value)
                    else:
                        print '<td><input type=text size=1 maxlength=1 name=%s></td>' % key
                print '</tr>'
            print '</table>'
            print '</td>'
        print '</tr>'
    print '</table>'
    print '<p align=center><input type=submit name=solve value=Solve></p>'
    print '</form>'

def solve(form):
    sudoku = Sudoku()

    link = 'sudoku.cgi?solve=Solve'

    for col in range(0, 9):
        for row in range(0, 9):
            key = 'num%d%d' % (col, row)
            if form.has_key(key):
                val = int(form[key].value)
                sudoku[col, row] = val
                link = link + '&%s=%d' % (key, val)

    solutions = sudoku.solve()

    if solutions:
        for sol in solutions:
            htmlGrid(sol, sudoku)
    else:
        print '<p align=center>Sorry, no solutions.</p>'
        showForm(form)

    print '<p align=center><a href="%s">Link here</a> | <a href=sudoku.cgi>Start again</a></p>' % link

def htmlGrid(sudoku, original):
    print '<table align=center border=0 cellspacing=4 cellpadding=0 bgcolor=#7f7f7f>'
    for row in range(0, 3):
        print '<tr>'
        for col in range(0, 3):
            print '<td>'
            print '<table border=0 cellpadding=0 cellspacing=1 bgcolor=#000000>'
            for row2 in range(0, 3):
                print '<tr>'
                for col2 in range(0, 3):
                    val = sudoku[col * 3 + col2, row * 3 + row2]
                    if val:
                        valStr = str(val)
                    else:
                        valStr = '&nbsp;'

                    if original[col * 3 + col2, row * 3 + row2]:
                        valStr = '<b>%s</b>' % valStr

                    print '<td width=30 align=center bgcolor=#ffffff><font color=#000000 size=+2>%s</font></td>' % valStr
                    
                print '</tr>'
            print '</table>'
            print '</td>'
        print '</tr>'
    print '</table>'
    print '<br>'
    
            

def main():
    print 'Status: 200 OK'
    print 'Content-type: text/html'
    print
    print '<html><head><title>Sudoku solver</title></head>'
    print '<body bgcolor=#00003f text=#ffffff link=#7f7fff vlink=#bf7fff>'
    print '<h2 align=center>Sudoku Solver</h2>'
    print '<p align=center><a href=mailto:dave@dmcleish.id.au>by Shishberg</a></p>'
    print '<br>'
    
    form = cgi.FieldStorage()
    if form.has_key('solve'):
        solve(form)
    else:
        showForm()

    print '</body></html>'

if __name__ == '__main__':
    sys.exit(main())
