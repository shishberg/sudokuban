from wxPython.wx import *
from wxPython.lib.grids import *

class BoardFrame(wxFrame):
    def __init__(self):
        wxFrame.__init__(self, None, -1, "Sudoku")

class SudokuApp(wxApp):
    def OnInit(self):
        frame = BoardFrame()
        frame.Show(True)
        self.SetTopWindow(frame)
        return True
        

if __name__ == '__main__':
    app = SudokuApp(0)
    app.MainLoop()
    
