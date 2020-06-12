
class WizardOption:
    """
    An option for the wizard to use at runtime

    Variables:
        CHECKBOX {int} -- Identifier for an option that's a checkbox
        DROPDOWN {int} -- Identifier for an option that's a dropdown
    """
    CHECKBOX, DROPDOWN = range(2)

    def __init__(self,
        label,
        method,
        type = 0,
        default = False,
        added = False,
        values = {}):
        """
        Create a runtime Wizard option
        
        Arguments:
            label {str} -- Label of the option
            label {method} -- Method to call with the value when its changed
        
        Keyword Arguments:
            type {int} -- The type of option (default: {self.CHECKBOX})
            default {bool} -- Default value (default: {False})
            added {bool} -- Has been added to the UI (default: {False})
            values {dict} -- Possible values
        """
        self.label = label
        self.method = method
        self.type = type
        self.default = default
        self.value = default
        self.added = added
        self.ui = None
        self.values = values

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
        NO_OVERRIDE {int} -- Type to let the user fully control appending
        FORCE_APPEND {int} -- Type to force append a message
        FORCE_DONT_APPEND {int} -- Type to force no appending of messages
    """
    NO_OVERRIDE, FORCE_APPEND, FORCE_DONT_APPEND = range(0,3)

    def __init__(self,
        text,
        override = NO_OVERRIDE,
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
                message
                (default: {Message.NO_OVERRIDE})
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
        NOTHING, SPEAKING, LISTENING, COMPUTING {int} -- States of the Wizard

    """
    NOTHING, SPEAKING, LISTENING, COMPUTING = range(0,4)