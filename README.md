# JARVIS
Jarvis like Personal Assistant for running locally in my personal laptop, that uses Vosk mobile model for fast speech recognition and uses pyttsx3 for speech output.

Uses **_multi-threading_** (and daemon processes) for waiting I/O while processing the input and monitoring background processes and system vitals.

User interface made using **_PyQt_**.

**_Sklearn intent classifier_** for classifying the intent of the user into different possible condition action pairs

Some simple inputs were pattern matched instead of using intent classification due a to small dataset and decrease in accuracy because of many possible classes in the classifier model.

**_Pyinstaller_** used to pack the files into a .exe executable.

## IMAGE OF RUNNING OUTPUT

