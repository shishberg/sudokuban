import sys, math

CELL_PRESET = 0
CELL_UNSET  = 1

def readSudoku(filename):
    
    infile = file(filename)
    numbers = []
    for line in infile.readlines():
        preset = True
        cur = ''
        for char in line:
            if char == '.' or char.isdigit():
                cur += char
            else:
                if cur:
                    cur = cur.replace('.', '')
                    if cur.isdigit():
                        numbers.append((int(cur), preset))
                    else:
                        numbers.append((None, False))
                    cur = ''
                    preset = True
                if char == '*':
                    preset = False
    
    size = int(math.sqrt(math.sqrt(len(numbers))))
    board = SudokuBoard((size, size), (size, size))
    numbers.reverse()
    for y in range(size * size):
        for x in range(size * size):
            (value, preset) = numbers.pop()
            board[x, y] = value
            if preset:
                board[x, y].state = CELL_PRESET

    return board
    

class SudokuBoard:
    def __init__(self, regionSize = (3, 3), regionCount = (3, 3)):
        self.regionSize = regionSize
        self.regionCount = regionCount
        self.size = (regionSize[0] * regionCount[0], regionSize[1] * regionCount[1])
        
        self.values = regionSize[0] * regionSize[1]

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
                newCell = newBoard[x, y]
                oldCell = self[x, y]
                newCell.setValue(oldCell.value)
                newCell.state = oldCell.state

        return newBoard

    def __repr__(self):
        
        maxLength = len(str(self.values))
        emptyCell = '.' * maxLength

        divider = ''
        for xRegion in range(self.regionCount[0]):
            divider += '+'
            for xSquare in range(self.regionSize[0] * (maxLength + 1)):
                divider += '-'
        divider += '+\n'

        board = ''
        for yRegion in range(0, self.size[1], self.regionSize[1]):
            board += divider
            for ySquare in range(self.regionSize[1]):
                for xRegion in range(0, self.size[0], self.regionSize[0]):
                    board += '|'
                    for xSquare in range(self.regionSize[0]):
                        cell = self.cells[yRegion + ySquare][xRegion + xSquare]
                        if cell.value:
                            if cell.state == CELL_UNSET:
                                board += '*'
                            else:
                                board += ' '
                                
                            cellStr = str(cell.value)
                            while len(cellStr) < maxLength:
                                cellStr = '.' + cellStr
                            board += cellStr
                        else:
                            board += ' ' + emptyCell
                board += '|\n'
        board += divider

        return board

    def __getitem__(self, (x, y)):
        return self.cells[y][x]
            
    def __setitem__(self, (x, y), value):
        self.cells[y][x].setValue(value)

    def difficulty(self):

        sweep = self.logicalMoves(True, False)
        exclude = self.logicalMoves(False, True)
        diff = 50 - (2 * len(sweep)) - len(exclude)

        cell = None
        value = None
        if sweep:
            keys = sweep.keys()
            cell = keys[0]
            value = sweep[cell]
        elif exclude:
            keys = exclude.keys()
            cell = keys[0]
            value = exclude[cell]

        if cell:
            cell.setValue(value)
            diff += self.difficulty()
            cell.setValue(None)
            return diff

        nextCell = None
        nextPossible = None
        
        for row in self.cells:
            for cell in row:
                if not cell.value:
                    possible = cell.possibleValues()
                    if not possible:
                        # Dead end
                        return 10
                    if (not nextCell) or (len(possible) < len(nextPossible)):
                        nextCell = cell
                        nextPossible = possible

        if not nextCell:
            # Solved
            return 0

        for value in nextPossible:
            nextCell.setValue(value)
            diff += self.difficulty()
            nextCell.setValue(None)

        return diff


    def logicalMoves(self, sweep = True, exclude = True, maxCount = 0):
        moves = {}

        if exclude:
            for row in self.cells:
                for cell in row:
                    if not cell.value:
                        possible = cell.possibleValues()
                        if len(possible) == 1:
                            moves[cell] = possible[0]
                            if maxCount and (len(moves) >= maxCount):
                                return moves

        if sweep:
            for set in self.sets:
                for (value, cell) in set.determinedValues():
                    if not cell.value:
                        moves[cell] = value
                        if maxCount and (len(moves) >= maxCount):
                            return moves

        return moves

    def solve(self, countOnly = False, maxCount = None):
        if (maxCount != None) and (maxCount <= 0):
            if countOnly:
                return 0
            else:
                return []

        revert = []
        
        while True:
            moves = self.logicalMoves(maxCount = 1)
            if not moves:
                break
            
            for (cell, value) in moves.items():
                revert.append(cell)
                cell.setValue(value)
        
        nextCell = None
        nextPossible = None

        for row in self.cells:
            for cell in row:
                if not cell.value:
                    possible = cell.possibleValues()
                    if not possible:
                        for cell in revert:
                            cell.setValue(None)
                        if countOnly:
                            return 0
                        else:
                            return []
                    if (not nextCell) or (len(possible) < len(nextPossible)):
                        nextCell = cell
                        nextPossible = possible
                        break
        
        if not nextCell:
            if countOnly:
                solutions = 1
            else:
                solutions = [self.copy()]
            for cell in revert:
                cell.setValue(None)
            return solutions

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
                    break

        for cell in revert:
            cell.setValue(None)
            
        return solutions
        

class SudokuCell:
    "One cell of a Sudoku board."
    
    def __init__(self, board, coord):
        self.value = None
        self.board = board
        self.coord = coord
        self.sets = []
        self.state = CELL_UNSET

        self.clearCache()

    def __repr__(self):
        return str(self.coord)

    def __hash__(self):
        return self.coord[0] | (self.coord[1] << 16)

    def __cmp__(self, other):
        # Note - this won't make much sense if the
        # cells are from different boards. You have
        # been warned.
        return cmp(self.coord, other.coord)

    def possibleValues(self):
        if self.cachedPossibleValues == None:
            self.cachedPossibleValues = range(1, self.board.values + 1)

            for set in self.sets:
                self.cachedPossibleValues = [value for value in self.cachedPossibleValues if set.isAvailable(value)]

        return self.cachedPossibleValues

    def couldBe(self, value):
        if self.value:
            return self.value == value

        #if self.cachedPossibleValues != None:
        #    return value in self.cachedPossibleValues
        
        #for set in self.sets:
        #    if not set.isAvailable(value):
        #        return False
        
        #return True

        return value in self.possibleValues()

    def setValue(self, value):
        for set in self.sets:
            if value and not self.value:
                set.cachedIsAvailable[value - 1] = False
            else:
                set.clearCache()
            for cell in set.cells:
                cell.clearCache()

        self.value = value
        
    def clearCache(self):
        self.cachedPossibleValues = None

class ExclusionSet:
    def __init__(self, board):
        self.board = board
        self.cells = []

        self.cachedIsAvailable = [None] * self.board.values
        
    def isAvailable(self, value):
        cached = self.cachedIsAvailable[value - 1]
        if cached != None:
            return cached

        available = True
        for cell in self.cells:
            if cell.value == value:
                available = False
                break

        self.cachedIsAvailable[value - 1] = available
        return available

    def add(self, cell):
        self.cells.append(cell)
        cell.sets.append(self)

    def determinedValues(self):
        determined = []
        for value in range(1, self.board.values + 1):
            possibleCell = None
            for cell in self.cells:
                if cell.couldBe(value):
                    if not possibleCell:
                        possibleCell = cell
                    else:
                        possibleCell = None
                        break
            if possibleCell:
                determined.append((value, possibleCell))

        return determined

    def clearCache(self):
        for i in range(len(self.cachedIsAvailable)):
            self.cachedIsAvailable[i] = None


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

#s1 = readSudoku('easy.txt')
#s2 = readSudoku('moderate.txt')
#s3 = readSudoku('medium.txt')
#s4 = readSudoku('challenging.txt')
#s5 = readSudoku('tough.txt')
#s6 = readSudoku('deadend.txt')
#four = readSudoku('4x4.txt', (4,4), (4,4))
#sList = [s1, s2, s3, s4, s5, s6]

if __name__ == '__main__':
    for filename in sys.argv[1:]:
        print filename
        sudoku = readSudoku(filename)
        solutions = sudoku.solve()
        for board in solutions:
            print board
