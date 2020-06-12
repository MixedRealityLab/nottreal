<h1 align="center">
	NottReal
</h1>

A Python application for running Wizard of Oz studies with a voice-based  user interface.

## Dependencies
NottReal requires Python 3 and some dependencies, run `pip3` in the root directory:

	 pip install -r requirements.txt

## Running
Run the code by calling `python3 nottreal.py`, with the various options accessible with `-h` option. Summarily:

* Logging is controlled by using the `-l` option, with the levels `WARNING`, `DEBUG`, `ERROR`, `INFO`, `CRITICAL`

* The configuration directory can be set using the `-c` option. A sample configuration directory is in `.cfg-dist`. Create a copy of this directory and use the option to specify the location.

  If you put your configuration in a directory called `cfg`, you do not need to set this option. 

* NottReal can log all 'spoken' output to TSB files in a specified directory, where a file is created each time the application is run. Point NottReal to this directory with the `-d` option.

* Multiple voices are supported and can be set using the `-v` option followed by the chosen system. Built in choices are `ShellCmd`, `macOS`, `activeMQ`, `cerevoice`, and `outputToLog` (most have configuration in `settings.cfg`). 

* Multiple output windows are supported, although only `MVUIWindow` is implemented. This window  looks a bit like a Mobile VUI). Set this to open automatically with the `-o` option, e.g.` -oMVUIWindow`.



## App layout and configuration
Copy the contents of the `.cfg_dist` directory to a new directory (e.g. `cfg`).  The application doesn't load configuration files from `cfg_dist`---these are only accessed if no configuration is specified.

In summary, the NottReal *Wizard Window* UI has the following features:
	a) A *textbox* to type messages to send to participant
	b) A list of queued *messages*
	c) A list of previously sent *messages*
	d) A list of categories of *prepared messages*
	e) A list of *prepared messages*
	f) A list of previously filled *slots*
	g) A list of optional *log-only messages*
	h) A list of *loading messages* to display on the Wizard window
	g) A list of options, dependant upon the voice used

NottReal can store all sent messages in a timestamped log. You can configure this by passing in a directory's path to the `-d` option.

There is a fake mobile voice user interface view that can be enabled from the menu (or opened by default using the `-w` option). The configuration for this is in the `settings.cfg` file.

In more detail, the application includes a *textbox* to type messages to send to the participant. If a previous message is being spoken when another message is sent, it will be queued up. Previously uttered/delivered messages are displayed at the bottom of the UI.

NottReal also includes *prepared messages* that can be quickly sent to the participant through the simulated voice. These messages are categorised and presented as tabs in the UI. The categories can be configured in the file `categorises.tsv` in the configuration directory and consist of a unique category ID and the label in a tab-separated format:

	unique_cat_1	Category 1
	unique_cat_2	Category 1
	unique_cat_3	Category 1
	unique_cat_4	Category 1

You must have at least once category, thus if you do not wish to use this feature, simply leave a placeholder category in `cfg/categorises.tsv`, e.g.:

	category	Prepared messages

Prepared messages are words that will be sent to the voice simulator on being double clicked. They are defined in `messages.tsv` in the configuration directory as a unique message ID, a category ID, a title and the text:

	unique_message_1	unique_cat_1	Title	Prepared message to be sent to the participant 

Prepared messages can also contain *slots*, which are segments of text to be replaced at run-time by the Wizard. For example, part of a message may include words uttered by a participant. Slots are defined as a name within square brackets:

	unique_message_2	unique_cat_1	Title 2	Prepared message to be sent to the participant with a [slot]

When you double click a message with a slot, the UI will place the message in the *textbox* and automatically highlight it so that it can be edited quickly. Subsituted slot values are displayed in the UI also. If there are multiple slots, pressing either the `enter` or `tab` key will move to the next slot. Press `ctrl` + `enter` will send a message if there are no slots left.

Slots can use a previously substituted value automatically using the asterisk at the end of its name:

	unique_message_3	unique_cat_1	Title 3	Prepared message to be sent to the participant with a [slot*]

On the first use of this message, the Wizard will have to type a value for the slot. On successive double-clicks of this message, NottReal will automatically substitue the value. There is an option to reset this tracking on a category change. Alternatively, if a particular should cancel tracking for that particular slot, it can use a dollar at the end of its name:

	unique_message_4	unique_cat_1	Title 4	Prepared message to be sent to the participant with a [slot$]

The window also includes a dropdown list of messages to be sent to the voice simulator. These automatically show the loading animation during and after being sent. They are specified in `loading.tsv`, consisting of a unique ID and the message:

	unique_loading_message_1	Message text

The window contains messages that can be added to the log data only (e.g. if you wanted to record certain events occuring without simulating a voice):

	unique_log_message_1	Log message

Finally, to interrupt the currently delivered output, press `Ctrl` + `c` (or `Cmd` + `c` on macOS). Optionally (and by default), this clears queued messages too.
