# Note: for compatibility with older versions of Python
# (i.e. hosted at Fissure), 0 and 1 are used instead of
# False and True.

class Sudoku:
    def __init__(self, other = None):
        self.valid = 1 
        self.data = []
        if other:
            for x in range(0, 9):
                row = []
                self.data.append(row)
                for y in range(0, 9):
                    row.append(other.data[x][y][:])
        else:
            for x in range(0, 9):
                row = []
                self.data.append(row)
                for y in range(0, 9):
                    row.append(range(1, 10))

    def __getitem__(self, (x, y)):
        item = self.data[x][y]
        if len(item) == 1:
            return item[0]
        else:
            return None

    def __setitem__(self, (x, y), num):
        item = self.data[x][y]
        if not num in item:
            self.valid = 0
        else:
            self.data[x][y] = [num]
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
        if num in item:
            item.remove(num)
            if len(item) == 0:
                self.valid = 0
            elif len(item) == 1:
                self[x, y] = item[0]

    def possible(self, (x, y)):
        return self.data[x][y]

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
