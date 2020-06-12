
import abc

class AbstractController:
    def __init__(self, nottreal, args):
        """
        Abstract controller class. All controllers should inherit
        this class
        
        Arguments:
            nottreal {App} -- Application instance
            args {[str]} -- Application arguments
        """
        self.nottreal = nottreal
        self.args = args
        
        self.responder = self.nottreal.responder
        self.router = self.nottreal.router

    @abc.abstractmethod
    def respond_to(self):
        """
        Label of the controller this class will respond to. Note
        that multiple controllers can have the same label, but the 
        last controller to be instantiated wins

        Alternatively can be a list of labels.
        
        Decorators:
            abc.abstractmethod
        Returns:
            str/[str] -- Label(s) for this controller
        """
        pass

    def relinquish(self, instance):
        """
        Relinquish control over signals destined for this 
        controller to the controller?

        Arguments:
            instance {AbstractController} -- Controller that has 
                said it wants to be a responder for the same signals 
                as this controller.
        Returns:
            {bool} -- True if it's OK to relinquish control
        """
        return False

    def ready(self):
        """
        Run any additional commands once all controllers are ready 
        (allows for running cross-controller hooks)
        """
        pass

    @abc.abstractmethod
    def quit(self):
        """
        Make any necessary arrangements to quit the app now
        """
        pass
