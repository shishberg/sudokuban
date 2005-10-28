import random

class Sudoku:
    def __init__(self, other = None):
        self.valid = 1
        self.set = 0
        self.data = []
        self.availCol = []
        self.availRow = []
        self.availBox = []
        if other:
            self.set = other.set
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
            self.set += 1
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

    def solved(self):
        return self.set == 81

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

    def possibleNext(self, evaluate = True, count = 0):
        if not self.valid:
            return []

        next = []
        for x in range(9):
            for y in range(9):
                item = self.data[x][y]
                if isinstance(item, list) and len(item) == 1:
                    next.append(((x, y), item[0]))
                    if count and len(next) >= count:
                        break

                item = self.availCol[x][y]
                if isinstance(item, list) and len(item) == 1:
                    next.append(((x, item[0]), y+1))
                    if count and len(next) >= count:
                        break

                item = self.availRow[x][y]
                if isinstance(item, list) and len(item) == 1:
                    next.append(((item[0], x), y+1))
                    if count and len(next) >= count:
                        break

                item = self.availBox[x][y]
                if isinstance(item, list) and len(item) == 1:
                    xPos = (x % 3) * 3 + (item[0] % 3)
                    yPos = (x / 3) * 3 + (item[0] / 3)
                    next.append(((xPos, yPos), y+1))
                    if count and len(next) >= count:
                        break
            if count and len(next) >= count:
                break

        if evaluate:
            nextBoards = []
            for ((x, y), n) in next:
                s = Sudoku(self)
                s[x, y] = n
                nextBoards.append(s)
            return nextBoards

        return next

    def __cmp__(self, other):
        return cmp(self.data, other.data)

    def __hash__(self):
        curHash = 0
        for x in range(9):
            for y in range(9):
                left = ((x << 4) ^ y) % 28
                item = self.data[x][y]
                if isinstance(item, int):
                    curHash = curHash ^ (item << left)
        return curHash

def paths(start, count=0):
    current = [start]
    seen = []
    seenHash = {}
    while current:
        s = current.pop()
        if not seenHash.has_key(s):
            seen.append(s)
            seenHash[s] = True
            next = s.possibleNext(count = count)
            #if (len(seen) % 100 == 0):
            #    print len(seen), len(current), len(next)
	
            #current += next
	    for n in next:
	        # Technically redundant, but gives better info.
		if not seenHash.has_key(n):
		    current.append(n)
    return seen

def maxPaths(start):
    s = start
    maxCount = 0
    while True:
        next = s.possibleNext(False)
        if not next:
            break
        nextUnique = []
        for n in next:
            if not n in nextUnique:
                nextUnique.append(n)
        if len(nextUnique) > maxCount:
            maxCount = len(nextUnique)
        s = s.possibleNext(count = 1)[0]
    return maxCount

def randomPuzzle(threshold = 1000):
    s = Sudoku()
    noneCount = 0
    while not s.solved():
        noneCount += 1
        if noneCount >= threshold:
            noneCount = 0
            s = Sudoku()
        x = random.randint(0, 8)
        y = random.randint(0, 8)
        if s[x,y]:
            continue
        num = random.randint(1, 9)
        sTmp = Sudoku(s)
        sTmp[x,y] = num
        ps = paths(sTmp, 1)
        if ps:
            p = ps[-1]
            if p.valid:
                s = sTmp
                noneCount = 0
                if p.solved():
                    return s

def findConstrainedPuzzle(minMax = 10):
    while True:
        r = randomPuzzle()
        maxP = maxPaths(r)
        print maxP
        if maxP <= minMax:
            return r

def workBackwards(maxPaths = 10000):
    while True:
        r = randomPuzzle()
        rSolved = r
        while True:
            p = rSolved.possibleNext(count = 1)
            if not p:
                break
            rSolved = p[0]

        rCurrent = rSolved
        while True:
            minGrid = None
            minNext = 0
            for x in range(9):
                for y in range(9):
                    if not rCurrent[x, y]:
                        continue
                    next = Sudoku()
                    for i in range(9):
                        for j in range(9):
                            if i != x or j != y:
                                num = rCurrent[i, j]
                                if num:
                                    next[i, j] = num
                    p = next.possibleNext(False)
                    if p:
                        if (not minGrid) or (len(p) < minNext):
                            minGrid = next
                            minNext = len(p)

            if not minGrid:
                return rCurrent
            
            p = paths(minGrid)
            print len(p), minNext
            if len(p) > maxPaths:
                return rCurrent

            print minGrid
            
            rCurrent = minGrid
            

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

def sampleTough():
    tough = Sudoku()
    tough[2,0] = 1
    tough[3,0] = 9
    tough[6,0] = 3
    tough[6,1] = 2
    tough[0,2] = 7
    tough[1,2] = 6
    tough[4,2] = 2
    tough[8,2] = 9
    tough[0,3] = 3
    tough[4,3] = 6
    tough[8,3] = 5
    tough[2,4] = 2
    tough[3,4] = 1
    tough[5,4] = 3
    tough[6,4] = 4
    tough[0,5] = 4
    tough[4,5] = 9
    tough[8,5] = 3
    tough[0,6] = 1
    tough[4,6] = 3
    tough[7,6] = 9
    tough[8,6] = 7
    tough[2,7] = 4
    tough[2,8] = 5
    tough[5,8] = 8
    tough[6,8] = 6
    return tough

def sampleMed():
    med = Sudoku()
    med[5,0] = 6
    med[6,0] = 1
    med[5,1] = 3
    med[7,1] = 8
    med[2,2] = 9
    med[3,2] = 4
    med[6,2] = 5
    med[8,2] = 2
    med[1,3] = 2
    med[3,3] = 5
    med[7,3] = 4
    med[0,4] = 5
    med[2,4] = 7
    med[6,4] = 9
    med[8,4] = 3
    med[1,5] = 8
    med[5,5] = 1
    med[7,5] = 6
    med[0,6] = 7
    med[2,6] = 6
    med[5,6] = 8
    med[6,6] = 2
    med[1,7] = 4
    med[3,7] = 7
    med[2,8] = 1
    med[3,8] = 9
    return med

def sampleHard():
    hard = Sudoku()
    hard[3,0] = 2
    hard[5,0] = 9
    hard[2,1] = 7
    hard[6,1] = 8
    hard[1,2] = 3
    hard[4,2] = 4
    hard[7,2] = 6
    hard[0,3] = 9
    hard[8,3] = 7
    hard[3,4] = 4
    hard[4,4] = 8
    hard[5,4] = 3
    hard[0,5] = 2
    hard[8,5] = 5
    hard[1,6] = 4
    hard[4,6] = 5
    hard[7,6] = 9
    hard[2,7] = 8
    hard[6,7] = 3
    hard[3,8] = 7
    hard[5,8] = 6
    return hard

def sampleTele():
    tele = Sudoku()
    tele[1,0] = 6
    tele[3,0] = 8
    tele[6,0] = 1
    tele[0,1] = 9
    tele[3,1] = 6
    tele[8,1] = 4
    tele[2,2] = 2
    tele[4,2] = 4
    tele[5,2] = 7
    tele[8,2] = 6
    tele[2,3] = 8
    tele[4,3] = 2
    tele[5,3] = 1
    tele[8,3] = 5
    tele[0,5] = 2
    tele[3,5] = 5
    tele[4,5] = 6
    tele[6,5] = 8
    tele[0,6] = 1
    tele[3,6] = 4
    tele[4,6] = 3
    tele[6,6] = 2
    tele[0,7] = 5
    tele[5,7] = 9
    tele[8,7] = 8
    tele[2,8] = 9
    tele[5,8] = 5
    tele[7,8] = 7
    return tele
