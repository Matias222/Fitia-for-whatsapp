from moviepy.editor import AudioFileClip
from openai_calls import transcribe_audio, parseo_calorias
from bd_functions import update_usuario

import random
import os
import requests

def audio_2_text(audio_file):  

    audio_data = audio_file['MediaUrl0']


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

    return transcription

def identificar_confirmacion(query):
    
    query=query.lower()

    query=query.split()

    afirmativo=["si","sip","correcto","aja","afirmativo"]
    negativo=["no","nop","incorrecto","negativo"]

    for i in afirmativo:
        if(i in query): return "SI"

    for i in negativo:
        if(i in query): return "NO"

    return "NN"

def verificar_datos_bd(datos_usuario,datos_nuevo):

    falta_info=[]

    for categoria in datos_usuario:
        
        val=datos_nuevo[categoria]
        if(val=="" or val==0): falta_info.append(categoria)
        else: datos_usuario[categoria]=val

    print(datos_usuario,datos_nuevo)

    return falta_info

def verificar_datos_usuario(datos_usuario,datos_nuevo,antigua):

    falta_info=[]

    for categoria in datos_usuario:
            
        if(categoria in antigua):
            if(categoria not in datos_nuevo): falta_info.append(categoria)
            else: datos_usuario[categoria]=datos_nuevo[categoria]

    print(datos_usuario,datos_nuevo,falta_info)

    return falta_info


async def guardar_plan_personalizado(mensaje_retornar,sender_number,datos_usuario,objetivo):
    
    parseo_dic=parseo_calorias(mensaje_retornar)

    print(parseo_dic)

    await update_usuario(int(sender_number[10:]),datos_usuario["nombre"],datos_usuario["peso"],datos_usuario["talla"],datos_usuario["edad"],objetivo,True,parseo_dic["calorias"],parseo_dic["litros"])
