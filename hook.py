from fastapi import FastAPI, Request,Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
import datetime
from openai.embeddings_utils import get_embedding, cosine_similarity
from bd_functions import insertar_usuario,update_usuario, update_estado, insertar_user_history, update_calorias,recuperar_comida_tarde,recuperar_comida_noche,recuperar_comida_temprano
from aux_functions import audio_2_text, identificar_confirmacion, verificar_datos_bd, verificar_datos_usuario, guardar_plan_personalizado
from openai_calls import plan_personalizado, parseo_info, segmentador, sugerencias
from identificador import identificar_comida


import os
import openai
import random
import numpy as np
import pandas as pd


load_dotenv()

account_sid = os.getenv("account_sid")
auth_token = os.getenv("auth_token")
numero_from = os.getenv("numero")
openai.api_key = os.getenv("OPENAI_API_KEY")

client = Client(account_sid, auth_token)

app = FastAPI()


datafile_path = "comidas_embeddings.csv"

df = pd.read_csv(datafile_path)
df["embedding"] = df.embedding.apply(eval).apply(np.array)


def conteo_calorias_service(df, product_description, n=3, pprint=True):
    product_embedding = get_embedding(
        product_description,
        engine="text-embedding-ada-002"
    )
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, product_embedding))

    results = (
        df.sort_values("similarity", ascending=False)
        .head(n)
        .combined.str.replace("Platos: ", "")
        .str.replace("; Calorias:", ": ")
    )
    pruebas = (
        df.sort_values("similarity", ascending=False)
        .head(n).Calorias
    )
    if pprint:
        for r in results:
            print(r[:200])
            print()

    return pruebas.iloc[0]


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

    if sender_number == 'SECRETO':
        mensaje_retornar = incoming_msg
        numeros = message_body.getlist('numeros')
        for numero in numeros:
            numero_enviar = 'whatsapp:+' + numero
            message = client.messages.create(body=mensaje_retornar,from_=numero_from,to=numero_enviar)
    else:
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

                        print("Segmentador",tipo)

                        if(tipo=="Reporte de comidas" or tipo=="Reporte de comidas."): #TO DO
                            #TO DO
                            print("Reporte de comidas")

                            datos_comida=await insertar_user_history(id_numero=int(sender_number[10:]))

                            calorias_day=datos_comida[1]["calorias"]

                            json_comidas=await identificar_comida(sender_number,incoming_msg)

                            print("Hook",json_comidas)

                            calorias=0

                            mensaje_retornar=""""""

                            alimentos_arr=[]

                            for i in json_comidas:
                                print(i)
                                conteo_alimento=0
                                if(i=="mayonesa"): conteo_alimento=119
                                else: conteo_alimento=int(conteo_calorias_service(df,i,n=3))
                                cadena="Alimento "+i.capitalize()+" Calorias "+str(conteo_alimento)
                                print("Alimento "+i+" Calorias "+str(conteo_alimento))
                                calorias=conteo_alimento*int(json_comidas[i])+calorias
                                alimentos_arr.append(cadena)

                            my_string = '\n'.join(alimentos_arr)

                            cal_total=calorias_day+calorias
                            #mensaje_retornar="Su consumo de calorias hasta ahora era de %d"%calorias_day +"\n" "Con lo que acaba de ingerir aumento a %d"%cal_total
                            my_string=my_string+"\n"+"Su consumo de calorias hasta ahora era de %d"%calorias_day +"\n" "Con lo que acaba de ingerir aumento a %d"%cal_total

                            mensaje_retornar=my_string

                            funciones_al_finalizar.append((update_calorias,int(sender_number[10:]),int(calorias+calorias_day)))

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

#apis testeadas

@app.post("/insert-user")
async def insert_user():
    try:
        numero_aleatorio = random.randint(900000000, 999999999)
        nombres = ["Juan", "María", "Pedrito", "Ana", "Luis", "Carla"]
        await insertar_usuario("51" + str(numero_aleatorio), random.choice(nombres),
                         peso=random.randint(30, 120), talla=round(random.uniform(0.5, 2.5), 2),
                         objetivo="", objetivo_confirmado=random.choice([True, False]),
                         edad=random.randint(10, 100))
        
        # En caso de éxito, enviar una respuesta con un mensaje de éxito
        return {"message": "Usuario insertado correctamente"}
    
    except Exception as e:
        # En caso de error, enviar una respuesta con un mensaje de error
        return Response(content="Error al insertar el usuario", status_code=500)
    
@app.post("/update-user")
async def update_user():
    try:        
        numeros_prueba=["51951257655"," 51973633360","51951733905"]
        numero_aleatorio = random.randint(0, len(numeros_prueba)) 
        await update_usuario(numero_aleatorio, "Modificado",
                         peso=40, talla=2.1,
                         objetivo="Bajar de peso", objetivo_confirmado=True,
                         edad=18)
        
        # En caso de éxito, enviar una respuesta con un mensaje de éxito
        return {"message": "Usuario Modificado correctamente"}
    
    except Exception as e:
        # En caso de error, enviar una respuesta con un mensaje de error
        return Response(content="Error al Modificar el usuario", status_code=500)    
    
@app.post("/calculate-calories")
async def calculate_calories():
    try:
        new_cal = random.randint(0,500)
        numero="51926883329"
        await update_calorias(numero,new_cal)
        
        # En caso de éxito, enviar una respuesta con un mensaje de éxito
        return {"message": "Calorias actualizadas"}
    
    except Exception as e:
        # En caso de error, enviar una respuesta con un mensaje de error
        return Response(content="Las calorias no fueron actualizadas", status_code=500)


@app.post("/recovery-morning")
async def recovery_morning():
    try:
        numero="51927144823"
        await recuperar_comida_temprano(numero,datetime.datetime.now())    
        return {"message": "Desayuno guardado"}
    
    except Exception as e:
        # En caso de error, enviar una respuesta con un mensaje de error
        return Response(content="No se pudo obtener el desayuno", status_code=500)

@app.post("/recovery-afternon")
async def recovery_afternon():
    try:
        numero="51999999999"
        await recuperar_comida_tarde(numero,datetime.datetime.now())    
        return {"message": "Almuerzo guardado"}
    
    except Exception as e:
        # En caso de error, enviar una respuesta con un mensaje de error
        return Response(content="No se pudo obtener el Almuerzo", status_code=500)

@app.post("/recovery-night")
async def recovery_night():
    try:
        numero="51999999999"
        await recuperar_comida_noche(numero,datetime.datetime.now())    
        return {"message": "Cena guardado"}
    
    except Exception as e:
        # En caso de error, enviar una respuesta con un mensaje de error
        return Response(content="No se pudo obtener el Cena", status_code=500)
    

@app.post("/verified-dates")
async def recovery_night():
    try:
        datos_user1 = {"nombre": "", "talla": 0, "peso": 0, "edad": 0}
        datos_user_nuevo = {"nombre": "", "talla": 1.77, "peso": 70, "edad": 23}
        verificar_datos_bd(
            datos_usuario=datos_user1, datos_nuevo=datos_user_nuevo
        )
    
        return {"message": "Datos verificados correctamente"}
    
    except Exception as e:
        # En caso de error, enviar una respuesta con un mensaje de error
        return Response(content="Los datos no concuerdan", status_code=500)
    

@app.post("/insert-user-history")
async def insert_user_history():
    try:
        insertar_user_history(
            "51999999999",
            1372,
            0.0,
            "",
            [{"cereal": 1, "vaso de yogurt": 1}],
            [{"Lomo saltado": 1, "Coca Cola": 1}],
            [],
        )
        
    
        return {"message": "Datos insertados correctamente"}
    
    except Exception as e:
        # En caso de error, enviar una respuesta con un mensaje de error
        return Response(content="Los datos no fueron insertados", status_code=500)
