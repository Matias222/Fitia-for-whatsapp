from fastapi import FastAPI, Request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
from datetime import datetime

from bd_functions import insertar_usuario,update_usuario, update_estado, insertar_user_history, update_calorias
from aux_functions import audio_2_text, identificar_confirmacion, verificar_datos_bd, verificar_datos_usuario, guardar_plan_personalizado
from openai_calls import plan_personalizado, parseo_info, segmentador, sugerencias
from identificador import identificar_comida


import os
import openai
import random

load_dotenv()

account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
numero_from = os.getenv("numero")
openai.api_key = os.getenv("OPENAI_API_KEY")

client = Client(account_sid, auth_token)

app = FastAPI()




def leer_objetivo(incoming_msg,datos_usuario,sender_number,funciones_al_finalizar,objetivo):

    clasificar_afirmacion=identificar_confirmacion(incoming_msg)

    print(incoming_msg,datos_usuario,sender_number,funciones_al_finalizar)
    print(clasificar_afirmacion)

    if(clasificar_afirmacion=="SI"): 

        plan_nutricional=plan_personalizado(datos_usuario["nombre"],datos_usuario["talla"],datos_usuario["peso"],datos_usuario["edad"],objetivo)

        funciones_al_finalizar.append((guardar_plan_personalizado,plan_nutricional,sender_number,datos_usuario,objetivo))

        funciones_al_finalizar.append((update_estado,int(sender_number[10:]),"INICIO"))

        return plan_nutricional

    elif(clasificar_afirmacion=="NO"): 

        funciones_al_finalizar.append((update_usuario,int(sender_number[10:]),datos_usuario["nombre"],datos_usuario["peso"],datos_usuario["talla"],datos_usuario["edad"],objetivo))

        return "Digame su objetivo porfavor"

    else:

        #Pedir de nuevo el objetivo
        objetivo=incoming_msg
        
        funciones_al_finalizar.append((update_usuario,int(sender_number[10:]),datos_usuario["nombre"],datos_usuario["peso"],datos_usuario["talla"],datos_usuario["edad"],objetivo))

        return "Su objetivo a alcanzar es, \""+str(objetivo)+"\", es correcto?"


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
        transcription = ""

        if media_type.startswith('audio/'):
           
            audio_file = await request.form()
           
            transcription = audio_2_text(audio_file)

            mensaje_retornar = "Received an audio file. Audio saved as .mp3."
        else:
            mensaje_retornar = "Received a media file. Currently, only audio files are supported."

        incoming_msg=transcription
        mensaje_retornar="audio"
   
    print(sender_number[10:])


    funciones_al_finalizar=[]
    usuario=await insertar_usuario(int(sender_number[10:]))
    datos_usuario=usuario[1]
    objetivo=""
    
    
    if("estado" in datos_usuario and datos_usuario["estado"]=="CAMBIO DE OBJETIVO"):
        
        objetivo=datos_usuario["objetivo"]
        mensaje_retornar=leer_objetivo(incoming_msg,datos_usuario,sender_number,funciones_al_finalizar,objetivo)

    else:

        if(usuario[0]==0):
        
            mensaje_retornar="Hola soy Wanly, tu amigo nutricionista. Dime tu nombre, edad, peso y talla"
        
        else:


            datos_usuario={"nombre":"","talla":0,"peso":0,"edad":0}

            falta_info=verificar_datos_bd(datos_usuario,usuario[1])

            if(falta_info==[]):
                
                objetivo=usuario[1]["objetivo"]
                objetivo_confirmado=usuario[1]["objetivo_confirmado"]

                print(objetivo,objetivo_confirmado)

                if(objetivo_confirmado==True):
                    
                    #Antes del login el bot no es inteligente

                    tipo=segmentador(incoming_msg)

                    if(tipo=="Reporte de comidas"): #TO DO
                        #TO DO
                        print("Reporte de comidas")


                        datos_comida=await insertar_user_history(id_numero=int(sender_number[10:]))

                        calorias_day=datos_comida[1]["calorias"]

                        await identificar_comida(sender_number,incoming_msg)

                        calorias=random.randint(100,500)

                        mensaje_retornar="Su consumo de calorias hasta ahora era de %d"%calorias_day +"\n" "Con lo que acaba de ingerir aumento a %d"%calorias

                        funciones_al_finalizar.append((update_calorias,int(sender_number[10:]),calorias+calorias_day))

                    elif(tipo=="Cambio de objetivo"): #DONE
                        
                        print("Cambio de objetivo")

                        mensaje_retornar="Digame cual es su objetivo porfavor"

                        funciones_al_finalizar.append((update_estado,int(sender_number[10:]),"CAMBIO DE OBJETIVO"))

                    elif(tipo=="Consejo nutricional"): #TO DO
                        #Buscar las calorias de la comida a comer con Embeddings + wrapper
                        mensaje_retornar = sugerencias(incoming_msg)
                        print("Consejo nutricional:")
                        print(mensaje_retornar)

                    else: #TO DO
                        #Query a OpenAI
                        print("Otrossss")
                        mensaje_retornar="\U0001F600"

                else:
                    
                    mensaje_retornar=leer_objetivo(incoming_msg,datos_usuario,sender_number,funciones_al_finalizar,objetivo)

            else:

                dic_datos=parseo_info(incoming_msg)
                
                if(dic_datos=={}): mensaje_retornar="Hubo un error porfavor vuelva a introducir sus datos"
                else:
                    
                    nuevo_falta_info=verificar_datos_usuario(datos_usuario,dic_datos,falta_info)

                    nombre=datos_usuario["nombre"]

                    if(len(nuevo_falta_info)==0): mensaje_retornar=f"Genial, {nombre}, ahora dime cuales son tus objetivos alimenticios"
                    elif(len(nuevo_falta_info)==1): mensaje_retornar=f"Porfavor indicame tu {nuevo_falta_info[0]}"
                    elif(len(nuevo_falta_info)==2): mensaje_retornar=f"Porfavor indicame tu {nuevo_falta_info[0]} y {nuevo_falta_info[1]}"
                    elif(len(nuevo_falta_info)==3): mensaje_retornar=f"Porfavor indicame tu {nuevo_falta_info[0]}, {nuevo_falta_info[1]} y {nuevo_falta_info[2]}"
                    else: mensaje_retornar="Ya p no me dijiste tus datos"
                    
                    funciones_al_finalizar.append((update_usuario,int(sender_number[10:]),nombre,datos_usuario["peso"],datos_usuario["talla"],datos_usuario["edad"]))
        
    message = client.messages.create(body=mensaje_retornar,from_=numero_from,to=sender_number)
    
    for call in funciones_al_finalizar:
        function, *args = call
        await function(*args)
