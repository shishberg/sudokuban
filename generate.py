from sudoku import *
import random, os

sizes = [(3,3), (4,4), (5,5), (2,3), (2,4), (3,4), (3,5), (4,5),
         (3,3), (3,3), (3,3), (3,3), (3,3)]

filename = 'random/random-%dx%d-%d.txt'

if __name__ == '__main__':
    while True:
        #size = random.choice(sizes)
        size = (3, 3)
        if size[0] * size[1] < 10 and random.random() < 0.25:
            maxBranch = random.randint(1, 6)
        else:
            maxBranch = 0

        #if size[0] * size[1] < 9:
        #    bailout = 100
        #elif size[0] * size[1] > 15:
        #    bailout = 10
        #elif maxBranch == 0:
        #    bailout = 100
        #elif maxBranch == 1:
        #    bailout = 50
        #else:
        #    bailout = 10
        #bailout = 200 / (maxBranch + 1)
        
        print size, maxBranch
        board = randomPuzzle(size, maxBranch, hatchOnly = True)
        
        n = 1
        while True:
            fn = filename % (size[0], size[1], n)
            if not os.path.exists(fn):
                writeSudoku(board, fn)
                break
            n += 1
