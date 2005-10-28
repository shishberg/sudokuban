from wxPython.wx import *
from wxPython.grid import *
from sudoku import *

class BoardGrid(wxGrid):
    givenNumberFont = wxFont(24, wxSWISS, wxNORMAL, wxBOLD)
    userNumberFont = wxFont(24, wxSWISS, wxNORMAL, wxNORMAL)
    regionBorderSize = 3
    
    def __init__(self, parent, board):
        wxGrid.__init__(self, parent, -1)

        self.board = board

        regionSize = board.regionSize
        regionCount = board.regionCount
        size = (regionSize[0] * regionCount[0],
                regionSize[1] * regionCount[1])
        gridSize = (size[0] + regionCount[0] - 1,
                    size[1] + regionCount[1] - 1)
        
        self.CreateGrid(gridSize[0], gridSize[1])
        self.DisableDragColSize()
        self.DisableDragRowSize()

        self.SetRowMinimalAcceptableHeight(BoardGrid.regionBorderSize)
        self.SetColMinimalAcceptableWidth(BoardGrid.regionBorderSize)

        for y in range(gridSize[1]):
            if (y + 1) % (regionSize[1] + 1) == 0:
                self.SetRowSize(y, BoardGrid.regionBorderSize)
                for x in range(gridSize[0]):
                    self.SetCellBackgroundColour(x, y, wxBLACK)
                continue
            
            self.SetRowSize(y, 30)
            
            for x in range(gridSize[0]):
                if (x + 1) % (regionSize[0] + 1) == 0:
                    if y == 0:
                        self.SetColSize(x, BoardGrid.regionBorderSize)
                        self.SetCellBackgroundColour(x, y, wxBLACK)
                    continue
                
                if y == 0:
                    self.SetColSize(x, 30)

                boardX = x - (x / (regionSize[0] + 1))
                boardY = y - (y / (regionSize[1] + 1))

                self.SetCellAlignment(x, y, wxALIGN_CENTRE, wxALIGN_CENTRE)
                
                cell = board[boardX, boardY]
                if cell.value:
                    self.SetCellValue(x, y, str(cell.value))
                    self.SetCellFont(x, y, BoardGrid.givenNumberFont)
                else:
                    self.SetCellFont(x, y, BoardGrid.userNumberFont)

class BoardFrame(wxFrame):
    def __init__(self, board):
        wxFrame.__init__(self, None, -1, "Sudoku")
        grid = BoardGrid(self, board)        

class SudokuApp(wxApp):
    def OnInit(self):
        frame = BoardFrame(readSudoku('sample.txt'))
        frame.Show(True)
        self.SetTopWindow(frame)
        return True
        
if __name__ == '__main__':
    app = SudokuApp(0)
    app.MainLoop()
    
