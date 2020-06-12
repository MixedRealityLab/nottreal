
from ..utils.log import Logger
from ..models.m_mvc import WizardOption

from collections import OrderedDict, deque
from PySide2.QtWidgets import (QAbstractItemView, QAction, QApplication,
                               QCheckBox, QComboBox, QDialogButtonBox,
                               QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                               QMainWindow, QPlainTextEdit, QPushButton,
                               QStyleFactory, QVBoxLayout, QTabWidget,
                               QTreeView, QWidget)
from PySide2.QtGui import (QIcon, QTextCursor, QStandardItemModel, QPalette)
from PySide2.QtCore import (Qt, QItemSelection, QItemSelectionModel, QTimer,
                            Slot)

import re


class WizardWindow(QMainWindow):
    """
    The main window of the application (i.e. the Wizard's control panel)

    Extends:
        QMainWindow
    """
    def __init__(self, nottreal, args, data, config):
        """
        The Window for controlling the VUI

        Arguments:
            nottreal {App} -- Main NottReal class
            args {[str]} -- CLI arguments
            data {TSVModel} -- Data from static data files
            config {ConfigModel} -- Data from static configuration files
        """
        self.nottreal = nottreal
        self.args = args
        self.data = data
        self.config = config

        # shortcuts
        self.router = nottreal.router

        super(WizardWindow, self).__init__()
        self.setWindowTitle(nottreal.appname)

        Logger.debug(__name__, 'Initialising the Wizard window')

        # Window layout
        layout = QGridLayout()
        layout.setVerticalSpacing(0)

        window_main = QWidget()
        window_main.setLayout(layout)
        self.setCentralWidget(window_main)

        # add prepared messages
        self.prepared_msgs = PreparedMessagesWidget(self, data.cats)
        layout.addWidget(self.prepared_msgs, 0, 0)
        layout.setRowStretch(0, 3)

        # add slot history and message queue
        row2widget = QGroupBox()
        row2layout = QHBoxLayout()

        row2widget.setContentsMargins(0, 5, 0, 0)

        self.slot_history = SlotHistoryWidget(row2widget)
        row2layout.addWidget(self.slot_history)

        self.msg_queue = MessageQueueWidget(row2widget)
        row2layout.addWidget(self.msg_queue)
        row2widget.setLayout(row2layout)

        layout.addWidget(row2widget, 1, 0)
        layout.setRowStretch(1, 2)

        # add the command area
        self.command = CommandWidget(
            self,
            data.log_msgs,
            data.loading_msgs)
        layout.addWidget(self.command, 2, 0)
        layout.setRowStretch(2, 1)

        # add the runtime options area
        self.options = OptionsWidget(self, {})
        layout.addWidget(self.options, 3, 0)
        layout.setRowStretch(3, 0)

        # add the message history
        self.msg_history = MessageHistoryWidget(self)
        layout.addWidget(self.msg_history, 4, 0)
        layout.setRowStretch(4, 1)

        self.setGeometry(0, 0, 800, 600)

    def init_ui(self):
        """
        Called by the controller when the UI should be finalised and
        made ready to show
        """
        self._create_menu()
        Logger.info(__name__, 'Wizard window ready')

    def _create_menu(self):
        """
        Create the menu
        """
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu(_('File'))
        wizard_menu = main_menu.addMenu(_('Wizard'))
        output_menu = main_menu.addMenu(_('Output'))

        exit_button = QAction(_('Quit'), self)
        exit_button.setMenuRole(QAction.QuitRole)
        exit_button.setShortcut('Ctrl+Q')
        exit_button.setStatusTip(_('Quit %s' % self.nottreal.appname))
        exit_button.triggered.connect(self.close)
        file_menu.addAction(exit_button)

        next_tab_button = QAction(_('Next tab'), self)
        next_tab_button.setData('next_tab')
        next_tab_button.setShortcut('Meta+Tab')
        next_tab_button.setStatusTip(_('Move to the next tab/category'))
        next_tab_button.triggered.connect(self._on_menu_item_selected)
        wizard_menu.addAction(next_tab_button)

        prev_tab_button = QAction(_('Previous tab'), self)
        prev_tab_button.setData('prev_tab')
        prev_tab_button.setShortcut('Meta+Shift+Tab')
        prev_tab_button.setStatusTip(_('Move to the previous tab/category'))
        prev_tab_button.triggered.connect(self._on_menu_item_selected)
        wizard_menu.addAction(prev_tab_button)

        wizard_menu.addSeparator()

        interrupt_voice_button = QAction(
            _('Interrupt current voice output'),
            self)

        interrupt_voice_button.setData('interrupt_output')
        interrupt_voice_button.setShortcuts(['Meta+C', 'Ctrl+C'])
        interrupt_voice_button.setStatusTip(
            _('Interrupt the current output and optionally clear the queue'))
        interrupt_voice_button.triggered.connect(self._on_menu_item_selected)
        wizard_menu.addAction(interrupt_voice_button)

        first = True
        for output in self.nottreal.view.output.items():
            suffix = output[0]
            name = output[1].get_label()

            show_output_button = QAction(_('Show/hide %s window' % name), self)
            show_output_button.setData('show_output_button_%s' % suffix)
            show_output_button.setStatusTip(
                _('Toggle the visibility of the %s window') % name)
            show_output_button.triggered.connect(self._on_menu_item_selected)
            if first:
                show_output_button.setShortcut('Ctrl+W')
            output_menu.addAction(show_output_button)

            max_output_button = QAction(_('Maximise %s window') % name, self)
            max_output_button.setData('max_output_button_%s' % suffix)
            max_output_button.setStatusTip(
                _('Toggle the maximisation of the %s window') % name)
            max_output_button.triggered.connect(self._on_menu_item_selected)
            if first:
                max_output_button.setShortcut('Ctrl+Shift+F')
                first = False
            output_menu.addAction(max_output_button)

            output_menu.addSeparator()

        resting_orb_button = QAction(_('Trigger resting orb'), self)
        resting_orb_button.setData('resting_orb_button')
        resting_orb_button.setShortcut('Ctrl+R')
        resting_orb_button.setStatusTip(
            _('Show the user that the Wizard is resting'))
        resting_orb_button.triggered.connect(self._on_menu_item_selected)
        output_menu.addAction(resting_orb_button)

        computing_orb_button = QAction(_('Trigger busy orb'), self)
        computing_orb_button.setData('computing_orb_button')
        computing_orb_button.setShortcut('Ctrl+B')
        computing_orb_button.setStatusTip(
            _('Show the user that the Wizard is computing'))
        computing_orb_button.triggered.connect(self._on_menu_item_selected)
        output_menu.addAction(computing_orb_button)

        listening_orb_button = QAction(_('Trigger listening orb'), self)
        listening_orb_button.setData('listening_orb_button')
        listening_orb_button.setShortcut('Ctrl+L')
        listening_orb_button.setStatusTip(
            _('Show the user that the Wizard is listening'))
        listening_orb_button.triggered.connect(self._on_menu_item_selected)
        output_menu.addAction(listening_orb_button)

        output_menu.addSeparator()

    @Slot()
    def _on_menu_item_selected(self):
        data = self.sender().data()
        if data == 'resting_orb_button':
            self.router('output', 'now_resting')
            return
        elif data == 'computing_orb_button':
            self.router('output', 'now_computing')
            return
        elif data == 'listening_orb_button':
            self.router('output', 'now_listening')
            return
        elif data == 'next_tab':
            self.prepared_msgs.adjust_selected_tab(1)
            return
        elif data == 'prev_tab':
            self.prepared_msgs.adjust_selected_tab(-1)
            return
        elif data == 'interrupt_output':
            self.router('wizard', 'stop_speaking')
            return
        else:
            for output in self.nottreal.view.output.items():
                suffix = output[0]

                if data == ('show_output_button_%s' % suffix):
                    self.router('output', 'toggle_show', output=suffix)
                    return
                elif data == ('max_output_button_%s' % suffix):
                    self.router('output', 'toggle_maximise', output=suffix)
                    return

        Logger.critical(__name__, 'Unknown menu item selected')

    def closeEvent(self, event):
        """
        A close event triggered by the user and sent via PySide2

        Arguments:
            event {QCloseEvent} -- Event from PySide2
        """
        self.router('app', 'quit')
        event.accept()


class PreparedMessagesWidget(QTabWidget):
    """
    Tabbed view of prepared messages

    Extends:
        {QTabWidget}

    Variables:
        DOUBLE_CLICK_TIMER {int} -- Two clicks in this many ms is
            a double click
        ID, LABEL, TEXT {int} -- Column IDs for the prepared messages
            list
    """
    DOUBLE_CLICK_TIMER = 450
    ID, LABEL, TEXT = range(3)

    def __init__(self, parent, cats):
        """
        Create the tabs and lists of prepared messages.

        Arguments
            parent {QWidget} -- Parent widget
            cats {dict(str,str)} -- Categories and their messages
        """
        super(PreparedMessagesWidget, self).__init__(parent)

        self.parent = parent

        self.selected_msg = None

        self._cats = cats
        self._msgs_models = OrderedDict()
        self._msgs_widgets = OrderedDict()

        first = True
        for cat_id, cat in cats.items():
            treeview = QTreeView()
            treeview.setRootIsDecorated(False)
            treeview.setAlternatingRowColors(True)

            model = QStandardItemModel(0, 3, self)
            model.setHeaderData(self.ID, Qt.Horizontal, _('ID'))
            model.setHeaderData(self.LABEL, Qt.Horizontal, _('Label'))
            model.setHeaderData(self.TEXT, Qt.Horizontal, _('Text'))

            treeview.clicked.connect(self._on_msg_doubleclick_check)
            treeview.keyReleaseEvent = self._on_msg_key_release

            self._doubleclick_timer = QTimer()
            self._doubleclick_timer.setSingleShot(True)
            self._doubleclick_timer.timeout.connect(self._on_msg_click)

            treeview.setModel(model)
            treeview.setSelectionMode(QAbstractItemView.SingleSelection)
            treeview.setEditTriggers(QAbstractItemView.NoEditTriggers)

            for idx, msg in enumerate(cat['msgs']):
                model.insertRow(idx)
                model.setData(model.index(idx, self.ID), msg['id'])
                model.setData(model.index(idx, self.LABEL), msg['label'])
                model.setData(model.index(idx, self.TEXT), msg['text'])

            treeview.resizeColumnToContents(0)
            treeview.resizeColumnToContents(1)

            widget = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(treeview)
            widget.setLayout(layout)

            self._msgs_models[cat_id] = model
            self._msgs_widgets[cat_id] = treeview
            self.addTab(widget, cat['label'])

        self.currentChanged.connect(self._on_tab_change)
        self.resize(300, 200)

    def selected_tab_label(self):
        """
        Get the label of the currently selected tab

        Returns:
            {str}
        """
        return self.tabText(self.currentIndex())

    def adjust_selected_tab(self, adjustment):
        """
        Change the currently selected tab by the value of {adjustment}

        Arguments:
            adjustment {int} -- A positive or negative integer
        """
        num_tabs = len(self._msgs_widgets)
        curr_tab = self.currentIndex()
        new_tab = (curr_tab+adjustment) % num_tabs

        self.setCurrentIndex(new_tab)

    def _speak_msg(self, msg_id):
        """
        Speak a message with the text from a prepared message.

        Arguments:
            msg_id {str} -- Message ID
        """
        self.selected_msg = msg_id
        msgs = list(self._cats.values())[self.currentIndex()]['msgs']
        msg = next(msg for msg in msgs if msg['id'] == msg_id)

        self.parent.command.speak_text(msg['text'])

    def _fill_msg(self, msg_id):
        """
        Fill the text box with the text from a prepared message.

        Arguments:
            msg_id {str} -- Message ID
        """
        self.selected_msg = msg_id
        msgs = list(self._cats.values())[self.currentIndex()]['msgs']
        msg = next(msg for msg in msgs if msg['id'] == msg_id)

        self.parent.command.set_text(msg['text'])

    def _set_msgs(self, model, msgs):
        """Set the messages for a particular model

        Arguments:
            model {QStandardItemModel} -- Model of prepared messages
            msgs {dict} -- Messages with `id`, `label`, & `text` values
        """
        for idx, msg in enumerate(msgs):
            model.insertRow(idx)
            model.setData(model.index(idx, self.ID), msg['id'])
            model.setData(model.index(idx, self.LABEL), msg['label'])
            model.setData(model.index(idx, self.TEXT), msg['text'])

    def _get_selected_msg(self, treeview):
        """
        Get the ID of the currently selected message in a treeview

        Arguments:
            treeview {QTreeVIew} -- List widget that shows all
                prepared messages

        Returns:
            {str} -- Message ID
        """
        model = treeview.model()

        selected_indicies = treeview.selectionModel().selectedIndexes()
        selected_index = selected_indicies[0]

        index = model.index(
            selected_index.row(),
            self.ID,
            selected_index.parent())

        return model.itemData(index)[0]

    @Slot()
    def _on_tab_change(self):
        """Identify the tab to notify other areas of the application"""
        tab_index = self.currentIndex()
        cat_id = list(self._cats.keys())[tab_index]
        treeview = self._msgs_widgets[cat_id]
        model = treeview.model()

        treeview.setFocus()
        if model.rowCount() > 0:
            selection_model = treeview.selectionModel()
            selection_model.clear()
            selection_model.setCurrentIndex(
                model.index(0, 0),
                QItemSelectionModel.Select | QItemSelectionModel.Rows)

        self.parent.router('wizard', 'tab_changed', new_tab=cat_id)

    @Slot()
    def _on_msg_click(self):
        """
        Slot called when a message is clicked in the list view

        Double clicks are proxied through a timer to prevent the click
        slot and the double click slot firing

        Decorators:
            {Slot}
        """
        try:
            if isinstance(self.sender(), QTimer):
                msg_id = self._get_selected_msg(self._timerProxyFor)
            else:
                msg_id = self._get_selected_msg(self.sender())

            self._fill_msg(msg_id)
        except IndexError:
            Log.error(__name__, 'Message unclicked?')

    @Slot()
    def _on_msg_doubleclick(self):
        """
        Slot called when a message is double clicked in the list view

        Decorators:
            {Slot}
        """
        try:
            msg_id = self._get_selected_msg(self.sender())
            self._speak_msg(msg_id)
        except IndexError:
            Log.warning(__name__, 'Message unclicked?')

    @Slot()
    def _on_msg_doubleclick_check(self):
        """
        Start/check previous timer to see if this is a double click or
        a single click. If the last click was within the doubleclick
        threshold then call the double click function.

        Decorators:
            {Slot}
        """
        if self._doubleclick_timer.isActive():
            self._doubleclick_timer.stop()
            self._on_msg_doubleclick()
        else:
            self._doubleclick_timer.start(self.DOUBLE_CLICK_TIMER)
            self._timerProxyFor = self.sender()

    @Slot()
    def _on_msg_key_release(self, event):
        """
        Handle key releases on the message list, to catch the return
        key being pressed. Enter is the same as clicking, Ctrl+Eenter
        (cmd on a Mac) is the same as double clicking.

        Decorators:
            {Slot}

        Arguments:
            event {KeyEvent} -- Event triggered by the key release
        """
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            tab_index = self._msg_tabs.currentIndex()
            cat_id = list(self._cats.keys())[tab_index]
            treeview = self._msg_widgets[cat_id]
            msg_id = self.selected_msg_id(treeview)
            if (event.modifiers() == Qt.ControlModifier):
                self._speak_msg(msg_id)
            else:
                self._fill_msg(msg_id)
        else:
            event.accept()


class SlotHistoryWidget(QTreeView):
    """
    A list of previously filled slots in a treeview widget

    Extends:
        {QTreeView}

    Variables:
        SLOT_NAME, SLOT_VALUE {int} -- Column IDs for the slot history
    """
    SLOT_NAME, SLOT_VALUE = range(2)

    def __init__(self, parent):
        """Create the list for queued messages

        Arguments
            parent {QWidget} -- Parent widget
        """
        super(SlotHistoryWidget, self).__init__(parent)

        self.parent = parent

        self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)

        self.model = QStandardItemModel(0, 2, self)
        self.model.setHeaderData(
            self.SLOT_NAME,
            Qt.Horizontal,
            _('Slot'))
        self.model.setHeaderData(
            self.SLOT_VALUE,
            Qt.Horizontal,
            _('Previously entered value'))

        self.setModel(self.model)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def add(self, name, value):
        """
        Add an item to the list of used slots

        Arguments:
            name {str} -- Slot name
            value {str} -- User entered value
        """
        self.model.insertRow(0)
        self.model.setData(self.model.index(0, self.SLOT_NAME), name)
        self.model.setData(self.model.index(0, self.SLOT_VALUE), value)


class MessageQueueWidget(QTreeView):
    """
    A list of queued messages in a treeview widget

    Extends:
        QTreeView

    Variables:
        UPCOMING_MESSAGE {int} -- Column ID for the queue
    """
    QUEUED_MESSAGE = 0

    def __init__(self, parent):
        """Create the list for queued messages

        Arguments
            parent {QWidget} -- Parent widget
        """
        super(MessageQueueWidget, self).__init__(parent)

        self.parent = parent

        self._queued_messages = deque()

        self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)

        self.model = QStandardItemModel(0, 1, self)
        self.model.setHeaderData(
            self.QUEUED_MESSAGE,
            Qt.Horizontal,
            _('Queued message'))

        self.setModel(self.model)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def add(self, text):
        """
        Add an item to the top of the model of the message queue

        Arguments:
            text {str} -- Text to add to the queue
        """
        self._queued_messages.append(text)
        idx = len(self._queued_messages) - 1
        self.model.insertRow(idx)
        self.model.setData(self.model.index(idx, self.QUEUED_MESSAGE), text)

    def clear(self):
        """
        Clear the message queue
        """
        self.model.removeRows(0, len(self._queued_messages))
        self._queued_messages.clear()

    def remove(self, text):
        """
        Remove an item from the queued messages.

        Arguments:
            text {str} -- Text to delete from the queue
        """
        try:
            idx = self._queued_messages.index(text)
            self.model.removeRow(idx)
            del self._queued_messages[idx]
        except ValueError:
            pass


class CommandWidget(QGroupBox):
    """
    Primary command area that includes the text box

    Extends:
        {QGroupBox}

    Variables:
        RE_TEXT_SLOT {str} -- Regex matching slots in text
        RE_TEXT_SLOT_REPL {str} -- Symbol that denotes this
            slot value can auto changed to the previously used value
            (if it exists)
        RE_TEXT_SLOT_REPL {str} -- Symbol that denotes this
            slot's value tracking should be stopped
    """
    RE_TEXT_SLOT = '\[([\w /\*\$|]*)\]'
    RE_TEXT_SLOT_REPL = '*'
    RE_TEXT_SLOT_ENDREPL = '$'

    def __init__(self, parent, log_msgs, loading_msgs):
        """
        Create the area to type text and submit it to the voice
        subsystem

        Arguments
            parent {QWidget} -- Parent widget
            log_msgs {dict} -- Configured log messages
            loading_msgs {dict} -- Configured loading messages
        """
        super(CommandWidget, self).__init__(parent)

        self.parent = parent

        self._reset_slot_tracking()
        self.clear_saved_slots()

        self.setContentsMargins(0, 5, 0, 0)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.setLayout(layout)

        # text area
        self._text_speak = QPlainTextEdit()
        self._on_text_key_press_input = self._text_speak.keyPressEvent
        self._text_speak.keyPressEvent = self._on_text_key_press
        layout.addWidget(self._text_speak)

        # button bar
        buttonBar = QGroupBox()
        buttonBar.setContentsMargins(0, 5, 0, 0)
        buttonBarLayout = QHBoxLayout()
        buttonBar.setLayout(buttonBarLayout)

        # options for log mesages
        if not self.parent.args.output_dir is None:
            self._combo_log_messages = QComboBox()
            self._combo_log_messages.currentIndexChanged.connect(
                self._on_log_message)
            self._combo_log_messages.setPlaceholderText(_('Log an event'))

            for key, value in log_msgs.items():
                self._combo_log_messages.addItem(
                    value['message'],
                    value['id'])

            buttonBarLayout.addWidget(self._combo_log_messages)

        # options for loading messages
        self._combo_loading_messages = QComboBox()
        self._combo_loading_messages.currentIndexChanged.connect(
            self._on_loading_message)
        self._combo_loading_messages.setPlaceholderText(
            _('Send a loading message...'))
        for key, value in loading_msgs.items():
            self._combo_loading_messages.addItem(value['message'])

        buttonBarLayout.addWidget(self._combo_loading_messages)

        # clear and speak buttons
        self._button_clear = QPushButton(_('Clear'))
        self._button_clear.clicked.connect(self._on_clear)

        self._button_speak = QPushButton(_('Speak'))
        self._button_speak.clicked.connect(self._on_speak)
        self._button_speak.setDefault(True)
        self._button_speak.setAutoDefault(True)

        buttonBox = QDialogButtonBox()
        buttonBox.addButton(self._button_clear, QDialogButtonBox.HelpRole)
        buttonBox.addButton(self._button_speak, QDialogButtonBox.HelpRole)
        buttonBarLayout.addWidget(buttonBox)

        layout.addWidget(buttonBar)

    def set_text(self, text):
        """
        Set the message text

        Arguments:
            text {str} -- Text to set
        """
        self._text_speak.setPlainText(text)
        self._text_speak.setFocus()
        self._select_msg_slot(from_start=True)

    def speak_text(self, text, loading=False):
        """
        Send text to the voice subsystem. if it contains slots, then
        the first slot is selected and the text will not be sent. When
        sent the textbox is cleared.

        Arguments:
            text {str} -- Text to speak
            loading {bool} -- Is a loading message (default: False)
        """
        text = text.strip()
        if len(text) > 0:
            requires_editing = False
            min_match_idx = 0

            matches = re.finditer(self.RE_TEXT_SLOT, text)
            for match in matches:
                start = match.start(0)
                end = match.end(0)

                autoreplace = \
                    match.group(0)[1:-1].endswith(self.RE_TEXT_SLOT_REPL)
                autoreplace_end = \
                    match.group(0)[1:-1].endswith(self.RE_TEXT_SLOT_ENDREPL)
                name = match.group(0)[1:-1].replace(self.RE_TEXT_SLOT_REPL, '')
                name = name.replace(self.RE_TEXT_SLOT_ENDREPL, '')

                if (autoreplace or autoreplace_end) and \
                        name in self._saved_slots:
                    value = self._saved_slots[name]
                    Logger.debug(
                        __name__,
                        'Replacing slot "%s" with value "%s"' % (name, value))
                    text = text.replace(match.group(0), value)

                    if autoreplace_end:
                        del self._saved_slots[name]
                else:
                    requires_editing = True

            if requires_editing:
                Logger.debug(
                    __name__,
                    'Message has slots that aren\'t filled ("%s")' % name)
                self.set_text(text)
            else:
                self._record_last_msg_slot()
                self.parent.router(
                    'wizard',
                    'speak_text',
                    text=text,
                    cat=self.parent.prepared_msgs.selected_tab_label(),
                    id=self.parent.prepared_msgs.selected_msg,
                    slots=self._current_slots,
                    loading=loading)
                self._reset_slot_tracking()
                self._text_speak.setPlainText('')

    def clear_saved_slots(self):
        """
        Clear saved slots
        """
        self._saved_slots = {}

    def _reset_slot_tracking(self):
        """
        Reset the tracking of text slots.
        """
        self._current_slots = {}
        self._cache_slot_autoreplace = False
        self._cache_slot_autoreplace_end = False
        self._cache_slot_name = None
        self._cache_slot_before = None
        self._cache_slot_after = None

    def _record_last_msg_slot(self):
        """
        Called once all the message slots have been selected, and at
        the selection of every message slot.

        Saves the previously entered message slot.
        """
        text = self._text_speak.toPlainText()
        if self._cache_slot_name is not None and \
                text.startswith(self._cache_slot_before):
            slot_value = text[len(self._cache_slot_before):]
            slot_value = slot_value[:-len(self._cache_slot_after)]
            try:
                if slot_value[0] != '[':
                    self._current_slots[self._cache_slot_name] = slot_value
                    if self._cache_slot_autoreplace_end:
                        try:
                            del self._saved_slots[self._cache_slot_name]
                        except KeyError:
                            pass
                        self._cache_slot_autoreplace = False
                    elif self._cache_slot_autoreplace:
                        self._saved_slots[self._cache_slot_name] = slot_value
            except IndexError:
                pass

    def _select_msg_slot(
            self,
            from_start=False,
            reverse=False,
            loop=True):
        """
        Select the next slot in the prepared message. Slots are
        encoded as text between square brackets, [like] so.

        If there are no more slots, then the cursor/selection remain
        unchanged.

        Arguments:
            from_start {bool} -- Seek from start of input (True) or
                the current position ({False}). If {reverse} is
                true, will start from the end (Default: {False})
            reverse {bool} -- Select the previous item
            loop {bool} -- If at the end, loop back to the start

        Returns:
            {bool} -- {True} if slot selected, {False} if none exists
        """
        text = self._text_speak.toPlainText()
        current_pos = self._text_speak.textCursor().position()

        self._record_last_msg_slot()

        if reverse:
            if from_start:
                current_pos = len(text)
                Logger.debug(
                    __name__,
                    'Seek to previous sloteter in the message from the end')
            else:
                current_pos -= 1
                Logger.debug(
                    __name__,
                    'Seek to previous sloteter in the message from pos %d'
                    % current_pos)

            for match in re.finditer(self.RE_TEXT_SLOT, text[:current_pos]):
                pass

            # reverse doesn't need this offset
            current_pos = 0
        else:
            if from_start:
                current_pos = 0

            match = re.search(self.RE_TEXT_SLOT, text[current_pos:])

        try:
            if match:
                start = match.start(0)
                end = match.end(0)

                self._cache_slot_autoreplace = \
                    match.group(0)[1:-1].endswith(self.RE_TEXT_SLOT_REPL)
                self._cache_slot_autoreplace_end = \
                    match.group(0)[1:-1].endswith(self.RE_TEXT_SLOT_ENDREPL)

                self._cache_slot_name = \
                    match.group(0)[1:-1].replace(self.RE_TEXT_SLOT_REPL, '')
                self._cache_slot_before = text[0:start+current_pos]

                if self._cache_slot_autoreplace_end:
                    self._cache_slot_name = \
                        match.group(0)[1:-1].replace(
                            self.RE_TEXT_SLOT_ENDREPL,
                            '')
                    self._cache_slot_autoreplace = True

                after_pos = (
                    start
                    + current_pos
                    + len(self._cache_slot_name)
                    + 2)

                if (self._cache_slot_autoreplace
                        or self._cache_slot_autoreplace_end):
                    after_pos += 1

                self._cache_slot_after = text[after_pos:]

                self._text_speak.moveCursor(QTextCursor.Start)

                for charn in range(0, start+current_pos):
                    self._text_speak.moveCursor(QTextCursor.NextCharacter)

                for charn in range(0, end-start):
                    self._text_speak.moveCursor(
                        QTextCursor.NextCharacter,
                        mode=QTextCursor.KeepAnchor)

                return True
            elif loop:
                # only hit here if moving forward and at the end
                self._select_msg_slot(from_start=True, loop=False)
                return True
            else:
                return False
        except UnboundLocalError:
            # we'll get here if moving backward and at the start
            if loop:
                self._select_msg_slot(
                    from_start=True,
                    reverse=True,
                    loop=False)
            else:
                return False

    @Slot()
    def _on_text_key_press(self, event):
        """
        Respond to key presses on the text box. This function replaces
        the default key press method (which is moved to
        {_on_text_key_press_input()}). This will swallow returns and
        tabs presses.

        Tab/enter moves between slots (i.e. next in [square] brackets
        in the prepared message), with the shift modifier returning
        the direction of travel.

        Ctrl+enter (cmd on a Mac) presses the 'Speak' button.

        Decorators:
            Slot

        Arguments:
            event {QKeyEvent} -- Event triggered by the key press
        """
        all_highlighted = \
            self._text_speak.toPlainText() == \
            self._text_speak.textCursor().selectedText()

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if (event.modifiers() == Qt.ControlModifier):
                self._on_speak()
            elif (event.modifiers() == Qt.ShiftModifier):
                self._select_msg_slot(reverse=True)
            elif self._select_msg_slot():
                self._on_speak()
        elif (event.key() == Qt.Key_C
                and (event.modifiers() == Qt.ControlModifier
                     or event.modifiers() == Qt.MetaModifier)):
            self.router('wizard', 'stop_speaking')
        elif event.key() == Qt.Key_Tab:
            self._select_msg_slot()
        elif event.key() == Qt.Key_Backtab:
            self._select_msg_slot(reverse=True)
        elif all_highlighted:
            self.parent.prepared_msgs.selected_msg = None
            self._on_text_key_press_input(event)
        else:
            self._on_text_key_press_input(event)

    @Slot(int)
    def _on_log_message(self, num):
        """
        Log an event

        Arguments:
            num {int} -- Selected item

        Decorators:
            Slot
        """
        if num > -1:
            id = self._combo_log_messages.currentData()
            text = self._combo_log_messages.currentText()
            self.parent.router('wizard', 'log_message', id=id, text=text)
            self._combo_log_messages.setCurrentIndex(-1)

    @Slot(int)
    def _on_loading_message(self, num):
        """
        Loading message selected, send it as if it was spoken

        Arguments:
            num {int} -- Selected item

        Decorators:
            Slot
        """
        if num > -1:
            text = self._combo_loading_messages.currentText()
            self.speak_text(text, loading=True)
            self._combo_loading_messages.setCurrentIndex(-1)

    @Slot()
    def _on_clear(self):
        """
        Clear button pressed -- just remove the text from the text box

        Decorators:
            Slot
        """
        self._reset_slot_tracking()
        self.parent.prepared_msgs.selected_msg = None
        self._text_speak.setPlainText('')

    @Slot()
    def _on_speak(self):
        """
        Speak button pressed, so speak the text if there are no
        slots in it

        Decorators:
            Slot
        """
        text = self._text_speak.toPlainText()
        self.speak_text(text)


class OptionsWidget(QGroupBox):
    """
    Runtime options

    Extends:
        {QGroupBox}

    Variables:
        OPTIONS_COLUMNS {int} -- Number of columns of options
    """
    OPTIONS_COLUMNS = 2

    def __init__(self, parent, options={}):
        """
        Create the area for runtime Wizard options

        Arguments
            parent {QWidget} -- Parent widget
            options {dict} -- Runtime options
        """
        super(OptionsWidget, self).__init__(parent)

        self.parent = parent

        self.setContentsMargins(10, 5, 0, 0)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self._options = {}
        for label, option in options.items():
            self.add(option)

    def add(self, option):
        """
        Add wizard option to the manager window

        Arguments:
            option {models.nottreal.WizardOption} -- A wizard option
        """
        if option.opt_type is WizardOption.CHECKBOX:
            ui_control = QCheckBox(option.label, self)
            ui_control.setCheckState(
                Qt.Checked
                if option.value
                else Qt.Unchecked)
            ui_control.stateChanged.connect(self._option_changed)
        elif option.opt_type is WizardOption.DROPDOWN:
            ui_control = QComboBox()
            ui_control.currentIndexChanged.connect(self._option_changed)
            ui_control.setPlaceholderText(option.label)
            for key, value in option.values.items():
                ui_control.addItem(value, key)
        else:
            Logger.error(
                __name__,
                'Unknown Wizard option type for option "%s"' % option.label)
            return

        if option.label not in self._options:
            row = len(self._options) // self.OPTIONS_COLUMNS
            col = len(self._options) % self.OPTIONS_COLUMNS
        else:
            row = self._options[option.label].ui_row
            col = self._options[option.label].ui_col

        self.layout.addWidget(ui_control, row, col)
        self._options[option.label] = option
        option.ui = ui_control
        option.ui_row = row
        option.ui_col = col
        option.added = True

    @Slot()
    def _option_changed(self, value=None):
        """
        Slot when an option is changed

        Arguments:
            value {mixed} -- Value sent by the option
        """
        sender = type(self.sender()).__name__
        if sender == 'QCheckBox':
            label = self.sender().text()
            try:
                checkbox = self._options[label].ui
                state = True if checkbox.checkState() == Qt.Checked else False
                self._options[label].method(state)
            except KeyError:
                Logger.error(
                    __name__,
                    'Could not find registered option with label "%s"' % label)
                pass
        elif sender == 'QComboBox':
            label = self.sender().placeholderText()
            try:
                dropdown = self._options[label].ui
                if dropdown.currentIndex() > -1:
                    id = dropdown.currentData()
                    dropdown.setCurrentIndex(-1)
                    self._options[label].method(id)
            except KeyError:
                Logger.error(
                    __name__,
                    'Could not find registered option with label "%s"' % label)
                pass

        else:
            Logger.error(
                __name__,
                'Unknown Wizard option value set by a "%s"' % sender)


class MessageHistoryWidget(QGroupBox):
    """
    A list of previously sent messages in a treeview widget inside a groupbox

    Extends:
        QGroupBox

    Variables:
        SPOKEN_MESSAGE {int} -- Column ID for the sent message
    """
    SPOKEN_MESSAGE = 0

    def __init__(self, parent):
        """
        Create the list for sent messages

        Arguments
            parent {QWidget} -- Parent widget
        """
        super(MessageHistoryWidget, self).__init__(parent)

        self.parent = parent

        self.setContentsMargins(0, 5, 0, 0)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self._widget = QTreeView(self)
        self._widget.setRootIsDecorated(False)
        self._widget.setAlternatingRowColors(True)

        self.model = QStandardItemModel(0, 1, self)
        self.model.setHeaderData(
            self.SPOKEN_MESSAGE,
            Qt.Horizontal,
            _('Previously spoken message'))

        self._widget.setModel(self.model)
        self._widget.setSelectionMode(QAbstractItemView.NoSelection)
        self._widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.layout.addWidget(self._widget)

    def add(self, text):
        """
        Add an item to the top of the model of history of spoken messages

        Arguments:
            text {str} -- Text to add to the queue
        """
        self.model.insertRow(0)
        self.model.setData(self.model.index(0, self.SPOKEN_MESSAGE), text)
