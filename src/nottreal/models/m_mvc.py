
class WizardOption:
    """
    An option for the wizard to use at runtime

    Variables:
        CHECKBOX {int}     -- Identifier for an option that's boolean
        BOOLEAN {int}      -- Identifier for an option that's boolean
        SINGLE_CHOICE {int}-- Identifier for an option that the user
                              has to choose one item from a list
        DIRECTORY {int}    -- Identifier for an option that the user
                              has to choose a directory
        CAT_WIZARD {int}   -- Identifier for options relating to the
                              Wizard
        CAT_VOICE {int}    -- Identifier for options relating to the
                              synthesised voice
        CAT_INPUT {int}    -- Identifier for options relating to the
                              audible input to NottReal
        CAT_OUTPUT {int}   -- Identifier for options relating to the
                              visual output
    """
    CHECKBOX = 0
    BOOLEAN, SINGLE_CHOICE, DIRECTORY = range(3)
    CAT_WIZARD, CAT_VOICE, CAT_INPUT, CAT_OUTPUT = range(4)

    def __init__(self,
                 label,
                 method,
                 opt_cat=0,
                 opt_type=0,
                 default=False,
                 added=False,
                 values={},
                 order=99,
                 group=49):
        """
        Create a runtime Wizard option

        Arguments:
            label {str} -- Label of the option
            label {method} -- Method to call with the value when its
                              changed

        Keyword Arguments:
            opt_cat {int}  -- The category of the option
                              (default: {self.CAT_WIZARD})
            opt_type {int} -- The type of option
                              (default: {self.BOOLEAN})
            default {bool} -- Default value (default: {False})
            added {bool}   -- Has been added to the UI
                              (default: {False})
            values {dict}  -- Possible values as a dictionary
            order {int}    -- Position of the option within a group
            grouping {int} -- Grouping of options
        """
        self.label = label
        self.method = method
        self.opt_cat = opt_cat
        self.opt_type = opt_type
        self.default = default
        self.added = added
        self.values = values
        self.order = order
        self.group = group

        self.value = default
        self.ui = None

    def change(self, value):
        """
        Change the value and call the method that wants it.

        Arguments:
            value {mixed} -- New value (depends on type)
        """
        self.value = value
        self.method(value)


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
