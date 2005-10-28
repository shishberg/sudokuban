class Sudoku:
    def __init__(self, other = None):
        self.valid = 1
        self.data = []
        self.availCol = []
        self.availRow = []
        self.availBox = []
        if other:
            for x in range(9):
                dat = []
                col = []
                row = []
                box = []
                self.data.append(dat)
                self.availCol.append(col)
                self.availRow.append(row)
                self.availBox.append(box)
                for y in range(9):
                    item = other.data[x][y]
                    if isinstance(item, list):
                        dat.append(item[:])
                    else:
                        dat.append(item)
 
                    item = other.availCol[x][y]
                    if isinstance(item, list):
                        col.append(item[:])
                    else:
                        col.append(item)

                    item = other.availRow[x][y]
                    if isinstance(item, list):
                        row.append(item[:])
                    else:
                        row.append(item)

                    item = other.availBox[x][y]
                    if isinstance(item, list):
                        box.append(item[:])
                    else:
                        box.append(item)

        else:
            for x in range(9):
                dat = []
                col = []
                row = []
                box = []
                self.data.append(dat)
                self.availCol.append(col)
                self.availRow.append(row)
                self.availBox.append(box)
                for y in range(9):
                    dat.append(range(1, 10))
                    col.append(range(9))
                    row.append(range(9))
                    box.append(range(9))

    def __getitem__(self, (x, y)):
        item = self.data[x][y]
        if isinstance(item, list):
            return None
        else:
            return item

    def __setitem__(self, (x, y), num):
        item = self.data[x][y]
        if num == item:
            return
        elif not num in item:
            self.valid = 0
        else:
            self.data[x][y] = num
            self.availCol[x][num-1] = y
            self.availRow[y][num-1] = x
            gridNum = (y / 3) * 3 + (x / 3)
            gridPos = (y % 3) * 3 + (x % 3)
            self.availBox[gridNum][num-1] = gridPos
 
            for n in range(9):
                if n != num:
                    self.ruleOut((x, y), n)
 
            for row in range(0, 9):
                if row != y:
                    self.ruleOut((x, row), num)
            for col in range(0, 9):
                if col != x:
                    self.ruleOut((col, y), num)

            startX = (x / 3) * 3
            startY = (y / 3) * 3
            for col in range(startX, startX + 3):
                for row in range(startY, startY + 3):
                    if col != x or row != y:
                        self.ruleOut((col, row), num)

            for row in range(0, 9):
                if row != y:
                    self.ruleOut((x, row), num)
            for col in range(0, 9):
                if col != x:
                    self.ruleOut((col, y), num)

            startX = (x / 3) * 3
            startY = (y / 3) * 3
            for col in range(startX, startX + 3):
                for row in range(startY, startY + 3):
                    if col != x or row != y:
                        self.ruleOut((col, row), num)

    def ruleOut(self, (x, y), num):
        item = self.data[x][y]
        if isinstance(item, list):
            if num in item:
                item.remove(num)
                if len(item) == 0:
                    self.valid = 0

        col = self.availCol[x][num-1]
        if isinstance(col, list) and y in col:
            col.remove(y)
            #if num == 6:
            #    print 'col', x, y, num
            #    print col
            if len(col) == 0:
                self.valid = 0

        row = self.availRow[y][num-1]
        if isinstance(row, list) and x in row:
            #print 'row', x, y, num
            row.remove(x)
            if len(row) == 0:
                self.valid = 0

        gridNum = (y / 3) * 3 + (x / 3)
        gridPos = (y % 3) * 3 + (x % 3)
        box = self.availBox[gridNum][num-1]
        if isinstance(box, list) and gridPos in box:
            box.remove(gridPos)
            #if x < 3 and y > 5 and num == 3:
            #    print 'box', x, y, num
            #    print box
            if len(box) == 0:
                self.valid = 0

    def possible(self, (x, y)):
        item = self.data[x][y]
        if isinstance(item, list):
            return item
        else:
            return [item]

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
        if not self.valid:
            return []

        mostConstrained = None
        leastPossible = None

        for y in range(0, 9):
            for x in range(0, 9):
                poss = self.possible((x, y))

                if len(poss) > 1:
                    # If most constrained so far, cache it
                    if (not mostConstrained) or len(leastPossible) > len(poss):
                        mostConstrained = (x, y)
                        leastPossible = poss

                if not self.valid:
                    return []

        if not mostConstrained:
            # Solution found
            return [self]

        # Follow branches
        solutions = []
        for n in leastPossible:
            branch = Sudoku(self)
            branch[mostConstrained] = n
            if branch.valid:
                solutions = solutions + branch.solve()

        return solutions

    def possibleNext(self, evaluate = True):
        if not self.valid:
            return []

        next = []
        for x in range(9):
            for y in range(9):
                item = self.data[x][y]
                if isinstance(item, list) and len(item) == 1:
                    next.append(((x, y), item[0], 'dat'))

                item = self.availCol[x][y]
                if isinstance(item, list) and len(item) == 1:
                    #print 'col', x, y+1, item
                    next.append(((x, item[0]), y+1, 'col'))

                item = self.availRow[x][y]
                if isinstance(item, list) and len(item) == 1:
                    next.append(((item[0], x), y+1, 'row'))

                item = self.availBox[x][y]
                if isinstance(item, list) and len(item) == 1:
                    xPos = (x % 3) * 3 + (item[0] % 3)
                    yPos = (x / 3) * 3 + (item[0] / 3)
                    next.append(((xPos, yPos), y+1, 'box'))

        if evaluate:
            nextBoards = []
            for ((x, y), n, descr) in next:
                s = Sudoku(self)
                s[x, y] = n
                nextBoards.append(s)
            return nextBoards

        return next

    def __cmp__(self, other):
        return cmp(self.data, other.data)

def paths(start):
    current = [start]
    seen = []
    while current:
        s = current.pop()
        if not s in seen:
            seen.append(s)
            next = s.possibleNext()
            print len(next)
            current += next
    return seen


def sampleSudoku():
    sample = Sudoku()
    sample[3,0] = 9
    sample[5,0] = 7
    sample[6,0] = 3
    sample[8,0] = 8
    sample[2,1] = 8
    sample[4,1] = 2
    sample[0,2] = 3
    sample[5,2] = 8
    sample[7,2] = 4
    sample[0,3] = 2
    sample[1,3] = 3
    sample[4,3] = 7
    sample[2,4] = 7
    sample[3,4] = 1
    sample[5,4] = 4
    sample[6,4] = 9
    sample[4,5] = 6
    sample[7,5] = 7
    sample[8,5] = 1
    sample[1,6] = 5
    sample[3,6] = 7
    sample[8,6] = 3
    sample[4,7] = 9
    sample[6,7] = 7
    sample[0,8] = 6
    sample[2,8] = 9
    sample[3,8] = 8
    sample[5,8] = 5
    
    return sample
