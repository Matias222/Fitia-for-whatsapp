from fastapi import FastAPI, Request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
from datetime import datetime
from moviepy.editor import AudioFileClip
from bd_functions import insertar_usuario,update_usuario

import tempfile
import os
import requests
import supabase
import random
import openai
import json


load_dotenv()

account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
numero_from = os.getenv("numero")
openai.api_key = os.getenv("OPENAI_API_KEY")

client = Client(account_sid, auth_token)

app = FastAPI()



def parseo_info(query):

    prompt="""Tu unica funcion es dado el input del usuario, devolver un JSON con tres caracteristicas, Nombre, Peso y Talla.
    Usuario: Hola soy Matias, mido 1.77 y peso 86.
    AI: {"Nombre":"Matias","Talla":1.77,"Peso":86}

    Usuario: Buenas tardes me llamo Juan Diego, mi altura es de 2.11 y peso 95kg
    AI: {"Nombre":"Juan Diego","Talla":2.11,"Peso":95}

    Usuario: Hola soy Diego
    AI: {"Nombre":"Diego"}

    Usuario: %s
    AI: """%(query)


    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=prompt,
        temperature=0,
        max_tokens= 256
    )
    
    result = response.choices[0]['text']
    
    print(result)

    ans={}
    try: ans=json.loads(result)
    except: ans={}

    print(ans)

    return ans

def transcribe_audio(audio_file):

    audio_file = open(audio_file, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file,language="es")
    transcript = str(transcript["text"])

    print("Transcription complete")

    return transcript

@app.post("/bot")
async def webhook(request: Request):

    message_body = await request.form()
    
    sender_number = message_body['From']

    incoming_msg = message_body['Body']

    print(numero_from)
    print(incoming_msg)
    print(sender_number)

    mensaje_retornar=""

    if 'MediaContentType0' in message_body:

        media_type = message_body['MediaContentType0']
        
        if media_type.startswith('audio/'):
            audio_file = await request.form()
            audio_data = audio_file['MediaUrl0']
            
            # Save the audio file as .mp3
            
            transcription=""

            nombre_file=random.randint(1, int(1e9))

            while(1):
                if os.path.exists(str(nombre_file)+".webm")==0: break
                nombre_file=random.randint(1, int(1e9))

            nombre_file=str(nombre_file)+".webm"

            with open(nombre_file, "wb") as buffer: 
                response = requests.get(audio_data)
                buffer.write(response.content)

            clip = AudioFileClip(nombre_file)

            nombre_file_mp3=nombre_file[0:-5]+".mp3"

            clip.write_audiofile(nombre_file_mp3, codec="mp3")

            transcription=transcribe_audio(nombre_file_mp3)

            os.remove(nombre_file)
            os.remove(nombre_file_mp3)

            print(transcription)

            mensaje_retornar = "Received an audio file. Audio saved as .mp3."
        else:
            mensaje_retornar = "Received a media file. Currently, only audio files are supported."

        incoming_msg=transcription
        mensaje_retornar="audio"
   
    else:
        # Handle text messages
        mensaje_retornar="texto"

    print(sender_number[10:])

    usuario=await insertar_usuario(int(sender_number[10:]))
    
    if(usuario[0]==0):
        mensaje_retornar="Hola soy Wanly, tu amigo nutricionista. Dime tu nombre, peso y talla"
    else:
    

        falta_info=[]

        nombre=""
        peso=0.0
        talla=0.0

        if(usuario[1]["nombre"]==""): falta_info.append("nombre")
        else: nombre=usuario[1]["nombre"]

        if(usuario[1]["peso"]==0.0): falta_info.append("peso")
        else: peso=usuario[1]["peso"]

        if(usuario[1]["talla"]==0.0): falta_info.append("talla")
        else: talla=usuario[1]["talla"]


        if(falta_info==[]):
            print("Usuario ya creado exitosamente")
        else:

            dic=parseo_info(incoming_msg)

            if(dic=={}): mensaje_retornar="Hubo un error porfavor vuelva a introducir sus datos"
            else:
                
                nuevo_falta_info=[]

                if("nombre" in falta_info):
                    if "Nombre" not in dic: nuevo_falta_info.append("nombre")
                    else: nombre=dic["Nombre"]
                
                if("peso" in falta_info):
                    if "Peso" not in dic:  nuevo_falta_info.append("peso")
                    else: peso=dic["Peso"]
                
                if("talla" in falta_info):
                    if "Talla" not in dic: nuevo_falta_info.append("talla")
                    else: talla=dic["Talla"]
            

                if(len(nuevo_falta_info)==0): mensaje_retornar=f"Genial, {nombre}, ahora dime cuales son tus objetivos alimenticios"

                elif(len(nuevo_falta_info)==1): mensaje_retornar=f"Porfavor indicame tu {nuevo_falta_info[0]}"

                elif(len(nuevo_falta_info)==2): mensaje_retornar=f"Porfavor indicame tu {nuevo_falta_info[0]} y {nuevo_falta_info[1]}"

                else: mensaje_retornar="Ya p no me dijiste tus datos"

                await update_usuario(int(sender_number[10:]),nombre,peso,talla)
  

    message = client.messages \
    .create(
            body=mensaje_retornar,
            from_=numero_from,
            to=sender_number
        )


    return "Hello"
