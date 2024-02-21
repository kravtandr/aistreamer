print('Initializing... Dependencies')
from Conversation.conversation import character_msg_constructor
from vtube_studio import Char_control
import romajitable # temporary use this since It'll blow up our ram if we use Machine Translation Model
import pyaudio
import soundfile as sf
import scipy.io.wavfile as wavfile
import requests
import random
import os
import logging
from IPython.display import Audio, display
import io
import simpleaudio as sa
logging.getLogger("requests").setLevel(logging.WARNING) # make requests logging only important stuff
logging.getLogger("urllib3").setLevel(logging.WARNING) # make requests logging only important stuff

talk = character_msg_constructor("Lilia", None) # initialize character_msg_constructor



# initialize Vstudio Waifu Controller
print('Initializing... Vtube Studio')
waifu = Char_control(port=8001, plugin_name='MyBitchIsAI', plugin_developer='HRNPH')
print('Initialized')


# chat api
def chat(msg, reset=False):
    command = 'chat'
    if reset:
        command = 'reset'
    params = {
        'command': f'{command}',
        'data': msg,
    }
    try:
        # r = requests.get('http://141.105.66.7:8267/waifuapi', params=params)
        r = requests.get('http://127.0.0.1:8267/waifuapi', params=params)
    except requests.exceptions.ConnectionError as e:
        print('--------- Exception Occured ---------')
        print('if you have run the server on different device, please specify the ip address of the server with the port')
        print('Example: http://192.168.1.112:8267 or leave it blank to use localhost')
        print('***please specify the ip address of the server with the port*** at:')
        print(f'*Line {e.__traceback__.tb_lineno}: {e}')
        print('-------------------------------------')
        exit()
    return r.text

split_counter = 0
history = ''
while True:
    try:
        con = str(input("You: "))
        if con.lower() == 'exit':
            print('Stopping...')
            break # exit prototype

        if con.lower() == 'reset':
            print('Resetting...')
            print(chat('None', reset=True))
            continue # reset story skip to next loop

        # ----------- Create Response --------------------------
        emo_answer = chat(con).replace("\"","") # send message to api
        emo, answer, audio = emo_answer.split("<split_token>")
        print("**"+emo)
        print("type audio: ", type(audio))
        if len(answer) > 2:
            use_answer = answer
            sample_rate = 48000
            # # audio_otput = Audio(audio, rate=sample_rate)
            output_filename = 'test_output_sound.wav'
            
            
            # baudio = bytes(audio, 'utf-8')
            # print(baudio)
            # Open the file in binary write mode ('wb')
            import base64
            audio = base64.b64decode(audio)
            # audio = audio.encode('utf-8')
            with open(output_filename, 'wb') as file:
                file.write(audio)
            
            # wave_obj = sa.WaveObject.from_wave_file(output_filename) 
            # play = wave_obj.play() 
           
            # display(sound_data)
            # sf.write(output_filename, sound_data, sample_rate, 'PCM_24')
            # ------------------------------------------------------
            print(f'Answer: {answer}')
            if answer.strip().endswith(f'{talk.name}:') or answer.strip() == '':
                continue # skip audio processing if the answer is just the name (no talking)



            # ----------- Waifu Talking -----------------------
            wave_obj = sa.WaveObject.from_wave_file(output_filename) 
            play = wave_obj.play() 

            # --------------------------------------------------
            if emo:  ## express emotion
                waifu.express(emo)  # express emotion in Vtube Studio
            # --------------------------------------------------
    except Exception as e:
        print('--------- Exception Occured ---------')
        print(f'*Line {e.__traceback__.tb_lineno}: {e}')
        print('-------------------------------------')
     