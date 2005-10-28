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
        (0xb7ff, 0xd7ff, 0xefff),
        (0xb7ff, 0xefff, 0x97ff),
        (0xefff, 0xb7ff, 0xb7ff)
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

        if self.gui.scanHighlight and self.gui.selectedValue:
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
    borderColour = gtk.gdk.Color(0x3fff, 0x3fff, 0x3fff)
    
    def __init__(self, board = SudokuBoard(), filename = None):
        openWindows.append(self)

        self.scanHighlight = False
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
        self.window.modify_bg(gtk.STATE_NORMAL, SudokuGUI.borderColour)

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
            if self.scanHighlight:
                self.updateAll()

    def createActions(self):
        uimanager = gtk.UIManager()
        self.window.add_accel_group(uimanager.get_accel_group())

        self.actionGroup = gtk.ActionGroup('SudokuSensei')
        self.actionGroup.add_actions([('File', None, '_File'),
                                      ('New', gtk.STOCK_NEW, '_New', '<Control>N', None, newPuzzleDialog),
                                      ('Open', gtk.STOCK_OPEN, '_Open', '<Control>O', None, openDialog),
                                      ('Save', gtk.STOCK_SAVE, '_Save', '<Control>S', None, self.saveFile),
                                      ('SaveAs', gtk.STOCK_SAVE_AS, 'Save _As...', '<Control><Shift>S', None, self.saveAsDialog),
                                      ('Close', gtk.STOCK_CLOSE, '_Close', '<Control>W', None, self.destroy),
                                      ('Quit', gtk.STOCK_QUIT, '_Quit', '<Control>Q', None, quit),
                                      ('Settings', None, '_Settings'),
                                      ('Fonts', gtk.STOCK_SELECT_FONT, '_Fonts', None, None, fontsDialog),
                                      ('Colours', gtk.STOCK_SELECT_COLOR, '_Colours', None, None, coloursDialog),
                                      ('Puzzle', None, '_Puzzle'),
                                      ('CheckValid', None, 'Check _Valid', None, None, self.checkValid),
                                      ('CheckSolvable', None, 'Check _Solvable', None, None, self.checkSolvable),
                                      ('Difficulty', None, '_Difficulty', None, None, self.difficulty),
                                      ('Hints', None, '_Hints'),
                                      ('Solve', None, '_Solve', None, None, self.solve)
                                      ])
        self.actionGroup.add_toggle_actions([('Scan', None, '_Highlighting', None, None, self.toggleScanHighlight)
                                             ])

        uimanager.insert_action_group(self.actionGroup, 0)

        uimanager.add_ui_from_file('sudoku-ui.xml')
        self.vbox.pack_start(uimanager.get_widget('/MenuBar'),
                             False, True, 0)
        self.vbox.pack_start(uimanager.get_widget('/Toolbar'),
                             False, True, 0)

    def toggleScanHighlight(self, action):
        self.scanHighlight = action.get_active()
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
        self.window.modify_bg(gtk.STATE_NORMAL, SudokuGUI.borderColour)
        for entry in self.entries:
            entry.update()

    def setEntry(self, entry, value):
        if value:
            entry.cell.setValue(value)
        else:
            entry.cell.setValue(None)

        if self.scanHighlight:
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
            quit()


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


class ColourDialog(gtk.Dialog):
    def __init__(self):
        gtk.Dialog.__init__(self, 'Colours',
                            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                       gtk.STOCK_OK, gtk.RESPONSE_OK))

        self.table = gtk.Table(7, 2)
        self.table.set_row_spacings(5)
        self.table.set_col_spacings(5)
        self.table.set_border_width(10)
        self.table.show()

        self.row = 0

        self.oldBackground = BoardEntry.backgroundColour
        self.oldBorder = SudokuGUI.borderColour
        self.oldPreset = BoardEntry.presetColour
        self.oldUnset = BoardEntry.unsetColour
        #self.oldRows = BoardEntry.

        self.backgroundButton = self.createButton('Background', self.oldBackground)
        self.borderButton = self.createButton('Border', self.oldBorder)
        self.presetButton = self.createButton('Given numbers', self.oldPreset)
        self.unsetButton = self.createButton('Filled-in numbers', self.oldUnset)
        
        self.vbox.add(self.table)
        self.connect('response', self.response)
        self.show()

    def createButton(self, text, colour):
        label = gtk.Label(text)
        label.show()
        self.table.attach(label, 0, 1, self.row, self.row+1)
        
        button = gtk.ColorButton(colour)
        button.show()
        button.set_title(text)
        button.connect('color-set', self.setColour)
        self.table.attach(button, 1, 2, self.row, self.row+1)

        self.row += 1

        return button

    def setColour(self, button):
        newColour = button.get_color()

        if button is self.backgroundButton:
            BoardEntry.backgroundColour = newColour
        elif button is self.borderButton:
            SudokuGUI.borderColour = newColour
        elif button is self.presetButton:
            BoardEntry.presetColour = newColour
        elif button is self.unsetButton:
            BoardEntry.unsetColour = newColour

        self.updateAll()

    def response(self, widget, data):
        if data == gtk.RESPONSE_CANCEL:
            BoardEntry.backgroundColour = self.oldBackground
            SudokuGUI.borderColour = self.oldBorder
            BoardEntry.presetColour = self.oldPreset
            BoardEntry.unsetColour = self.oldUnset
            self.updateAll()

        self.destroy()

    def updateAll(self):
        for window in openWindows:
            window.updateAll()


class FontDialog(gtk.Dialog):
    def __init__(self):
        gtk.Dialog.__init__(self, 'Fonts',
                            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                       gtk.STOCK_OK, gtk.RESPONSE_OK))

        self.table = gtk.Table(2, 2)
        self.table.set_row_spacings(5)
        self.table.set_col_spacings(5)
        self.table.set_border_width(10)
        self.table.show()

        self.row = 0

        self.oldPreset = BoardEntry.presetFont
        self.oldUnset = BoardEntry.unsetFont

        self.presetButton = self.createButton('Given numbers', self.oldPreset)
        self.unsetButton = self.createButton('Filled-in numbers', self.oldUnset)
        
        self.vbox.add(self.table)
        self.connect('response', self.response)
        self.show()

    def createButton(self, text, font):
        label = gtk.Label(text)
        label.show()
        self.table.attach(label, 0, 1, self.row, self.row+1)
        
        button = gtk.FontButton(font.to_string())
        button.show()
        button.connect('font-set', self.setFont)
        self.table.attach(button, 1, 2, self.row, self.row+1)

        self.row += 1

        return button

    def setFont(self, fontButton):
        newFont = pango.FontDescription(fontButton.get_font_name())
        
        if fontButton is self.presetButton:
            BoardEntry.presetFont = newFont
        elif fontButton is self.unsetButton:
            BoardEntry.unsetFont = newFont

        self.updateAll()
        
    def response(self, widget, data):
        if data == gtk.RESPONSE_CANCEL:
            BoardEntry.presetFont = self.oldPreset
            BoardEntry.unsetFont = self.oldUnset
            self.updateAll()

        self.destroy()

    def updateAll(self):
        for window in openWindows:
            window.updateAll()
            window.window.resize(1, 1)


class NewPuzzleDialog(gtk.Dialog):
    def __init__(self):
        gtk.Dialog.__init__(self, 'New puzzle',
                            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                       gtk.STOCK_NEW, gtk.RESPONSE_OK))

        self.set_modal(True)

        sizeLabel = gtk.Label('Size')
        sizeLabel.show()
        xLabel = gtk.Label('x')
        xLabel.show()
        self.widthSpin = gtk.SpinButton(gtk.Adjustment(3, 1, 6, 1, 1))
        self.heightSpin = gtk.SpinButton(gtk.Adjustment(3, 1, 6, 1, 1))
        self.widthSpin.show()
        self.heightSpin.show()

        sizeBox = gtk.HBox(spacing = 5)
        sizeBox.show()
        sizeBox.set_border_width(5)
        sizeBox.add(sizeLabel)
        sizeBox.add(self.widthSpin)
        sizeBox.add(xLabel)
        sizeBox.add(self.heightSpin)

        self.radioEmpty = gtk.RadioButton(None, 'Empty puzzle')
        self.radioEmpty.show()
        self.radioRandom = gtk.RadioButton(self.radioEmpty, 'Random puzzle')
        self.radioRandom.show()

        self.radioRandom.connect('toggled', self.toggleRandom)

        self.symmetricalCheck = gtk.CheckButton('Symmetrical')
        self.symmetricalCheck.set_active(True)
        self.scanCheck = gtk.CheckButton('Scanning only')
        self.scanCheck.set_active(False)

        branchLabel = gtk.Label('Maximum branches')
        branchLabel.show()
        self.branchSpin = gtk.SpinButton(gtk.Adjustment(0, 0, 5, 1, 1))
        self.branchSpin.show()

        self.branchBox = gtk.HBox(spacing = 5)
        self.branchBox.add(branchLabel)
        self.branchBox.add(self.branchSpin)

        frame = gtk.Frame()
        frame.show()
        frame.set_border_width(5)
        frameVBox = gtk.VBox(spacing = 10)
        frameVBox.show()
        frameVBox.add(self.radioEmpty)
        frameVBox.add(self.radioRandom)
        frameVBox.add(self.symmetricalCheck)
        frameVBox.add(self.scanCheck)
        frameVBox.add(self.branchBox)
        frameVBox.set_border_width(5)
        frame.add(frameVBox)
        
        self.vbox.add(sizeBox)
        self.vbox.add(frame)
        self.vbox.show()
        self.connect('response', self.response)

    def toggleRandom(self, button):
        if button.get_active():
            self.symmetricalCheck.show()
            self.scanCheck.show()
            self.branchBox.show()
        else:
            self.symmetricalCheck.hide()
            self.scanCheck.hide()
            self.branchBox.hide()
        self.resize(1, 1)

    def response(self, widget, data):
        if data == gtk.RESPONSE_OK:
            size = (int(self.widthSpin.get_value()), int(self.heightSpin.get_value()))
            if self.radioRandom.get_active():
                maxBranch = int(self.branchSpin.get_value())
                symmetrical = self.symmetricalCheck.get_active()
                scanOnly = self.scanCheck.get_active()
                
                self.hide()
                
                progress = ProgressDialog('Random puzzle')
                progress.setLabel('Generating puzzle...')
                progress.show()
                progress.update()

                board = randomPuzzle(size, maxBranch, scanOnly, symmetrical,
                                     progress.pulse, progress.setFraction, progress.cancelled)

                cancelled = progress.isCancelled
                progress.hide()

                if cancelled:
                    return
            else:
                self.hide()
                board = SudokuBoard(size, (size[1], size[0]))

            gui = SudokuGUI(board)

        else:
            self.hide()
        
        

# Global stuff


openWindows = []
newDialog = None

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

    
def newPuzzleDialog(widget = None):
    global newDialog
    if not newDialog:
        newDialog = NewPuzzleDialog()
    newDialog.show()
    return newDialog

def fontsDialog(widget = None):
    FontDialog().show()

def coloursDialog(widget = None):
    ColourDialog().show()

def quit(widget = None):
    gtk.main_quit()


if __name__ == '__main__':
    args = sys.argv[1:]

    gtk.window_set_default_icon_from_file('images/icon.png')
    
    if args:
        for filename in args:
            newGui = SudokuGUI(readSudoku(filename), filename)
    else:
        newGui = SudokuGUI()

    gtk.main()
