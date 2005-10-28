import pygtk
import gtk
import pango

from sudoku import *

class BoardEntry(gtk.Entry):
    def __init__(self, max, cell):
        gtk.Entry.__init__(self, max)

        self.cell = cell
        
        self.set_alignment(0.5)
        self.set_width_chars(2)
        self.set_has_frame(False)

    def update(self):
        if self.cell.value:
            self.set_text(str(self.cell.value))
        else:
            self.set_text('')

class SudokuGUI:
    presetFont = pango.FontDescription('sans bold 16')
    unsetFont = pango.FontDescription('sans normal 16')
    unsetColour = gtk.gdk.Color(0x0000, 0x3fff, 0x7fff)
    
    def __init__(self, board):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('destroy', self.destroy)

        vbox = gtk.VBox(False, 0)
        self.window.add(vbox)
        vbox.show()

        self.menubar = gtk.MenuBar()
        vbox.add(self.menubar)
        self.menubar.show()

        fileMenu = gtk.MenuItem('File')
        fileMenu.show()
        self.menubar.append(fileMenu)

        hintsMenuItem = gtk.MenuItem('Hints')
        hintsMenuItem.show()
        self.menubar.append(hintsMenuItem)

        hintsMenu = gtk.Menu()
        hintsMenuItem.set_submenu(hintsMenu)
        
        menuSolve = gtk.MenuItem('Solve')
        menuSolve.connect('activate', self.solve)
        menuSolve.show()
        hintsMenu.append(menuSolve)

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

        vbox.add(self.table)
        self.table.show()
        self.window.show()

    def numberMenu(self, widget, event, cell):
        if event.button == 3:
            menu = gtk.Menu()
            for value in range(self.board.values + 1):
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

    def solve(self, widget):
        solutions = self.board.solve(maxCount = 1)
        if solutions:
            for y in range(self.board.regionCount[1] * self.board.regionSize[1]):
                for x in range(self.board.regionCount[0] * self.board.regionSize[0]):
                    self.board[x, y] = solutions[0][x, y].value

            for entry in self.entries:
                entry.update()
    
    def main(self):
        gtk.main()

    def destroy(self, widget, data = None):
        gtk.main_quit()

if __name__ == '__main__':
    gui = SudokuGUI(readSudoku('sample.txt'))
    gui.main()
    
