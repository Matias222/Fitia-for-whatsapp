import openai
import os
from dotenv import load_dotenv
import requests
import asyncio
from pydub import AudioSegment
from moviepy.editor import AudioFileClip
from bd_functions import insertar_usuario, update_usuario
import gender_guesser.detector as gender



load_dotenv()

openai.api_key= os.getenv("OPENAI_API_KEY")


def transcribe_audio(audio_file):

    audio_file = open(audio_file, "rb")
    
    transcript = openai.Audio.transcribe("whisper-1", audio_file,language="es")
    transcript = str(transcript["text"])

    print("Transcription complete",transcript)

    return transcript

"""

clip = AudioFileClip("574229777.webm")

# Export the audio as MP3
clip.write_audiofile("jaaa.mp3", codec="mp3")

transcribe_audio("jaaa.mp3")

"""

def bienvenida():
    prompt="""Eres un experto en vida saludable y nutricion, tu nombre es David. Existes para ayudar al usuario a conseguir sus objetivos alimenticios. Haz que el usuario se introduzca, diga su NOMBRE, TALLA y PESO.
    Usuario: Hola
    David: """

    response = openai.Completion.create(
                model='text-davinci-003',
                prompt=prompt,
                temperature=0.7,
                max_tokens= 256
        )
    result = response.choices[0]['text']

    print(result)

    return result

#bienvenida()

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

    print(prompt)

    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=prompt,
        temperature=0,
        max_tokens= 256
    )
    
    result = response.choices[0]['text']

    print(result)

    return result

#parseo_info("Hola soy Luis")



# SECCION CALCULAR CALORIAS POR DIA
d = gender.Detector()


async def my_async_function():
    return await insertar_usuario("51993211937","Marcos",80,1.8)

async def update_data_user(number,nombre,peso,talla,objetivo,confirmado,calorias, litros_agua):
    return await update_usuario(number,nombre=nombre,peso=float(peso),talla=float(talla),objetivo=objetivo,objetivo_confirmado=confirmado,
                                calorias=float(calorias),litros_agua=float(litros_agua))

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
    
    loop.run_until_complete(update_data_user(number=numero,nombre=nombre,peso=peso,talla=talla,objetivo=objetivo,confirmado=confirmado,calorias=result.split(",")[4].split(":")[1],litros_agua=0.0))
    loop.close()
    return result

def calcular_litros_agua(query):
    loop = asyncio.get_event_loop()
    user=loop.run_until_complete(my_async_function())
    nombre= user[1]["nombre"]
    peso = user[1]["peso"]
    edad = 20
    actividad="muy activa"
    talla = user[1]["talla"]
    objetivo = user[1]["objetivo"]
    confirmado = user[1]["objetivo_confirmado"]
    numero = user[1]["numero"]
    calorias = user[1]["calorias_dia"]
    
    
    if (d.get_gender(nombre) == "male"):
        genero="hombre"
    else:
        genero="mujer"
    query = f"calculame cuanta cantidad maxima de litros de agua debo tomar al dia si soy un {genero}, tengo un peso de {peso} kg, talla de {talla} y mi objetivo es {objetivo}"
    
    completion = openai.ChatCompletion.create(
        
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": """calculame cuanta cantidad maxima de litros de agua debo tomar al dia usando mi genero, peso, talla y mis objetivos.
        Usuario: calculame cuanta cantidad maxima de litros de agua debo tomar al dia si soy un hombre, tengo un peso de 65 kg, talla de 1.69 y mi objetivo es bajar 10 kg
        AI: {"Genero":"hombre","Peso":65,"Talla":1.69,"Litros de agua": 2.275 litros,"Objetivo":"objetivo es bajar 10 kilos"}

        Usuario: %s
        AI: """%(query),
        }],
        temperature=0,
        max_tokens=100,
    )
    result = completion.choices[0].message
    litros = completion.choices[0].message["content"].split(",")[3].split(":")[1].split(" ")[1]
    print(result)
    loop.run_until_complete(update_data_user(number=numero,nombre=nombre,peso=peso,talla=talla,objetivo=objetivo,confirmado=confirmado,calorias=calorias,litros_agua=litros))
    loop.close()
    return result







#Si quieres probar el codigo, ponlo ahi abajo y compila el archivo
if __name__ == "__main__":
    #recuperar_alimento_texto("Acabo de jamear pan con pollo")
    #bienvenida()
    #calcular_calorias("")
    calcular_litros_agua("")


    