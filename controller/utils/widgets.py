import os
import sys
import re
import time
from collections import OrderedDict

from PyQt5.QtGui import QColor, QPalette, QTextCursor, QTextOption, QMouseEvent, QClipboard, \
    QTextCharFormat, QFont
from PyQt5.QtWidgets import QPlainTextEdit, QMainWindow, QTextEdit, QApplication, QToolTip, QMenu
from PyQt5.QtCore import pyqtSignal as Signal, Qt, QPoint, QEvent, QTimer, QCoreApplication
# from rope.base.builtins import Property

from controller.utils import BaseEditMixin
from controller.utils.py3compat import to_text_string, PY3, str_lower, is_text_string, is_string
from controller.utils.qthelpers import create_action, add_actions, restore_keyevent


def insert_text_to(cursor, text, fmt):
    """Helper to print text, taking into account backspaces"""
    while True:
        index = text.find(chr(8))  # backspace
        if index == -1:
            break
        cursor.insertText(text[:index], fmt)
        if cursor.positionInBlock() > 0:
            cursor.deletePreviousChar()
        text = text[index+1:]
    cursor.insertText(text, fmt)


class TextEditBaseWidget(QPlainTextEdit, BaseEditMixin):
    """Text edit base widget"""
    BRACE_MATCHING_SCOPE = ('sof', 'eof')
    cell_separators = None
    focus_in = Signal()
    zoom_in = Signal()
    zoom_out = Signal()
    zoom_reset = Signal()
    focus_changed = Signal()
    sig_eol_chars_changed = Signal(str)

    def __init__(self, parent=None):
        QPlainTextEdit.__init__(self, parent)
        BaseEditMixin.__init__(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.extra_selections_dict = OrderedDict()

        self.textChanged.connect(self.changed)
        self.cursorPositionChanged.connect(self.cursor_position_changed)

        self.indent_chars = " "*4
        self.tab_stop_width_spaces = 4

        # Code completion / calltips
        if parent is not None:
            mainwin = parent
            while not isinstance(mainwin, QMainWindow):
                mainwin = mainwin.parent()
                if mainwin is None:
                    break
            if mainwin is not None:
                parent = mainwin

        # self.completion_widget = CompletionWidget(self, parent)
        self.codecompletion_auto = False
        self.codecompletion_case = True
        self.codecompletion_enter = False
        self.completion_text = ""
        self.setup_completion()

        # self.calltip_widget = CallTipWidget(self, hide_timer_on=False)
        self.calltips = True
        self.calltip_position = None

        self.has_cell_separators = False
        self.highlight_current_cell_enabled = False

        # The color values may be overridden by the syntax highlighter
        # Highlight current line color
        self.currentline_color = QColor(Qt.red).lighter(190)
        self.currentcell_color = QColor(Qt.red).lighter(194)

        # Brace matching
        self.bracepos = None
        self.matched_p_color = QColor(Qt.green)
        self.unmatched_p_color = QColor(Qt.red)

        self.last_cursor_cell = None

    # def setup_completion(self):
    #     size = CONF.get('main', 'completion/size')
    #     font = get_font()
    #     self.completion_widget.setup_appearance(size, font)

    def set_indent_chars(self, indent_chars):
        self.indent_chars = indent_chars

    def set_tab_stop_width_spaces(self, tab_stop_width_spaces):
        self.tab_stop_width_spaces = tab_stop_width_spaces
        self.update_tab_stop_width_spaces()

    def update_tab_stop_width_spaces(self):
        self.setTabStopWidth(self.fontMetrics().width(
            '9' * self.tab_stop_width_spaces))

    def set_palette(self, background, foreground):
        """
        Set text editor palette colors:
        background color and caret (text cursor) color
        """
        palette = QPalette()
        palette.setColor(QPalette.Base, background)
        palette.setColor(QPalette.Text, foreground)
        self.setPalette(palette)

        # Set the right background color when changing color schemes
        # or creating new Editor windows. This seems to be a Qt bug.
        # Fixes Issue 2028
        if sys.platform == 'darwin':
            if self.objectName():
                style = "QPlainTextEdit#%s {background: %s; color: %s;}" % \
                        (self.objectName(), background.name(), foreground.name())
                self.setStyleSheet(style)

    #------Extra selections
    def extra_selection_length(self, key):
        selection = self.get_extra_selections(key)
        if selection:
            cursor = self.extra_selections_dict[key][0].cursor
            selection_length = cursor.selectionEnd() - cursor.selectionStart()
            return selection_length
        else:
            return 0

    def get_extra_selections(self, key):
        return self.extra_selections_dict.get(key, [])

    def set_extra_selections(self, key, extra_selections):
        self.extra_selections_dict[key] = extra_selections
        self.extra_selections_dict = \
            OrderedDict(sorted(self.extra_selections_dict.items(),
                               key=lambda s: self.extra_selection_length(s[0]),
                               reverse=True))

    def update_extra_selections(self):
        extra_selections = []

        # Python 3 compatibility (weird): current line has to be
        # highlighted first
        if 'current_cell' in self.extra_selections_dict:
            extra_selections.extend(self.extra_selections_dict['current_cell'])
        if 'current_line' in self.extra_selections_dict:
            extra_selections.extend(self.extra_selections_dict['current_line'])

        for key, extra in list(self.extra_selections_dict.items()):
            if not (key == 'current_line' or key == 'current_cell'):
                extra_selections.extend(extra)
        self.setExtraSelections(extra_selections)

    def clear_extra_selections(self, key):
        self.extra_selections_dict[key] = []
        self.update_extra_selections()

    def changed(self):
        """Emit changed signal"""
        self.modificationChanged.emit(self.document().isModified())

    # #------Highlight current line
    # def highlight_current_line(self):
    #     """Highlight current line"""
    #     selection = QTextEdit.ExtraSelection()
    #     selection.format.setProperty(QTextFormat.FullWidthSelection, True)  # to_qvariant(True))
    #     selection.format.setBackground(self.currentline_color)
    #     selection.cursor = self.textCursor()
    #     selection.cursor.clearSelection()
    #     self.set_extra_selections('current_line', [selection])
    #     self.update_extra_selections()
    #
    # def unhighlight_current_line(self):
    #     """Unhighlight current line"""
    #     self.clear_extra_selections('current_line')
    #
    # #------Highlight current cell
    # def highlight_current_cell(self):
    #     """Highlight current cell"""
    #     if self.cell_separators is None or \
    #             not self.highlight_current_cell_enabled:
    #         return
    #     selection = QTextEdit.ExtraSelection()
    #     selection.format.setProperty(QTextFormat.FullWidthSelection,
    #                                  to_qvariant(True))
    #     selection.format.setBackground(self.currentcell_color)
    #     selection.cursor, whole_file_selected, whole_screen_selected = \
    #         self.select_current_cell_in_visible_portion()
    #     if whole_file_selected:
    #         self.clear_extra_selections('current_cell')
    #     elif whole_screen_selected:
    #         if self.has_cell_separators:
    #             self.set_extra_selections('current_cell', [selection])
    #             self.update_extra_selections()
    #         else:
    #             self.clear_extra_selections('current_cell')
    #     else:
    #         self.set_extra_selections('current_cell', [selection])
    #         self.update_extra_selections()
    #
    # def unhighlight_current_cell(self):
    #     """Unhighlight current cell"""
    #     self.clear_extra_selections('current_cell')

    #------Brace matching
    def find_brace_match(self, position, brace, forward):
        start_pos, end_pos = self.BRACE_MATCHING_SCOPE
        if forward:
            bracemap = {'(': ')', '[': ']', '{': '}'}
            text = self.get_text(position, end_pos)
            i_start_open = 1
            i_start_close = 1
        else:
            bracemap = {')': '(', ']': '[', '}': '{'}
            text = self.get_text(start_pos, position)
            i_start_open = len(text)-1
            i_start_close = len(text)-1

        while True:
            if forward:
                i_close = text.find(bracemap[brace], i_start_close)
            else:
                i_close = text.rfind(bracemap[brace], 0, i_start_close+1)
            if i_close > -1:
                if forward:
                    i_start_close = i_close+1
                    i_open = text.find(brace, i_start_open, i_close)
                else:
                    i_start_close = i_close-1
                    i_open = text.rfind(brace, i_close, i_start_open+1)
                if i_open > -1:
                    if forward:
                        i_start_open = i_open+1
                    else:
                        i_start_open = i_open-1
                else:
                    # found matching brace
                    if forward:
                        return position+i_close
                    else:
                        return position-(len(text)-i_close)
            else:
                # no matching brace
                return

    def __highlight(self, positions, color=None, cancel=False):
        if cancel:
            self.clear_extra_selections('brace_matching')
            return
        extra_selections = []
        for position in positions:
            if position > self.get_position('eof'):
                return
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(color)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            selection.cursor.setPosition(position)
            selection.cursor.movePosition(QTextCursor.NextCharacter,
                                          QTextCursor.KeepAnchor)
            extra_selections.append(selection)
        self.set_extra_selections('brace_matching', extra_selections)
        self.update_extra_selections()

    def cursor_position_changed(self):
        """Brace matching"""
        if self.bracepos is not None:
            self.__highlight(self.bracepos, cancel=True)
            self.bracepos = None
        cursor = self.textCursor()
        if cursor.position() == 0:
            return
        cursor.movePosition(QTextCursor.PreviousCharacter,
                            QTextCursor.KeepAnchor)
        text = to_text_string(cursor.selectedText())
        pos1 = cursor.position()
        if text in (')', ']', '}'):
            pos2 = self.find_brace_match(pos1, text, forward=False)
        elif text in ('(', '[', '{'):
            pos2 = self.find_brace_match(pos1, text, forward=True)
        else:
            return
        if pos2 is not None:
            self.bracepos = (pos1, pos2)
            self.__highlight(self.bracepos, color=self.matched_p_color)
        else:
            self.bracepos = (pos1,)
            self.__highlight(self.bracepos, color=self.unmatched_p_color)

    #-----Widget setup and options
    def set_codecompletion_auto(self, state):
        """Set code completion state"""
        self.codecompletion_auto = state

    def set_codecompletion_case(self, state):
        """Case sensitive completion"""
        self.codecompletion_case = state
        self.completion_widget.case_sensitive = state

    def set_codecompletion_enter(self, state):
        """Enable Enter key to select completion"""
        self.codecompletion_enter = state
        self.completion_widget.enter_select = state

    def set_calltips(self, state):
        """Set calltips state"""
        self.calltips = state

    def set_wrap_mode(self, mode=None):
        """
        Set wrap mode
        Valid *mode* values: None, 'word', 'character'
        """
        if mode == 'word':
            wrap_mode = QTextOption.WrapAtWordBoundaryOrAnywhere
        elif mode == 'character':
            wrap_mode = QTextOption.WrapAnywhere
        else:
            wrap_mode = QTextOption.NoWrap
        self.setWordWrapMode(wrap_mode)

    #------Reimplementing Qt methods
    # @Slot()
    def copy(self):
        """
        Reimplement Qt method
        Copy text to clipboard with correct EOL chars
        """
        if self.get_selected_text():
            QApplication.clipboard().setText(self.get_selected_text())

    def toPlainText(self):
        """
        Reimplement Qt method
        Fix PyQt4 bug on Windows and Python 3
        """
        # Fix what appears to be a PyQt4 bug when getting file
        # contents under Windows and PY3. This bug leads to
        # corruptions when saving files with certain combinations
        # of unicode chars on them (like the one attached on
        # Issue 1546)
        if os.name == 'nt' and PY3:
            text = self.get_text('sof', 'eof')
            return text.replace('\u2028', '\n').replace('\u2029', '\n') \
                .replace('\u0085', '\n')
        else:
            return super(TextEditBaseWidget, self).toPlainText()

    def keyPressEvent(self, event):
        text, key = event.text(), event.key()
        ctrl = event.modifiers() & Qt.ControlModifier
        meta = event.modifiers() & Qt.MetaModifier
        # Use our own copy method for {Ctrl,Cmd}+C to avoid Qt
        # copying text in HTML (See Issue 2285)
        if (ctrl or meta) and key == Qt.Key_C:
            self.copy()
        else:
            super(TextEditBaseWidget, self).keyPressEvent(event)

    #------Text: get, set, ...
    def get_selection_as_executable_code(self):
        """Return selected text as a processed text,
        to be executable in a Python/IPython interpreter"""
        ls = self.get_line_separator()

        _indent = lambda line: len(line)-len(line.lstrip())

        line_from, line_to = self.get_selection_bounds()
        text = self.get_selected_text()
        if not text:
            return

        lines = text.split(ls)
        if len(lines) > 1:
            # Multiline selection -> eventually fixing indentation
            original_indent = _indent(self.get_text_line(line_from))
            text = (" "*(original_indent-_indent(lines[0])))+text

        # If there is a common indent to all lines, find it.
        # Moving from bottom line to top line ensures that blank
        # lines inherit the indent of the line *below* it,
        # which is the desired behavior.
        min_indent = 999
        current_indent = 0
        lines = text.split(ls)
        for i in range(len(lines)-1, -1, -1):
            line = lines[i]
            if line.strip():
                current_indent = _indent(line)
                min_indent = min(current_indent, min_indent)
            else:
                lines[i] = ' ' * current_indent
        if min_indent:
            lines = [line[min_indent:] for line in lines]

        # Remove any leading whitespace or comment lines
        # since they confuse the reserved word detector that follows below
        while lines:
            first_line = lines[0].lstrip()
            if first_line == '' or first_line[0] == '#':
                lines.pop(0)
            else:
                break

        # Add an EOL character after indentation blocks that start with some
        # Python reserved words, so that it gets evaluated automatically
        # by the console
        varname = re.compile('[a-zA-Z0-9_]*') # matches valid variable names
        maybe = False
        nextexcept = ()
        for n, line in enumerate(lines):
            if not _indent(line):
                word = varname.match(line).group()
                if maybe and word not in nextexcept:
                    lines[n-1] += ls
                    maybe = False
                if word:
                    if word in ('def', 'for', 'while', 'with', 'class'):
                        maybe = True
                        nextexcept = ()
                    elif word == 'if':
                        maybe = True
                        nextexcept = ('elif', 'else')
                    elif word == 'try':
                        maybe = True
                        nextexcept = ('except', 'finally')
        if maybe:
            if lines[-1].strip() == '':
                lines[-1] += ls
            else:
                lines.append(ls)

        return ls.join(lines)

    def __exec_cell(self):
        init_cursor = QTextCursor(self.textCursor())
        start_pos, end_pos = self.__save_selection()
        cursor, whole_file_selected = self.select_current_cell()
        if not whole_file_selected:
            self.setTextCursor(cursor)
        text = self.get_selection_as_executable_code()
        self.last_cursor_cell = init_cursor
        self.__restore_selection(start_pos, end_pos)
        if text is not None:
            text = text.rstrip()
        return text

    def get_cell_as_executable_code(self):
        """Return cell contents as executable code"""
        return self.__exec_cell()

    def get_last_cell_as_executable_code(self):
        text = None
        if self.last_cursor_cell:
            self.setTextCursor(self.last_cursor_cell)
            self.highlight_current_cell()
            text = self.__exec_cell()
        return text

    def is_cell_separator(self, cursor=None, block=None):
        """Return True if cursor (or text block) is on a block separator"""
        assert cursor is not None or block is not None
        if cursor is not None:
            cursor0 = QTextCursor(cursor)
            cursor0.select(QTextCursor.BlockUnderCursor)
            text = to_text_string(cursor0.selectedText())
        else:
            text = to_text_string(block.text())
        if self.cell_separators is None:
            return False
        else:
            return text.lstrip().startswith(self.cell_separators)

    def select_current_cell(self):
        """Select cell under cursor
        cell = group of lines separated by CELL_SEPARATORS
        returns the textCursor and a boolean indicating if the
        entire file is selected"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cur_pos = prev_pos = cursor.position()

        # Moving to the next line that is not a separator, if we are
        # exactly at one of them
        while self.is_cell_separator(cursor):
            cursor.movePosition(QTextCursor.NextBlock)
            prev_pos = cur_pos
            cur_pos = cursor.position()
            if cur_pos == prev_pos:
                return cursor, False
        prev_pos = cur_pos
        # If not, move backwards to find the previous separator
        while not self.is_cell_separator(cursor):
            cursor.movePosition(QTextCursor.PreviousBlock)
            prev_pos = cur_pos
            cur_pos = cursor.position()
            if cur_pos == prev_pos:
                if self.is_cell_separator(cursor):
                    return cursor, False
                else:
                    break
        cursor.setPosition(prev_pos)
        cell_at_file_start = cursor.atStart()
        # Once we find it (or reach the beginning of the file)
        # move to the next separator (or the end of the file)
        # so we can grab the cell contents
        while not self.is_cell_separator(cursor):
            cursor.movePosition(QTextCursor.NextBlock,
                                QTextCursor.KeepAnchor)
            cur_pos = cursor.position()
            if cur_pos == prev_pos:
                cursor.movePosition(QTextCursor.EndOfBlock,
                                    QTextCursor.KeepAnchor)
                break
            prev_pos = cur_pos
        cell_at_file_end = cursor.atEnd()
        return cursor, cell_at_file_start and cell_at_file_end

    def select_current_cell_in_visible_portion(self):
        """Select cell under cursor in the visible portion of the file
        cell = group of lines separated by CELL_SEPARATORS
        returns
         -the textCursor
         -a boolean indicating if the entire file is selected
         -a boolean indicating if the entire visible portion of the file is selected"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock)
        cur_pos = prev_pos = cursor.position()

        beg_pos = self.cursorForPosition(QPoint(0, 0)).position()
        bottom_right = QPoint(self.viewport().width() - 1,
                              self.viewport().height() - 1)
        end_pos = self.cursorForPosition(bottom_right).position()

        # Moving to the next line that is not a separator, if we are
        # exactly at one of them
        while self.is_cell_separator(cursor):
            cursor.movePosition(QTextCursor.NextBlock)
            prev_pos = cur_pos
            cur_pos = cursor.position()
            if cur_pos == prev_pos:
                return cursor, False, False
        prev_pos = cur_pos
        # If not, move backwards to find the previous separator
        while not self.is_cell_separator(cursor) \
                and cursor.position() >= beg_pos:
            cursor.movePosition(QTextCursor.PreviousBlock)
            prev_pos = cur_pos
            cur_pos = cursor.position()
            if cur_pos == prev_pos:
                if self.is_cell_separator(cursor):
                    return cursor, False, False
                else:
                    break
        cell_at_screen_start = cursor.position() <= beg_pos
        cursor.setPosition(prev_pos)
        cell_at_file_start = cursor.atStart()
        # Selecting cell header
        if not cell_at_file_start:
            cursor.movePosition(QTextCursor.PreviousBlock)
            cursor.movePosition(QTextCursor.NextBlock,
                                QTextCursor.KeepAnchor)
        # Once we find it (or reach the beginning of the file)
        # move to the next separator (or the end of the file)
        # so we can grab the cell contents
        while not self.is_cell_separator(cursor) \
                and cursor.position() <= end_pos:
            cursor.movePosition(QTextCursor.NextBlock,
                                QTextCursor.KeepAnchor)
            cur_pos = cursor.position()
            if cur_pos == prev_pos:
                cursor.movePosition(QTextCursor.EndOfBlock,
                                    QTextCursor.KeepAnchor)
                break
            prev_pos = cur_pos
        cell_at_file_end = cursor.atEnd()
        cell_at_screen_end = cursor.position() >= end_pos
        return cursor,  cell_at_file_start and cell_at_file_end, cell_at_screen_start and cell_at_screen_end

    def go_to_next_cell(self):
        """Go to the next cell of lines"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.NextBlock)
        cur_pos = prev_pos = cursor.position()
        while not self.is_cell_separator(cursor):
            # Moving to the next code cell
            cursor.movePosition(QTextCursor.NextBlock)
            prev_pos = cur_pos
            cur_pos = cursor.position()
            if cur_pos == prev_pos:
                return
        self.setTextCursor(cursor)

    def go_to_previous_cell(self):
        """Go to the previous cell of lines"""
        cursor = self.textCursor()
        cur_pos = prev_pos = cursor.position()

        if self.is_cell_separator(cursor):
            # Move to the previous cell
            cursor.movePosition(QTextCursor.PreviousBlock)
            cur_pos = prev_pos = cursor.position()

        while not self.is_cell_separator(cursor):
            # Move to the previous cell or the beginning of the current cell
            cursor.movePosition(QTextCursor.PreviousBlock)
            prev_pos = cur_pos
            cur_pos = cursor.position()
            if cur_pos == prev_pos:
                return

        self.setTextCursor(cursor)

    def get_line_count(self):
        """Return document total line number"""
        return self.blockCount()

    def __save_selection(self):
        """Save current cursor selection and return position bounds"""
        cursor = self.textCursor()
        return cursor.selectionStart(), cursor.selectionEnd()

    def __restore_selection(self, start_pos, end_pos):
        """Restore cursor selection from position bounds"""
        cursor = self.textCursor()
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

    def __duplicate_line_or_selection(self, after_current_line=True):
        """Duplicate current line or selected text"""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        start_pos, end_pos = self.__save_selection()
        if to_text_string(cursor.selectedText()):
            cursor.setPosition(end_pos)
            # Check if end_pos is at the start of a block: if so, starting
            # changes from the previous block
            cursor.movePosition(QTextCursor.StartOfBlock,
                                QTextCursor.KeepAnchor)
            if not to_text_string(cursor.selectedText()):
                cursor.movePosition(QTextCursor.PreviousBlock)
                end_pos = cursor.position()

        cursor.setPosition(start_pos)
        cursor.movePosition(QTextCursor.StartOfBlock)
        while cursor.position() <= end_pos:
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            if cursor.atEnd():
                cursor_temp = QTextCursor(cursor)
                cursor_temp.clearSelection()
                cursor_temp.insertText(self.get_line_separator())
                break
            cursor.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        cursor.clearSelection()

        if not after_current_line:
            # Moving cursor before current line/selected text
            cursor.setPosition(start_pos)
            cursor.movePosition(QTextCursor.StartOfBlock)
            start_pos += len(text)
            end_pos += len(text)

        cursor.insertText(text)
        cursor.endEditBlock()
        self.setTextCursor(cursor)
        self.__restore_selection(start_pos, end_pos)

    def duplicate_line(self):
        """
        Duplicate current line or selected text
        Paste the duplicated text *after* the current line/selected text
        """
        self.__duplicate_line_or_selection(after_current_line=True)

    def copy_line(self):
        """
        Copy current line or selected text
        Paste the duplicated text *before* the current line/selected text
        """
        self.__duplicate_line_or_selection(after_current_line=False)

    def __move_line_or_selection(self, after_current_line=True):
        """Move current line or selected text"""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        start_pos, end_pos = self.__save_selection()
        last_line = False

        # ------ Select text

        # Get selection start location
        cursor.setPosition(start_pos)
        cursor.movePosition(QTextCursor.StartOfBlock)
        start_pos = cursor.position()

        # Get selection end location
        cursor.setPosition(end_pos)
        if not cursor.atBlockStart() or end_pos == start_pos:
            cursor.movePosition(QTextCursor.EndOfBlock)
            cursor.movePosition(QTextCursor.NextBlock)
        end_pos = cursor.position()

        # Check if selection ends on the last line of the document
        if cursor.atEnd():
            if not cursor.atBlockStart() or end_pos == start_pos:
                last_line = True

        # ------ Stop if at document boundary

        cursor.setPosition(start_pos)
        if cursor.atStart() and not after_current_line:
            # Stop if selection is already at top of the file while moving up
            cursor.endEditBlock()
            self.setTextCursor(cursor)
            self.__restore_selection(start_pos, end_pos)
            return

        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        if last_line and after_current_line:
            # Stop if selection is already at end of the file while moving down
            cursor.endEditBlock()
            self.setTextCursor(cursor)
            self.__restore_selection(start_pos, end_pos)
            return

        # ------ Move text

        sel_text = to_text_string(cursor.selectedText())
        cursor.removeSelectedText()


        if after_current_line:
            # Shift selection down
            text = to_text_string(cursor.block().text())
            sel_text = os.linesep + sel_text[0:-1]  # Move linesep at the start
            cursor.movePosition(QTextCursor.EndOfBlock)
            start_pos += len(text)+1
            end_pos += len(text)
            if not cursor.atEnd():
                end_pos += 1
        else:
            # Shift selection up
            if last_line:
                # Remove the last linesep and add it to the selected text
                cursor.deletePreviousChar()
                sel_text = sel_text + os.linesep
                cursor.movePosition(QTextCursor.StartOfBlock)
                end_pos += 1
            else:
                cursor.movePosition(QTextCursor.PreviousBlock)
            text = to_text_string(cursor.block().text())
            start_pos -= len(text)+1
            end_pos -= len(text)+1

        cursor.insertText(sel_text)

        cursor.endEditBlock()
        self.setTextCursor(cursor)
        self.__restore_selection(start_pos, end_pos)

    def move_line_up(self):
        """Move up current line or selected text"""
        self.__move_line_or_selection(after_current_line=False)

    def move_line_down(self):
        """Move down current line or selected text"""
        self.__move_line_or_selection(after_current_line=True)

    def extend_selection_to_complete_lines(self):
        """Extend current selection to complete lines"""
        cursor = self.textCursor()
        start_pos, end_pos = cursor.selectionStart(), cursor.selectionEnd()
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        if cursor.atBlockStart():
            cursor.movePosition(QTextCursor.PreviousBlock,
                                QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.EndOfBlock,
                                QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

    def delete_line(self):
        """Delete current line"""
        cursor = self.textCursor()
        if self.has_selected_text():
            self.extend_selection_to_complete_lines()
            start_pos, end_pos = cursor.selectionStart(), cursor.selectionEnd()
            cursor.setPosition(start_pos)
        else:
            start_pos = end_pos = cursor.position()
        cursor.beginEditBlock()
        cursor.setPosition(start_pos)
        cursor.movePosition(QTextCursor.StartOfBlock)
        while cursor.position() <= end_pos:
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            if cursor.atEnd():
                break
            cursor.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.endEditBlock()
        self.ensureCursorVisible()

    #------Code completion / Calltips
    def hide_tooltip_if_necessary(self, key):
        """Hide calltip when necessary"""
        try:
            calltip_char = self.get_character(self.calltip_position)
            before = self.is_cursor_before(self.calltip_position,
                                           char_offset=1)
            other = key in (Qt.Key_ParenRight, Qt.Key_Period, Qt.Key_Tab)
            if calltip_char not in ('?', '(') or before or other:
                QToolTip.hideText()
        except (IndexError, TypeError):
            QToolTip.hideText()

    def show_completion_widget(self, textlist, automatic=True):
        """Show completion widget"""
        self.completion_widget.show_list(textlist, automatic=automatic)

    def hide_completion_widget(self):
        """Hide completion widget"""
        self.completion_widget.hide()

    def show_completion_list(self, completions, completion_text="",
                             automatic=True):
        """Display the possible completions"""
        if not completions:
            return
        if not isinstance(completions[0], tuple):
            completions = [(c, '') for c in completions]
        if len(completions) == 1 and completions[0][0] == completion_text:
            return
        self.completion_text = completion_text
        # Sorting completion list (entries starting with underscore are
        # put at the end of the list):
        underscore = set([(comp, t) for (comp, t) in completions
                          if comp.startswith('_')])

        completions = sorted(set(completions) - underscore,
                             key=lambda x: str_lower(x[0]))
        completions += sorted(underscore, key=lambda x: str_lower(x[0]))
        self.show_completion_widget(completions, automatic=automatic)

    def select_completion_list(self):
        """Completion list is active, Enter was just pressed"""
        self.completion_widget.item_selected()

    def insert_completion(self, text):
        if text:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.PreviousCharacter,
                                QTextCursor.KeepAnchor,
                                len(self.completion_text))
            cursor.removeSelectedText()
            self.insert_text(text)

    def is_completion_widget_visible(self):
        """Return True is completion list widget is visible"""
        return self.completion_widget.isVisible()

    #------Standard keys
    def stdkey_clear(self):
        if not self.has_selected_text():
            self.moveCursor(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
        self.remove_selected_text()

    def stdkey_backspace(self):
        if not self.has_selected_text():
            self.moveCursor(QTextCursor.PreviousCharacter,
                            QTextCursor.KeepAnchor)
        self.remove_selected_text()

    def __get_move_mode(self, shift):
        return QTextCursor.KeepAnchor if shift else QTextCursor.MoveAnchor

    def stdkey_up(self, shift):
        self.moveCursor(QTextCursor.Up, self.__get_move_mode(shift))

    def stdkey_down(self, shift):
        self.moveCursor(QTextCursor.Down, self.__get_move_mode(shift))

    def stdkey_tab(self):
        self.insert_text(self.indent_chars)

    def stdkey_home(self, shift, ctrl, prompt_pos=None):
        """Smart HOME feature: cursor is first moved at
        indentation position, then at the start of the line"""
        move_mode = self.__get_move_mode(shift)
        if ctrl:
            self.moveCursor(QTextCursor.Start, move_mode)
        else:
            cursor = self.textCursor()
            if prompt_pos is None:
                start_position = self.get_position('sol')
            else:
                start_position = self.get_position(prompt_pos)
            text = self.get_text(start_position, 'eol')
            indent_pos = start_position+len(text)-len(text.lstrip())
            if cursor.position() != indent_pos:
                cursor.setPosition(indent_pos, move_mode)
            else:
                cursor.setPosition(start_position, move_mode)
            self.setTextCursor(cursor)

    def stdkey_end(self, shift, ctrl):
        move_mode = self.__get_move_mode(shift)
        if ctrl:
            self.moveCursor(QTextCursor.End, move_mode)
        else:
            self.moveCursor(QTextCursor.EndOfBlock, move_mode)

    def stdkey_pageup(self):
        pass

    def stdkey_pagedown(self):
        pass

    def stdkey_escape(self):
        pass

    #----Qt Events
    def mousePressEvent(self, event):
        """Reimplement Qt method"""
        if sys.platform.startswith('linux') and event.button() == Qt.MidButton:
            self.calltip_widget.hide()
            self.setFocus()
            event = QMouseEvent(QEvent.MouseButtonPress, event.pos(),
                                Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
            QPlainTextEdit.mousePressEvent(self, event)
            QPlainTextEdit.mouseReleaseEvent(self, event)
            # Send selection text to clipboard to be able to use
            # the paste method and avoid the strange Issue 1445
            # NOTE: This issue seems a focusing problem but it
            # seems really hard to track
            mode_clip = QClipboard.Clipboard
            mode_sel = QClipboard.Selection
            text_clip = QApplication.clipboard().text(mode=mode_clip)
            text_sel = QApplication.clipboard().text(mode=mode_sel)
            QApplication.clipboard().setText(text_sel, mode=mode_clip)
            self.paste()
            QApplication.clipboard().setText(text_clip, mode=mode_clip)
        else:
            self.calltip_widget.hide()
            QPlainTextEdit.mousePressEvent(self, event)

    def focusInEvent(self, event):
        """Reimplemented to handle focus"""
        self.focus_changed.emit()
        self.focus_in.emit()
        self.highlight_current_cell()
        QPlainTextEdit.focusInEvent(self, event)

    def focusOutEvent(self, event):
        """Reimplemented to handle focus"""
        self.focus_changed.emit()
        QPlainTextEdit.focusOutEvent(self, event)

    def wheelEvent(self, event):
        """Reimplemented to emit zoom in/out signals when Ctrl is pressed"""
        # This feature is disabled on MacOS, see Issue 1510
        if sys.platform != 'darwin':
            if event.modifiers() & Qt.ControlModifier:
                if hasattr(event, 'angleDelta'):
                    if event.angleDelta().y() < 0:
                        self.zoom_out.emit()
                    elif event.angleDelta().y() > 0:
                        self.zoom_in.emit()
                elif hasattr(event, 'delta'):
                    if event.delta() < 0:
                        self.zoom_out.emit()
                    elif event.delta() > 0:
                        self.zoom_in.emit()
                return
        QPlainTextEdit.wheelEvent(self, event)
        self.highlight_current_cell()


class ConsoleBaseWidget(TextEditBaseWidget):
    """Console base widget"""
    BRACE_MATCHING_SCOPE = ('sol', 'eol')
    COLOR_PATTERN = re.compile('\x01?\x1b\[(.*?)m\x02?')
    exception_occurred = Signal(str, bool)
    userListActivated = Signal(int, str)
    completion_widget_activated = Signal(str)

    def __init__(self, parent=None):
        TextEditBaseWidget.__init__(self, parent)

        self.light_background = True

        self.setMaximumBlockCount(300)

        # ANSI escape code handler
        self.ansi_handler = QtANSIEscapeCodeHandler()

        # Disable undo/redo (nonsense for a console widget...):
        self.setUndoRedoEnabled(False)

        self.userListActivated.connect(lambda user_id, text:
                                       self.completion_widget_activated.emit(text))

        self.default_style = ConsoleFontStyle(
            foregroundcolor=0x000000, backgroundcolor=0xFFFFFF,
            bold=False, italic=False, underline=False)
        self.error_style  = ConsoleFontStyle(
            foregroundcolor=0xFF0000, backgroundcolor=0xFFFFFF,
            bold=False, italic=False, underline=False)
        self.traceback_link_style  = ConsoleFontStyle(
            foregroundcolor=0x0000FF, backgroundcolor=0xFFFFFF,
            bold=True, italic=False, underline=True)
        self.prompt_style  = ConsoleFontStyle(
            foregroundcolor=0x00AA00, backgroundcolor=0xFFFFFF,
            bold=True, italic=False, underline=False)
        self.font_styles = (self.default_style, self.error_style,
                            self.traceback_link_style, self.prompt_style)
        self.set_pythonshell_font()
        self.setMouseTracking(True)

    def set_light_background(self, state):
        self.light_background = state
        if state:
            self.set_palette(background=QColor(Qt.white),
                             foreground=QColor(Qt.darkGray))
        else:
            self.set_palette(background=QColor(Qt.black),
                             foreground=QColor(Qt.lightGray))
        self.ansi_handler.set_light_background(state)
        self.set_pythonshell_font()

    def set_selection(self, start, end):
        cursor = self.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

    def truncate_selection(self, position_from):
        """Unselect read-only parts in shell, like prompt"""
        position_from = self.get_position(position_from)
        cursor = self.textCursor()
        start, end = cursor.selectionStart(), cursor.selectionEnd()
        if start < end:
            start = max([position_from, start])
        else:
            end = max([position_from, end])
        self.set_selection(start, end)

    def restrict_cursor_position(self, position_from, position_to):
        """In shell, avoid editing text except between prompt and EOF"""
        position_from = self.get_position(position_from)
        position_to = self.get_position(position_to)
        cursor = self.textCursor()
        cursor_position = cursor.position()
        if cursor_position < position_from or cursor_position > position_to:
            self.set_cursor_position(position_to)

    #------Python shell
    def insert_text(self, text):
        """Reimplement TextEditBaseWidget method"""
        # Eventually this maybe should wrap to insert_text_to if
        # backspace-handling is required
        self.textCursor().insertText(text, self.default_style.format)

    def paste(self):
        """Reimplement Qt method"""
        if self.has_selected_text():
            self.remove_selected_text()
        self.insert_text(QApplication.clipboard().text())

    def append_text_to_shell(self, text, error, prompt):
        """
        Append text to Python shell
        In a way, this method overrides the method 'insert_text' when text is
        inserted at the end of the text widget for a Python shell

        Handles error messages and show blue underlined links
        Handles ANSI color sequences
        Handles ANSI FF sequence
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        if '\r' in text:    # replace \r\n with \n
            text = text.replace('\r\n', '\n')
            text = text.replace('\r', '\n')
        while True:
            index = text.find(chr(12))
            if index == -1:
                break
            text = text[index+1:]
            self.clear()
        if error:
            is_traceback = False
            for text in text.splitlines(True):
                if text.startswith('  File') \
                        and not text.startswith('  File "<'):
                    is_traceback = True
                    # Show error links in blue underlined text
                    cursor.insertText('  ', self.default_style.format)
                    cursor.insertText(text[2:],
                                      self.traceback_link_style.format)
                else:
                    # Show error/warning messages in red
                    cursor.insertText(text, self.error_style.format)
            self.exception_occurred.emit(text, is_traceback)
        elif prompt:
            # Show prompt in green
            insert_text_to(cursor, text, self.prompt_style.format)
        else:
            # Show other outputs in black
            last_end = 0
            for match in self.COLOR_PATTERN.finditer(text):
                insert_text_to(cursor, text[last_end:match.start()],
                               self.default_style.format)
                last_end = match.end()
                try:
                    for code in [int(_c) for _c in match.group(1).split(';')]:
                        self.ansi_handler.set_code(code)
                except ValueError:
                    pass
                self.default_style.format = self.ansi_handler.get_format()
            insert_text_to(cursor, text[last_end:], self.default_style.format)
        #            # Slower alternative:
        #            segments = self.COLOR_PATTERN.split(text)
        #            cursor.insertText(segments.pop(0), self.default_style.format)
        #            if segments:
        #                for ansi_tags, text in zip(segments[::2], segments[1::2]):
        #                    for ansi_tag in ansi_tags.split(';'):
        #                        self.ansi_handler.set_code(int(ansi_tag))
        #                    self.default_style.format = self.ansi_handler.get_format()
        #                    cursor.insertText(text, self.default_style.format)
        self.set_cursor_position('eof')
        self.setCurrentCharFormat(self.default_style.format)

    def set_pythonshell_font(self, font=None):
        """Python Shell only"""
        if font is None:
            font = QFont()
        for style in self.font_styles:
            style.apply_style(font=font,
                              light_background=self.light_background,
                              is_default=style is self.default_style)
        self.ansi_handler.set_base_format(self.default_style.format)


class ANSIEscapeCodeHandler(object):
    """ANSI Escape sequences handler"""
    if os.name == 'nt':
        # Windows terminal colors:
        ANSI_COLORS = ( # Normal, Bright/Light
            ('#000000', '#808080'), # 0: black
            ('#800000', '#ff0000'), # 1: red
            ('#008000', '#00ff00'), # 2: green
            ('#808000', '#ffff00'), # 3: yellow
            ('#000080', '#0000ff'), # 4: blue
            ('#800080', '#ff00ff'), # 5: magenta
            ('#008080', '#00ffff'), # 6: cyan
            ('#c0c0c0', '#ffffff'), # 7: white
        )
    elif os.name == 'mac':
        # Terminal.app colors:
        ANSI_COLORS = ( # Normal, Bright/Light
            ('#000000', '#818383'), # 0: black
            ('#C23621', '#FC391F'), # 1: red
            ('#25BC24', '#25BC24'), # 2: green
            ('#ADAD27', '#EAEC23'), # 3: yellow
            ('#492EE1', '#5833FF'), # 4: blue
            ('#D338D3', '#F935F8'), # 5: magenta
            ('#33BBC8', '#14F0F0'), # 6: cyan
            ('#CBCCCD', '#E9EBEB'), # 7: white
        )
    else:
        # xterm colors:
        ANSI_COLORS = ( # Normal, Bright/Light
            ('#000000', '#7F7F7F'), # 0: black
            ('#CD0000', '#ff0000'), # 1: red
            ('#00CD00', '#00ff00'), # 2: green
            ('#CDCD00', '#ffff00'), # 3: yellow
            ('#0000EE', '#5C5CFF'), # 4: blue
            ('#CD00CD', '#ff00ff'), # 5: magenta
            ('#00CDCD', '#00ffff'), # 6: cyan
            ('#E5E5E5', '#ffffff'), # 7: white
        )

    def __init__(self):
        self.intensity = 0
        self.italic = None
        self.bold = None
        self.underline = None
        self.foreground_color = None
        self.background_color = None
        self.default_foreground_color = 30
        self.default_background_color = 47

    def set_code(self, code):
        assert isinstance(code, int)
        if code == 0:
            # Reset all settings
            self.reset()
        elif code == 1:
            # Text color intensity
            self.intensity = 1
            # The following line is commented because most terminals won't
            # change the font weight, against ANSI standard recommendation:
        #            self.bold = True
        elif code == 3:
            # Italic on
            self.italic = True
        elif code == 4:
            # Underline simple
            self.underline = True
        elif code == 22:
            # Normal text color intensity
            self.intensity = 0
            self.bold = False
        elif code == 23:
            # No italic
            self.italic = False
        elif code == 24:
            # No underline
            self.underline = False
        elif code >= 30 and code <= 37:
            # Text color
            self.foreground_color = code
        elif code == 39:
            # Default text color
            self.foreground_color = self.default_foreground_color
        elif code >= 40 and code <= 47:
            # Background color
            self.background_color = code
        elif code == 49:
            # Default background color
            self.background_color = self.default_background_color
        self.set_style()

    def set_style(self):
        """
        Set font style with the following attributes:
        'foreground_color', 'background_color', 'italic',
        'bold' and 'underline'
        """
        raise NotImplementedError

    def reset(self):
        self.current_format = None
        self.intensity = 0
        self.italic = False
        self.bold = False
        self.underline = False
        self.foreground_color = None
        self.background_color = None


class QtANSIEscapeCodeHandler(ANSIEscapeCodeHandler):
    def __init__(self):
        ANSIEscapeCodeHandler.__init__(self)
        self.base_format = None
        self.current_format = None

    def set_light_background(self, state):
        if state:
            self.default_foreground_color = 30
            self.default_background_color = 47
        else:
            self.default_foreground_color = 37
            self.default_background_color = 40

    def set_base_format(self, base_format):
        self.base_format = base_format

    def get_format(self):
        return self.current_format

    def set_style(self):
        """
        Set font style with the following attributes:
        'foreground_color', 'background_color', 'italic',
        'bold' and 'underline'
        """
        if self.current_format is None:
            assert self.base_format is not None
            self.current_format = QTextCharFormat(self.base_format)
        # Foreground color
        if self.foreground_color is None:
            qcolor = self.base_format.foreground()
        else:
            cstr = self.ANSI_COLORS[self.foreground_color-30][self.intensity]
            qcolor = QColor(cstr)
        self.current_format.setForeground(qcolor)
        # Background color
        if self.background_color is None:
            qcolor = self.base_format.background()
        else:
            cstr = self.ANSI_COLORS[self.background_color-40][self.intensity]
            qcolor = QColor(cstr)
        self.current_format.setBackground(qcolor)

        font = self.current_format.font()
        # Italic
        if self.italic is None:
            italic = self.base_format.fontItalic()
        else:
            italic = self.italic
        font.setItalic(italic)
        # Bold
        if self.bold is None:
            bold = self.base_format.font().bold()
        else:
            bold = self.bold
        font.setBold(bold)
        # Underline
        if self.underline is None:
            underline = self.base_format.font().underline()
        else:
            underline = self.underline
        font.setUnderline(underline)
        self.current_format.setFont(font)


def inverse_color(color):
    color.setHsv(color.hue(), color.saturation(), 255-color.value())


class ConsoleFontStyle(object):
    def __init__(self, foregroundcolor, backgroundcolor, bold, italic, underline):
        self.foregroundcolor = foregroundcolor
        self.backgroundcolor = backgroundcolor
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.format = None

    def apply_style(self, font, light_background, is_default):
        self.format = QTextCharFormat()
        self.format.setFont(font)
        foreground = QColor(self.foregroundcolor)
        if not light_background and is_default:
            inverse_color(foreground)
        self.format.setForeground(foreground)
        background = QColor(self.backgroundcolor)
        if not light_background:
            inverse_color(background)
        self.format.setBackground(background)
        font = self.format.font()
        font.setBold(self.bold)
        font.setItalic(self.italic)
        font.setUnderline(self.underline)
        self.format.setFont(font)


class ShellBaseWidget(ConsoleBaseWidget):
    """
    Shell base widget
    """

    redirect_stdio = Signal(bool)
    sig_keyboard_interrupt = Signal()
    execute = Signal(str)
    append_to_history = Signal(str, str)

    def __init__(self, parent, history_filename, profile=False,
                 initial_message=None):
        """
        parent : specifies the parent widget
        """
        ConsoleBaseWidget.__init__(self, parent)

        # Prompt position: tuple (line, index)
        self.current_prompt_pos = None
        self.new_input_line = True

        # History
        assert is_text_string(history_filename)
        self.history = self.load_history()

        # # Session
        # self.historylog_filename = CONF.get('main', 'historylog_filename',
        #                                     get_conf_path('history.log'))

        # Context menu
        self.menu = None
        self.setup_context_menu()

        # Simple profiling test
        self.profile = profile

        # Buffer to increase performance of write/flush operations
        self.__buffer = []
        if initial_message:
            self.__buffer.append(initial_message)

        self.__timestamp = 0.0
        self.__flushtimer = QTimer(self)
        self.__flushtimer.setSingleShot(True)
        self.__flushtimer.timeout.connect(self.flush)

        # Give focus to widget
        self.setFocus()

        # Cursor width
        self.setCursorWidth(2)

    def toggle_wrap_mode(self, enable):
        """Enable/disable wrap mode"""
        self.set_wrap_mode('character' if enable else None)

    def set_font(self, font):
        """Set shell styles font"""
        self.setFont(font)
        self.set_pythonshell_font(font)
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        charformat = QTextCharFormat()
        charformat.setFontFamily(font.family())
        charformat.setFontPointSize(font.pointSize())
        cursor.mergeCharFormat(charformat)

    #------ Context menu
    def setup_context_menu(self):
        """Setup shell context menu"""
        self.menu = QMenu(self)
        self.cut_action = create_action(self, _("Cut"),
                                        shortcut=keybinding('Cut'),
                                        icon=ima.icon('editcut'),
                                        triggered=self.cut)
        self.copy_action = create_action(self, _("Copy"),
                                         shortcut=keybinding('Copy'),
                                         icon=ima.icon('editcopy'),
                                         triggered=self.copy)
        paste_action = create_action(self, _("Paste"),
                                     shortcut=keybinding('Paste'),
                                     icon=ima.icon('editpaste'),
                                     triggered=self.paste)
        save_action = create_action(self, _("Save history log..."),
                                    icon=ima.icon('filesave'),
                                    tip=_("Save current history log (i.e. all "
                                          "inputs and outputs) in a text file"),
                                    triggered=self.save_historylog)
        self.delete_action = create_action(self, _("Delete"),
                                           shortcut=keybinding('Delete'),
                                           icon=ima.icon('editdelete'),
                                           triggered=self.delete)
        selectall_action = create_action(self, _("Select All"),
                                         shortcut=keybinding('SelectAll'),
                                         icon=ima.icon('selectall'),
                                         triggered=self.selectAll)
        add_actions(self.menu, (self.cut_action, self.copy_action,
                                paste_action, self.delete_action, None,
                                selectall_action, None, save_action) )

    def contextMenuEvent(self, event):
        """Reimplement Qt method"""
        state = self.has_selected_text()
        self.copy_action.setEnabled(state)
        self.cut_action.setEnabled(state)
        self.delete_action.setEnabled(state)
        self.menu.popup(event.globalPos())
        event.accept()

        #------ Input buffer
    def get_current_line_from_cursor(self):
        return self.get_text('cursor', 'eof')

    def _select_input(self):
        """Select current line (without selecting console prompt)"""
        line, index = self.get_position('eof')
        if self.current_prompt_pos is None:
            pline, pindex = line, index
        else:
            pline, pindex = self.current_prompt_pos
        self.setSelection(pline, pindex, line, index)

    # @Slot()
    def clear_terminal(self):
        """
        Clear terminal window
        Child classes reimplement this method to write prompt
        """
        self.clear()

    # The buffer being edited

    # def _get_input_buffer(self):
    @property
    def input_buffer(self):
        """Return input buffer"""
        input_buffer = ''
        if self.current_prompt_pos is not None:
            input_buffer = self.get_text(self.current_prompt_pos, 'eol')
            input_buffer = input_buffer.replace(os.linesep, '\n')
        return input_buffer

    # def _set_input_buffer(self, text):
    @input_buffer.setter
    def input_buffer(self, text):
        """Set input buffer"""
        if self.current_prompt_pos is not None:
            self.replace_text(self.current_prompt_pos, 'eol', text)
        else:
            self.insert(text)
        self.set_cursor_position('eof')

    # input_buffer = Property("QString", _get_input_buffer, _set_input_buffer)

    #------ Prompt
    def new_prompt(self, prompt):
        """
        Print a new prompt and save its (line, index) position
        """
        if self.get_cursor_line_column()[1] != 0:
            self.write('\n')
        self.write(prompt, prompt=True)
        # now we update our cursor giving end of prompt
        self.current_prompt_pos = self.get_position('cursor')
        self.ensureCursorVisible()
        self.new_input_line = False

    def check_selection(self):
        """
        Check if selected text is r/w,
        otherwise remove read-only parts of selection
        """
        if self.current_prompt_pos is None:
            self.set_cursor_position('eof')
        else:
            self.truncate_selection(self.current_prompt_pos)

    #------ Copy / Keyboard interrupt
    # @Slot()
    def copy(self):
        """Copy text to clipboard... or keyboard interrupt"""
        if self.has_selected_text():
            ConsoleBaseWidget.copy(self)
        elif not sys.platform == 'darwin':
            self.interrupt()

    def interrupt(self):
        """Keyboard interrupt"""
        self.sig_keyboard_interrupt.emit()

    # @Slot()
    def cut(self):
        """Cut text"""
        self.check_selection()
        if self.has_selected_text():
            ConsoleBaseWidget.cut(self)

    # @Slot()
    def delete(self):
        """Remove selected text"""
        self.check_selection()
        if self.has_selected_text():
            ConsoleBaseWidget.remove_selected_text(self)

    # # @Slot()
    # def save_historylog(self):
    #     """Save current history log (all text in console)"""
    #     title = _("Save history log")
    #     self.redirect_stdio.emit(False)
    #     filename, _selfilter = getsavefilename(self, title,
    #                                            self.historylog_filename, "%s (*.log)" % _("History logs"))
    #     self.redirect_stdio.emit(True)
    #     if filename:
    #         filename = osp.normpath(filename)
    #         try:
    #             encoding.write(to_text_string(self.get_text_with_eol()),
    #                            filename)
    #             self.historylog_filename = filename
    #             CONF.set('main', 'historylog_filename', filename)
    #         except EnvironmentError as error:
    #             QMessageBox.critical(self, title,
    #                                  _("<b>Unable to save file '%s'</b>"
    #                                    "<br><br>Error message:<br>%s"
    #                                    ) % (osp.basename(filename),
    #                                         to_text_string(error)))

    #------ Basic keypress event handler
    def on_enter(self, command):
        """on_enter"""
        self.execute_command(command)

    def execute_command(self, command):
        self.execute.emit(command)
        self.add_to_history(command)
        self.new_input_line = True

    def on_new_line(self):
        """On new input line"""
        self.set_cursor_position('eof')
        self.current_prompt_pos = self.get_position('cursor')
        self.new_input_line = False

    # @Slot()
    def paste(self):
        """Reimplemented slot to handle multiline paste action"""
        if self.new_input_line:
            self.on_new_line()
        ConsoleBaseWidget.paste(self)

    def keyPressEvent(self, event):
        """
        Reimplement Qt Method
        Basic keypress event handler
        (reimplemented in InternalShell to add more sophisticated features)
        """
        if self.preprocess_keyevent(event):
            # Event was accepted in self.preprocess_keyevent
            return
        self.postprocess_keyevent(event)

    def preprocess_keyevent(self, event):
        """Pre-process keypress event:
        return True if event is accepted, false otherwise"""
        # Copy must be done first to be able to copy read-only text parts
        # (otherwise, right below, we would remove selection
        #  if not on current line)
        ctrl = event.modifiers() & Qt.ControlModifier
        meta = event.modifiers() & Qt.MetaModifier    # meta=ctrl in OSX
        if event.key() == Qt.Key_C and \
                ((Qt.MetaModifier | Qt.ControlModifier) & event.modifiers()):
            if meta and sys.platform == 'darwin':
                self.interrupt()
            elif ctrl:
                self.copy()
            event.accept()
            return True

        if self.new_input_line and ( len(event.text()) or event.key() in \
                                     (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right) ):
            self.on_new_line()

        return False

    def postprocess_keyevent(self, event):
        """Post-process keypress event:
        in InternalShell, this is method is called when shell is ready"""
        event, text, key, ctrl, shift = restore_keyevent(event)

        # Is cursor on the last line? and after prompt?
        if len(text):
            #XXX: Shouldn't it be: `if len(unicode(text).strip(os.linesep))` ?
            if self.has_selected_text():
                self.check_selection()
            self.restrict_cursor_position(self.current_prompt_pos, 'eof')

        cursor_position = self.get_position('cursor')

        if key in (Qt.Key_Return, Qt.Key_Enter):
            if self.is_cursor_on_last_line():
                self._key_enter()
            # add and run selection
            else:
                self.insert_text(self.get_selected_text(), at_end=True)

        elif key == Qt.Key_Insert and not shift and not ctrl:
            self.setOverwriteMode(not self.overwriteMode())

        elif key == Qt.Key_Delete:
            if self.has_selected_text():
                self.check_selection()
                self.remove_selected_text()
            elif self.is_cursor_on_last_line():
                self.stdkey_clear()

        elif key == Qt.Key_Backspace:
            self._key_backspace(cursor_position)

        elif key == Qt.Key_Tab:
            self._key_tab()

        elif key == Qt.Key_Space and ctrl:
            self._key_ctrl_space()

        elif key == Qt.Key_Left:
            if self.current_prompt_pos == cursor_position:
                # Avoid moving cursor on prompt
                return
            method = self.extend_selection_to_next if shift \
                else self.move_cursor_to_next
            method('word' if ctrl else 'character', direction='left')

        elif key == Qt.Key_Right:
            if self.is_cursor_at_end():
                return
            method = self.extend_selection_to_next if shift \
                else self.move_cursor_to_next
            method('word' if ctrl else 'character', direction='right')

        elif (key == Qt.Key_Home) or ((key == Qt.Key_Up) and ctrl):
            self._key_home(shift, ctrl)

        elif (key == Qt.Key_End) or ((key == Qt.Key_Down) and ctrl):
            self._key_end(shift, ctrl)

        elif key == Qt.Key_Up:
            if not self.is_cursor_on_last_line():
                self.set_cursor_position('eof')
            y_cursor = self.get_coordinates(cursor_position)[1]
            y_prompt = self.get_coordinates(self.current_prompt_pos)[1]
            if y_cursor > y_prompt:
                self.stdkey_up(shift)
            else:
                self.browse_history(backward=True)

        elif key == Qt.Key_Down:
            if not self.is_cursor_on_last_line():
                self.set_cursor_position('eof')
            y_cursor = self.get_coordinates(cursor_position)[1]
            y_end = self.get_coordinates('eol')[1]
            if y_cursor < y_end:
                self.stdkey_down(shift)
            else:
                self.browse_history(backward=False)

        elif key in (Qt.Key_PageUp, Qt.Key_PageDown):
            #XXX: Find a way to do this programmatically instead of calling
            # widget keyhandler (this won't work if the *event* is coming from
            # the event queue - i.e. if the busy buffer is ever implemented)
            ConsoleBaseWidget.keyPressEvent(self, event)

        elif key == Qt.Key_Escape and shift:
            self.clear_line()

        elif key == Qt.Key_Escape:
            self._key_escape()

        elif key == Qt.Key_L and ctrl:
            self.clear_terminal()

        elif key == Qt.Key_V and ctrl:
            self.paste()

        elif key == Qt.Key_X and ctrl:
            self.cut()

        elif key == Qt.Key_Z and ctrl:
            self.undo()

        elif key == Qt.Key_Y and ctrl:
            self.redo()

        elif key == Qt.Key_A and ctrl:
            self.selectAll()

        elif key == Qt.Key_Question and not self.has_selected_text():
            self._key_question(text)

        elif key == Qt.Key_ParenLeft and not self.has_selected_text():
            self._key_parenleft(text)

        elif key == Qt.Key_Period and not self.has_selected_text():
            self._key_period(text)

        elif len(text) and not self.isReadOnly():
            self.hist_wholeline = False
            self.insert_text(text)
            self._key_other(text)

        else:
            # Let the parent widget handle the key press event
            ConsoleBaseWidget.keyPressEvent(self, event)

    #------ Key handlers
    def _key_enter(self):
        command = self.input_buffer
        self.insert_text('\n', at_end=True)
        self.on_enter(command)
        self.flush()
    def _key_other(self, text):
        raise NotImplementedError
    def _key_backspace(self, cursor_position):
        raise NotImplementedError
    def _key_tab(self):
        raise NotImplementedError
    def _key_ctrl_space(self):
        raise NotImplementedError
    def _key_home(self, shift, ctrl):
        if self.is_cursor_on_last_line():
            self.stdkey_home(shift, ctrl, self.current_prompt_pos)
    def _key_end(self, shift, ctrl):
        if self.is_cursor_on_last_line():
            self.stdkey_end(shift, ctrl)
    def _key_pageup(self):
        raise NotImplementedError
    def _key_pagedown(self):
        raise NotImplementedError
    def _key_escape(self):
        raise NotImplementedError
    def _key_question(self, text):
        raise NotImplementedError
    def _key_parenleft(self, text):
        raise NotImplementedError
    def _key_period(self, text):
        raise NotImplementedError

    #------ Simulation standards input/output
    def write_error(self, text):
        """Simulate stderr"""
        self.flush()
        self.write(text, flush=True, error=True)
        if DEBUG:
            STDERR.write(text)

    def write(self, text, flush=False, error=False, prompt=False):
        """Simulate stdout and stderr"""
        if prompt:
            self.flush()
        if not is_string(text):
            # This test is useful to discriminate QStrings from decoded str
            text = to_text_string(text)
        self.__buffer.append(text)
        ts = time.time()
        if flush or prompt:
            self.flush(error=error, prompt=prompt)
        elif ts - self.__timestamp > 0.05:
            self.flush(error=error)
            self.__timestamp = ts
            # Timer to flush strings cached by last write() operation in series
            self.__flushtimer.start(50)

    def flush(self, error=False, prompt=False):
        """Flush buffer, write text to console"""
        # Fix for Issue 2452
        if PY3:
            try:
                text = "".join(self.__buffer)
            except TypeError:
                text = b"".join(self.__buffer)
                try:
                    # text = text.decode(locale.getdefaultlocale()[1])
                    text = text.decode('utf-8')
                except:
                    pass
        else:
            text = "".join(self.__buffer)

        self.__buffer = []
        self.insert_text(text, at_end=True, error=error, prompt=prompt)
        QCoreApplication.processEvents()
        self.repaint()
        # Clear input buffer:
        self.new_input_line = True

    #------ Text Insertion
    def insert_text(self, text, at_end=False, error=False, prompt=False):
        """
        Insert text at the current cursor position
        or at the end of the command line
        """
        if at_end:
            # Insert text at the end of the command line
            self.append_text_to_shell(text, error, prompt)
        else:
            # Insert text at current cursor position
            ConsoleBaseWidget.insert_text(self, text)

    #------ Re-implemented Qt Methods
    def focusNextPrevChild(self, next):
        """
        Reimplemented to stop Tab moving to the next window
        """
        if next:
            return False
        return ConsoleBaseWidget.focusNextPrevChild(self, next)

    #------ Drag and drop
    def dragEnterEvent(self, event):
        """Drag and Drop - Enter event"""
        event.setAccepted(event.mimeData().hasFormat("text/plain"))

    def dragMoveEvent(self, event):
        """Drag and Drop - Move event"""
        if (event.mimeData().hasFormat("text/plain")):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Drag and Drop - Drop event"""
        if (event.mimeData().hasFormat("text/plain")):
            text = to_text_string(event.mimeData().text())
            if self.new_input_line:
                self.on_new_line()
            self.insert_text(text, at_end=True)
            self.setFocus()
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def drop_pathlist(self, pathlist):
        """Drop path list"""
        raise NotImplementedError


class TerminalWidget(ShellBaseWidget):
    """
    Terminal widget
    """
    COM = 'rem' if os.name == 'nt' else '#'
    INITHISTORY = ['%s *** Spyder Terminal History Log ***' % COM, COM,]
    SEPARATOR = '%s%s ---(%s)---' % (os.linesep*2, COM, time.ctime())
    go_to_error = Signal(str)

    def __init__(self, parent, history_filename, profile=False):
        ShellBaseWidget.__init__(self, parent, history_filename, profile)

    #------ Key handlers
    def _key_other(self, text):
        """1 character key"""
        pass

    def _key_backspace(self, cursor_position):
        """Action for Backspace key"""
        if self.has_selected_text():
            self.check_selection()
            self.remove_selected_text()
        elif self.current_prompt_pos == cursor_position:
            # Avoid deleting prompt
            return
        elif self.is_cursor_on_last_line():
            self.stdkey_backspace()

    def _key_tab(self):
        """Action for TAB key"""
        if self.is_cursor_on_last_line():
            self.stdkey_tab()

    def _key_ctrl_space(self):
        """Action for Ctrl+Space"""
        pass

    def _key_escape(self):
        """Action for ESCAPE key"""
        self.clear_line()

    def _key_question(self, text):
        """Action for '?'"""
        self.insert_text(text)

    def _key_parenleft(self, text):
        """Action for '('"""
        self.insert_text(text)

    def _key_period(self, text):
        """Action for '.'"""
        self.insert_text(text)

    #------ Drag'n Drop
    def drop_pathlist(self, pathlist):
        """Drop path list"""
        if pathlist:
            files = ['"%s"' % path for path in pathlist]
            if len(files) == 1:
                text = files[0]
            else:
                text = " ".join(files)
            if self.new_input_line:
                self.on_new_line()
            self.insert_text(text)
            self.setFocus()