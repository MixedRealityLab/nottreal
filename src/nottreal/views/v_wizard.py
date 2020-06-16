
from ..utils.log import Logger
from ..models.m_mvc import VUIState, WizardOption

from collections import OrderedDict, deque
from PySide2.QtWidgets import (QAbstractItemView, QAction, QComboBox,
                               QDialogButtonBox, QGridLayout, QGroupBox,
                               QHBoxLayout, QMainWindow, QPlainTextEdit,
                               QPushButton, QVBoxLayout, QTabWidget, QMenuBar,
                               QMenu, QTreeView, QWidget)
from PySide2.QtGui import (QTextCursor, QStandardItemModel)
from PySide2.QtCore import (Qt, QItemSelectionModel, QTimer,
                            Slot)

import re
import sys


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
        self.router = nottreal.router

        super(WizardWindow, self).__init__()
        self.setWindowTitle(nottreal.appname)

        Logger.debug(__name__, 'Initialising the Wizard window widgets')

        self.menu = MenuBar(self)

        self.recognised_words = RecognisedWordsWidget(self)
        self.prepared_msgs = PreparedMessagesWidget(self, data.cats)
        self.slot_history = SlotHistoryWidget(self)
        self.msg_queue = MessageQueueWidget(self)
        self.command = CommandWidget(
            self,
            data.log_msgs,
            data.loading_msgs)
        self.msg_history = MessageHistoryWidget(self)

    def init_ui(self):
        """
        Called by the controller when the UI should be finalised and
        made ready to show
        """
        self.menu.init_ui()

        self.layout = QGridLayout()
        self.layout.setVerticalSpacing(0)

        window_main = QWidget()
        window_main.setLayout(self.layout)
        self.setCentralWidget(window_main)

        self.recognised_words.hide()
        self.layout.addWidget(self.prepared_msgs, 0, 0, 1, 2)
    
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 3)

        row2widget = QGroupBox()
        row2widget.setContentsMargins(0, 5, 0, 0)

        row2layout = QHBoxLayout()

        row2layout.addWidget(self.slot_history)
        row2layout.addWidget(self.msg_queue)

        row2widget.setLayout(row2layout)

        self.layout.addWidget(row2widget, 1, 0, 1, 2)
        self.layout.addWidget(self.command, 2, 0, 1, 2)
        self.layout.addWidget(self.msg_history, 3, 0, 1, 2)

        self.layout.setRowStretch(0, 3)
        self.layout.setRowStretch(1, 2)
        self.layout.setRowStretch(2, 1)
        self.layout.setRowStretch(3, 1)

        self.setGeometry(0, 0, 800, 600)

        Logger.info(__name__, 'Wizard window ready')    
        
    def toggle_recogniser(self):
        """
        Toggle the visibility of the recogniser
        """
        if self.recognised_words.isVisible():
            self.recognised_words.hide()
            self.layout.removeWidget(self.recognised_words)
            self.layout.addWidget(self.prepared_msgs, 0, 0, 1, 2)
        else:
            self.layout.addWidget(self.recognised_words, 0, 0)
            self.layout.addWidget(self.prepared_msgs, 0, 1)
            self.recognised_words.show()


class MenuBar(QMenuBar):
    """
    Create and manage the menu bar for the application

    Variables:
        MENU_FILE {int} -- Key for the File menu
        MENU_WIZARD {int} -- Key for the Wizard menu
        MENU_INPUT {int} -- Key for the Input menu
        MENU_OUTPUT {int} -- Key for the Output menu
    """
    MENU_FILE, MENU_WIZARD, MENU_INPUT, MENU_OUTPUT = range(4)

    def __init__(self, parent):
        """
        Create the menu

        Arguments:
            parent {QWidget} -- Parent widget
        """
        super(MenuBar, self).__init__()

        self.parent = parent
        self._options = {}

        self._generated_menu = False

        self.MENUS = {
            self.MENU_FILE: 'File',
            self.MENU_WIZARD: 'Wizard',
            self.MENU_INPUT: 'Input',
            self.MENU_OUTPUT: 'Output'
        }

        self._menu_functions = {
            self.MENU_FILE: self._create_file_menu,
            self.MENU_WIZARD: self._create_wizard_menu,
            self.MENU_INPUT: self._create_input_menu,
            self.MENU_OUTPUT: self._create_output_menu
        }

        self._instantiated_menus = {}

        self.option_category_to_menu = {
            WizardOption.CAT_WIZARD: self.MENU_WIZARD,
            WizardOption.CAT_INPUT: self.MENU_INPUT,
            WizardOption.CAT_OUTPUT: self.MENU_OUTPUT
        }

        self.menu_to_option_category = \
            {v: k for k, v in self.option_category_to_menu.items()}

    def init_ui(self):
        """
        Initialise and generate the menus
        """
        self._generate_menu(self.MENU_FILE)
        self._generate_menu(self.MENU_WIZARD)
        self._generate_menu(self.MENU_INPUT)
        self._generate_menu(self.MENU_OUTPUT)

        self._generated_menu = True

    def add_option(self, option):
        """
        Add an option to the Wizard interface

        Arguments:
            option {WizardOption} -- Constructed option object
        """
        try:
            self._options[option.opt_cat].append(option)
        except KeyError:
            self._options[option.opt_cat] = []
            return self.add_option(option)

        if self._generated_menu:
            try:
                self._generate_menu(
                    self.option_category_to_menu[option.opt_cat])
            except KeyError:
                pass

    def remove_option(self, label, opt_cat):
        """
        Remove an option from the Wizard interface

        Arguments:
            label {str} -- Label of the option
            opt_cat {int} -- Option category
        """
        try:
            cat_options = self._options[opt_cat]

            option = [idx
                      for idx, c
                      in enumerate(cat_options)
                      if c.label == label][0]

            del self._options[opt_cat][option]
        except KeyError:
            return
        except IndexError:
            return

        if self._generated_menu:
            try:
                self._generate_menu(
                    self.option_category_to_menu[opt_cat])
            except KeyError:
                pass

    def _generate_menu(self, menu):
        """
        (Re)generate a menu

        Arguments:
            menu {int} -- Menu ID to create (see {self.MENUS})
        """
        try:
            function = self._menu_functions[menu]
        except KeyError:
            tb = sys.exc_info()[2]
            raise KeyError(
                'No menu found with id "%d"' % menu).with_traceback(tb)

        try:
            opt_cat = self.menu_to_option_category[menu]
        except KeyError:
            opt_cat = None

        try:
            menu_object = self._instantiated_menus[menu]
        except KeyError:
            menu_object = self.addMenu(self.MENUS[menu])
            self._instantiated_menus[menu] = menu_object

        function(menu_object, self._options, opt_cat)

    def _create_file_menu(self, menu, options, category):
        """
        Create the File menu

        Arguments:
            menu {QMenu} -- Qt menu to populate
            options {dict} -- {WizardOption}s by cat:[{WizardOption}]
            category {int} -- Category of options to select
        """
        menu.clear()

        self._add_action_to_menu(
            menu,
            text='Quit',
            role=QAction.QuitRole,
            shortcut='Ctrl+Q',
            tooltip='Quit ' + self.parent.nottreal.appname,
            callback=self.close)

    def _create_wizard_menu(self, menu, options, category):
        """
        Create the Wizard menu

        Arguments:
            menu {QMenu} -- Qt menu to populate
            options {dict} -- {WizardOption}s by cat:[{WizardOption}]
            category {int} -- Category of options to select
        """
        menu.clear()

        added = self._add_action_to_menu(
            menu,
            text='Next tab',
            data='next_tab',
            shortcut='Meta+Tab',
            tooltip='Move to the next tab',
            callback=self._on_menu_item_selected)

        self._add_action_to_menu(
            menu,
            text='Previous tab',
            data='prev_tab',
            shortcut='Meta+Shift+Tab',
            tooltip='Move to the next tab',
            callback=self._on_menu_item_selected)

        if added:
            menu.addSeparator()

        self._add_action_to_menu(
            menu,
            text='Interrupt output',
            data='interrupt_output',
            shortcut=['Meta+C', 'Ctrl+C'],
            tooltip='Interrupt the current output',
            callback=self._on_menu_item_selected)

        if added:
            menu.addSeparator()

        self._add_options_to_menu(menu, options, category)

    def _create_input_menu(self, menu, options, category):
        """
        Create the Input menu

        Arguments:
            menu {QMenu} -- Qt menu to populate
            options {dict} -- {WizardOption}s by cat:[{WizardOption}]
            category {int} -- Category of options to select
        """
        menu.clear()

        self._add_options_to_menu(menu, options, category)

    def _create_output_menu(self, menu, options, category):
        """
        Create the Output menu

        Arguments:
            menu {QMenu} -- Qt menu to populate
            options {dict} -- {WizardOption}s by cat:[{WizardOption}]
            category {int} -- Category of options to select
        """
        menu.clear()

        first = True
        for output in self.parent.nottreal.view.output.items():
            suffix = output[0]
            name = output[1].get_label()

            if first:
                shortcut = 'Ctrl+W'
            else:
                shortcut = None

            added = self._add_action_to_menu(
                menu,
                text='Show/hide %s window' % name,
                data='show_output_button_' + suffix,
                shortcut=shortcut,
                tooltip='Toggle the visibility of the %s window' % name,
                callback=self._on_menu_item_selected)

            if first:
                shortcut = 'Ctrl+Shift+F'
            else:
                shortcut = None

            self._add_action_to_menu(
                menu,
                text='Fullscreen/window %s' % name,
                data='max_output_button_' + suffix,
                shortcut=shortcut,
                tooltip='Toggle the maximisation of the %s window' % name,
                callback=self._on_menu_item_selected)

            if added:
                menu.addSeparator()

        added = self._add_action_to_menu(
            menu,
            text='Trigger resting orb',
            data='trigger_orb_resting',
            shortcut='Ctrl+R',
            tooltip='Show the user that the VUI is resting',
            callback=self._on_menu_item_selected)

        self._add_action_to_menu(
            menu,
            text='Trigger busy orb',
            data='trigger_orb_busy',
            shortcut='Ctrl+B',
            tooltip='Show the user that the VUI is busy',
            callback=self._on_menu_item_selected)

        self._add_action_to_menu(
            menu,
            text='Trigger listening orb',
            data='trigger_orb_listening',
            shortcut='Ctrl+L',
            tooltip='Show the user that the VUI is listening',
            callback=self._on_menu_item_selected)

        if added:
            menu.addSeparator()

        self._add_options_to_menu(menu, options, category)

    def _add_action_to_menu(
            self,
            menu,
            text,
            role=None,
            data=None,
            checkable=False,
            value=False,
            shortcut=None,
            tooltip=None,
            callback=None):
        """
        Add an action to a menu if it doesn't exist in the menu
        (only checks based on {text})

        Arguments:
            menu {QMenu} -- Menu to append action to
            text {str} -- Text of the item

        Keyword Arguments:
            role {int} -- {QAction} role to be set
            data {str} -- Data to be set
            checkable {bool} -- Whether this is a checkable item
            value {bool} -- Default value of a checkable item
            shortcut {str/[str]} -- Keyboard shortcut(s)
            tooltip {str} -- Tooltip
            callback {func} -- Function callback

        Returns:
            {QAction} if item now added or {False}
        """
        actions = menu.actions()
        for action in iter(actions):
            if action.text() == text:
                return False

        action = QAction(text, self)

        if role is not None:
            action.setMenuRole(role)

        if data is not None:
            action.setData(data)

        if checkable is not None:
            action.setCheckable(checkable)
            action.setChecked(value)

        if type(shortcut) is list:
            action.setShortcuts(shortcut)
        elif type(shortcut) is str:
            action.setShortcut(shortcut)

        if tooltip is not None:
            action.setToolTip(tooltip)

        if callback is not None:
            action.triggered.connect(callback)

        menu.addAction(action)
        return action

    def _add_options_to_menu(self, menu, all_options, category):
        """
        Append a set of options to a menu
        """
        try:
            unsorted_options = all_options[category]
        except KeyError:
            return

        options = sorted(
            unsorted_options,
            key=lambda option: str(option.group) + ":" + str(option.order))

        current_group = options[0].group

        for idx, option in enumerate(options):
            if current_group is not option.group:
                menu.addSeparator()
                current_group = option.group

            if option.opt_type == WizardOption.CHECKBOX:
                action = self._add_action_to_menu(
                    menu,
                    option.label,
                    data=str(category),
                    checkable=True,
                    value=option.default,
                    callback=self._on_option_checkbox_toggled)

                option.ui = action

            elif option.opt_type == WizardOption.SINGLE_CHOICE:
                actions = menu.actions()
                for action in iter(actions):
                    if action.text() == option.label:
                        return False

                submenu = QMenu(option.label)

                ui_elements = {'root': submenu, 'actions': []}
                for key, value in option.values.items():
                    ui_elements['actions'].append(self._add_action_to_menu(
                        submenu,
                        value,
                        data=(str(category)
                              + ':'
                              + option.label
                              + ":"
                              + str(key)),
                        checkable=True,
                        value=True if key == option.default else False,
                        callback=self._on_option_single_choice_toggled))

                option.ui = ui_elements
                menu.addMenu(submenu)

    @Slot(bool)
    def _on_option_checkbox_toggled(self, checked):
        text = self.sender().text()
        category = self.sender().data()

        try:
            cat_options = self._options[int(category)]
        except KeyError:
            tb = sys.exc_info()[2]
            raise KeyError(
                'Unknown option category: "%s"' % category).with_traceback(tb)

        try:
            option = [o for o in iter(cat_options) if o.label == text][0]
        except IndexError:
            tb = sys.exc_info()[2]
            raise KeyError(
                'Unknown option: "%s"' % text).with_traceback(tb)

        option.method(checked)

    @Slot(bool)
    def _on_option_single_choice_toggled(self, checked):
        text = self.sender().text()
        data = self.sender().data()
        category = data.split(':')[0]
        label = data.split(':')[1]
        value_key = data.split(':')[2]

        try:
            cat_options = self._options[int(category)]
        except KeyError:
            tb = sys.exc_info()[2]
            raise KeyError(
                'Unknown option category: "%s"' % category).with_traceback(tb)

        try:
            option = [o for o in iter(cat_options) if o.label == label][0]
        except IndexError:
            tb = sys.exc_info()[2]
            raise KeyError(
                'Unknown option: "%s"' % label).with_traceback(tb)

        action = [a
                  for a in option.ui['actions']
                  if isinstance(a, QAction) and a.text() == text][0]
        action.setChecked(True)

        option.default = value_key

        if not checked:
            return False
        else:
            actions = [a for a in option.ui['actions'] if a.text() != text]
            for action in iter(actions):
                action.setChecked(False)

        choices = option.values
        choice = [c_id
                  for c_id, c_label
                  in choices.items()
                  if c_label == text][0]

        option.method(choice)

    @Slot()
    def _on_menu_item_selected(self):
        data = self.sender().data()
        if data == 'trigger_orb_resting':
            self.parent.router(
                'wizard',
                'change_state',
                state=VUIState.RESTING)
            return
        elif data == 'trigger_orb_busy':
            self.parent.router(
                'wizard',
                'change_state',
                state=VUIState.BUSY)
            return
        elif data == 'trigger_orb_listening':
            self.parent.router(
                'wizard',
                'change_state',
                state=VUIState.LISTENING)
            return
        elif data == 'next_tab':
            self.parent.prepared_msgs.adjust_selected_tab(1)
            return
        elif data == 'prev_tab':
            self.parent.prepared_msgs.adjust_selected_tab(-1)
            return
        elif data == 'interrupt_output':
            self.parent.router('wizard', 'stop_speaking')
            return
        else:
            for output in self.parent.nottreal.view.output.items():
                suffix = output[0]

                if data == ('show_output_button_%s' % suffix):
                    self.parent.router(
                        'output',
                        'toggle_show',
                        output=suffix)
                    return
                elif data == ('max_output_button_%s' % suffix):
                    self.parent.router(
                        'output',
                        'toggle_maximise',
                        output=suffix)
                    return

        Logger.critical(__name__, 'Unknown menu item selected')

    def closeEvent(self, event):
        """
        A close event triggered by the user and sent via PySide2

        Arguments:
            event {QCloseEvent} -- Event from PySide2
        """
        self.parent.router('app', 'quit')
        event.accept()


class RecognisedWordsWidget(QTreeView):
    """
    A list of previously recognised words

    Extends:
        QGroupBox

    Variables:
        RECOGNISED_WORDS {int} -- Column ID for the some words
    """
    RECOGNISED_WORDS = 0

    def __init__(self, parent):
        """
        Create the list for recognised words

        Arguments
            parent {QWidget} -- Parent widget
        """
        super(RecognisedWordsWidget, self).__init__(parent)

        self.parent = parent

        self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)

        self.model = QStandardItemModel(0, 1, self)
        self.model.setHeaderData(
            self.RECOGNISED_WORDS,
            Qt.Horizontal,
            'Recognised words')

        self.setModel(self.model)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def add(self, text):
        """
        Add an item to the top of the model of recognised words
        Arguments:
            text {str} -- Text to add to the queue
        """
        self.model.insertRow(0)
        self.model.setData(self.model.index(0, self.RECOGNISED_WORDS), text)


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

        for cat_id, cat in cats.items():
            treeview = QTreeView()
            treeview.setRootIsDecorated(False)
            treeview.setAlternatingRowColors(True)

            model = QStandardItemModel(0, 3, self)
            model.setHeaderData(self.ID, Qt.Horizontal, 'ID')
            model.setHeaderData(self.LABEL, Qt.Horizontal, 'Label')
            model.setHeaderData(self.TEXT, Qt.Horizontal, 'Text')

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
            Logger.error(__name__, 'Message unclicked?')

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
            Logger.warning(__name__, 'Message unclicked?')

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
            'Slot')
        self.model.setHeaderData(
            self.SLOT_VALUE,
            Qt.Horizontal,
            'Previously entered value')

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
            'Queued message')

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
    RE_TEXT_SLOT = r'\[([\w /\*\$|]*)\]'
    RE_TEXT_SLOT_REPL = r'*'
    RE_TEXT_SLOT_ENDREPL = r'$'

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
        if self.parent.args.output_dir is not None:
            self._combo_log_messages = QComboBox()
            self._combo_log_messages.currentIndexChanged.connect(
                self._on_log_message)
            self._combo_log_messages.setPlaceholderText('Log an event')

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
            'Send a loading message...')
        for key, value in loading_msgs.items():
            self._combo_loading_messages.addItem(value['message'])

        buttonBarLayout.addWidget(self._combo_loading_messages)

        # clear and speak buttons
        self._button_clear = QPushButton('Clear')
        self._button_clear.clicked.connect(self._on_clear)

        self._button_speak = QPushButton('Speak')
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

            matches = re.finditer(self.RE_TEXT_SLOT, text)
            for match in matches:
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
            'Previously spoken message')

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
