import openai
import os
from dotenv import load_dotenv
import requests
import asyncio
from pydub import AudioSegment
from moviepy.editor import AudioFileClip
from bd_functions import insertar_usuario,update_usuario
import gender_guesser.detector as gender
import json

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

ans=contador_calorias("Matias",1.76,89,21,"Bajar 10 kilos")
parseo_openai(ans)