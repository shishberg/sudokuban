import os, sys, time
import pygtk, gtk, pango

from sudoku import *

class BoardEntry(gtk.EventBox):
    backgroundColour = gtk.gdk.Color(0xffff, 0xffff, 0xffff)
    normalShade = 0xffff
    minHighlightShade = 0x7fff
    highlightShades = [
        (0xafff, 0xcfff, 0xefff), # Blue
        (0xafff, 0xefff, 0x8fff), # Green
        (0xefff, 0xafff, 0xafff) # Red
        ]

    def __init__(self, cell, gui):
        gtk.EventBox.__init__(self)

        self.cell = cell
        self.gui = gui

        self.label = gtk.Label()
        self.label.set_alignment(0.5, 0.5)
        self.label.show()
        self.add(self.label)

        self.connect('button_press_event', gui.clickInCell, self.cell)
        self.connect('popup_menu', gui.numberMenu, self.cell)
        self.connect('focus', gui.setSelection)

    def update(self):
        if self.cell.value:
            self.label.set_text(str(self.cell.value))
        else:
            self.label.set_text(' ')

        if self.gui.sweepHighlight and self.gui.selectedValue:
            channels = [BoardEntry.normalShade] * 3

            for n in range(3):
                if not self.cell.sets[n].isAvailable(self.gui.selectedValue):
                    shade = BoardEntry.highlightShades[n]
                    for i in range(3):
                        channels[i] = max(channels[i] - (0xffff - shade[i]),
                                          BoardEntry.minHighlightShade)
            
            self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(channels[0], channels[1], channels[2]))
        else:
            self.modify_bg(gtk.STATE_NORMAL, BoardEntry.backgroundColour)

        if self is self.gui.selection:
            self.set_state(gtk.STATE_SELECTED)
        else:
            self.set_state(gtk.STATE_NORMAL)

class SudokuGUI:
    presetFont = pango.FontDescription('sans bold 18')
    unsetFont = pango.FontDescription('sans normal 18')
    unsetColour = gtk.gdk.Color(0x0000, 0x3fff, 0x7fff)
    
    def __init__(self, board = SudokuBoard(), filename = None):
        openWindows.append(self)

        self.sweepHighlight = False
        self.selection = None
        self.selectedValue = 0

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
                        entry = BoardEntry(cell, self)
                        self.entries.append(entry)
                        
                        if cell.value:
                            entry.label.modify_font(SudokuGUI.presetFont)
                        else:
                            entry.label.modify_font(SudokuGUI.unsetFont)
                            entry.label.modify_fg(gtk.STATE_NORMAL, SudokuGUI.unsetColour)

                        entry.update()

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

    def setSelection(self, widget, data = None):
        oldSelection = self.selection
        self.selection = widget
        oldSelection.update()
        self.selection.update()
        if self.selection.cell.value and self.selection.cell.value != self.selectedValue:
            self.selectedValue = self.selection.cell.value
            if self.sweepHighlight:
                self.updateAll()

    def createActions(self):
        uimanager = gtk.UIManager()
        self.window.add_accel_group(uimanager.get_accel_group())

        self.actionGroup = gtk.ActionGroup('SudokuSensei')
        self.actionGroup.add_actions([('File', None, '_File'),
                                      ('Open', gtk.STOCK_OPEN, '_Open', '<Control>O', None, openDialog),
                                      ('Quit', gtk.STOCK_QUIT, '_Quit', None, None, self.destroy),
                                      ('Hints', None, '_Hints'),
                                      ('Solve', None, '_Solve', None, None, self.solve)
                                      ])
        self.actionGroup.add_toggle_actions([('Sweep', None, '_Sweep Highlighting', None, None, self.toggleSweepHighlight)
                                             ])

        uimanager.insert_action_group(self.actionGroup, 0)

        uimanager.add_ui_from_file('sudoku-ui.xml')
        self.vbox.add(uimanager.get_widget('/MenuBar'))

    def toggleSweepHighlight(self, action):
        self.sweepHighlight = action.get_active()
        if self.selection:
            self.selectedValue = self.selection.cell.value
        else:
            self.selectedValue = 0
        self.updateAll()

    def clickInCell(self, widget, event, cell):
        if event.button == 1:
            self.setSelection(widget)
        elif event.button == 3:
            return self.numberMenu(widget, cell, event.button, event.time)

    def numberMenu(self, widget, cell, button = 0, eventTime = 0):
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

        menu.popup(None, None, None, button, eventTime)

        return True

    def updateAll(self):
        for entry in self.entries:
            entry.update()

    def setEntry(self, entry, value):
        if value:
            entry.cell.setValue(value)
        else:
            entry.cell.setValue(None)

        if self.sweepHighlight:
            self.updateAll()
        else:
            entry.update()

    def solve(self, action):
        solutions = self.board.solve(maxCount = 1)
        if solutions:
            for y in range(self.board.regionCount[1] * self.board.regionSize[1]):
                for x in range(self.board.regionCount[0] * self.board.regionSize[0]):
                    self.board[x, y] = solutions[0][x, y].value

            for entry in self.entries:
                entry.update()

    def destroy(self, widget, data = None):
        if self in openWindows:
            openWindows.remove(self)
            
        if openWindows:
            self.window.destroy()
        else:
            gtk.main_quit()


# Global stuff


openWindows = []


def openDialog(widget = None):
    filedialog = gtk.FileSelection('Open Sudoku puzzle')
    filedialog.ok_button.connect_object('clicked', loadFromDialog, filedialog)
    filedialog.cancel_button.connect_object('clicked', destroyFileDialog, filedialog)
    filedialog.show()


def loadFromDialog(filedialog):
    filename = filedialog.get_filename()
    
    filedialog.destroy()

    newGui = SudokuGUI(readSudoku(filename), filename)


def destroyFileDialog(widget):
    widget.destroy()

    if not openWindows:
        gtk.main_quit()

    
if __name__ == '__main__':
    args = sys.argv[1:]
    if args:
        for filename in args:
            newGui = SudokuGUI(readSudoku(filename), filename)
    else:
        newGui = SudokuGUI()

    gtk.main()
