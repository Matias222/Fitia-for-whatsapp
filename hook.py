from fastapi import FastAPI, Request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
from datetime import datetime
from moviepy.editor import AudioFileClip
from bd_functions import insertar_usuario,update_usuario

import gender_guesser.detector as gender
import tempfile
import os
import requests
import supabase
import random
import openai
import json
import time

load_dotenv()

account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
numero_from = os.getenv("numero")
openai.api_key = os.getenv("OPENAI_API_KEY")

client = Client(account_sid, auth_token)

app = FastAPI()


def contador_calorias(nombre,talla,peso,edad,objetivo):
    
    detector = gender.Detector()
    genero=""

    if (detector.get_gender(nombre) == "male"): genero="hombre"
    else: genero="mujer"

    query = {"edad":edad,"peso":peso,"talla":talla,"genero":genero,"objetivos":objetivo}
    
    ej1= {"edad":20,"peso":89,"talla":1.76,"genero":"hombre","objetivo":"Bajar de peso 10k"}
    ej2= {"edad":38,"peso":72,"talla":1.66,"genero":"mujer","objetivo":"Bajar de peso 5k"}

    print(query)

    completion = openai.ChatCompletion.create(
        
        model="gpt-3.5-turbo",
        messages=[
            
            {"role": "system","content": """Eres un nutricionista experto, dado mi edad, peso, talla, genero y objetivos. Calcula la cantidad maxima de calorias que debo consumir en 1 dia y cuantos litros de agua debo tomar, se conciso."""},
            
            {"role": "system", "name":"example_user", "content":str(ej1)},
            {"role": "system", "name": "example_assistant", "content": "{\"Calorias\":2100,\"Agua\":2}"},

            {"role": "system", "name":"example_user", "content":str(ej2)},
            {"role": "system", "name": "example_assistant", "content": "{\"Calorias\":1600,\"Agua\":1.8"},

            {"role":"user","content":str(query)}

        ],
        temperature=0,
        max_tokens=300,
    )

    result = completion.choices[0].message["content"]
    
    print(result)

    return result

def parseo_info(query):

    prompt="""Tu unica funcion es dado el input del usuario, devolver un JSON con cuatro caracteristicas, nombre, peso, talla y edad.
    Usuario: Hola soy Matias, mido 1.77 y peso 86.
    AI: {"nombre":"Matias","talla":1.77,"peso":86}

    Usuario: Buenas tardes me llamo Juan Diego, mi altura es de 2.11 y peso 95kg
    AI: {"nombre":"Juan Diego","talla":2.11,"peso":95}

    Usuario: Hola soy Paolo
    AI: {"nombre":"Paolo"}

    Usuario: Me llamo Diego, tengo 21, mido 1.77 y peso 88
    AI: {"nombre":"Diego","talla":1.77,"peso":88,"edad":21}
    
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

def parseo_openai(query):

    prompt="""Tu unica funcion es dado el input del usuario, devolver un JSON con dos caracteristicas, calorias y litros.
    Usuario: Basándome en los datos que me proporcionaste, para lograr tu objetivo de bajar 10 kilos, deberías consumir alrededor de 2000 calorías al día y tomar al menos 2 litros de agua diariamente. Es importante que tengas en cuenta que estos valores son aproximados y que pueden variar dependiendo de tu nivel de actividad física y otros factores individuales. Además, es recomendable que consultes con un nutricionista para que te brinde una dieta personalizada y adecuada a tus necesidades.
    AI: {"calorias":"2000","litros":2}

    Usuario: Para una mujer de 21 años, con un peso de 89 kg, una talla de 1.76 m y un objetivo de bajar 10 kg, se recomienda un consumo diario de aproximadamente 1800-2000 calorías. Además, se recomienda tomar al menos 1.8 litros de agua al día. Es importante recordar que estos son valores aproximados y que pueden variar según el nivel de actividad física y otros factores individuales. Es recomendable consultar con un nutricionista para obtener una evaluación más precisa y personalizada.  
    AI: {"calorias":"1800-2000","litros":1.8}

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

    guardar_info=False

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
    datos_usuario={}
    objetivo=""

    if(usuario[0]==0):
        mensaje_retornar="Hola soy Wanly, tu amigo nutricionista. Dime tu nombre, edad, peso y talla"
    else:
    

        falta_info=[]

        datos_usuario={"nombre":"","talla":0,"peso":0,"edad":0}

        if(usuario[1]["nombre"]==""): falta_info.append("nombre")
        else: datos_usuario["nombre"]=usuario[1]["nombre"]
   
        for categoria in datos_usuario:
            if(categoria!="nombre"):
                if(usuario[1][categoria]==0): falta_info.append(categoria)
                else: datos_usuario[categoria]=usuario[1][categoria]

        print(datos_usuario)
        print(falta_info)

        if(falta_info==[]):
            print("Usuario ya creado exitosamente")

            objetivo=usuario[1]["objetivo"]
            objetivo_confirmado=usuario[1]["objetivo_confirmado"]

            print(objetivo,objetivo_confirmado)

            if(objetivo_confirmado==True):
                
                print("Todos los datos del usuario confirmados")

                await update_usuario(int(sender_number[10:]),usuario[1]["nombre"],usuario[1]["peso"],usuario[1]["talla"],usuario[1]["edad"],objetivo,True,calorias_dia=1,litros_dia=2.2)

            else:

                if(incoming_msg.lower()=="si"): 

                    plan_nutricional=contador_calorias(usuario[1]["nombre"],usuario[1]["talla"],usuario[1]["peso"],usuario[1]["edad"],usuario[1]["objetivo"])

                    mensaje_retornar=plan_nutricional

                    guardar_info=True

                

                elif(incoming_msg.lower()=="no"): 
                    mensaje_retornar="Digame su objetivo porfavor"
                    await update_usuario(int(sender_number[10:]),datos_usuario["nombre"],datos_usuario["peso"],datos_usuario["talla"],datos_usuario["edad"],objetivo)
                
                else:
                    #Pedir de nuevo el objetivo
                    objetivo=incoming_msg
                    mensaje_retornar="Su objetivo a alcanzar es, \""+str(objetivo)+"\", es correcto? Para confirmar escriba Si, caso contrario, No"
                    await update_usuario(int(sender_number[10:]),datos_usuario["nombre"],datos_usuario["peso"],datos_usuario["talla"],datos_usuario["edad"],objetivo)

        else:

            dic=parseo_info(incoming_msg)

            if(dic=={}): mensaje_retornar="Hubo un error porfavor vuelva a introducir sus datos"
            else:
                
                nuevo_falta_info=[]

                if("nombre" in falta_info):
                    if "nombre" not in dic: nuevo_falta_info.append("nombre")
                    else: datos_usuario["nombre"]=dic["nombre"]
            
                for categoria in datos_usuario:
                    if(categoria!="nombre"):
                        if(categoria in falta_info):
                            if categoria not in dic:  nuevo_falta_info.append(categoria)
                            else: datos_usuario[categoria]=dic[categoria]

                print(nuevo_falta_info)
                nombre=datos_usuario["nombre"]

                if(len(nuevo_falta_info)==0): mensaje_retornar=f"Genial, {nombre}, ahora dime cuales son tus objetivos alimenticios"
                elif(len(nuevo_falta_info)==1): mensaje_retornar=f"Porfavor indicame tu {nuevo_falta_info[0]}"
                elif(len(nuevo_falta_info)==2): mensaje_retornar=f"Porfavor indicame tu {nuevo_falta_info[0]} y {nuevo_falta_info[1]}"
                elif(len(nuevo_falta_info)==3): mensaje_retornar=f"Porfavor indicame tu {nuevo_falta_info[0]}, {nuevo_falta_info[1]} y {nuevo_falta_info[2]}"
                else: mensaje_retornar="Ya p no me dijiste tus datos"

                await update_usuario(int(sender_number[10:]),nombre,datos_usuario["peso"],datos_usuario["talla"],datos_usuario["edad"])
  

    message = client.messages \
    .create(
            body=mensaje_retornar,
            from_=numero_from,
            to=sender_number
        )

    if(guardar_info==True):
        parseo_dic=parseo_openai(mensaje_retornar)

        print(parseo_dic)

        await update_usuario(int(sender_number[10:]),datos_usuario["nombre"],datos_usuario["peso"],datos_usuario["talla"],datos_usuario["edad"],objetivo,True,parseo_dic["calorias"],parseo_dic["litros"])
        

    return "Hello"
