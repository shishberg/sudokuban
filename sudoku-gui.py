import os
import pygtk, gtk, pango

from sudoku import *

openWindows = []

class BoardEntry(gtk.Entry):
    def __init__(self, max, cell):
        gtk.Entry.__init__(self, max)

        self.cell = cell
        
        self.set_alignment(0.5)
        self.set_width_chars(2)
        self.set_has_frame(False)
        self.set_editable(False)

    def update(self):
        if self.cell.value:
            self.set_text(str(self.cell.value))
        else:
            self.set_text('')

class SudokuGUI:
    presetFont = pango.FontDescription('sans bold 18')
    unsetFont = pango.FontDescription('sans normal 18')
    unsetColour = gtk.gdk.Color(0x0000, 0x3fff, 0x7fff)
    
    def __init__(self, board, filename = None):
        openWindows.append(self)

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('destroy', self.destroy)

        self.filename = filename
        self.setTitle()

        self.vbox = gtk.VBox(False, 0)
        self.window.add(self.vbox)
        self.vbox.show()

        self.createActions()

        self.board = board

        regions = self.board.regionCount
        regionSize = self.board.regionSize
        
        self.table = gtk.Table(regions[0], regions[1], True)
        self.table.set_row_spacings(5)
        self.table.set_col_spacings(5)
        self.window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0x3fff, 0x3fff, 0x3fff))

        self.entries = []

        for regionY in range(regions[1]):
            for regionX in range(regions[0]):
                regionTable = gtk.Table(regionSize[0], regionSize[1], True)
                regionTable.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0xffff, 0, 0))
                regionTable.set_row_spacings(1)
                regionTable.set_col_spacings(1)

                xStart = regionX * regionSize[0]
                yStart = regionY * regionSize[1]
                for y in range(regionSize[1]):
                    for x in range(regionSize[0]):
                        cellX = xStart + x
                        cellY = yStart + y

                        cell = self.board[cellX, cellY]
                        entry = BoardEntry(2, cell)
                        self.entries.append(entry)
                        
                        if cell.value:
                            entry.modify_font(SudokuGUI.presetFont)
                        else:
                            entry.modify_font(SudokuGUI.unsetFont)
                            entry.modify_text(gtk.STATE_NORMAL, SudokuGUI.unsetColour)

                        entry.update()

                        entry.connect("button_press_event", self.numberMenu, cell);

                        regionTable.attach(entry, x, x + 1, y, y + 1)
                        entry.show()

                self.table.attach(regionTable,
                                  regionX, regionX + 1,
                                  regionY, regionY + 1)
                regionTable.show()

        self.vbox.add(self.table)
        self.table.show()
        self.window.show()


    def setTitle(self):
        title = 'Sudoku Sensei'
        if self.filename:
            title += ' - ' + os.path.basename(self.filename)

        self.window.set_title(title)


    def createActions(self):
        uimanager = gtk.UIManager()
        self.window.add_accel_group(uimanager.get_accel_group())

        self.actionGroup = gtk.ActionGroup('SudokuSensei')
        self.actionGroup.add_actions([('File', None, '_File'),
                                      ('Open', gtk.STOCK_OPEN, '_Open', '<Control>O', None, self.openDialog),
                                      ('Quit', gtk.STOCK_QUIT, '_Quit', None, None, self.destroy),
                                      ('Hints', None, '_Hints'),
                                      ('Solve', None, '_Solve', None, None, self.solve)])

        uimanager.insert_action_group(self.actionGroup, 0)

        uimanager.add_ui_from_file('sudoku-ui.xml')
        self.vbox.add(uimanager.get_widget('/MenuBar'))


    def numberMenu(self, widget, event, cell):
        if event.button == 3:
            values = [0] + cell.possibleValues()
            
            menu = gtk.Menu()
            for value in values:
                if value:
                    text = str(value)
                else:
                    text = ' '

                item = gtk.MenuItem(text)
                item.connect_object('activate', self.setEntry, widget, value)
                item.show()
                menu.append(item)

            menu.popup(None, None, None, event.button, event.time)

            return True

    def setEntry(self, entry, value):
        if value:
            entry.cell.setValue(value)
        else:
            entry.cell.setValue(None)

        entry.update()

    def solve(self, action):
        solutions = self.board.solve(maxCount = 1)
        if solutions:
            for y in range(self.board.regionCount[1] * self.board.regionSize[1]):
                for x in range(self.board.regionCount[0] * self.board.regionSize[0]):
                    self.board[x, y] = solutions[0][x, y].value

            for entry in self.entries:
                entry.update()
    
    def main(self):
        gtk.main()

    def openDialog(self, widget = None):
        # FIXME - save changes?

        self.filedialog = gtk.FileSelection('Open Sudoku puzzle')
        self.filedialog.ok_button.connect('clicked', self.loadFromDialog)
        self.filedialog.cancel_button.connect('clicked', lambda w: filedialog.destroy())
        self.filedialog.show()

    def loadFromDialog(self, widget):
        filename = self.filedialog.get_filename()
        
        self.filedialog.destroy()

        newGui = SudokuGUI(readSudoku(filename), filename)

    def destroy(self, widget, data = None):
        if self in openWindows:
            openWindows.remove(self)
            
        if openWindows:
            self.window.destroy()
        else:
            gtk.main_quit()

if __name__ == '__main__':
    gui = SudokuGUI(readSudoku('sample.txt'))
    gui.main()
