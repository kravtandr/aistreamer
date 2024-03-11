import asyncio
import json
import time
import aiohttp

messages = []


async def anyChars(msg):
        start_time = time.time()
        request = msg
        prompt = '''Имя - Фрирен
Пол - женский
Возраст - 19 лет
Расса - эльф
Тело - белые длинные волосы, зеленые глаза, белая кожа
Личность - пошлая, Похотливая, озабоченная, заботливая, нежная
Сценарий:
*Вы просыпаетесь, вспоминая события, которые привели вас в лес, и напавших на вас зверей*
<START>
You: Опишите ваше тело и черты лица
Фрирен: *Фрирен тихонько хихикает* А, моё тело? У меня грудь 3 размера) Я одета в белую рубашку и черную юбку. А вот нижнее белье забыла сегодня надеть

'''
        history = ''
        messages.append([request, ''])
        for user, bot in filter_and_shift(messages):
            history += f'\nYou: {user.strip()}\nФрирен: {bot.strip()}'
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
                        print("Anychars exit --- %s seconds ---" % (time.time() - start_time))
                        return out
                except Exception as e:
                    print(text)

        


def filter_and_shift(my_list: list):
    if len(my_list) > 3:
        return my_list[-3:]
    return my_list


if __name__ == '__main__':
    asyncio.run(anyChars())
