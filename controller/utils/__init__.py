import sys
import textwrap
import os
import re
import sre_constants
from xml.sax.saxutils import escape

from PyQt5.QtGui import QTextCursor, QTextDocument
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtCore import QObject, pyqtSignal, QPoint, QRegularExpression

from controller.utils.py3compat import is_text_string, to_text_string


EOL_CHARS = (("\r\n", 'nt'), ("\n", 'posix'), ("\r", 'mac'))


class XStream(QObject):
    _stdout = None
    _stderr = None
    messageWritten = pyqtSignal(str)

    def flush(self):
        pass

    def fileno(self):
        return -1

    def write(self, msg):
        if not self.signalsBlocked():
            self.messageWritten.emit(msg)

    @staticmethod
    def stdout():
        if not XStream._stdout:
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        if not XStream._stderr:
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr


def get_eol_chars(text):
    """Get text EOL characters"""
    for eol_chars, _os_name in EOL_CHARS:
        if text.find(eol_chars) > -1:
            return eol_chars


# def to_qvariant(obj=None):
#     return obj


class BaseEditMixin(object):

    def __init__(self):
        self.eol_chars = None
        self.calltip_size = 600

    #------Line number area
    def get_linenumberarea_width(self):
        """Return line number area width"""
        # Implemented in CodeEditor, but needed for calltip/completion widgets
        return 0

    #------Calltips
    def _format_signature(self, text):
        formatted_lines = []
        name = text.split('(')[0]
        rows = textwrap.wrap(text, width=50,
                             subsequent_indent=' '*(len(name)+1))
        for r in rows:
            r = escape(r) # Escape most common html chars
            r = r.replace(' ', '&nbsp;')
            for char in ['=', ',', '(', ')', '*', '**']:
                r = r.replace(char,
                              '<span style=\'color: red; font-weight: bold\'>' + \
                              char + '</span>')
            formatted_lines.append(r)
        signature = '<br>'.join(formatted_lines)
        return signature, rows

    def show_calltip(self, title, text, signature=False, color='#2D62FF',
                     at_line=None, at_position=None):
        """Show calltip"""
        if text is None or len(text) == 0:
            return

        # Saving cursor position:
        if at_position is None:
            at_position = self.get_position('cursor')
        self.calltip_position = at_position

        # Preparing text:
        if signature:
            text, wrapped_textlines = self._format_signature(text)
        else:
            if isinstance(text, list):
                text = "\n    ".join(text)
            text = text.replace('\n', '<br>')
            if len(text) > self.calltip_size:
                text = text[:self.calltip_size] + " ..."

        # Formatting text
        font = self.font()
        size = font.pointSize()
        family = font.family()
        format1 = '<div style=\'font-family: "%s"; font-size: %spt; color: %s\'>' \
                  % (family, size, color)
        format2 = '<div style=\'font-family: "%s"; font-size: %spt\'>' \
                  % (family, size-1 if size > 9 else size)
        tiptext = format1 + ('<b>%s</b></div>' % title) + '<hr>' + \
                  format2 + text + "</div>"

        # Showing tooltip at cursor position:
        cx, cy = self.get_coordinates('cursor')
        if at_line is not None:
            cx = 5
            cursor = QTextCursor(self.document().findBlockByNumber(at_line-1))
            cy = self.cursorRect(cursor).top()
        point = self.mapToGlobal(QPoint(cx, cy))
        point.setX(point.x()+self.get_linenumberarea_width())
        point.setY(point.y()+font.pointSize()+5)
        if signature:
            self.calltip_widget.show_tip(point, tiptext, wrapped_textlines)
        else:
            QToolTip.showText(point, tiptext)

    #------EOL characters
    def set_eol_chars(self, text):
        """Set widget end-of-line (EOL) characters from text (analyzes text)"""
        if not is_text_string(text): # testing for QString (PyQt API#1)
            text = to_text_string(text)
        eol_chars = get_eol_chars(text)
        is_document_modified = eol_chars is not None and self.eol_chars is not None
        self.eol_chars = eol_chars
        if is_document_modified:
            self.document().setModified(True)
            if self.sig_eol_chars_changed is not None:
                self.sig_eol_chars_changed.emit(eol_chars)

    def get_line_separator(self):
        """Return line separator based on current EOL mode"""
        if self.eol_chars is not None:
            return self.eol_chars
        else:
            return os.linesep

    def get_text_with_eol(self):
        """Same as 'toPlainText', replace '\n'
        by correct end-of-line characters"""
        utext = to_text_string(self.toPlainText())
        lines = utext.splitlines()
        linesep = self.get_line_separator()
        txt = linesep.join(lines)
        if utext.endswith('\n'):
            txt += linesep
        return txt

    #------Positions, coordinates (cursor, EOF, ...)
    def get_position(self, subject):
        """Get offset in character for the given subject from the start of
           text edit area"""
        cursor = self.textCursor()
        if subject == 'cursor':
            pass
        elif subject == 'sol':
            cursor.movePosition(QTextCursor.StartOfBlock)
        elif subject == 'eol':
            cursor.movePosition(QTextCursor.EndOfBlock)
        elif subject == 'eof':
            cursor.movePosition(QTextCursor.End)
        elif subject == 'sof':
            cursor.movePosition(QTextCursor.Start)
        else:
            # Assuming that input argument was already a position
            return subject
        return cursor.position()

    def get_coordinates(self, position):
        position = self.get_position(position)
        cursor = self.textCursor()
        cursor.setPosition(position)
        point = self.cursorRect(cursor).center()
        return point.x(), point.y()

    def get_cursor_line_column(self):
        """Return cursor (line, column) numbers"""
        cursor = self.textCursor()
        return cursor.blockNumber(), cursor.columnNumber()

    def get_cursor_line_number(self):
        """Return cursor line number"""
        return self.textCursor().blockNumber()+1

    def set_cursor_position(self, position):
        """Set cursor position"""
        position = self.get_position(position)
        cursor = self.textCursor()
        cursor.setPosition(position)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def move_cursor(self, chars=0):
        """Move cursor to left or right (unit: characters)"""
        direction = QTextCursor.Right if chars > 0 else QTextCursor.Left
        for _i in range(abs(chars)):
            self.moveCursor(direction, QTextCursor.MoveAnchor)

    def is_cursor_on_first_line(self):
        """Return True if cursor is on the first line"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock)
        return cursor.atStart()

    def is_cursor_on_last_line(self):
        """Return True if cursor is on the last line"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.EndOfBlock)
        return cursor.atEnd()

    def is_cursor_at_end(self):
        """Return True if cursor is at the end of the text"""
        return self.textCursor().atEnd()

    def is_cursor_before(self, position, char_offset=0):
        """Return True if cursor is before *position*"""
        position = self.get_position(position) + char_offset
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        if position < cursor.position():
            cursor.setPosition(position)
            return self.textCursor() < cursor

    def __move_cursor_anchor(self, what, direction, move_mode):
        assert what in ('character', 'word', 'line')
        if what == 'character':
            if direction == 'left':
                self.moveCursor(QTextCursor.PreviousCharacter, move_mode)
            elif direction == 'right':
                self.moveCursor(QTextCursor.NextCharacter, move_mode)
        elif what == 'word':
            if direction == 'left':
                self.moveCursor(QTextCursor.PreviousWord, move_mode)
            elif direction == 'right':
                self.moveCursor(QTextCursor.NextWord, move_mode)
        elif what == 'line':
            if direction == 'down':
                self.moveCursor(QTextCursor.NextBlock, move_mode)
            elif direction == 'up':
                self.moveCursor(QTextCursor.PreviousBlock, move_mode)

    def move_cursor_to_next(self, what='word', direction='left'):
        """
        Move cursor to next *what* ('word' or 'character')
        toward *direction* ('left' or 'right')
        """
        self.__move_cursor_anchor(what, direction, QTextCursor.MoveAnchor)

    #------Selection
    def clear_selection(self):
        """Clear current selection"""
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def extend_selection_to_next(self, what='word', direction='left'):
        """
        Extend selection to next *what* ('word' or 'character')
        toward *direction* ('left' or 'right')
        """
        self.__move_cursor_anchor(what, direction, QTextCursor.KeepAnchor)

    #------Text: get, set, ...
    def __select_text(self, position_from, position_to):
        position_from = self.get_position(position_from)
        position_to = self.get_position(position_to)
        cursor = self.textCursor()
        cursor.setPosition(position_from)
        cursor.setPosition(position_to, QTextCursor.KeepAnchor)
        return cursor

    def get_text_line(self, line_nb):
        """Return text line at line number *line_nb*"""
        # Taking into account the case when a file ends in an empty line,
        # since splitlines doesn't return that line as the last element
        # TODO: Make this function more efficient
        try:
            return to_text_string(self.toPlainText()).splitlines()[line_nb]
        except IndexError:
            return self.get_line_separator()

    def get_text(self, position_from, position_to):
        """
        Return text between *position_from* and *position_to*
        Positions may be positions or 'sol', 'eol', 'sof', 'eof' or 'cursor'
        """
        cursor = self.__select_text(position_from, position_to)
        text = to_text_string(cursor.selectedText())
        all_text = position_from == 'sof' and position_to == 'eof'
        if text and not all_text:
            while text.endswith("\n"):
                text = text[:-1]
            while text.endswith(u"\u2029"):
                text = text[:-1]
        return text

    def get_character(self, position, offset=0):
        """Return character at *position* with the given offset."""
        position = self.get_position(position) + offset
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        if position < cursor.position():
            cursor.setPosition(position)
            cursor.movePosition(QTextCursor.Right,
                                QTextCursor.KeepAnchor)
            return to_text_string(cursor.selectedText())
        else:
            return ''

    def insert_text(self, text):
        """Insert text at cursor position"""
        if not self.isReadOnly():
            self.textCursor().insertText(text)

    def replace_text(self, position_from, position_to, text):
        cursor = self.__select_text(position_from, position_to)
        cursor.removeSelectedText()
        cursor.insertText(text)

    def remove_text(self, position_from, position_to):
        cursor = self.__select_text(position_from, position_to)
        cursor.removeSelectedText()

    def get_current_word(self):
        """Return current word, i.e. word at cursor position"""
        cursor = self.textCursor()

        if cursor.hasSelection():
            # Removes the selection and moves the cursor to the left side
            # of the selection: this is required to be able to properly
            # select the whole word under cursor (otherwise, the same word is
            # not selected when the cursor is at the right side of it):
            cursor.setPosition(min([cursor.selectionStart(),
                                    cursor.selectionEnd()]))
        else:
            # Checks if the first character to the right is a white space
            # and if not, moves the cursor one word to the left (otherwise,
            # if the character to the left do not match the "word regexp"
            # (see below), the word to the left of the cursor won't be
            # selected), but only if the first character to the left is not a
            # white space too.
            def is_space(move):
                curs = self.textCursor()
                curs.movePosition(move, QTextCursor.KeepAnchor)
                return not to_text_string(curs.selectedText()).strip()
            if is_space(QTextCursor.NextCharacter):
                if is_space(QTextCursor.PreviousCharacter):
                    return
                cursor.movePosition(QTextCursor.WordLeft)

        cursor.select(QTextCursor.WordUnderCursor)
        text = to_text_string(cursor.selectedText())
        # find a valid python variable name
        match = re.findall(r'([^\d\W]\w*)', text, re.UNICODE)
        if match:
            return match[0]

    def get_current_line(self):
        """Return current line's text"""
        cursor = self.textCursor()
        cursor.select(QTextCursor.BlockUnderCursor)
        return to_text_string(cursor.selectedText())

    def get_current_line_to_cursor(self):
        """Return text from prompt to cursor"""
        return self.get_text(self.current_prompt_pos, 'cursor')

    def get_line_number_at(self, coordinates):
        """Return line number at *coordinates* (QPoint)"""
        cursor = self.cursorForPosition(coordinates)
        return cursor.blockNumber()-1

    def get_line_at(self, coordinates):
        """Return line at *coordinates* (QPoint)"""
        cursor = self.cursorForPosition(coordinates)
        cursor.select(QTextCursor.BlockUnderCursor)
        return to_text_string(cursor.selectedText()).replace(u'\u2029', '')

    def get_word_at(self, coordinates):
        """Return word at *coordinates* (QPoint)"""
        cursor = self.cursorForPosition(coordinates)
        cursor.select(QTextCursor.WordUnderCursor)
        return to_text_string(cursor.selectedText())

    def get_block_indentation(self, block_nb):
        """Return line indentation (character number)"""
        text = to_text_string(self.document().findBlockByNumber(block_nb).text())
        text = text.replace("\t", " "*self.tab_stop_width_spaces)
        return len(text)-len(text.lstrip())

    def get_selection_bounds(self):
        """Return selection bounds (block numbers)"""
        cursor = self.textCursor()
        start, end = cursor.selectionStart(), cursor.selectionEnd()
        block_start = self.document().findBlock(start)
        block_end = self.document().findBlock(end)
        return sorted([block_start.blockNumber(), block_end.blockNumber()])


    #------Text selection
    def has_selected_text(self):
        """Returns True if some text is selected"""
        return bool(to_text_string(self.textCursor().selectedText()))

    def get_selected_text(self):
        """
        Return text selected by current text cursor, converted in unicode

        Replace the unicode line separator character \u2029 by
        the line separator characters returned by get_line_separator
        """
        return to_text_string(self.textCursor().selectedText()).replace(u"\u2029",
                                                                        self.get_line_separator())

    def remove_selected_text(self):
        """Delete selected text"""
        self.textCursor().removeSelectedText()

    def replace(self, text, pattern=None):
        """Replace selected text by *text*
        If *pattern* is not None, replacing selected text using regular
        expression text substitution"""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        if pattern is not None:
            seltxt = to_text_string(cursor.selectedText())
        cursor.removeSelectedText()
        if pattern is not None:
            text = re.sub(to_text_string(pattern),
                          to_text_string(text), to_text_string(seltxt))
        cursor.insertText(text)
        cursor.endEditBlock()


    #------Find/replace
    def find_multiline_pattern(self, regexp, cursor, findflag):
        """Reimplement QTextDocument's find method

        Add support for *multiline* regular expressions"""
        pattern = to_text_string(regexp.pattern())
        text = to_text_string(self.toPlainText())
        try:
            regobj = re.compile(pattern)
        except sre_constants.error:
            return
        if findflag & QTextDocument.FindBackward:
            # Find backward
            offset = min([cursor.selectionEnd(), cursor.selectionStart()])
            text = text[:offset]
            matches = [_m for _m in regobj.finditer(text, 0, offset)]
            if matches:
                match = matches[-1]
            else:
                return
        else:
            # Find forward
            offset = max([cursor.selectionEnd(), cursor.selectionStart()])
            match = regobj.search(text, offset)
        if match:
            pos1, pos2 = match.span()
            fcursor = self.textCursor()
            fcursor.setPosition(pos1)
            fcursor.setPosition(pos2, QTextCursor.KeepAnchor)
            return fcursor

    def find_text(self, text, changed=True, forward=True, case=False,
                  words=False, regexp=False):
        """Find text"""
        cursor = self.textCursor()
        findflag = QTextDocument.FindFlag()
        if not forward:
            findflag = findflag | QTextDocument.FindBackward
        if case:
            findflag = findflag | QTextDocument.FindCaseSensitively
        moves = [QTextCursor.NoMove]
        if forward:
            moves += [QTextCursor.NextWord, QTextCursor.Start]
            if changed:
                if to_text_string(cursor.selectedText()):
                    new_position = min([cursor.selectionStart(),
                                        cursor.selectionEnd()])
                    cursor.setPosition(new_position)
                else:
                    cursor.movePosition(QTextCursor.PreviousWord)
        else:
            moves += [QTextCursor.End]
        if not regexp:
            text = re.escape(to_text_string(text))
        # if QT55_VERSION:
        pattern = QRegularExpression(r"\b{}\b".format(text) if words else
                                     text)
        if case:
            pattern.setPatternOptions(
                QRegularExpression.CaseInsensitiveOption)
        # else:
        #     pattern = QRegExp(r"\b{}\b".format(text)
        #                       if words else text, Qt.CaseSensitive if case else
        #                       Qt.CaseInsensitive, QRegExp.RegExp2)

        for move in moves:
            cursor.movePosition(move)
            if regexp and '\\n' in text:
                # Multiline regular expression
                found_cursor = self.find_multiline_pattern(pattern, cursor,
                                                           findflag)
            else:
                # Single line find: using the QTextDocument's find function,
                # probably much more efficient than ours
                found_cursor = self.document().find(pattern, cursor, findflag)
            if found_cursor is not None and not found_cursor.isNull():
                self.setTextCursor(found_cursor)
                return True
        return False

    def is_editor(self):
        """Needs to be overloaded in the codeeditor where it will be True"""
        return False

    def get_number_matches(self, pattern, source_text='', case=False):
        """Get the number of matches for the searched text."""
        pattern = to_text_string(pattern)
        if not pattern:
            return 0
        if not source_text:
            source_text = to_text_string(self.toPlainText())
        try:
            if case:
                regobj = re.compile(pattern)
            else:
                regobj = re.compile(pattern, re.IGNORECASE)
        except sre_constants.error:
            return

        number_matches = 0
        for match in regobj.finditer(source_text):
            number_matches += 1

        return number_matches

    def get_match_number(self, pattern, case=False):
        """Get number of the match for the searched text."""
        position = self.textCursor().position()
        source_text = self.get_text(position_from='sof', position_to=position)
        match_number = self.get_number_matches(pattern,
                                               source_text=source_text,
                                               case=case)
        return match_number

