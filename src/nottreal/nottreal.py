
from .utils.init import ClassUtils
from .utils.dir import *
from .utils.log import Logger
from .controllers import c_abstract
from .models import *
from .views import *


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
        self._responders = {'app': self}

        # initialise the models
        self.data = m_tsv.TSVModel(args)
        self.config = m_cfg.ConfigModel(args)

        # initialise the controllers
        module_path = DirUtils.pwd() + '/src/nottreal/controllers'
        classes = ClassUtils.load_all_subclasses(
            module_path,
            c_abstract.AbstractController,
            'controllers.')

        self.controllers = {}
        for name, cls in classes.items():
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
        self.view = v_gui.Gui(self, args, self.data, self.config)
        self.view.init_ui()

        try:
            self.router('voice_root', 'ready')
        except KeyError:
            Logger.critical(__name__, 'Root voice controller not found')
            return

        try:
            self.router('wizard', 'ready')
        except KeyError:
            Logger.critical(__name__, 'Wizard window controller not found')
            return

        try:
            self.router('output', 'ready')
        except KeyError:
            Logger.critical(__name__, 'Output window controller not found')
            return

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
            if name not in self._responders:
                self._responders[name] = responder
                Logger.debug(
                    __name__,
                    'Controller "%s" is handling "%s" signals'
                    % (responder_class, name))
            elif self._responders[name].relinquish(responder):
                curr_class = self._responders[name].__class__.__name__
                self._responders[name] = responder
                Logger.debug(
                    __name__,
                    'Controller "%s" is handling "%s" signals (taking over '
                    'from "%s")' % (responder_class, name, curr_class))
            else:
                curr_class = self._responders[name].__class__.__name__
                Logger.warning(
                    __name__,
                    'Controller "%s" requested to respond to "%s" signals, '
                    'but rejected by current holder, "%s"'
                    % (responder_class, name, curr_class))

        try:
            return self._responders[name]
        except KeyError:
            raise KeyError('No responder named "%s"' % name)

    def router(self, responder, action, **kwargs):
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
            if responder is '_':
                responderInstances = {
                    responder: self._responders[responder]
                    for responder in self._responders.keys()
                    if responder is not 'app'
                }
            else:
                responderInstances[responder] = self._responders[responder]
        except KeyError as e:
            Logger.critical(
                __name__,
                'No responder for "%s": "%s"' % (responder, repr(e)))
            raise e

        for responder, responderInstance in responderInstances.items():
            if self.args.dev:
                method = getattr(responderInstance, action)
                method(**kwargs)
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
                        try:
                            method(**kwargs)
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
