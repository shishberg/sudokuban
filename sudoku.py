def readSudoku(filename, regionSize = (3, 3), regionCount = (3, 3)):
    board = SudokuBoard(regionSize, regionCount)
    infile = file(filename)
    x = 0
    y = 0
    for line in infile.readlines():
        if regionSize[0] * regionSize[1] < 10:
	    cells = line
	else:
	    if '+' in line:
	        cells = line
	    else:
	        line = line.replace('|',',').replace('+',',').replace('-',',')
		if len(line) == (regionSize[0] * regionSize[1]) - 2:
		    line = line[1:-1]
	        cells = [cell.strip() or ' ' for cell in line.split(',')]
        for c in cells:
            if c.isdigit():
                board[x, y] = int(c)
            elif c != ' ':
                continue
            x += 1
            if x >= regionSize[0] * regionCount[0]:
                x = 0
                y += 1

    return board
    

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
        
        maxLength = len(str(self.values[-1]))
        cellPrint = '%' + str(maxLength) + 'd'
        emptyCell = ' ' * maxLength

        divider = ''
        for xRegion in range(self.regionCount[0]):
            divider += '+'
            for xSquare in range(self.regionSize[0] * maxLength):
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
        
        nextCell = None
        nextPossible = None

	moves = self.logicalMoves(maxCount = 1)
	if moves:
            for (cell, value) in moves.items():
                cell.setValue(value)
            solutions = self.solve(countOnly, maxCount)
            for (cell, value) in moves.items():
                cell.setValue(None)
            return solutions
	else:
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

    def __hash__(self):
        return self.coord[0] | (self.coord[1] << 16)

    def __cmp__(self, other):
        # Note - this won't make much sense if the
        # cells are from different boards. You have
        # been warned.
        return cmp(self.coord, other.coord)

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

s1 = readSudoku('easy.txt')
s2 = readSudoku('moderate.txt')
s3 = readSudoku('medium.txt')
s4 = readSudoku('challenging.txt')
s5 = readSudoku('tough.txt')
s6 = readSudoku('deadend.txt')
four = readSudoku('4x4.txt', (4,4), (4,4))
sList = [s1, s2, s3, s4, s5, s6]

