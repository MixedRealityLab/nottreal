<h1 align="center">
	NottReal
</h1>


A Python application for running Wizard of Oz studies with a voice-based user interface. Currently only tested with macOS.


## Configuring NottReal

When you run the app it will offer you to select an existing configuration directory, or create a new one. If you choose to create a new one, NottReal copies the source from `dist.nrc` into this new directory. You are then shown the *Wizard Window*.

You can choose to edit the files in this directory by selecting *File > Edit configuration*. Currently, you must close and re-open NottReal, or reload the configuration using *File > Load configuration*.

### Prepared messages

A list of *prepared messages*, which are pre-scripted messages that can be sent to the participant using the simulated voice. These messages are categorised by and presented across a tabs in the UI. The categories can be configured in the configuration file `categorises.tsv` and consist of a unique category ID and a label in a tab-separated format:

	unique_cat_1	Category 1
	unique_cat_2	Category 1
	unique_cat_3	Category 1
	unique_cat_4	Category 1

You must have at least once category, thus if you do not wish to use this feature, simply leave a placeholder category in `categorises.tsv`, e.g.:

	category	Prepared messages

The prepared messages themselves are defined in `messages.tsv` in the configuration directory as: unique message ID, a category ID, a title and the text:

	unique_message_1	unique_cat_1	Title	Prepared message to be sent to the participant 

Prepared messages can also contain *slots*, which are segments of text to be replaced at run-time by the Wizard. For example, part of a message may include words uttered by a participant. Slots are defined as a name within square brackets:

	unique_message_2	unique_cat_1	Title 2	Prepared message to be sent to the participant with a [slot]

When you double click a message with a slot, the UI will place the message in the *textbox* and automatically highlight it so that it can be edited quickly. Subsituted slot values are displayed in the UI also. If there are multiple slots, pressing either the `enter` or `tab` key will move to the next slot. Press `ctrl` + `enter` will send a message if there are no slots left.

Slots can use a previously substituted value automatically using the asterisk at the end of its name:

	unique_message_3	unique_cat_1	Title 3	Prepared message to be sent to the participant with a [slot*]

On the first use of this message, the Wizard will have to type a value for the slot. On successive double-clicks of this message, NottReal will automatically substitute the value. There is an option to reset this tracking on a category change. Alternatively, if a particular should cancel tracking for that particular slot, it can use a dollar at the end of its name:

	unique_message_4	unique_cat_1	Title 4	Prepared message to be sent to the participant with a [slot$]

### Data recording

NottReal can record all messages sent as well as transcribed words (if transcription is enabled). Each time the app is open, a new file is created, the user specifies the directory where this recording will happen.

If data recording is enabled (from the *File* menu), the window contains a dropdown of messages that can be added to the log data only (e.g. if you wanted to record certain events occurring without simulating a voice). These are configured in the `log.tsv` file as such:

	unique_log_message_1	Log message

### Fake Mobile VUI interface

There is a fake mobile voice user interface view that can be enabled from the *Output* menu. The configuration for this is in the `settings.cfg` file.

### Loading messages

The window also includes a dropdown list of messages to be sent that are loading/computing messages. These automatically show the 'busy' animation during and after being sent in the Mobile VUI window, as opposed to the typical speaking animation in the output. These messages are specified in `loading.tsv`, consisting of a unique ID and the message:

	unique_loading_message_1	Message text

### Voice recognition

NottReal also supports automated/machine voice transcription. Outputs from this _only_ displayed in the Wizard window—nothing else happens with them at the moment. The following services are supported:

* [Google Cloud Speech API](https://cloud.google.com/speech/)
* [Wit.ai](https://wit.ai/)
* [Microsoft Bing Voice Recognition](https://www.microsoft.com/cognitive-services/en-us/speech-api)
* [Microsoft Azure Speech API](https://azure.microsoft.com/en-gb/services/cognitive-services/speech-to-text/)
* [Amazon Lex](https://aws.amazon.com/lex/) (also requires the [boto3](https://pypi.org/project/boto3/) library)
* [Houndify API](https://houndify.com/)
* [IBM Speech to Text](http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/speech-to-text.html)
* [Tensorflow](https://www.tensorflow.org/)

Configuration options—such as API keys—can be found in the `settings.cfg`.

## Installing from source

If you wish to install NottReal from source, follow the below steps.

### 1. Install Python and PortAudio

NottReal requires some Python dependencies. You should ensure [Python 3.7](http://python.org) or higher is installed on your system. If asked during install, install `pip` also.

#### 1a. Windows-specific instructions

If you're on Windows, in addition to installing Python, you need to be able to compile C++ code to install portaudio. Alternatively, follow this answer on [StackOverflow](https://stackoverflow.com/a/55630212) to install a PortAudio binary.

If you wish to use the native Windows TTS library, you should install the Windows Python library by running the following command in terminal:
```bash
$ pip3 install pywin32
```

#### 1b. macOS-specific instructions

If you're on macOS, in addition to installing Python, you also need to install the PortAudio library. The recommended way to install Python and PortAudio on macOS is to use the package manager [Homebrew](https://brew.sh/):

```bash
$ brew install python
$ brew install portaudio
```

NottReal has only been tested with macOS 10.14 Mojave and 10.15 Catalina.

### 2. Installing NottReal dependencies

Once the above is completed, download the NottReal source code from GitHub. Next, you should install the additional libraries required by NottReal using the `pip3` command with the requirements file in the root of the downloaded directory:

```bash
 $ pip3 install -r requirements.txt
```

### 3. Run NottReal

Call the following command in your terminal:

```bash
$ python3 nottreal.py
```

There are various options you can supply at call time:

* Logging is controlled by using the `-l` option, with the levels `WARNING`, `DEBUG`, `ERROR`, `INFO`, `CRITICAL`. *This option can only be set at call time, all other options are configurable through the application menus.*

* The configuration directory can be set using the `-c` option. A sample configuration directory is in `dist.cfg`. Create a copy of this directory and use the option to specify the location.

* The application state is saved to `appstate.json` in the configuration directory, and restored on each successive reopening of the application. Disable this with the `-ns` option.

  If you put your configuration in a directory called `cfg`, you do not need to set this option. 

* NottReal can log all 'spoken' output to TSV files in a specified directory, where a file is created each time the application is run. Point NottReal to this directory with the `-d` option.

* Multiple voices are supported and can be set using the `-v` option followed by the chosen system. Built in choices are `ShellCmd`, `macOS`, `activeMQ`, `cerevoice`, and `outputToLog` (most have configuration in `settings.cfg`).

* Multiple output windows are supported, although only `MVUIWindow` is implemented. This window  looks a bit like a Mobile VUI). Set this to open automatically with the `-o` option, e.g.` -oMVUIWindow`.

* Voice recognition using the `-r` option followed by the chosen library (available: `GoogleCloud`, `Witai`, `Bing`, `Azure`,`Lex`,`Houndify`,`IBM`,`Tensorflow`). You need to configure these in `settings.cfg`.

## NottReal in publications

If you use NottReal in a research study, you can cite it in a publications using the following reference:

> Martin Porcheron, Joel E Fischer, and Michel Valstar. 2020. NottReal: A tool for voice-based Wizard of Oz studies. In *2nd Conference on Conversational User Interfaces (CUI ’20), July 22–24, 2020, Bilbao, Spain*. ACM, New York, NY, USA, 3 pages. https://doi.org/10.1145/3405755.3406168

The following publications have used NottReal in their research:

* Philipp Kirschthaler, Martin Porcheron, and Joel E Fischer. 2020. **What Can I Say? Effects of Discoverability in VUIs on Task Performance and User Experience**. In *2nd Conference on Conversational User Interface (CUI ‘20), July 22–24, 2020, Bilbao, Spain*. ACM, New York, NY, USA, 9 pages. https://doi.org/10.1145/3405755.3406119

If you have used NottReal in your project, please file an issue to let us know and we can list it above.

