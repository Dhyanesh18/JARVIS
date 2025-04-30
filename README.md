# JARVIS - A PERSONAL ASSISTANT

Jarvis like Personal Assistant for running locally in my personal laptop, that uses Vosk mobile model for fast speech recognition and uses pyttsx3 for speech output.

Uses **_multi-threading_** (and daemon processes) for waiting I/O while processing the input and monitoring background processes and system vitals.

User interface made using **_PyQt_**.

**_Sklearn intent classifier_** for classifying the intent of the user into different possible condition action pairs

Some simple inputs were pattern matched instead of using intent classification due a to small dataset and decrease in accuracy because of many possible classes in the classifier model.

**_Pyinstaller_** used to pack the files into a .exe executable.

## IMAGE OF RUNNING OUTPUT
***NOTE: THIS IS A PRETTY OLD VERSION OF THE APPLICATION (FURTHER CHANGES HAVE BEEN MADE INCLUDING NETWORK DETAILS AND TEXT MODAL INPUT INCASE OF UNAVOIDABLE BACKGROUND NOISE**

![D](https://github.com/user-attachments/assets/8c085d51-4e38-455e-a8ba-012f2f4c18c6)

![439111729-a6bd4b97-c524-4632-9605-cd52b2f968d5](https://github.com/user-attachments/assets/f96aba26-1801-450d-916f-2b832087b68e)

