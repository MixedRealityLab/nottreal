

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

        appstate {instance}-- App state controller
    """
    CHOOSE_BOOLEAN, CHOOSE_SINGLE_CHOICE, CHOOSE_DIRECTORY = range(3)
    CAT_CORE, CAT_WIZARD, CAT_VOICE, CAT_INPUT, CAT_OUTPUT = range(5)

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
                 restore=True):
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

        self.ui = None
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

    def __str__(self):
        return '<[Option] %s: %s>' % (self.label, self.value)

    def __repr__(self):
        return '<[Option] %s: %s>' % (self.label, self.value)


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
