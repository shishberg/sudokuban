from sudoku import *
import random, os

sizes = [(3,3), (4,4), (5,5), (2,3), (2,4), (3,4), (3,5), (4,5)]

filename = 'random/random-%dx%d-%d.txt'

if __name__ == '__main__':
    while True:
        size = random.choice(sizes)
        if random.random() < 0.75:
            maxBranch = random.randint(1, 2)
        else:
            maxBranch = 0

        if maxBranch == 0:
            bailout = 100
        elif maxBranch == 1:
            bailout = 50
        else:
            bailout = 10
        
        print size, maxBranch, bailout
        board = randomPuzzle(size=size, maxBranch=maxBranch,
                             bailout=bailout, output=False)
        n = 1
        while True:
            fn = filename % (size[0], size[1], n)
            if not os.path.exists(fn):
                writeSudoku(board, fn)
                break
            n += 1
