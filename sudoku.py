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
        return [self[i, n] for i in range(0, 9)]

    def col(self, n):
        return [self[n, i] for i in range(0, 9)]

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
                string += '+---+---+---+\n'
            for x in range(0, 9):
                if x % 3 == 0:
                    string += '|'
                val = self[x, y]
                if val:
                    string += str(val)
                else:
                    string += ' '
            string += '|\n'
        string += '+---+---+---+\n'
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
            solutions += branch.solve()

        return solutions
                        

#sample = Sudoku()
#sample[3,0] = 9
#sample[5,0] = 7
#sample[6,0] = 3
#sample[8,0] = 8
#sample[2,1] = 8
#sample[4,1] = 2
#sample[0,2] = 3
#sample[5,2] = 8
#sample[7,2] = 4
#sample[0,3] = 2
#sample[1,3] = 3
#sample[4,3] = 7
#sample[2,4] = 7
#sample[3,4] = 1
#sample[5,4] = 4
#sample[6,4] = 9
#sample[4,5] = 6
#sample[7,5] = 7
#sample[8,5] = 1
#sample[1,6] = 5
#sample[3,6] = 7
#sample[8,6] = 3
#sample[4,7] = 9
#sample[6,7] = 7
#sample[0,8] = 6
#sample[2,8] = 9
#sample[3,8] = 8
#sample[5,8] = 5
