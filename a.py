import openai
import os
from dotenv import load_dotenv
import requests
import asyncio
from pydub import AudioSegment
from moviepy.editor import AudioFileClip
from bd_functions import insertar_usuario
from bd_functions import insertar_user_history
from bd_functions import update_user_history

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

parseo_info("Hola soy Luis")




#pruebas user_history

#id_numero,dia="",calorias=0.0,litros=0.0,chat="",comidas=[]
async def my_async_function():
    return await insertar_user_history("51926883329","2023-06-02",74.25,10,"Hoy tome bastante agua como 10lt",["Arroz con pollo","Pan con mayonesa"])

def validar(query):
     # Create an event loop
    loop = asyncio.get_event_loop()
    # Run the async function
    user=loop.run_until_complete(my_async_function())
    print("========== user ===========",user[0])
    # Close the event loop
    loop.close()


#id_numero,dia="",calorias=0.0,litros=0.0,chat="",comidas=[]
async def my_async_function2():
    return await update_user_history("51926883329","2023-06-02",200,2,"Hoy comi mucho, estoy lleno",["Loma saltado","Chaufa","Papa","Pizza"])

def validar2(query):
     # Create an event loop
    loop = asyncio.get_event_loop()
    # Run the async function
    user=loop.run_until_complete(my_async_function2())
    print("=====Listo==============")
    # Close the event loop
    loop.close()

#Si quieres probar el codigo, ponlo ahi abajo y compila el archivo
if __name__ == "__main__":
        #prueba validar ingreso user_history
        #validar("")

        #Prueba de validar update
        validar2("")
