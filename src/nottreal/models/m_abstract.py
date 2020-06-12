
import abc

class AbstractModel:
    def __init__(self, args):
        """
        Abstract model class. All models should inherit this class.
        
        Arguments:
            args {[str]} -- Application arguments
        """
        pass

    @abc.abstractmethod
    def cats(self, cat_id = None):
        """
        Return one or all categories.
        
        Arguments:
            cat_id {str} -- Return a particular category
        
        Returns:
            [{str}] -- Categor(y/ies)

        Raises:
                KeyError -- If no matching category is found
            NotImplementedError -- If the child class hasn't implemented this method
        """
        raise NotImplementedError('cats method not implemented')

    def stmnts(self, cat_id = None, stmnt_id = None):
        """
        Return one or more message by their ID or category
        
        Arguments:
            cat_id {str} -- Find messages within a category
            stmnt_id {str} -- Find a message by its ID
        
        Returns:
            str/[str] -- Message(s)

        Raises:
            KeyError -- If no matching messages are found
            NotImplementedError -- If the child class hasn't implemented this method
        """
        raise NotImplementedError('stmnts method not implemented')