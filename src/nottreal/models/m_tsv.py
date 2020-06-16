
from ..utils.log import Logger

from collections import OrderedDict

import csv


class TSVModel:
    def __init__(self, args):
        """
        Load data from tab-separated values.

        Arguments:
            args {[arg]} -- Application arguments
        """
        dir = args.config_dir

        Logger.debug(__name__, 'Loading data from the TSV files')

        Logger.debug(__name__, 'Load categories data')
        self.cats = self._parseTsv(
            dir,
            'categories.tsv',
            ['id', 'label'])

        Logger.debug(__name__, 'Load messages data')
        self.msgs = self._parseTsv(
            dir,
            'messages.tsv',
            ['id', 'cat_id', 'label', 'text'])

        Logger.debug(__name__, 'Load loading messages data')
        default = OrderedDict()
        default[0] = {'id': 0, 'message': 'Just a minute'}
        default[1] = {'id': 0, 'message': 'I\'m working on it'}
        self.loading_msgs = self._parseTsv(
            dir,
            'loading.tsv',
            ['id', 'message'],
            default)

        Logger.debug(__name__, 'Load custom log messages data')
        self.log_msgs = self._parseTsv(
            dir,
            'log.tsv',
            ['id', 'message'],
            OrderedDict())

        for idx, message in self.msgs.items():
            if 'msgs' not in self.cats[message['cat_id']]:
                self.cats[message['cat_id']]['msgs'] = []

            if message['cat_id'] not in self.cats[message['cat_id']]['msgs']:
                self.cats[message['cat_id']]['msgs'].append(message)

        for cat_id, cat in self.cats.items():
            if 'msgs' not in cat:
                cat['msgs'] = OrderedDict()

        Logger.info(__name__, 'Loaded prepared messages')

    def msgs(self, cat_id=None, msg_id=None):
        """
        Return one or more messages by their ID or category

        Arguments:
            cat_id {str} -- Find messages within a category
            msg_id {str} -- Find a message by its ID

        Returns:
            str/[str] -- Message(s)

        Raises:
            KeyError -- If no matching messages are found
        """
        if cat_id is not None:
            try:
                self.cats[cat_id]['msgs']
            except KeyError:
                raise KeyError('No matching category for id "%s"' % cat_id)
            cat_id_str = '"%s"' % cat_id
        else:
            cat_id_str = 'all messages'

        if msg_id is not None:
            try:
                return self.msgs[msg_id]
            except KeyError:
                raise KeyError(
                    'No matching message for id "%s" in %s'
                    % (msg_id, cat_id_str))

        return self.msgs

    def _parseTsv(self, dir, file_name, field_names, default=None):
        """
        Parse a tab-separated values file into an OrderedDict.
        Must include an id column (specify location with the
        field_names argument).

        Arguments:
            dir {str} -- Directory to load file from
            file_name {str} -- File name to parse in the
                configured directory
            field_names {[str]} -- List of field name keys

        Keyword Arguments:
            default {OrderedDict} -- Default values (or None)

        Returns:
            OrderedDict -- Dict of values from the model
        """
        data = OrderedDict()
        try:
            with open(dir + '/' + file_name) as tsv_file:
                reader = csv.DictReader(
                    tsv_file,
                    delimiter='\t',
                    fieldnames=field_names)
                for row in reader:
                    data[row['id']] = row
        except FileNotFoundError as e:
            if default is not None:
                return default
            else:
                raise e
        return data
