from wxPython.wx import *
from wxPython.lib.grids import *
from sudoku import *

class BoardFrame(wxFrame):
    def __init__(self, board):
        wxFrame.__init__(self, None, -1, "Sudoku")

        self.board = board

        regionSize = board.regionSize
        regionCount = board.regionCount
        
        boardGrid = wxGridSizer(regionCount[0], regionCount[1], 5, 5)

        for y in range(regionCount[1]):
            for x in range(regionCount[0]):
                regionGrid = wxGridSizer(regionSize[0], regionSize[1], 0, 0)
                for n in range(regionCount[0] * regionCount[1]):
                    cellX = (x * 3) + (n % 3)
                    cellY = (y * 3) + (n / 3)
                    cell = board[cellX, cellY]
                    if cell.value:
                        value = str(cell.value)
                    else:
                        value = ''
                    button = wxButton(self, -1, value)
                    button.SetSize((30, 30))
                    button.SetBackgroundColour((255, 255, 255))
                    regionGrid.Add(button)
                boardGrid.Add(regionGrid)
        
        self.SetSizer(boardGrid)
        

class SudokuApp(wxApp):
    def OnInit(self):
        frame = BoardFrame(readSudoku('sample.txt'))
        frame.Show(True)
        self.SetTopWindow(frame)
        return True
        
if __name__ == '__main__':
    app = SudokuApp(0)
    app.MainLoop()
    
