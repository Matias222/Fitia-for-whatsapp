import openai
import os
from dotenv import load_dotenv
import requests
import asyncio
from pydub import AudioSegment
from moviepy.editor import AudioFileClip
from bd_functions import insertar_usuario,update_usuario
import gender_guesser.detector as gender


load_dotenv()

openai.api_key= os.getenv("OPENAI_API_KEY")



async def my_async_function():
    return await insertar_usuario("51927144823")

d = gender.Detector()

def calcular_calorias(query):
    loop = asyncio.get_event_loop()
    user=loop.run_until_complete(my_async_function())
    print(user)
    nombre= user[1]["nombre"]
    peso = user[1]["peso"]
    edad = 20
    actividad="muy activa"
    talla = user[1]["talla"]
    objetivo = user[1]["objetivo"]
    confirmado = user[1]["objetivo_confirmado"]
    numero = user[1]["numero"]
    if (d.get_gender(nombre) == "male"):
        genero="hombre"
    else:
        genero="mujer"
    
    query = f"calculame las calorias diarias si soy un {genero}, peso {peso}, mido {talla}, tengo {edad} años y tengo una actividad fisica {actividad} y mi objetivo es {objetivo}"
    
    print(query)

    completion = openai.ChatCompletion.create(
        
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": """Calcula las calorias diarias usando mi genero, peso, talla, edad y actividad fisica, usando la formula de Harris-Benedict y multiplicar el resultado por el factor de actividad correspondiente.
        Usuario: calculame las calorias diarias si soy un hombre, peso 65, mido 1.69, tengo 20 años y tengo una actividad fisica muy activa y mi objetivo es bajar 20 kilos
        AI: {"Genero":"hombre","Peso":65,"Talla":1.69,"Edad":20,"Calorias": 2873.42,"Objetivo":"objetivo es bajar 20 kilos"}

        Usuario: %s
        AI: """%(query),
        }],
        temperature=0,
        max_tokens=100,
    )
    result = completion.choices[0].message["content"]
    print(result)
    
    #loop.run_until_complete(update_usuario(number=numero,nombre=nombre,peso=peso,talla=talla,objetivo=objetivo,confirmado=confirmado,calorias=result.split(",")[4].split(":")[1],litros_agua=0.0))
    loop.close()
    return result


calcular_calorias("")
