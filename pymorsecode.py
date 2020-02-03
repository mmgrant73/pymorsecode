import pyaudio
import struct
import math
import time
import soundfile
import copy
import wave

class MorseCode:

    FORMAT = 2
    CHANNELS = 1
    RATE = 44100
    PARIS = 40
    MIN = 60

    morse = {
        "a": ".-",
        "b": "-...",
        "c": "-.-.",
        "d": "-..",
        "e": ".",
        "f": "..-.",
        "g": "--.",
        "h": "....",
        "i": "..",
        "j": ".---",
        "k": "-.-",
        "l": ".-..",
        "m": "--",
        "n": "-.",
        "o": "---",
        "p": ".--.",
        "q": "--.-",
        "r": ".-.",
        "s": "...",
        "t": "-",
        "u": "..-",
        "v": "...-",
        "w": ".--",
        "x": "-..-",
        "y": "-.--",
        "z": "--..",
        "1": ".----",
        "2": "..---",
        "3": "...--",
        "4": "....-",
        "5": ".....",
        "6": "-....",
        "7": "--...",
        "8": "---..",
        "9": "----.",
        "0": "-----"
    }

    def __init__(self, textstr, wpm = 10, hz = 800):
        """
        Constructor for the morsecode class which generates morse code text
        and audio from a string text.  Can also translate morse code audio(wav)
        files back to string text
        
        Parameters:
            time_period(float): is the timing for the morse code
            tone(float): is the frequency of the tone used by morse code
            morse_text(str): is the string text that will be translated to morsecode
            morse_code(str): is the morse code for the string text
        """
        self.time_period = self.set_time_period(wpm)
        self.tone = self.set_tone(hz)
        self.audio = pyaudio.PyAudio()
        self.morse_text = textstr
        self.morse_code = self.to_morse(self.morse_text)

    def set_tone(self, hz):
        if(hz < 500 or hz > 1000):
            raise ValueError("Tone must be between 500 andd 1000")
        return hz

    def set_time_period(self, wpm):
        """ 
        Get the time_period used for timing of morsecode based on
        wpm (words per minute)
        """
        if(wpm < 5 or wpm > 25):
            raise ValueError("WPM must be between 5 andd 25")
        time_period = self.MIN/(self.PARIS * wpm)
        return time_period

################# test to morse functions #################

    def to_string(self, mcode):
        """ convert morsecode to text"""
        morse_text = ""
        word_list = self.get_words(mcode)
        for word in word_list:
            letter_list = self.get_letters(word)
            for letters in letter_list:
                str1 = self.get_word(letters)
                morse_text += str1
            morse_text += " "
        self.morse_text = morse_text
        self.morse_code = mcode
        return morse_text

    def get_word(self, mcode):
        """ Convert a word in morse to regular text"""
        morse_text = ""
        for k, v in self.morse.items():
            if(v == mcode):
                morse_text += k
        return morse_text

    @staticmethod
    def get_letters(mcode):
        """ Get a list of morsecode from a string of mcode split by space"""
        letter_list = mcode.split(" ")
        return letter_list

    def get_words(self, mcode):
        """ Get a list of words from a morsecode from a string split by double spaces"""
        word_list = mcode.split("  ")
        word_list = self.strip_word(word_list)
        return word_list

    @staticmethod
    def strip_word(word):
        """ Split whitespace from a word """
        for x in range(len(word)):
            word[x] = word[x].strip()
        return word

    def to_morse(self, mcode):
        """ Convert text to morse code """
        mcode = mcode.lower()
        morse_text = ""
        for x in mcode:
            if(x == " "):
                morse_text += " "
            else:
                morse_text += self.morse[x] + " "
        self.morse_text = mcode
        self.morse_code = morse_text
        return morse_text

################### Process audio data ############################

    def get_timing(self, process_list, type_timing):
        """ 
        Used to get a sort set for different duration needed to conver to 
        morse code.
        """
        timing = []
        for x in process_list:
            if(x[0] == type_timing):
                timing.append(x[3])
        timing = set(timing)
        return sorted(timing)

    def fix_zero_crossing(self, sample_list, sample_rate):
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
            elif(sample_list[x][3] > 0.01  and state != 1):
                process_list.append(sample_list[x])
            elif(sample_list[x][0] == 'off' and state == 1 and sample_list[x][3] > 0.002):
                sample_stop = sample_list[x - 1][2]
                duration = self.get_duration(sample_start, sample_stop, sample_rate)
                list1 = ["on", sample_start, sample_stop, duration]
                process_list.append(list1)
                process_list.append(sample_list[x])
                state = 0
            elif(x + 1 == len(sample_list) and sample_list[x-1][0] == 'off'):
                sample_stop = sample_list[x][2]
                duration = self.get_duration(sample_start, sample_stop, sample_rate)
                list1 = ["on", sample_start, sample_stop, duration]
                process_list.append(list1)
        return process_list

    def get_samples(self, audio_samples, sample_rate):
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
                    duration = self.get_duration(sample_start, sample_stop, sample_rate)
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
                    duration = self.get_duration(sample_start, sample_stop, sample_rate)
                    list1 = ["on", sample_start, sample_stop, duration]
                    sample_list.append(list1)
                    sample_start = x
                    state = 2

        return sample_list

    @staticmethod
    def get_duration(sample_start, sample_stop, sample_rate):
        """ Get the duration of a tone sample"""
        number_samples = sample_stop - sample_start
        duration = number_samples/sample_rate
        return duration

    @staticmethod
    def del_leading_off(process_list):
        """ if the first input of the process list is 'off' delete it"""
        if (process_list[0][0] == 'off'):
            del process_list[0]
        return process_list

    def post_process_timing(self, timing_val):
        '''
        Do some postprocessing on timing of the morsecode due to 
        timing that is not exact.  Validate two timing values that are
        close to be the same value
        '''
        list1 = []
        for x in range(len(timing_val)):
            for y in range(len(timing_val)):
                z = timing_val[x] / timing_val[y]
                if(z > 0.9 and z < 1.1):
                    timing_val[y] = timing_val[x]
        return timing_val

    def post_process(self, process_list, timing, spacing, timing1, spacing1):
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

    def process_to_morse(self, process_list, timing, spacing):
        """ loop through the process list and convert it to morse code"""
        morse_code = ""
        for x in process_list:
            if(x[0] == 'on'):
                if(timing[0] == x[3]):
                    morse_code +="."
                else:
                    morse_code +="-"
            else:
                if(spacing[1] == x[3]):
                    morse_code += " "
                elif(spacing[0] == x[3]):
                    pass
                else:
                    morse_code += "  "
        return morse_code
    
    def sound_to_morse(self, file_name = None):
        audio_samples, sample_rate  = soundfile.read(file_name, dtype='int16')
        number_samples = len(audio_samples)
        sample_list = self.get_samples(audio_samples, sample_rate)
        process_list = self.fix_zero_crossing(sample_list, sample_rate)
        process_list = self.del_leading_off(process_list)
        spacing = self.get_timing(process_list, 'off')
        timing = self.get_timing(process_list, 'on')
        spacing1 = copy.deepcopy(spacing)
        timing1 = copy.deepcopy(timing)
        spacing1 = self.post_process_timing(spacing1 )
        timing1 = self.post_process_timing(timing1)
        process_list = self.post_process(process_list, list(timing), list(spacing), timing1, spacing1)
        spacing1 = sorted(set(spacing1))
        timing1 = sorted(set(timing1))
        morse_code = self.process_to_morse(process_list, list(timing1), list(spacing1))
        morse_text = self.to_string(morse_code)
        self.morse_code = morse_code
        self.teststr = morse_text

######################## Create Audio Data ###################

    def data_for_offtime(self, time):
        """ Get data for offtime for morsecode for audio format"""
        frame_count = int(self.RATE * time)
        remainder_frames = frame_count % self.RATE
        wave_data = []
        for i in range(frame_count):
            wave_data.append(0)
        number_of_bytes = str(len(wave_data))  
        wave_data = struct.pack(number_of_bytes + 'h', *wave_data) 
        return wave_data

    def data_for_freq(self, frequency, time):
        """
        get frames for a fixed frequency for a specified time or
        number of frames, if frame_count is specified, the specified
        time is ignored
        """
        frame_count = int(self.RATE * time)
        remainder_frames = frame_count % self.RATE
        wave_data = []
        for i in range(frame_count):
            a = self.RATE / frequency  # number of frames per wave
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
            wave_data.append(e)
        number_of_bytes = str(len(wave_data))  
        wave_data = struct.pack(number_of_bytes + 'h', *wave_data)
        return wave_data

    def get_morse_frame(self, morse_code):
        morse_frames = []
        for x in morse_code:
            if(x == "."):
                frames = self.data_for_freq(self.tone, self.time_period)
                morse_frames.extend(frames)
                frames = self.data_for_offtime(self.time_period)
            elif(x == "-"):
                frames = self.data_for_freq(self.tone, self.time_period * 3)
                morse_frames.extend(frames)
                frames = self.data_for_offtime(self.time_period)
            elif(x == " "):
                frames = self.data_for_offtime(self.time_period * 3)
            morse_frames.extend(frames)
        return morse_frames

################## Audio Information #######################

    def sound_info(self, file_path):
        """ Prints out audio information for an wave file"""
        print('Open audio file path:', file_path)
        audio_samples, sample_rate  = soundfile.read(file_path, dtype='int16')
        number_samples = len(audio_samples)
        print('Audio Samples: ', audio_samples)
        print('Number of Sample', number_samples)
        print('Sample Rate: ', sample_rate)
        # duration of the audio file
        duration = round(number_samples/sample_rate, 2)
        print('Audio Duration: {0}s'.format(duration))

#################### Play Audio Functions ####################

    def play(self, frequency, time):
        """
        play a frequency for a fixed time!
        """
        frames = self.data_for_freq(frequency, time)
        stream = self.audio.open(format = self.FORMAT, channels = self.CHANNELS, rate = self.RATE, output=True)
        stream.write(frames)
        stream.stop_stream()
        stream.close()

    def play_morse(self, morse_code = None):
        """ used to play tone that represent the morsecode"""
        if(morse_code == None):
            morse_code = self.morse_code
        for x in morse_code:
            if(x == "."):
                self.play(self.tone, self.time_period)
                time.sleep(self.time_period)
            elif(x == "-"):
                self.play(self.tone, self.time_period * 3)
                time.sleep(self.time_period)
            elif(x == " "):
                time.sleep(self.time_period * 3)

##################### Save Wave File #######################

    def save_wav(self, file_name, morse_code = None):
        """ Save the recorded data as a WAV file """
        if(morse_code == None):
            morse_code = self.morse_code
        frames = self.get_morse_frame(morse_code)
        wf = wave.open(file_name, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(self.RATE)
        value = bytearray(frames)
        wf.writeframes(value)
        wf.close()
        print("Save the morse code audo to " + file_name)

def main():
    """ The main programming entry"""
    # -- .- - - .... . .--  --. .-. .- -. -  matthew grant
    morse = MorseCode("Kayleb Walter", 7, 500)
    # Open a file and get text from the morsecode audio
    #morse.sound_to_morse("test5wpm500.wav")
    # Get morse code for the given text
    #morse_code = morse.to_morse("Genavive Grant")
    # Convert morse code to text 
    #morse_text = morse.to_string(morse_code)
    # Play audio of morse code
    morse.play_morse()
    # save audio version of morse code to specified file
    #morse.save_wav("test7wpm500.wav")
    # show textstr and morse_code
    print(morse.morse_text)
    print(morse.morse_code)
    #soundinfo()

if __name__ == "__main__":
    main()