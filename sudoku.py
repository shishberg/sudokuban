# sudoku.py - Core Sudoku board representation, solving algorithm
# and other such.

import sys, re, math, random

def testDifficulty():
    for filename in ['easy.txt', 'moderate.txt', 'medium.txt', 'challenging.txt', 'tough.txt', 'deadend.txt']:
        print filename.ljust(16), readSudoku(filename).difficulty()

CELL_PRESET = 0
CELL_UNSET  = 1

sizeLine = re.compile('^\\s*([0-9]+)\\s*,\\s*([0-9]+)\\s*$')

DIFFICULTY_STR = (
    (5.0,  'Outrageous'),
    (15.0, 'Tough'),
    (25.0, 'Challenging'),
    (35.0, 'Moderate'),
    (None, 'Easy')
    )

def readSudoku(filename):
    infile = file(filename)
    numbers = []
    size = None
    for line in infile.readlines():
        sizeMatch = sizeLine.match(line)
        if sizeMatch:
            size = (int(sizeMatch.group(1)), int(sizeMatch.group(2)))
            continue
        
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

    if not size:
        width = int(math.sqrt(math.sqrt(len(numbers))))
        size = (width, width)
    board = SudokuBoard((size[0], size[1]), (size[1], size[0]))
    numbers.reverse()
    for y in range(size[0] * size[1]):
        for x in range(size[0] * size[1]):
            (value, preset) = numbers.pop()
            board[x, y] = value
            if preset:
                board[x, y].state = CELL_PRESET

    return board

def writeSudoku(board, filename):
    out = file(filename, 'w')
    print >> out, '%d, %d' % board.regionSize
    out.write(str(board))
    out.close()

def randomCompleted(size = (3, 3), progress = None, cancel = None):
    board = SudokuBoard((size[0], size[1]), (size[1], size[0]))
    solution = board.solve(maxCount = 1, shuffle = True,
                           progress = progress, cancel = cancel)
    return solution[0]

def randomPuzzle(size = (3, 3), maxBranch = 0,
                 symmetrical = True, hatchOnly = True,
                 progress = None, fraction = None, cancel = None):

    board = randomCompleted(size, progress=progress, cancel=cancel)
    width = size[0] * size[1]
    if symmetrical:
        cells = range(width * width / 2 + 1)
    else:
        cells = range(width * width)

    random.shuffle(cells)

    count = 0.0

    for n in cells:
        if fraction:
            fraction(count / len(cells))
            count += 1.0
        if cancel:
            if cancel():
                return None
            
        x = n % width
        y = n / width

        cell = board[x, y]
        value = cell.value
        if not value:
            continue
        cell.setValue(None)

        if symmetrical:
            x2 = width - x - 1
            y2 = width - y - 1
            if x2 != x or y2 != y:
                cell2 = board[x2, y2]
                value2 = cell2.value
                cell2.setValue(None)
            else:
                cell2 = None

        if board.difficulty(maxBranch, hatchOnly) == None or \
               board.solve(True, 2) != 1:
            
            cell.setValue(value)
            if symmetrical and cell2:
                cell2.setValue(value2)

    for row in board.cells:
        for cell in row:
            if cell.value:
                cell.state = CELL_PRESET
    
    return board
            

class SudokuBoard:
    def __init__(self, regionSize = (3, 3), regionCount = (3, 3)):
        self.regionSize = regionSize
        self.regionCount = regionCount
        self.size = (regionSize[0] * regionCount[0], regionSize[1] * regionCount[1])
        self.cellCount = self.size[0] * self.size[1]
        self.filled = 0
        
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

        self.regionSets = []
        # Regions
        for yStart in range(0, self.size[1], regionSize[1]):
            for xStart in range(0, self.size[0], regionSize[0]):
                set = ExclusionSet(self)
                self.sets.append(set)
                self.regionSets.append(set)
                for y in range(yStart, yStart + regionSize[1]):
                    for x in range(xStart, xStart + regionSize[0]):
                        set.add(self.cells[y][x])

    def copy(self, presetOnly = False):
        newBoard = SudokuBoard(self.regionSize, self.regionCount)
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                oldCell = self[x, y]
                if (not presetOnly) or (oldCell.state == CELL_PRESET):
                    newCell = newBoard[x, y]
                    newCell.setValue(oldCell.value)
                    newCell.state = oldCell.state

        return newBoard

    def isSolved(self):
        return self.filled == self.cellCount

    def isValid(self):
        values = range(1, self.values + 1)
        for set in self.sets:
            available = values[:]
            for cell in set.cells:
                if cell.value:
                    if not cell.value in available:
                        return False
                    available.remove(cell.value)

        return True

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

    def difficultyString(self, maxBranch = 0, progress = None, cancel = None):
        diff = self.difficulty(maxBranch, False, progress, cancel)

        for (minDiff, string) in DIFFICULTY_STR:
            if (diff == None) or (minDiff == None) or (diff < minDiff):
                return string

        return DIFFICULTY_STR[-1][1]

    def difficulty(self, maxBranch = 0, hatchOnly = False,
                   progress = None, cancel = None):
        
        (total, count) = self.calcDifficulty(maxBranch, hatchOnly, progress, cancel)
        if total < 0:
            return None
        elif count == 0:
            return 0.0
        else:
            return float(total) / count

    def calcDifficulty(self, maxBranch, hatchOnly, progress, cancel):
        if progress:
            progress()
        if cancel:
            if cancel():
                return (-1, 0)
        
        if self.isSolved():
            return (0, 0)
        
        if maxBranch < 0:
            return (-1, 0)

        # Cross-hatch moves
        moves = self.logicalMoves(False, False, True).items()
        if moves:
            diff = 5 * len(moves)
        elif not hatchOnly:
            moves = self.logicalMoves(True, True, False).items()
            diff = len(moves)

        for (cell, value) in moves:
            cell.setValue(value)

        if moves:
            (total, count) = self.calcDifficulty(maxBranch, hatchOnly, progress, cancel)

        for (cell, value) in moves:
            cell.setValue(None)
            
        if moves:
            if total == -1:
                return (-1, count + 1)
            else:
                return (total + diff, count + 1)

        if maxBranch <= 0:
            return (-1, 0)

        nextCell = None
        nextPossible = None

        for row in self.cells:
            for cell in row:
                if not cell.value:
                    possible = cell.possibleValues()
                    if not possible:
                        # Dead end
                        return (-1, 0)
                    if (not nextCell) or (len(possible) < len(nextPossible)):
                        nextCell = cell
                        nextPossible = possible

        if not nextCell:
            # Solved
            return (0, 1)

        total = 0
        count = 1

        if len(nextPossible) - 1 > maxBranch:
            nextPossible = nextPossible[:maxBranch]
            maxBranch = 0
        else:
            maxBranch -= len(nextPossible) - 1

        for value in nextPossible:
            nextCell.setValue(value)
            (nextTotal, nextCount) = self.calcDifficulty(maxBranch, hatchOnly, progress, cancel)
            if (nextTotal != -1):
                total += nextTotal
            count += nextCount
            nextCell.setValue(None)

        if count == 1:
            return (-1, 1)
        
        return (total, count)


    def logicalMoves(self, allScan = True, exclude = True, hatch = False, maxCount = 0):
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

        if allScan:
            for set in self.sets:
                for (value, cell) in set.determinedValues():
                    if not cell.value:
                        moves[cell] = value
                        if maxCount and (len(moves) >= maxCount):
                            return moves

        if hatch:
            for set in self.regionSets:
                for (value, cell) in set.determinedValues():
                    if not cell.value:
                        moves[cell] = value
                        if maxCount and (len(moves) >= maxCount):
                            return moves            

        return moves
    
    def solve(self, countOnly = False, maxCount = None, shuffle = False,
              progress = None, cancel = None):

        if progress:
            progress()
        if cancel:
            if cancel():
                if countOnly:
                    return 0
                else:
                    return []
        
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

        if shuffle:
            rows = self.cells[:]
            random.shuffle(rows)
        else:
            rows = self.cells

        for row in rows:
            if shuffle:
                row = row[:]
                random.shuffle(row)
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

        if shuffle:
            random.shuffle(nextPossible)
            
        for value in nextPossible:
            nextCell.setValue(value)
            solutions += self.solve(countOnly, maxCount, shuffle, progress, cancel)
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

    def possibleValues(self, excludeSelf = False):
        if excludeSelf:
            possible = None
            exclude = self
        else:
            possible = self.cachedPossibleValues
            exclude = None

        if possible == None:
            possible = range(1, self.board.values + 1)

            for set in self.sets:
                possible = [value for value in possible if set.isAvailable(value, exclude)]

        if not excludeSelf:
            self.cachedPossibleValues = possible
            
        return possible

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
        if value and not self.value:
            self.board.filled += 1
        elif self.value and not value:
            self.board.filled -= 1
        
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
        
    def isAvailable(self, value, exclude = None):
        if not exclude:
            cached = self.cachedIsAvailable[value - 1]
            if cached != None:
                return cached

        available = True
        for cell in self.cells:
            if (not cell is exclude) and (cell.value == value):
                available = False
                break

        if not exclude:
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
