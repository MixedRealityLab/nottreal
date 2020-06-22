

class Message:
    """
    A queued message to send to the user.

    Variables:
        NO_OVERRIDE {int} -- Type to let the user fully control
                             appending
        FORCE_APPEND {int} -- Type to force append a message
        FORCE_DONT_APPEND {int} -- Type to force no appending of
                                   messages
    """
    NO_OVERRIDE, FORCE_APPEND, FORCE_DONT_APPEND = range(0, 3)

    def __init__(self,
                 text,
                 override=NO_OVERRIDE,
                 cat=None,
                 id=None,
                 slots=None,
                 loading=False):
        """
        Create a message queue item.

        Arguments:
            text {[type]} -- [description]

        Keyword Arguments:
            override {int} -- Override the append option for this
                              message (default: {Message.NO_OVERRIDE})
            cat {str/int} -- Category ID if a prepared message
                            (default: {None})
            id {str/int} -- Prepared message ID if a prepared
                            message (default: {None})
            slots {dict(str,str)} -- Slots changed by the user
            loading {bool} -- Is a Loading message (default: {False})
        """
        self.text = text
        self.override = override
        self.cat = cat
        self.id = id
        self.slots = slots
        self.loading = loading

    def __str__(self):
        return '<[Message] %s.%s: %s>' % (self.cat, self.id, self.text)

    def __repr__(self):
        return '<[Message] %s.%s: %s>' % (self.cat, self.id, self.text)


class VUIState:
    """
    State of the Wizarded VUI.

    Extends:
        AbstractController

    Variables:
        RESTING, SPEAKING, LISTENING, BUSY {int} -- States of the VUI

    """
    RESTING, SPEAKING, LISTENING, BUSY = range(0, 4)

    LABELS = {
        RESTING: 'resting',
        SPEAKING: 'speaking',
        LISTENING: 'listening',
        BUSY: 'busy'
    }

    @staticmethod
    def str(state):
        """
        Get the state as a string

        Arguments:
            state {int} -- State as an integer

        Returns:
            {str}
        """
        return VUIState.LABELS[state]


class WizardAlert:
    """
    Show an alert to the Wizard. This is a wrapper for the Qt5
    {QMessageBox}. We reimplement it here so NottReal can mostly
    remain ambiguous to UI implementations.

    Variables:
        LEVEL_ERROR -- An error occurred
        LEVEL_WARN -- An error occurred that is not that problematic
        LEVEL_INFO -- Something the Wizard should be aware of
        LEVEL_QUESTION -- A question for the Wizard

    """
    LEVEL_ERROR, LEVEL_WARN, LEVEL_INFO, LEVEL_QUESTION = range(4)

    def __init__(self,
                 title,
                 text,
                 level=2,
                 buttons=[('ok', 1, None)],
                 default_button='ok'):
        """
        Create an alert for the Wizard

        Arguments:
            title {str} -- Alert title
            text {str} -- Alert text

        Keyword arguments:
            level {int} -- Alert level (default: ROLE_INFO)
            buttons [tuple(str, Button|hex, method)]
                 -- A list of tuples, where each tuple is a key
                    ({str}), either an instance of {Button} or hex
                    value from {DefaultButton}, and a method or
                    {None} called when the button is selected
            default_button {str} -- Key of the default button
        """
        self.title = title
        self.text = text
        self.level = level
        self.buttons = buttons
        self.default_button = default_button

    class Button:
        """
        Custom button information

        Variables:
            ROLE_INVALID     -- The button is invalid
            ROLE_ACCEPT      -- Clicking the button causes the dialog
                                to be accepted (e.g. OK)
            ROLE_REJECT      -- Clicking the button causes the dialog
                                to be rejected (e.g. Cancel)
            ROLE_DESTRUCTIVE -- Clicking the button causes a
                                destructive change (e.g. for Discarding
                                Changes) and closes the dialog
            ROLE_ACTION      -- Clicking the button causes changes to
                                the elements within the dialog
            ROLE_HELP        -- The button can be clicked to request help
            ROLE_YES         -- The button is a "Yes"-like button
            ROLE_NO          -- The button is a "No"-like button
            ROLE_RESET       -- The button resets the dialog's fields
                                to default values
            ROLE_APPLY       -- The button applies current changes
        """
        ROLE_INVALID = -1
        ROLE_ACCEPT = 0
        ROLE_REJECT = 1
        ROLE_DESTRUCTIVE = 2
        ROLE_ACTION = 3
        ROLE_HELP = 4
        ROLE_YES = 5
        ROLE_NO = 6
        ROLE_RESET = 7
        ROLE_APPLY = 8

        def __init__(self, text, role):
            """
            A custom button

            Argument:
                text {str} -- Button text
                role {int} -- Button role
            """
            self.text = text
            self.role = role

    class DefaultButton:
        """
        Default alert buttons

        Variables:
            BUTTON_OK               -- An "OK" button with the Accept
                                       role
            BUTTON_OPEN             -- An "Open" button with the Accept
                                       role
            BUTTON_SAVE             -- A "Save" button with the Accept
                                       role
            BUTTON_CANCEL           -- A "Cancel" button with the
                                       Reject role
            BUTTON_CLOSE            -- A "Close" button with the Reject
                                        role
            BUTTON_DISCARD          -- A "Discard" or "Don't Save"
                                       button with the Destructive role
            BUTTON_APPLY            -- An "Apply" button with the Apple
                                       role
            BUTTON_RESET            -- A "Reset" button with the Reset
                                       role
            BUTTON_RESTORE_DEFAULTS -- A "Restore Defaults" button with
                                       the Reset role
            BUTTON_HELP             -- A "Help" button with the Help
                                       role
            BUTTON_SAVE_ALL         -- A "Save All" button with the
                                       Accept role
            BUTTON_YES              -- A "Yes" button with the Yes role
            BUTTON_YES_TO_ALL       -- A "Yes to All" button with the
                                       Yes role
            BUTTON_NO               -- A "No" button with the No role
            BUTTON_NO_TO_ALL        -- A "No to All" button with the No
                                       role
            BUTTON_ABORT            -- An "Abort" button with the
                                       Reject role
            BUTTON_RETRY            -- A "Retry" button with the Accept
                                       role
            BUTTON_IGNORE           -- An "Ignore" button with the
                                       Accept role
            BUTTON_INVALID          -- An invalid button
        """
        BUTTON_OK = 1
        BUTTON_OPEN = 2
        BUTTON_SAVE = 3
        BUTTON_CANCEL = 4
        BUTTON_CLOSE = 5
        BUTTON_DISCARD = 6
        BUTTON_APPLY = 7
        BUTTON_RESET = 8
        BUTTON_RESTORE_DEFAULTS = 9
        BUTTON_HELP = 10
        BUTTON_SAVE_ALL = 11
        BUTTON_YES = 12
        BUTTON_YES_TO_ALL = 13
        BUTTON_NO = 14
        BUTTON_NO_TO_ALL = 15
        BUTTON_ABORT = 16
        BUTTON_RETRY = 17
        BUTTON_IGNORE = 18
        BUTTON_INVALID = 0


class WizardOption:
    """
    An option for the wizard to use at runtime

    Variables:
        CHOOSE_BOOLEAN
                     {int} -- Identifier for an option that's boolean
        CHOOSE_SINGLE_CHOICE
                     {int} -- Identifier for an option that the user
                              has to choose one item from a list
        CHOOSE_DIRECTORY
                     {int} -- Identifier for an option that the user
                              has to choose a directory
        CAT_CORE {int}     -- Identifier for options relating to the
                              application overall
        CAT_WIZARD {int}   -- Identifier for options relating to the
                              Wizard
        CAT_VOICE {int}    -- Identifier for options relating to the
                              synthesised voice
        CAT_INPUT {int}    -- Identifier for options relating to the
                              audible input to NottReal
        CAT_OUTPUT {int}   -- Identifier for options relating to the
                              visual output

        FILES_SAVE {int}   -- Show a file for saving
        FILE_OPEN {int}    -- Show a file for opening

        appstate {instance}-- App state controller
    """
    CHOOSE_BOOLEAN, CHOOSE_SINGLE_CHOICE, CHOOSE_DIRECTORY = range(3)
    CAT_CORE, CAT_WIZARD, CAT_VOICE, CAT_INPUT, CAT_OUTPUT = range(5)
    FILES_SAVE, FILES_OPEN = range(10, 12)

    appstate = None

    def __init__(self,
                 key,
                 label,
                 method=None,
                 category=0,
                 choose=0,
                 default=False,
                 added=False,
                 values={},
                 order=99,
                 group=49,
                 restorable=False,
                 restore=True,
                 extras=[]):
        """
        Create a runtime Wizard option

        Arguments:
            key {str}         -- String to identify the option
            label {str}       -- Label of the option (for the UI)
            method {method}   -- Method to call with the value when its
                                 changed

        Keyword Arguments:
            category {int}    -- The category of the option
                                 (default: {self.CAT_WIZARD})
            choose {int}      -- The type of option/what the user
                                 must choose
                                 (default: {self.CHOOSE_BOOLEAN})
            default {bool}    -- Default value (default: {False})
            added {bool}      -- Has been added to the UI
                                 (default: {False})
            values {dict}     -- Possible values as a dictionary
            order {int}       -- Position of the option within a group
            grouping {int}    -- Grouping of options
            restorable {bool} -- Save/restore value to app state
            restore {bool}    -- Restore if restorable
            extras {[mixed]}  -- Extra information
        """
        self.key = key
        self.label = label
        self.method = method
        self.category = category
        self.choose = choose
        self.default = default
        self.added = added
        self.values = values
        self.order = order
        self.group = group
        self.restorable = restorable
        self.restore = restore
        self.extras = extras

        self.ui = None
        self.ui_action = None
        self.ui_update = None

        if self.restorable and self.restore:
            self.value = WizardOption.appstate.get_option(self)
        else:
            self.value = default

    def change(self, value, dont_save=False):
        """
        Calls {self.method}, if the response is {True} then
        the value is changed.

        If the option is {restorable}, it is saved to the
        application state.

        Arguments:
            value {mixed} -- New value (depends on type)

        Keyword arguments:
            dont_save {bool} -- Force don't save

        Returns:
            {bool} -- If the change was successful
        """
        result = self.method(value)
        if result:
            self.value = value
            if self.restorable and not dont_save:
                WizardOption.appstate.save_option(self)
        return result

    @staticmethod
    def set_app_state_responder(responder):
        """
        Sets the application state responder. This is used for
        retrieving saved values from the app state.

        Don't call this unless you want to change where options
        are saved to (and why would you want to do that?)

        Arguments:
            responder {AppStateController}
        """
        WizardOption.appstate = responder

    def call_ui_update(self):
        try:
            self.ui_update(self)
        except TypeError:
            pass

    def call_ui_action(self):
        try:
            self.ui_action(self)
        except TypeError:
            pass

    def __str__(self):
        return '<[Option] %s: %s>' % (self.label, self.value)

    def __repr__(self):
        return '<[Option] %s: %s>' % (self.label, self.value)
