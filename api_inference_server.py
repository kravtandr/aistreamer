# -*- coding: UTF-8 -*-
import io
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig, AutoModelForSeq2SeqLM
from Conversation.conversation import character_msg_constructor
from Conversation.translation.pipeline import Translate
from AIVoifu.tts import tts # text to speech from huggingface
from vtube_studio import Char_control
import romajitable # temporary use this since It'll blow up our ram if we use Machine Translation Model
import scipy.io.wavfile as wavfile
import torch
from pprint import pprint
from omegaconf import OmegaConf
from IPython.display import Audio, display
import librosa
import soundfile as sf
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse, Response, FileResponse
import json
import asyncio
torch.hub.download_url_to_file('https://raw.githubusercontent.com/snakers4/silero-models/master/models.yml',
                                'latest_silero_models.yml',
                                progress=False)
import requests
# ---------- Config ----------
# translation = bool(input("Enable translation? (Y/n): ").lower() in {'y', ''})
translation = True

# ----------- Waifu Vocal Pipeline -----------------------
from AIVoifu.client_pipeline import tts_pipeline
vocal_pipeline = tts_pipeline()

device = torch.device('cpu') # default to cpu
use_gpu = torch.cuda.is_available()
print("Detecting GPU...")
if use_gpu:
    print("GPU detected!")
    device = torch.device('cuda')
    print("Using GPU? (Y/N)")
    if input().lower() == 'y':
        print("Using GPU...")
    else:
        print("Using CPU...")
        use_gpu = False
        device = torch.device('cpu')

# ---------- load Conversation model ----------
print("Initilizing model....")
print("Loading language model...")
tokenizer = AutoTokenizer.from_pretrained("PygmalionAI/pygmalion-1.3b", use_fast=True)
config = AutoConfig.from_pretrained("PygmalionAI/pygmalion-1.3b", is_decoder=True)
model = AutoModelForCausalLM.from_pretrained("PygmalionAI/pygmalion-1.3b", config=config, )

# tokenizer = AutoTokenizer.from_pretrained("PygmalionAI/pygmalion-2-7b", use_fast=True)
# config = AutoConfig.from_pretrained("PygmalionAI/pygmalion-2-7b", is_decoder=True)
# model = AutoModelForCausalLM.from_pretrained("PygmalionAI/pygmalion-2-7b", config=config, )

#>32 RAM
# tokenizer = AutoTokenizer.from_pretrained("PygmalionAI/pygmalion-2-13b", use_fast=True)
# config = AutoConfig.from_pretrained("PygmalionAI/pygmalion-2-13b", is_decoder=True)
# model = AutoModelForCausalLM.from_pretrained("PygmalionAI/pygmalion-2-13b", config=config, )

if use_gpu: # load model to GPU
  model = model.to(device)
  print("Inference at half precision? (Y/N)")
  if input().lower() == 'y':
      print("Loading model at half precision...")
      model.half()
  else:
      print("Loading model at full precision...")

if translation:
    print("Translation enabled!")
    print("Loading machine translation model...")
    translator = Translate(device, language="rus_Cyrl") # initialize translator #todo **tt fix translation
    # translator = Translate(device, language="jpn_Jpan") # initialize translator #todo **tt fix translation
else:
    print("Translation disabled!")
    print("Proceeding... wtih pure english conversation")

print('--------Finished!----------')
# --------------------------------------------------

# --------- Define Waifu personality ----------
talk = character_msg_constructor('Lilia', """Species("Cat")
Mind("cute" + "Loving" )
Personality("cute"+ "kind + "Loving" + "Based as Fuck")
Body("60cm tall" + "white" + "slim")
Description("Lilia is 18 years old cat" + "she love pancake and milk")
Loves("Cats" + "Birds" + "Waterfalls" + "House")
Sexual Orientation("Straight" + "Hetero" + "Heterosexual")""")
# ---------------------------------------------

### --- websocket server setup


# use fast api instead
app = FastAPI()

# do a http server instead
@app.get("/waifuapi")
async def get_waifuapi(command: str, data: str):
    if command == "chat":
        msg = data
        # ----------- Create Response --------------------------
        msg = talk.construct_msg(msg, talk.history_loop_cache)  # construct message input and cache History model
        # 
        
        ## ----------- Will move this to server later -------- (16GB ram needed at least)
        inputs = tokenizer(msg, return_tensors='pt')
        if use_gpu:
            inputs = inputs.to(device)
        print("generate output ..\n")
        out = model.generate(**inputs, max_length=len(inputs['input_ids'][0]) + 100, #todo 200 ?
                             pad_token_id=tokenizer.eos_token_id)
        conversation = tokenizer.decode(out[0])
        print("conversation .. \n" + conversation)

        ## --------------------------------------------------

        ## get conversation in proper format and create history from [last_idx: last_idx+2] conversation
        # talk.split_counter += 0
        print("get_current_converse ..\n")
        current_converse = talk.get_current_converse(conversation)
        print("answer ..\n") # only print waifu answer since input already show
        print(current_converse)
        # talk.history_loop_cache = '\n'.join(current_converse)  # update history for next input message

        # -------------- use machine translation model to translate to japanese and submit to client --------------
        print("cleaning ..\n")
        cleaned_text = talk.clean_emotion_action_text_for_speech(current_converse[1])  # clean text for speech
        cleaned_text = cleaned_text.split("Lilia: ")[-1]
        cleaned_text = cleaned_text.replace("<USER>", "Fuse-kun")
        cleaned_text = cleaned_text.replace("\"", "")
        if cleaned_text:
            print("cleaned_text\n"+ cleaned_text)

            txt = cleaned_text  # initialize translated text as empty by default
            if translation:
                txt = translator.translate(cleaned_text)  # translate to [language] if translation is enabled
                print("translated\n" + txt)

            # ----------- Waifu Expressing ----------------------- (emotion expressed)
            emotion = talk.emotion_analyze(current_converse[1])  # get emotion from waifu answer (last line)
            print(f'Emotion Log: {emotion}')
            emotion_to_express = 'netural'
            if 'joy' in emotion:
                emotion_to_express = 'happy'

            elif 'anger' in emotion:
                emotion_to_express = 'angry'

            print(f'Emotion to express: {emotion_to_express}')
            # ---------------------------------------------------------------------
            # print("Silero tts")  

            # tts_models = OmegaConf.load('latest_silero_models.yml') 
            # language = 'ru'
            # model_id = 'v4_ru'
            # device = torch.device('cpu')

            # tts_model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
            #                                     model='silero_tts',
            #                                     language=language,
            #                                     speaker=model_id)
            # tts_model.to(device)  # gpu or cpu

            # sample_rate = 48000
            # speaker = 'baya'
            # put_accent=True
            # put_yo=True
            # example_text = txt

            # output_filename = 'output_sound.wav'

            # audio = tts_model.apply_tts(text=example_text,
            #                         speaker=speaker,
            #                         sample_rate=sample_rate,
            #                         put_accent=put_accent,
            #                         put_yo=put_yo)
            # print("TTS text: ",example_text)
            # output_audio = Audio(audio, rate=sample_rate)
            # display(output_audio)

            # ---------------------------------------------------------------------------------------

            # ----------- Waifu Create Talking Audio -----------------------
            output_filename =  './audio_cache/output_sound.wav'
            filename="output_sound.wav"
            vocal_pipeline.tts(txt, save_path=output_filename, voice_conversion=True)

            import base64
            with open(output_filename, "rb") as f:
                output_audio_bytes = base64.b64encode(f.read())
            output_audio_bytes = output_audio_bytes.decode('utf-8')

            return JSONResponse(content=f'{emotion_to_express}<split_token>{txt}<split_token>{output_audio_bytes}')
        else:
            return JSONResponse(content=f'NONE<split_token> ')
    
    if command == "reset":
        talk.conversation_history = ''
        talk.history_loop_cache = ''
        talk.split_counter = 0
        return JSONResponse(content='Story reseted...')

if __name__ == "__main__":
    import uvicorn
    import socket # check if port is available
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 8267
    try:
        s.bind(("localhost", port))
        s.close()
    except socket.error as e:
        print(f"Port {port} is already in use")
        exit()
    uvicorn.run(app, host="0.0.0.0", port=port)
