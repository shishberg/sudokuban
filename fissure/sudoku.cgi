#!/usr/local/bin/python

import cgi, sys

# Main solver code included here - see sudoku.py

class Sudoku:
    def __init__(self, other = None):
        self.data = []
        if other:
            for n in range(0, 9):
                self.data.append(other.data[n][:])
        else:
            for n in range(0, 9):
                self.data.append([0] * 9)

    def __getitem__(self, (x, y)):
        return self.data[x][y]

    def __setitem__(self, (x, y), num):
        self.data[x][y] = num

    def row(self, n):
        list = []
        for i in range(0, 9):
            list.append(self[i, n])
        return list

    def col(self, n):
        list = []
        for i in range(0, 9):
            list.append(self[n, i])
        return list

    def grid(self, (gridX, gridY)):
        startX = gridX * 3
        startY = gridY * 3
        grid = []
        for y in range(startY, startY + 3):
            for x in range(startX, startX + 3):
                grid.append(self[x, y])

        return grid

    def __repr__(self):
        string = '\n'
        for y in range(0, 9):
            if y % 3 == 0:
                string = string + '+---+---+---+\n'
            for x in range(0, 9):
                if x % 3 == 0:
                    string = string + '|'
                val = self[x, y]
                if val:
                    string = string + str(val)
                else:
                    string = string + ' '
            string = string + '|\n'
        string = string + '+---+---+---+\n'
        return string

    def solve(self):
        mostConstrained = None
        mostConsValid = None

        for y in range(0, 9):
            for x in range(0, 9):
                val = self[x, y]
                if not val:
                    # Start with everything valid
                    valid = range(1, 10)
                    
                    # Then cancel some out
                    curRow  = self.row(y)
                    curCol  = self.col(x)
                    curGrid = self.grid((x/3, y/3))
                    
                    for n in curRow:
                        if n in valid:
                            valid.remove(n)
                            
                    for n in curCol:
                        if n in valid:
                            valid.remove(n)
                            
                    for n in curGrid:
                        if n in valid:
                            valid.remove(n)

                    # If none left, configuration is invalid
                    if not valid:
                        return []

                    # If most constrained so far, cache it
                    if (not mostConstrained) or len(mostConsValid) > len(valid):
                        mostConstrained = (x, y)
                        mostConsValid = valid

        if not mostConstrained:
            # Solution found
            return [self]
        
        # Follow branches
        solutions = []
        for n in mostConsValid:
            branch = Sudoku(self)
            branch[mostConstrained] = n
            solutions = solutions + branch.solve()

        return solutions


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
                sudoku[col, row] = int(form[key].value)
                link = link + '&%s=%d' % (key, sudoku[col, row])

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

