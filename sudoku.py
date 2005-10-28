class SudokuBoard:
    def __init__(self, regionSize = (3, 3), regionCount = (3, 3)):
        self.regionSize = regionSize
        self.regionCount = regionCount
        self.size = (regionSize[0] * regionCount[0], regionSize[1] * regionCount[1])
        
        self.values = range(1, regionSize[0] * regionSize[1] + 1)

        self.cells = []       
        for y in range(regionSize[1] * regionCount[1]):
            row = []
            self.cells.append(row)
            for x in range(regionSize[0] * regionCount[0]):
                row.append(SudokuCell(self, (x, y)))

        self.sets = []
        # Columns
        for x in range(self.size[0]):
            set = ExclusionSet(self)
            self.sets.append(set)
            for y in range(self.size[1]):
                set.add(self.cells[y][x])
                
        # Rows
        for y in range(self.size[1]):
            set = ExclusionSet(self)
            self.sets.append(set)
            row = self.cells[y]
            for cell in row:
                set.add(cell)

        # Regions
        for yStart in range(0, self.size[1], regionSize[1]):
            for xStart in range(0, self.size[0], regionSize[0]):
                set = ExclusionSet(self)
                self.sets.append(set)
                for y in range(yStart, yStart + regionSize[1]):
                    for x in range(xStart, xStart + regionSize[0]):
                        set.add(self.cells[y][x])

    def copy(self):
        newBoard = SudokuBoard(self.regionSize, self.regionCount)
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                newBoard[x, y] = self[x, y].value

        return newBoard

    def __repr__(self):
        
        divider = ''
        for xRegion in range(self.regionCount[0]):
            divider += '+'
            for xSquare in range(self.regionSize[0]):
                divider += '-'
        divider += '+\n'

        maxLength = len(str(self.values[-1]))
        cellPrint = '%' + str(maxLength) + 'd'
        emptyCell = ' ' * maxLength

        board = ''
        for yRegion in range(0, self.size[1], self.regionSize[1]):
            board += divider
            for ySquare in range(self.regionSize[1]):
                for xRegion in range(0, self.size[0], self.regionSize[0]):
                    board += '|'
                    for xSquare in range(self.regionSize[0]):
                        cell = self.cells[yRegion + ySquare][xRegion + xSquare]
                        if cell.value:
                            board += cellPrint % cell.value
                        else:
                            board += emptyCell
                board += '|\n'
        board += divider + '\n'

        return board

    def __getitem__(self, (x, y)):
        return self.cells[y][x]
            
    def __setitem__(self, (x, y), value):
        self.cells[y][x].setValue(value)

    def logicalMoves(self):
        moves = {}

        for row in self.cells:
            for cell in row:
                if not cell.value:
                    possible = cell.possibleValues()
                    if len(possible) == 1:
                        moves[cell] = possible[0]

        for set in self.sets:
            for (value, cell) in set.determinedValues():
                if not cell.value:
                    moves[cell] = value

        return moves    
            
        
    def solve(self, countOnly = False, maxCount = None):
        if (maxCount != None) and (maxCount <= 0):
            if countOnly:
                return 0
            else:
                return []
        
        nextCell = None
        nextPossible = None
        
        for row in self.cells:
            for cell in row:
                if not cell.value:
                    possible = cell.possibleValues()
                    if not possible:
                        if countOnly:
                            return 0
                        else:
                            return []
                    if (not nextCell) or (len(possible) < len(nextPossible)):
                        nextCell = cell
                        nextPossible = possible

        if not nextCell:
            if countOnly:
                return 1
            else:
                return [self.copy()]

        if countOnly:
            solutions = 0
        else:
            solutions = []
            
        for value in nextPossible:
            nextCell.setValue(value)
            solutions += self.solve(countOnly, maxCount)
            nextCell.setValue(None)

            if maxCount != None:
                if countOnly:
                    maxCount -= solutions
                else:
                    maxCount -= len(solutions)
                if maxCount <= 0:
                    return solutions

        return solutions
        

class SudokuCell:
    "One cell of a Sudoku board."
    
    def __init__(self, board, coord):
        self.value = None
        self.board = board
        self.coord = coord
        self.sets = []

    def __repr__(self):
        return str(self.coord)

    def possibleValues(self):
        possible = self.board.values[:]

        for set in self.sets:
            excluded = set.excludedValues[self]
            possible = [value for value in possible if excluded[value] <= 0]

        return possible

    def setValue(self, value):
        if self.value:
            for set in self.sets:
                set.unset(self, self.value)
                
        self.value = value

        if self.value:
            for set in self.sets:
                set.set(self, value)

    def exclude(self, value, increment = 1):
        for set in self.sets:
            set.exclude(self, value, increment)
        

class ExclusionSet:
    def __init__(self, board):
        self.board = board
        self.cells = []
        
        self.excludedValues = {}
        
        self.excludedCells = {}
        for value in self.board.values:
            self.excludedCells[value] = {}

    def add(self, cell):
        self.cells.append(cell)
        cell.sets.append(self)
        
        excludedValueMap = {}
        self.excludedValues[cell] = excludedValueMap
        for value in self.board.values:
            excludedValueMap[value] = 0
            self.excludedCells[value][cell] = 0

    def exclude(self, cell, value, increment = 1):
        self.excludedValues[cell][value] += increment
        self.excludedCells[value][cell] += increment

    def include(self, cell, value):
        self.exclude(cell, value, -1)
        
    def set(self, cell, value, increment = 1):
        for c in self.cells:
            if not c is cell:
                c.exclude(value, increment)

        for v in self.board.values:
            if v != value:
                cell.exclude(v, increment)

    def unset(self, cell, value):
        self.set(cell, value, -1)
    
    def determinedValues(self):
        determined = []
        for value in self.board.values:
            possibleCell = None
            for cell in self.cells:
                if self.excludedCells[value][cell] <= 0:
                    if not possibleCell:
                        possibleCell = cell
                    else:
                        possibleCell = None
                        break
            if possibleCell:
                determined.append((value, possibleCell))

        return determined











        

## class SudokuBoard:
##     def __init__(self, other = None):
##         self.valid = True 
##         self.data = []
##         if other:
##             for x in range(0, 9):
##                 row = []
##                 self.data.append(row)
##                 for y in range(0, 9):
##                     row.append(other.data[x][y][:])
##         else:
##             for x in range(0, 9):
##                 row = []
##                 self.data.append(row)
##                 for y in range(0, 9):
##                     row.append(range(1, 10))

##     def __getitem__(self, (x, y)):
##         item = self.data[x][y]
##         if len(item) == 1:
##             return item[0]
##         else:
##             return None

##     def __setitem__(self, (x, y), num):
##         item = self.data[x][y]
##         if not num in item:
##             self.valid = 0
##         else:
##             self.data[x][y] = [num]
##             for row in range(0, 9):
##                 if row != y:
##                     self.ruleOut((x, row), num)
##             for col in range(0, 9):
##                 if col != x:
##                     self.ruleOut((col, y), num)

##             startX = (x / 3) * 3
##             startY = (y / 3) * 3
##             for col in range(startX, startX + 3):
##                 for row in range(startY, startY + 3):
##                     if col != x or row != y:
##                         self.ruleOut((col, row), num)

##     def ruleOut(self, (x, y), num):
##         item = self.data[x][y]
##         if num in item:
##             item.remove(num)
##             if len(item) == 0:
##                 self.valid = 0
##             elif len(item) == 1:
##                 self[x, y] = item[0]

##     def possible(self, (x, y)):
##         return self.data[x][y]

##     def row(self, n):
##         list = []
##         for i in range(0, 9):
##             list.append(self[i, n])
##         return list

##     def col(self, n):
##         list = []
##         for i in range(0, 9):
##             list.append(self[n, i])
##         return list

##     def grid(self, (gridX, gridY)):
##         startX = gridX * 3
##         startY = gridY * 3
##         grid = []
##         for y in range(startY, startY + 3):
##             for x in range(startX, startX + 3):
##                 grid.append(self[x, y])

##         return grid

##     def __repr__(self):
##         string = '\n'
##         for y in range(0, 9):
##             if y % 3 == 0:
##                 string = string + '+---+---+---+\n'
##             for x in range(0, 9):
##                 if x % 3 == 0:
##                     string = string + '|'
##                 val = self[x, y]
##                 if val:
##                     string = string + str(val)
##                 else:
##                     string = string + ' '
##             string = string + '|\n'
##         string = string + '+---+---+---+\n'
##         return string

##     def solve(self):
##         if not self.valid:
##             return []
        
##         mostConstrained = None
##         leastPossible = None

##         for y in range(0, 9):
##             for x in range(0, 9):
##                 poss = self.possible((x, y))
                                
##                 if len(poss) > 1:
##                     # If most constrained so far, cache it
##                     if (not mostConstrained) or len(leastPossible) > len(poss):
##                         mostConstrained = (x, y)
##                         leastPossible = poss

##                 if not self.valid:
##                     return []

##         if not mostConstrained:
##             # Solution found
##             return [self]
        
##         # Follow branches
##         solutions = []
##         for n in leastPossible:
##             branch = Sudoku(self)
##             branch[mostConstrained] = n
##             if branch.valid:
##                 solutions = solutions + branch.solve()

##         return solutions
                        
def sample():
    sample = SudokuBoard()
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
