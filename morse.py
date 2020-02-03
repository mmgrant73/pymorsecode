import pyaudio
import struct
import math
import time
import soundfile
import copy
import wave

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
TONE = 700
TIMEPERIOD = 0.30
PARIS = 40
MIN = 60

p = pyaudio.PyAudio()

morse = {
    "a": "*-",
    "b": "-***",
    "c": "-*-*",
    "d": "-**",
    "e": "*",
    "f": "**-*",
    "g": "--*",
    "h": "****",
    "i": "**",
    "j": "*---",
    "k": "-*-",
    "l": "*-**",
    "m": "--",
    "n": "-*",
    "o": "---",
    "p": "*--*",
    "q": "--*-",
    "r": "*-*",
    "s": "***",
    "t": "-",
    "u": "**-",
    "v": "***-",
    "w": "*--",
    "x": "-**-",
    "y": "-*--",
    "z": "--**",
    "1": "*----",
    "2": "**---",
    "3": "***--",
    "4": "****-",
    "5": "*****",
    "6": "-****",
    "7": "--***",
    "8": "---**",
    "9": "----*",
    "0": "-----"
}

def get_time_period(wpm):
    timeperiod = MIN/(PARIS * wpm)
    return timeperiod

def save_wav(filename, morsecode):
    # Save the recorded data as a WAV file
    frames = get_morse_frame(morsecode)
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    value = bytearray(frames)
    wf.writeframes(value)  #('b'.join(frames))
    wf.close()
    print("Save the morse code audo to " + filename)

def data_for_offtime(time):
    frame_count = int(RATE * time)
    remainder_frames = frame_count % RATE
    wavedata = []
    for i in range(frame_count):
        wavedata.append(0)
    #for i in range(remainder_frames):
    #    wavedata.append(0)
    number_of_bytes = str(len(wavedata))  
    wavedata = struct.pack(number_of_bytes + 'h', *wavedata) 
    return wavedata

def data_for_freq(frequency, time):
    """get frames for a fixed frequency for a specified time or
    number of frames, if frame_count is specified, the specified
    time is ignored"""
    #RATE = 44100
    #TONE = 700 #400
    #TIMEPERIOD = 0.30
    frame_count = int(RATE * time)

    remainder_frames = frame_count % RATE
    wavedata = []

    for i in range(frame_count):
        a = RATE / frequency  # number of frames per wave
        b = i / a
        # explanation for b
        # considering one wave, what part of the wave should this be
        # if we graph the sine wave in a
        # displacement vs i graph for the particle
        # where 0 is the beginning of the sine wave and
        # 1 the end of the sine wave
        # which part is "i" is denoted by b
        # for clarity you might use
        # though this is redundant since math.sin is a looping function
        # b = b - int(b)

        c = b * (2 * math.pi)
        # explanation for c
        # now we map b to between 0 and 2*math.PI
        # since 0 - 2*PI, 2*PI - 4*PI, ...
        # are the repeating domains of the sin wave (so the decimal values will
        # also be mapped accordingly,
        # and the integral values will be multiplied
        # by 2*PI and since sin(n*2*PI) is zero where n is an integer)
        d = math.sin(c) * 32767
        e = int(d)
        wavedata.append(e)
        
    #for i in range(remainder_frames):
    #    wavedata.append(0)

    number_of_bytes = str(len(wavedata))  
    wavedata = struct.pack(number_of_bytes + 'h', *wavedata)

    return wavedata

def get_morse_frame(morsecode):
    global TONE, TIMEPERIOD
    morseframes = []
    for x in morsecode:
        if(x == "*"):
            #play(TONE, TIMEPERIOD)
            frames = data_for_freq(TONE, TIMEPERIOD)
            morseframes.extend(frames)
            frames = data_for_offtime(TIMEPERIOD)
        elif(x == "-"):
            #play(TONE, TIMEPERIOD * 3)
            frames = data_for_freq(TONE, TIMEPERIOD * 3)
            morseframes.extend(frames)
            frames = data_for_offtime(TIMEPERIOD)
        elif(x == " "):
            #time.sleep(TIMEPERIOD * 3)
            frames = data_for_offtime(TIMEPERIOD * 3)
        morseframes.extend(frames)
    return morseframes

def play(frequency, time):
    """
    play a frequency for a fixed time!
    """
    frames = data_for_freq(frequency, time)
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)
    stream.write(frames)
    stream.stop_stream()
    stream.close()

def play_morse(morsecode):
    """ used to play tone that represent the morsecode"""
    global TONE, TIMEPERIOD
    for x in morsecode:
        if(x == "*"):
            play(TONE, TIMEPERIOD)
            time.sleep(TIMEPERIOD)
        elif(x == "-"):
            play(TONE, TIMEPERIOD * 3)
            time.sleep(TIMEPERIOD)
        elif(x == " "):
            time.sleep(TIMEPERIOD * 3)

def to_string(mcode):
    """ convert morsecode to text"""
    morsetext = ""
    wordlist = getwords(mcode)
    for word in wordlist:
        letterlist = getletters(word)
        for letters in letterlist:
            str1 = getword(letters)
            morsetext += str1
        morsetext += " "
    return morsetext

def getword(mcode):
    """ Convert a word in morse to regular text"""
    global morse
    morsetext = ""
    for k, v in morse.items():
        if(v == mcode):
            morsetext += k
    return morsetext

def getletters(mcode):
    """ Get a list of morsecode from a string of mcode split by space"""
    letterlist = mcode.split(" ")
    return letterlist

def getwords(mcode):
    """ Get a list of words from a morsecode from a string split by double spaces"""
    wordlist = mcode.split("  ")
    wordlist = stripword(wordlist)
    return wordlist
    
def stripword(word):
    """ Split whitespace from a word """
    for x in range(len(word)):
        word[x] = word[x].strip()
    return word

def to_morse(mcode):
    """ Convert text to morse code """
    global morse
    mcode = mcode.lower()
    morsetext = ""
    for x in mcode:
        if(x == " "):
            morsetext += " "
        else:
            morsetext += morse[x] + " "
    return morsetext

def gettiming(process_list, typetiming):
    """ 
    Used to get a sort set for different duration needed to conver to 
    morse code.
    """
    timing = []
    for x in process_list:
        if(x[0] == typetiming):
            timing.append(x[3])
    timing = set(timing)
    return sorted(timing)

def fixzerocrossing(sample_list, sample_rate):
    """
    Walk through the sample list and find duration of a tone or absence of tone
    Adjust the list by taking into account zero crossing points of a single(tone)
    """
    state = 0
    process_list = []
    for x in range(len(sample_list)):
        if(sample_list[x][3] == 0.0 and state == 0):
            state = 1
            sample_start = sample_list[x][1]
        elif(sample_list[x][3] > 0.01 and state != 1):     #!= 0.0 and state != 1): # add fix here
            process_list.append(sample_list[x])
        elif(sample_list[x][0] == 'off' and state == 1 and sample_list[x][3] > 0.002):    # 9.049773755656108e-05):       #!= 0.0):
            sample_stop = sample_list[x - 1][2]
            duration = getduration(sample_start, sample_stop, sample_rate)
            list1 = ["on", sample_start, sample_stop, duration]
            process_list.append(list1)
            process_list.append(sample_list[x])
            state = 0
        elif(x + 1 == len(sample_list) and sample_list[x-1][0] == 'off'):
            sample_stop = sample_list[x][2]
            duration = getduration(sample_start, sample_stop, sample_rate)
            list1 = ["on", sample_start, sample_stop, duration]
            process_list.append(list1)
    return process_list

def getsamples(audio_samples, sample_rate):
    """ 
    Walk through the audio data and convert it to a list that can be process
    For each tone find its duration by finding the number of sample for the tone
    and using it find duration and also categories each input as 'on' or 'off'
    based on rather it is a tone or absent of a tone
    """
    state = 0
    sample_list = [] # [start, stop, duration]
    sample_start = 0
    sample_stop = 0
    for x in range(len(audio_samples)):
        if(audio_samples[x] != float(0)):
            if(state == 0):
                sample_start = x
                state = 1
            elif(state == 2):
                sample_stop = x - 1
                duration = getduration(sample_start, sample_stop, sample_rate)
                list1 = ["off", sample_start, sample_stop, duration]
                sample_list.append(list1)
                sample_start = x
                state = 1
        elif(audio_samples[x] == 0):
            if(state == 0):
                sample_start = x
                state = 2
            elif(state == 1):
                sample_stop = x - 1
                duration = getduration(sample_start, sample_stop, sample_rate)
                list1 = ["on", sample_start, sample_stop, duration]
                sample_list.append(list1)
                sample_start = x
                state = 2

    return sample_list

def getduration(sample_start, sample_stop, sample_rate):
    """ Get the duration of a tone sample"""
    number_samples = sample_stop - sample_start
    duration = number_samples/sample_rate
    return duration

def delleadingoff(process_list):
    """ if the first input of the process list is 'off' delete it"""
    if (process_list[0][0] == 'off'):
        del process_list[0]
    return process_list

def sound2morse(process_list, timing, spacing):
    """ loop through the process list and convert it to morse code"""
    morsecode = ""
    for x in process_list:
        if(x[0] == 'on'):
            if(timing[0] == x[3]):
                morsecode +="*"
            else:
                morsecode +="-"
        else:
            if(spacing[1] == x[3]):
                morsecode += " "
            elif(spacing[0] == x[3]):
                pass
            else:
                morsecode += "  "
    return morsecode

def postprocesstiming(timingval):
    '''
    [0.07656108597285068, 0.07683257918552036, 0.07656108597285068, 0.6114932126696833, 1.6805429864253394]
    [0.07656108597285068, 0.07656108597285068, 0.6112217194570135, 0.6112217194570135, 1.6805429864253394]
    '''
    list1 = []
    for x in range(len(timingval)):
        for y in range(len(timingval)):
            z = timingval[x] / timingval[y]
            if(z > 0.9 and z < 1.1):
                #list1.append(timingval[x])
                timingval[y] = timingval[x]
    #print("timingval - ", timingval)
    return timingval

def postprocess(process_list, timing, spacing, timing1, spacing1):
    """ 
    timing might not be exact thus, if two inputs are with 90% (.9 and 1.1)
    of each other then they are considered the same as far as timing
    walk through the process list and adjust accordingly
    """
    for x in range(len(process_list)):
        if(process_list[x][0] == 'on'):
            for y in range(len(timing)):
                if(timing[y] == process_list[x][3]):
                    process_list[x][3] = timing1[y]
                    break
        else:
            for y in range(len(spacing)):
                if(spacing[y] == process_list[x][3]):
                    process_list[x][3] = spacing1[y]
    return process_list

def soundinfo():
    file_path = 'test3morse.wav'
    print('Open audio file path:', file_path)
    audio_samples, sample_rate  = soundfile.read(file_path, dtype='int16')
    number_samples = len(audio_samples)
    print('Audio Samples: ', audio_samples)
    print('Number of Sample', number_samples)
    print('Sample Rate: ', sample_rate)
    # duration of the audio file
    duration = round(number_samples/sample_rate, 2)
    print('Audio Duration: {0}s'.format(duration))
    sample_list = getsamples(audio_samples, sample_rate)
    process_list = fixzerocrossing(sample_list, sample_rate)
    process_list = delleadingoff(process_list)
    spacing = gettiming(process_list, 'off')
    timing = gettiming(process_list, 'on')
    spacing1 = copy.deepcopy(spacing)
    timing1 = copy.deepcopy(timing)
    spacing1 = postprocesstiming(spacing1 )
    timing1 = postprocesstiming(timing1)
    process_list = postprocess(process_list, list(timing), list(spacing), timing1, spacing1)
    spacing1 = sorted(set(spacing1))
    timing1 = sorted(set(timing1))
    morsecode = sound2morse(process_list, list(timing1), list(spacing1))
    morsetext = to_string(morsecode)
    #print("sample list => ", sample_list)
    print("\n")
    print("process list => ", process_list)
    print("\n")
    print("spacing list => ", spacing)
    print("timing list => ", timing)
    print("spacing1 list => ", spacing1)
    print("timing1 list => ", timing1)
    print("morse code => ", morsecode)
    print("morse text => ", morsetext)

def printsamples(startsample, stopsample, audio_samples):
    for x in range(startsample, stopsample):
        print("audio_samples[x] ", audio_samples[x])
        print("x - ", x)

def main():
    """ The main programming entry"""
    #   -- *- - - **** * *--   --* *-* *- -* -  matthew Grant
    # -... .. --.  -.-. .- -  big cat
    # *--* *- *-* ** *** paris => * X 10 : _ X 4 (12) : "" X 9 : " " X 3(9) == 40
    # wpm => paris = 40 timeperiods => 40 X W X sec = wpm : 
    # example: paris * 5 = 5wpm: paris = 5wpm => 0.025 = 1/40
    # time 40 = wpm => 1/40 wpm = timeperiod => 60/40 = time(sec)
    teststr = "paris"
    print("test string - ", teststr)
    morse_code = to_morse(teststr)
    morse_text = to_string(morse_code)
    print("morsecode => ", morse_code)
    print("text => ", morse_text)
    play_morse(morse_code)
    #soundinfo() 
    #save_wav("cat5wpm1000.wav", morsecode)
   

if __name__ == "__main__":
    main()