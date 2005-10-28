import pygtk
import gtk
import pango
import gobject

from sudoku import *

class SudokuGUI:
    presetFont = pango.FontDescription('sans bold 16')
    unsetFont = pango.FontDescription('sans normal 16')
    unsetColour = gtk.gdk.Color(0x0000, 0x3fff, 0x7fff)
    cellBackground = gtk.gdk.Color(0xffff, 0xffff, 0xffff)
    
    def __init__(self, board):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('destroy', self.destroy)

        self.board = board

        regions = self.board.regionCount
        regionSize = self.board.regionSize
        
        self.table = gtk.Table(regions[0], regions[1], True)
        self.table.set_row_spacings(5)
        self.table.set_col_spacings(5)
        self.window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0x3fff, 0x3fff, 0x3fff))

        self.listModel = gtk.ListStore(gobject.TYPE_STRING)
        for n in range(1, self.board.values + 1):
            self.listModel.append([str(n)])
        self.listModel.append([' '])
        
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
                        entry = gtk.ComboBox(self.listModel)
                        entry.set_border_width(0)
                        entry.set_wrap_width(regionSize[0])
                        
                        entryCell = gtk.CellRendererText()
                        entry.pack_start(entryCell)
                        entry.add_attribute(entryCell, 'text', 0)
                        
                        cell = self.board[cellX, cellY]
                        index = cell.value
                        if index:
                            index -= 1
                        else:
                            index = self.board.values
                        entry.set_active(index)
                        
                        entry.modify_bg(gtk.STATE_NORMAL, SudokuGUI.cellBackground)
                        entry.modify_fg(gtk.STATE_NORMAL, SudokuGUI.cellBackground)
                        entry.modify_text(gtk.STATE_NORMAL, SudokuGUI.cellBackground)
                        entry.modify_base(gtk.STATE_NORMAL, SudokuGUI.cellBackground)
                        if cell.value:
                            #entryCell.modify_font(SudokuGUI.presetFont)
                            entryCell.set_property('font', 'bold 16')
                        else:
                            entryCell.set_property('font', 'normal 16')
                            entryCell.set_property('foreground-gdk', SudokuGUI.unsetColour)
                            #entryCell.modify_font(SudokuGUI.unsetFont)
                            #entryCell.modify_text(gtk.STATE_NORMAL, SudokuGUI.unsetColour)

                        regionTable.attach(entry, x, x + 1, y, y + 1)
                        entry.show()

                self.table.attach(regionTable,
                                  regionX, regionX + 1,
                                  regionY, regionY + 1)
                regionTable.show()
                

        self.window.add(self.table)
        self.table.show()
        self.window.show()
    
    def main(self):
        gtk.main()

    def destroy(self, widget, data = None):
        gtk.main_quit()

if __name__ == '__main__':
    gui = SudokuGUI(readSudoku('sample.txt'))
    gui.main()
    
