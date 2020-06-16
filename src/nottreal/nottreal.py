
from .utils.init import ClassUtils
from .utils.dir import DirUtils
from .utils.log import Logger
from .models.m_cfg import ConfigModel
from .views.v_gui import Gui
from .controllers import c_abstract

import inspect
import sys


class App:
    def __init__(self, args):
        """Create the controller for the application

        Arguments:
            args {[str]} -- Application arguments
        """
        Logger.debug(__name__, 'Welcome to the GUI application')

        self.appname = 'NottReal'

        self.args = args
        self._controllers = {}
        self.responders = {'app': self}

        # config model (actually loaded by the Wizard controller)
        self.config = ConfigModel(args)

        # initialise the controllers
        module_path = DirUtils.pwd() + '/src/nottreal/controllers'
        classes = ClassUtils.load_all_subclasses(
            module_path,
            c_abstract.AbstractController,
            'controllers.')

        self.controllers = {}
        for name, cls in classes.items():
            if self.args.dev:
                self.controllers[name] = cls(self, args)
                Logger.debug(__name__, 'Loaded controller "%s"' % name)
            else:
                try:
                    self.controllers[name] = cls(self, args)
                    Logger.debug(__name__, 'Loaded controller "%s"' % name)
                except TypeError:
                    Logger.error(
                        __name__,
                        '"%s" has invalid constructor arguments' % (name))

            respond_tos = self.controllers[name].respond_to()
            if type(respond_tos) is list:
                for repond_to in respond_tos:
                    self.responder(repond_to, self.controllers[name])
            elif type(respond_tos) is str:
                self.responder(respond_tos, self.controllers[name])

        # initialise the views
        self.view = Gui(self, args)
        self.view.init_ui()

        # ready the controllers
        def filter_func(x):
            return \
                hasattr(self.responders[x], 'ready_order') \
                and self.router(x, 'ready_order') > -1

        def sort_func(x):
            return self.router(x, 'ready_order')

        responders = filter(
            filter_func,
            self.responders)
        responders = sorted(
            responders,
            key=sort_func)

        for name in iter(responders):
            try:
                self.router(name, 'ready')
            except AttributeError:
                pass

        # boom!
        Logger.info(__name__, self.appname + ' is running')
        self.view.run_loop()

        Logger.debug(__name__, 'Exiting the GUI application')

    def quit(self):
        """Gracefully shutdown the application"""
        self.view.quit()

    def responder(self, name, responder=None):
        """
        Retrieve a particular message responder, or set one

        Arguments:
            name {str} -- Name of the responder
            responder [AbstractController] --
                Instance of the controller that responds (default: {None})

        Returns:
            AbstractController -- Controller instance
        """
        if responder is not None:
            responder_class = responder.__class__.__name__
            if name not in self.responders:
                self.responders[name] = responder
                Logger.debug(
                    __name__,
                    'Controller "%s" is handling "%s" signals'
                    % (responder_class, name))
            elif self.responders[name].relinquish(responder):
                curr_class = self.responders[name].__class__.__name__
                self.responders[name] = responder
                Logger.debug(
                    __name__,
                    'Controller "%s" is handling "%s" signals (taking over '
                    'from "%s")' % (responder_class, name, curr_class))
            else:
                curr_class = self.responders[name].__class__.__name__
                Logger.warning(
                    __name__,
                    'Controller "%s" requested to respond to "%s" signals, '
                    'but rejected by current holder, "%s"'
                    % (responder_class, name, curr_class))

        try:
            return self.responders[name]
        except KeyError:
            raise KeyError('No responder named "%s"' % name)

    def router(self, recipient, action, **kwargs):
        """
        Route a message between elements the framework to a responder

        Arguments:
            recipient {str} -- Recipient responder
            action {[str]} -- Message to pass
            **kwargs {[mixed]} -- Additional arguments to pass through
        """
        responderInstances = {}
        method = None

        try:
            if recipient == '_':
                responderInstances = {
                    responder: self.responders[responder]
                    for responder in self.responders.keys()
                    if responder != 'app'
                }
            else:
                responderInstances[recipient] = self.responders[recipient]
        except KeyError as e:
            tb = sys.exc_info()[2]
            Logger.critical(
                __name__,
                'No responder for "%s": "%s"' % (recipient, repr(e)))
            raise e.with_traceback(tb)

        for responder, responderInstance in responderInstances.items():
            if self.args.dev:
                method = getattr(responderInstance, action)

                args = inspect.getfullargspec(method)
                if 'responder' in args[0]:
                    return method(responder=recipient, **kwargs)
                else:
                    return method(**kwargs)
            else:
                try:
                    method = getattr(responderInstance, action)
                    if method is None:
                        Logger.error(
                            __name__,
                            'No actor for the "%s" signal in the '
                            'controller "%s"' % (action, responder)
                        )
                    else:
                        Logger.debug(
                            __name__,
                            'Pass "%s" signal to the controller "%s"'
                            % (action, responder)
                        )

                        args = inspect.getfullargspec(method)

                        try:
                            if 'responder' in args[0]:
                                return method(responder=recipient, **kwargs)
                            else:
                                return method(**kwargs)
                        except TypeError:
                            Logger.error(
                                __name__,
                                'Actor for "%s" signal in the controller "%s"'
                                ' is not type-compatible' % (action, responder)
                            )
                except SystemExit:
                    pass
                except Exception as e:
                    Logger.error(
                        __name__,
                        'Error calling the "%s" action on "%s": '
                        '"%s"' % (action, responder, repr(e))
                    )
