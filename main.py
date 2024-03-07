print('Initializing... Dependencies')
from Conversation.conversation import character_msg_constructor
from vtube_studio import Char_control
import requests
import logging
import simpleaudio as sa
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand
import asyncio
logging.getLogger("requests").setLevel(logging.WARNING) # make requests logging only important stuff
logging.getLogger("urllib3").setLevel(logging.WARNING) # make requests logging only important stuff
logging.getLogger("requests").setLevel(logging.WARNING) # make requests logging only important stuff
logging.getLogger("urllib3").setLevel(logging.WARNING) # make requests logging only important stuff

talk = character_msg_constructor("Lilia", None) # initialize character_msg_constructor

import ssl

ssl._create_default_https_context = ssl._create_unverified_context



def cert():
    import certifi
    import os
    import os.path
    import ssl
    import stat
    import subprocess
    import sys

    STAT_0o775 = ( stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
             | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
             | stat.S_IROTH |                stat.S_IXOTH )

    openssl_dir, openssl_cafile = os.path.split(
        ssl.get_default_verify_paths().openssl_cafile)

    print(" -- pip install --upgrade certifi")
    subprocess.check_call([sys.executable,
        "-E", "-s", "-m", "pip", "install", "--upgrade", "certifi"])

    import certifi

    # change working directory to the default SSL directory
    os.chdir(openssl_dir)
    relpath_to_certifi_cafile = os.path.relpath(certifi.where())
    print(" -- removing any existing file or link")
    try:
        os.remove(openssl_cafile)
    except FileNotFoundError:
        pass
    print(" -- creating symlink to certifi certificate bundle")
    os.symlink(relpath_to_certifi_cafile, openssl_cafile)
    print(" -- setting permissions")
    os.chmod(openssl_cafile, STAT_0o775)
    print(" -- update complete")


APP_ID = 'v0f353z2qpr8gpu90vj2yl34nl22vr'
APP_SECRET = 'uyijbbf4z83dgeuegjoav6zc511urr'
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
TARGET_CHANNEL = 'anyaai_bot'

async def on_ready(ready_event: EventData):
    print('Bot is ready for work, joining channels')
    # join our target channel, if you want to join multiple, either call join for each individually
    # or even better pass a list of channels as the argument
    await ready_event.chat.join_room(TARGET_CHANNEL)
    # you can do other bot initialization things in here

async def on_message(msg: ChatMessage):
    print(f'in {msg.room.name}, {msg.user.name} said: {msg.text}')
    try:
            # ----------- Create Response --------------------------
            con = msg.text
            print("con = ", con)
            emo_answer = chat(con).replace("\"","") # send message to api
            print("emo_answer = ", emo_answer)
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
                    pass # skip audio processing if the answer is just the name (no talking)
                else:
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

async def run():
    # set up twitch api instance and add user authentication with some scopes
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token, validate=False)
    # user = await first(twitch.get_users(logins='kravtandr'))
    # # print the ID of your user or do whatever else you want with it
    # print(user.id)

    # create chat instance
    chat = await Chat(twitch)

    # register the handlers for the events you want

    # listen to when the bot is done starting up and ready to join channels
    chat.register_event(ChatEvent.READY, on_ready)
    # listen to chat messages
    chat.register_event(ChatEvent.MESSAGE, on_message)

    # we are done with our setup, lets start this bot up!
    chat.start()

    # lets run till we press enter in the console
    try:
        input('press ENTER to stop\\n')
    finally:
        # now we can close the chat bot and the twitch api client
        chat.stop()
        await twitch.close()


# lets run our setup



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
        r = requests.get('http://141.105.66.7:8267/waifuapi', params=params)
        # r = requests.get('http://127.0.0.1:8267/waifuapi', params=params)
    except requests.exceptions.ConnectionError as e:
        print('--------- Exception Occured ---------')
        print('if you have run the server on different device, please specify the ip address of the server with the port')
        print('Example: http://192.168.1.112:8267 or leave it blank to use localhost')
        print('***please specify the ip address of the server with the port*** at:')
        print(f'*Line {e.__traceback__.tb_lineno}: {e}')
        print('-------------------------------------')
        exit()
    return r.text


cert()
split_counter = 0
history = ''
asyncio.run(run())
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
        print("con = ", con)
        emo_answer = chat(con).replace("\"","") # send message to api
        print("emo_answer = ", emo_answer)
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
     