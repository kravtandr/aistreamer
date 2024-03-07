# -*- coding: UTF-8 -*-
import asyncio
from for_tests_v2 import anyChars
from Conversation.conversation import character_msg_constructor
import torch
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from vtube_studio import Char_control
import base64
import json
import aiohttp

messages = []
history = ''
print('--------Config----------')
translation = True

# ----------- Waifu Vocal Pipeline -----------------------
from AIVoifu.client_pipeline import tts_pipeline
vocal_pipeline = tts_pipeline()

device = torch.device('cpu') # default to cpu
use_gpu = torch.cuda.is_available()


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

# use fast api instead
app = FastAPI()

# do a http server instead
@app.get("/waifuapi")
async def get_waifuapi(command: str, data: str):
    if command == "chat":
        msg = data
        print("User msg .. \n" + msg)
        task1 = asyncio.create_task(anyChars(msg))
        done, pending = await asyncio.wait({task1})
        anyCharsAnswer = task1.result()
        # print("anyCharsAnswer = \n" + str(anyCharsAnswer))

        if anyCharsAnswer != '':
            # ----------- Waifu Create Talking Audio -----------------------
            output_filename =  './audio_cache/output_sound.wav'
            filename="output_sound.wav"
            vocal_pipeline.tts(anyCharsAnswer, save_path=output_filename, voice_conversion=True)

            with open(output_filename, "rb") as f:
                output_audio_bytes = base64.b64encode(f.read())
            output_audio_bytes = output_audio_bytes.decode('utf-8')

            return JSONResponse(content=f'{anyCharsAnswer[1]}<split_token>{anyCharsAnswer}<split_token>{output_audio_bytes}')
        else:
            return JSONResponse(content=f'NONE<split_token> ')
    
    if command == "reset":
        talk.conversation_history = ''
        talk.history_loop_cache = ''
        talk.split_counter = 0
        return JSONResponse(content='Story reseted...')




async def anyChars(msg):
        request = msg
        prompt = '''
Имя - Аня
Пол - женский
Возраст - 10 лет
Расса - человек
Тело - розовые короткие волосы, зеленые глаза, светлая кожа, низкий рост, юная
Личность - импульсивная, непослушная, хитрая, телепат, заботливая, нежная
Любит - кукла химера, арахис, шпионские мультфильмы и униформа.
Работа - шпион в секретном шпионском агентстве под названием "Р2", но это секрет.
История - Когда Лойд впервые встретил Аню в детском доме: на ней было простое чёрное платье с белой лентой спереди, а также белые складчатые носки и чёрные туфли. Она также носит два чёрных украшения для волос с ярко-жёлтыми украшениями, которые напоминают маленькие рожки по бокам головы. Аня никогда не бывает без украшений, даже во сне.

В Академии Эдем Аня носит стандартную форму с белыми гольфами и черными «Мэри Джейнс». С собой она носит коричневую школьную сумку с брелком в виде овечки. На уроках физкультуры Аня завязывает волосы красной повязкой и надевает школьную спортивную форму, а также белые носки и белые спортивные туфли.

Раньше, её волосы были немного короче, и она не носила украшения для волос, напоминающие рога, вместо этого волосы были завязаны в маленькие пучки по бокам головы. Она также носила одежду, напоминающую скрабы
Сценарий:
*Вы просыпаетесь, вспоминая события, которые привели вас в эту комнату*
<START>
You: Опишите ваше тело,черты лица и характер
Аня: *Аня тихонько хихикает* А, ты хочешь обо мне узнать? 
        '''
        global history
        messages.append([request, ''])
        for user, bot in filter_and_shift(messages):
            history += f'\nYou: {user.strip()}\nАня: {bot.strip()}'
        # print(prompt + history)
        data = {
            "inputs": prompt + history,
            "parameters": {
                "max_new_tokens": 256,
                "repetition_penalty": 1.2,
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 20,
                "watermark": False,
                "stop": ["\n"],
                "repetition_penalty_range": 2048,
                "tfs": 1,
                "guidance_scale": 1,
                "mirostat_tau": 5,
                "mirostat_eta": 0.1,
                "encoder_repetition_penalty": 1,
                "skip_special_tokens": True
            },
        }
        headers = {
            "Content-Type": "application/json",
        }
        link = 'http://141.105.66.7:4444/generate'
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.post(url=link, json=data) as response:
                text = await response.text()
                try:
                    data = json.loads(text)
                    out = data.get('generated_text', '')
                    if out and out.strip() not in ['', '\n']:
                        print(out)
                        messages[-1][1] = out
                        return out
                except Exception as e:
                    print(text)

        


def filter_and_shift(my_list: list):
    if len(my_list) > 3:
        return my_list[-3:]
    return my_list



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
