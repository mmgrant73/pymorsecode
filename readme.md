# PyMorseCode:

### What is it?
PyMorseCode is a morse code reader/generator.  It can transacte a string text to morse code output.  Also, it can
play the morse code in audio format and save it to your computer in WAV format.  You can also load a WAV file that 
has morse code and it will translate it to a text string so that you can read it.  This project contains a library 
file called pymorse.py that you can use in your project and a GUI interface that you can use to generate morse code
text and audio.  Also, translate a morse code wave file.
 
Example Library Usage:
 ```
    from pymorsecode import MorseCode
    
    morse = MorseCode("Kayleb Walter", 7, 500)
    # save audio version of morse code to specified file
    morse.save_wav("morsecode.wav")
 ```
 
 Translate the text "Kayleb Walter", convert it to morse code and save it in audio format to "morsecode.wav"

### How to use it install?
Download and unzip the files.  Install the dependences which is shown below.  To run the GUI, go to terminal and
navigate to the folder that holds the file and run the following command

```
    python pymorsegui.py
```

Note: If using the library for a project, it has a couple of dependences: pyaudio, wave, soundfile, 
you can install them using pip

```
pip install pyaudio
pip install wave
pip install soundfile
```

### How to use the GUI?
The GUI is straight forward. Type in the text you want to convert to morse code in the top textbox.  Afterwhich,
click on the generate button.  This will generate the morse code for the text and be shown in the bottom textbox.
If you want to save the morse code in audio format just click on the save button.  If you click on the open button
it will allow you to open a morse code audio file.  It will translate the audio and show the morse code and the text
version in the textboxes 

![Alt text](https://github.com/mmgrant73/pymorsecode/blob/master/morsecode.png?raw=true "Image-PyMorseCode")

Note: When opening an audio file, it will take a couple of seconds for the program to process and output the morse code
so it might appear to do nothing.  Just give it a couple of seconds.  You can look at the terminal window and it show
you when it has finish 

### How to use the library?
1. It is quite easy to use the library.  Just import the class in your project:
```
   from pymorsecode import MorseCode
```

2. To initialize the morse code class in your code
   
```
    morse = MorseCode("Kayleb Walter", 7, 500)
```
MorseCode(textstring, wpm (default=10), frequency default(800)
textstring - is the text you want to convert to morsecode
wpm - words per minute, the speed of the morse code when in audio format(wpm 5 - 25)
frequency - the frequency of the tone that will be used for the morse code(frequency 500 - 1000)

textstring will be stored in the morse property morse_text(morse.morse_text)
The translated morse code for textstring will be calculate when you initialize the class and
be stored in the morse property morse_code (morse.morse_code)

3.  Converting text to and from morse code the following two functions can be use

```
    # Get morse code for the given text
    morse_code = morse.to_morse("Genavive Grant")
    # Convert morse code to text 
    morse_text = morse.to_string(morse_code)
```

4. To save the morse code in audio format(wav) use the following function:

```
    # save audio version of morse code to specified file
    morse.save_wav("morsecode.wav")
```

5. To get morse code from an audio format(wav), use the following function:

```
    # Open a file and get text from the morsecode audio
    morse.sound_to_morse("morsecode.wav")
```

The morse code from the audio will be stored in the property morse_code and the 
text version of the morse code will be stored in the property morse_text

### To Do:
1. Add an install file so that one does not have to worry about install the dependences 

