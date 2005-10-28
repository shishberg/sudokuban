import os, sys, time
import pygtk, gtk, pango

from sudoku import *

class BoardEntry(gtk.EventBox):
    backgroundColour = gtk.gdk.Color(0xffff, 0xffff, 0xffff)
    presetFont = pango.FontDescription('sans bold 18')
    unsetFont = pango.FontDescription('sans 18')
    presetColour = gtk.gdk.Color(0x0000, 0x0000, 0x0000)
    unsetColour = gtk.gdk.Color(0x0000, 0x3fff, 0x7fff)

    minShade = 0x7fff
    normalShade = [0xffff, 0xffff, 0xffff]
    highlightBaseShades = [
        (0xafff, 0xcfff, 0xefff), # Blue
        (0xafff, 0xefff, 0x8fff), # Green
        (0xefff, 0xafff, 0xafff)  # Red
        ]
    highlightShades = {}
    for a in (True, False):
        for b in (True, False):
            for c in (True, False):
                shade = normalShade[:]
                for n in range(3):
                    if not (a,b,c)[n]:
                        for channel in range(3):
                            shade[channel] = max(
                                shade[channel] - 0xffff + highlightBaseShades[n][channel],
                                minShade
                                )
                highlightShades[(a,b,c)] = gtk.gdk.Color(shade[0], shade[1], shade[2])

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
        self.connect('size-request', self.setSizeRequest)

        self.update()

    def update(self):
        if self.cell.value:
            self.label.set_text(str(self.cell.value))
        else:
            self.label.set_text(' ')

        if self.gui.sweepHighlight and self.gui.selectedValue:
            shadeKey = (
                self.cell.sets[0].isAvailable(self.gui.selectedValue),
                self.cell.sets[1].isAvailable(self.gui.selectedValue),
                self.cell.sets[2].isAvailable(self.gui.selectedValue)
                )
            self.modify_bg(gtk.STATE_NORMAL, BoardEntry.highlightShades[shadeKey])
        else:
            self.modify_bg(gtk.STATE_NORMAL, BoardEntry.backgroundColour)

        if self.cell.state == CELL_PRESET:
            self.label.modify_font(BoardEntry.presetFont)
            self.label.modify_fg(gtk.STATE_NORMAL, BoardEntry.presetColour)
        else:
            self.label.modify_font(BoardEntry.unsetFont)
            self.label.modify_fg(gtk.STATE_NORMAL, BoardEntry.unsetColour)
            
        if self is self.gui.selection:
            self.set_state(gtk.STATE_SELECTED)
        else:
            self.set_state(gtk.STATE_NORMAL)

    def setSizeRequest(self, widget, requisition):
        if requisition.width < requisition.height:
            self.set_size_request(requisition.height, requisition.height)
        elif requisition.height < requisition.width:
            self.set_size_request(requisition.width, requisition.width)

class SudokuGUI:
    def __init__(self, board = SudokuBoard(), filename = None):
        openWindows.append(self)

        self.sweepHighlight = False
        self.selection = None
        self.selectedValue = 0

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('destroy', self.destroy)

        self.vbox = gtk.VBox(False, 0)
        self.window.add(self.vbox)
        self.vbox.show()

        self.createActions()

        self.setFilename(filename)

        self.board = board

        regions = self.board.regionCount
        regionSize = self.board.regionSize
        
        self.table = gtk.Table(regions[1], regions[0], True)
        self.table.set_row_spacings(5)
        self.table.set_col_spacings(5)
        self.window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0x3fff, 0x3fff, 0x3fff))

        self.entries = []

        for regionY in range(regions[1]):
            for regionX in range(regions[0]):
                regionTable = gtk.Table(regionSize[1], regionSize[0], True)
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
                        
                        regionTable.attach(entry, x, x + 1, y, y + 1)
                        entry.show()

                self.table.attach(regionTable,
                                  regionX, regionX + 1,
                                  regionY, regionY + 1)
                regionTable.show()

        self.vbox.add(self.table)
        self.table.show()
        self.window.show()

    def setFilename(self, filename):
        self.filename = filename
        self.setTitle()
        self.actionGroup.get_action('Save').set_sensitive(filename != None)

    def setTitle(self):
        title = 'Sudoku Sensei'
        if self.filename:
            title = os.path.basename(self.filename) + ' - ' + title

        self.window.set_title(title)

    def setSelection(self, widget, data = None):
        oldSelection = self.selection
        self.selection = widget
        if oldSelection:
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
                                      ('New', gtk.STOCK_NEW, '_New', '<Control>N', None, newDialog),
                                      ('Open', gtk.STOCK_OPEN, '_Open', '<Control>O', None, openDialog),
                                      ('Save', gtk.STOCK_SAVE, '_Save', '<Control>S', None, self.saveFile),
                                      ('SaveAs', gtk.STOCK_SAVE_AS, 'Save _As...', '<Control><Shift>S', None, self.saveAsDialog),
                                      ('Quit', gtk.STOCK_QUIT, '_Quit', '<Control>Q', None, self.destroy),
                                      ('Puzzle', None, '_Puzzle'),
                                      ('CheckValid', None, 'Check _Valid', None, None, self.checkValid),
                                      ('CheckSolvable', None, 'Check _Solvable', None, None, self.checkSolvable),
                                      ('Difficulty', None, '_Difficulty', None, None, self.difficulty),
                                      ('Hints', None, '_Hints'),
                                      ('Solve', None, '_Solve', None, None, self.solve)
                                      ])
        self.actionGroup.add_toggle_actions([('Sweep', None, '_Sweep Highlighting', None, None, self.toggleSweepHighlight)
                                             ])

        uimanager.insert_action_group(self.actionGroup, 0)

        uimanager.add_ui_from_file('sudoku-ui.xml')
        self.vbox.pack_start(uimanager.get_widget('/MenuBar'),
                             False, True, 0)

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

    def checkValid(self, widget = None):
        if self.board.isValid():
            dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
            dialog.set_markup('Puzzle is valid.')
        else:
            dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_WARNING, gtk.BUTTONS_OK)
            dialog.set_markup('Puzzle is not valid.')

        dialog.connect('response', destroyDialog)
        dialog.show()

    def checkSolvable(self, widget = None):
        progress = ProgressDialog('Check Solvable')
        progress.setLabel('Checking for solutions...')
        progress.show()
        progress.update()

        solutions = self.board.solve(True, 2, progress = progress.pulse,
                                     cancel = progress.cancelled)

        cancelled = progress.isCancelled
        progress.destroy()

        if cancelled:
            return
        
        if solutions == 1:
            dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
            dialog.set_markup('Puzzle is solvable.')
        elif solutions == 0:
            dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_WARNING, gtk.BUTTONS_OK)
            dialog.set_markup('Puzzle has no solution.')
        else:
            dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_WARNING, gtk.BUTTONS_OK)
            dialog.set_markup('Puzzle has multiple solutions.')

        dialog.connect('response', destroyDialog)
        dialog.show()

    def difficulty(self, widget = None):
        basePuzzle = self.board.copy(True)
        
        progress = ProgressDialog('Difficulty')
        progress.setLabel('Estimating difficulty...')
        progress.show()
        progress.update()

        difficulty = basePuzzle.difficultyString(3, progress = progress.pulse,
                                                 cancel = progress.cancelled)

        cancelled = progress.isCancelled
        progress.destroy()

        if cancelled:
            return

        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                   gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
        dialog.set_markup('Puzzle difficulty: ' + difficulty)        

        dialog.connect('response', destroyDialog)
        dialog.show()

    def solve(self, action):
        progress = ProgressDialog('Solve Puzzle')
        progress.setLabel('Solving puzzle...')
        progress.show()
        progress.update()

        solutions = self.board.solve(maxCount = 1, progress = progress.pulse,
                                     cancel = progress.cancelled)

        cancelled = progress.isCancelled
        progress.destroy()

        if cancelled:
            return
        
        if solutions:
            for y in range(self.board.regionCount[1] * self.board.regionSize[1]):
                for x in range(self.board.regionCount[0] * self.board.regionSize[0]):
                    self.board[x, y] = solutions[0][x, y].value

            for entry in self.entries:
                entry.update()

    def saveAsDialog(self, widget):
        filedialog = gtk.FileSelection('Save As')
        filedialog.set_modal(True)
        filedialog.ok_button.connect_object('clicked', self.saveFromDialog, filedialog)
        filedialog.cancel_button.connect_object('clicked', destroyDialog, filedialog)
        filedialog.show()

    def saveFromDialog(self, filedialog, overwrite = False):
        filename = filedialog.get_filename()
        if filename:
            if not overwrite and os.path.exists(filename):
                confirm = gtk.MessageDialog(filedialog, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO)
                confirm.set_markup('Overwrite %s?' % filename)
                confirm.set_title('Confirm overwrite')
                confirm.set_modal(True)
                confirm.connect('response', self.confirmOverwrite, filedialog)
                confirm.show()
            else:
                self.setFilename(filename)
                try:
                    self.saveFile()
                finally:
                    filedialog.destroy()

    def confirmOverwrite(self, dialog, response, filedialog):
        dialog.destroy()
        if response == gtk.RESPONSE_YES:
            self.saveFromDialog(filedialog, True)            

    def saveFile(self, widget = None):
        out = file(self.filename, 'w')
        out.write(str(self.board))
        out.close()

    def destroy(self, widget, data = None):
        if self in openWindows:
            openWindows.remove(self)
            
        if openWindows:
            self.window.destroy()
        else:
            gtk.main_quit()


class ProgressDialog(gtk.Dialog):
    def __init__(self, title = 'Progress'):
        gtk.Dialog.__init__(self, title,
                            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        self.isCancelled = False

        self.bar = gtk.ProgressBar()
        self.bar.show()

        self.label = gtk.Label()
        self.vbox.pack_start(self.label, padding = 5)

        self.vbox.pack_start(self.bar, padding = 5)

        self.connect('response', self.cancel)
        self.connect('destroy', self.cancel)

    def setLabel(self, text):
        if not self.isCancelled:
            self.label.show()
            self.label.set_text(text)
            self.update()

    def setText(self, text):
        if not self.isCancelled:
            self.bar.set_text(text)
            self.update()

    def setFraction(self, fraction):
        if not self.isCancelled:
            self.bar.set_fraction(fraction)
            self.update()

    def pulse(self):
        if not self.isCancelled:
            self.bar.pulse()
            self.update()

    def cancelled(self):
        return self.isCancelled

    def cancel(self, widget = None, data = None):
        self.isCancelled = True

    def update(self):
        while gtk.events_pending():
            gtk.main_iteration()


class RandomPuzzleDialog(gtk.Dialog):
    def __init__(self):
        gtk.Dialog.__init__(self, 'Generate random puzzle',
                            buttons = (gtk.STOCK_NEW, gtk.RESPONSE_OK,
                                       gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        self.table = gtk.Table(2, 3)
        self.table.set_row_spacings(5)
        self.table.set_col_spacings(5)

        sizeLabel = gtk.Label('Size')
        sizeLabel.show()
        self.widthSpin = gtk.SpinButton(gtk.Adjustment(3, 2, 6, 1, 1))
        self.heightSpin = gtk.SpinButton(gtk.Adjustment(3, 2, 6, 1, 1))

        self.table.attach(sizeLabel, 0, 1, 0, 1)
        self.table.attach(self.widthSpin, 1, 2, 0, 1)
        self.table.attach(self.heightSpin, 2, 3, 0, 1)
        self.widthSpin.show()
        self.heightSpin.show()

        self.table.show()

        self.vbox.add(self.table)
        self.vbox.show()
        self.show()
        
        

# Global stuff


openWindows = []


def newDialog(widget = None):
    dialog = RandomPuzzleDialog()


def openDialog(widget = None):
    filedialog = gtk.FileSelection('Open')
    filedialog.set_modal(True)
    filedialog.ok_button.connect_object('clicked', loadFromDialog, filedialog)
    filedialog.cancel_button.connect_object('clicked', destroyDialog, filedialog)
    filedialog.show()


def loadFromDialog(filedialog):
    filename = filedialog.get_filename()
    
    filedialog.destroy()

    newGui = SudokuGUI(readSudoku(filename), filename)


def destroyDialog(widget, data = None):
    widget.destroy()

    #if not openWindows:
    #    gtk.main_quit()

    
if __name__ == '__main__':
    args = sys.argv[1:]
    if args:
        for filename in args:
            newGui = SudokuGUI(readSudoku(filename), filename)
    else:
        newGui = SudokuGUI()

    gtk.main()
