from dotenv import load_dotenv
import openai
import os
import json
import gender_guesser.detector as gender

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")



def plan_personalizado(nombre,talla,peso,edad,objetivo):
    
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
            
            {"role": "system","content": """Eres un nutricionista experto, dado mi edad, peso, talla, genero y objetivos. Calcula la cantidad maxima de calorias que debo consumir en 1 dia y cuantos litros de agua debo tomar, se conciso pero factualmente correcto."""},
            
            {"role": "system", "name":"example_user", "content":str(ej1)},
            {"role": "system", "name": "example_assistant", "content": "100,Agua:2}"},

            {"role": "system", "name":"example_user", "content":str(ej2)},
            {"role": "system", "name": "example_assistant", "content": "600,Agua:1.8"},

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
    
    ans={}
    try: ans=json.loads(result)
    except: ans={}

    return ans


def parseo_calorias(query):

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



def segmentador(query):


    plantilla="No me interesa tu opinion, solo clasifica el texto. Usuario: "

    completion = openai.ChatCompletion.create(
        
        model="gpt-3.5-turbo",
        messages=[
            
            {"role": "system","content": "Clasifica el siguiente texto en 4 categorias. Reporte de comidas (Cuando el usuario dice que ha comido), Cambio de objetivo (Cuando el usuario quiere cambiar de objetivo), Consejo nutricional (Cuando el usuario busca un consejo) y Otros (Cuando es ninguno de las anteriores)"""},
            
            {"role": "system", "name":"example_user", "content":plantilla+"Quisiera cambiar de objetivo"},
            {"role": "system", "name": "example_assistant", "content": "Cambio de objetivo"},

            {"role": "system", "name":"example_user", "content":plantilla+"Almorce 1/4 de pollo a la brasa con full papas"},
            {"role": "system", "name": "example_assistant", "content": "Reporte de comidas"},

            {"role": "system", "name":"example_user", "content":plantilla+"Cene arroz con leche"},
            {"role": "system", "name": "example_assistant", "content": "Reporte de comidas"},

            {"role": "system", "name":"example_user", "content":plantilla+"Creo que cenare una salchipapa que me recomiendas?"},
            {"role": "system", "name": "example_assistant", "content": "Consejo nutricional"},

            {"role": "system", "name":"example_user", "content":plantilla+"Comi tallarines verdes con huancaina"},
            {"role": "system", "name": "example_assistant", "content":"Reporte de comidas"},

            {"role": "system", "name":"example_user", "content":plantilla+"Que tan saludable es tomar gaseosa?"},
            {"role": "system", "name": "example_assistant", "content": "Consejo nutricional"},

            {"role": "system", "name":"example_user", "content":plantilla+"No me siento a gusto con mi plan actual"},
            {"role": "system", "name": "example_assistant", "content": "Cambio de objetivo"},

            {"role": "system", "name":"example_user", "content":plantilla+"Desayune dos huevos fritos con jamon"},
            {"role": "system", "name": "example_assistant", "content": "Reporte de comidas"},

            {"role": "system", "name":"example_user", "content":plantilla+"Es sano comer mayonesa?"},
            {"role": "system", "name": "example_assistant", "content": "Consejo nutricional"},

            {"role":"user","content":plantilla+str(query)}
        ],
        temperature=0,
        max_tokens=300,
    )


    result = completion.choices[0].message["content"]

    print(result)
        
    #print(ans)
    return result

def sugerencias(query):
    # promp = """Tu principal funcion es brindarle una sugerencia o recomendacion al usuario como si tu fueras un nutricionista experto, es decir, el usuario te brindara un alimento y tu debes de darle una perspectiva clara, como un nutricionista experto, mencionando las ventas y desventajas de consumirla y finalmente concluyendo en si es correcto consumirla o no. 
    # Usuario: Se me antojo tomarme una gaseosa, ¿Deberia tomarla?
    # AI: {"Consejo":"La gaseosa tiene un aproximado 160 calorias, ademas que esta puede generar cansancio en tu cuerpo, falta de apetito y flatulencias, por ende no te recomiendo que la consumas"}
    
    # Usuario: Tengo ganas de comer una barra de chocolate Sublime ¿Te parece correcto que la coma?
    # AI: {"Consejo":"Una barra de chocolate tiene aproximadamente 550 calorias, por ende es alta en azucares y sumandole los productos artificiales que esta pueda contener, no es recomendable consumirla en exceso."}

    # Usuario: ¿Esta bien almorzar un plato de fideos acompañado de una ensalada?
    # AI: {"Consejo":"Los platos de fideos son altos en carbohidratos y añadiendole la ensalada se logra un correcto balance en las proteinas, me parece una eleccion correcta para el almuerzo."}

    # Usuario: Es la hora del desayuno, ¿Te parece bien que desayune un plato de cereales con leche?
    # AI: {"Consejo":"Los cereales se caracterizan por tener un alto porcentaje de azucares y sumandole las proteinas que pueda obtener la leche, te podria decir que si podrias consumirla pero no en exceso."}

    # Usuario: Voy a cenar una hamburguesa con papas fritas ¿Te parece correcto consumirla como cena?
    # AI: {"Consejo":"Las hamgurguesa con papas fritas tienen un alto porcentaje de grasas saturadas y elementos artificiales, no son la mejor opcion para cenar de acorde a tus objetivos."}

    # Usuario: Son las 7:40 pm y se me antojo comer un plato de avena con frutas ¿Deberia?
    # AI: {"Consejo":"La avena se caracteriza por sus altos niveles de fibra y minerales, asimismo, la fruta es el acompañante perfecto para enriquecer el cuerpo de vitaminas, si lo recomendaria que lo consumas."}

    # Usuario: Son las 2:30 am y tengo un antojo de una ensalada de frutas ¿Que opinas?
    # AI: {"Consejo":"El momento del dia o el orden de los alimentos como la fruta no tienen ninguna influencia en los efectos beneficios de este alimento, si te recomeindo comerla pero no en exceso"}

    # Usuario: ¿Cual es tu perspectiva si te digo que voy a comer una sopa de verduras?
    # AI: {"Consejo":"La sopa de verduras contiene un indice alto de proteinas y es rica en vitaminas, me parece correcto que la vayas a comer"}

    # Usuario: %s
    # AI:"""(query)

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[

            {"role":"system", "content":"""Tu principal funcion es brindarle una sugerencia o recomendacion al usuario como si tu fueras un nutricionista experto, es decir, el usuario te brindara un alimento y tu debes de darle una perspectiva clara, como un nutricionista experto, mencionando las ventas y desventajas de consumirla y finalmente concluyendo en si es correcto consumirla o no."""},
            
            {"role":"system", "name":"example_user", "content":"""Se me antojo tomarme una gaseosa, ¿Deberia tomarla?"""},
            {"role":"system", "name":"example_assistant", "content":"La gaseosa tiene un aproximado 160 calorias, ademas que esta puede generar cansancio en tu cuerpo, falta de apetito y flatulencias, por ende no te recomiendo que la consumas."},

            {"role":"system", "name":"example_user", "content":"""Tengo ganas de comer una barra de chocolate Sublime ¿Te parece correcto que la coma?"""},
            {"role":"system", "name":"example_assistant", "content":"Una barra de chocolate tiene aproximadamente 550 calorias, por ende es alta en azucares y sumandole los productos artificiales que esta pueda contener, no es recomendable consumirla en exceso."},

            {"role":"system", "name":"example_user", "content":"""¿Esta bien almorzar un plato de fideos acompañado de una ensalada?"""},
            {"role":"system", "name":"example_assistant", "content":"Los platos de fideos son altos en carbohidratos y añadiendole la ensalada se logra un correcto balance en las proteinas, me parece una eleccion correcta para el almuerzo."},

            {"role":"system", "name":"example_user", "content":"""Es la hora del desayuno, ¿Te parece bien que desayune un plato de cereales con leche?"""},
            {"role":"system", "name":"example_assistant", "content":"Los cereales se caracterizan por tener un alto porcentaje de azucares y sumandole las proteinas que pueda obtener la leche, te podria decir que si podrias consumirla pero no en exceso."},

            {"role":"system", "name":"example_user", "content":""" Voy a cenar una hamburguesa con papas fritas ¿Te parece correcto consumirla como cena?"""},
            {"role":"system", "name":"example_assistant", "content":"Las hamgurguesa con papas fritas tienen un alto porcentaje de grasas saturadas y elementos artificiales, no son la mejor opcion para cenar de acorde a tus objetivos."},

            {"role":"system", "name":"example_user", "content":"""Son las 7:40 pm y se me antojo comer un plato de avena con frutas ¿Deberia?"""},
            {"role":"system", "name":"example_assistant", "content":"La avena se caracteriza por sus altos niveles de fibra y minerales, asimismo, la fruta es el acompañante perfecto para enriquecer el cuerpo de vitaminas, si lo recomendaria que lo consumas."},

            {"role":"system", "name":"example_user", "content":"""Son las 2:30 am y tengo un antojo de una ensalada de frutas ¿Que opinas?"""},
            {"role":"system", "name":"example_assistant", "content":"El momento del dia o el orden de los alimentos como la fruta no tienen ninguna influencia en los efectos beneficios de este alimento, si te recomeindo comerla pero no en exceso."},

            {"role":"system", "name":"example_user", "content":"""¿Cual es tu perspectiva si te digo que voy a comer una sopa de verduras?"""},
            {"role":"system", "name":"example_assistant", "content":"La sopa de verduras contiene un indice alto de proteinas y es rica en vitaminas, me parece correcto que la vayas a comer."},
        
            {"role":"user", "content":str(query)}
        ],
        temperature=0,
        max_tokens=300,
    )

    result = completion.choices[0].message["content"]

    print(result)

    return result