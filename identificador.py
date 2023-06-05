from aux_verbos import keyWords_especificos,keyWords_confusos,almuerzo_palabras,cena_palabras,desayuno_palabras
from bd_functions import (
    existe_usuario,
    existe_user_history_en_fecha,
    recuperar_comida_noche,
    recuperar_comida_temprano,
    recuperar_comida_tarde,
    update_user_history,
    insertar_user_history
)

import openai
import json
import datetime
import asyncio

def recuperar_alimento_texto(query):
    prompt="""Tu unica funcion es dado el input del usuario, devolver un JSON con una caracteristica, la comida o alimento que indica la persona.
    Usuario: Hoy he comido arroz con pollo con papa a la huancaina.
    AI: {"Alimento": "arroz con pollo con papa a la huancaina"}

    Usuario: He preparado lomo saltado con mucha cebolla
    AI: {"Alimento": "lomo saltado con mucha cebolla"}

    Usuario: He consumido una hamburguesa de carne con papas
    AI: {"Alimento":"hamburguesa de carne con papas"}
    
    Usuario: Me alimente con un cau cau de mondongo
    AI: {"Alimento":"cau cau de mondongo"}
    
    Usuario: Acabo de comer anticuchos con salsa de aji
    AI: {"Alimento":"anticuchos con salsa de aji"}
    
    Usuario: He desayunado cereales de chocolate con yogur de fresa
    AI: {"Alimento":"cereales de chocolate con yogur de fresa"}
    
    Usuario: Almorce sopa de verduras y lentejas 
    AI: {"Alimento":"sopa de verduras y lentejas"}
    
    Usuario: Acabo de cenar tostadas con mantequilla y mermelada
    AI: {"Alimento":"tostadas con mantequilla y mermelada"}
    
    Usuario: Hoy almorce
    AI: {"Alimento":""}
    
    Usuario: Hoy no desayune
    AI: {"Alimento":""}
    
    Usuario: No comi nada
    AI: {"Alimento":""}
    
    Usuario: Hoy almorcepapa a la huancaina
    AI: {"Alimento":"papa a la huancaina"}
    
    Usuario: Hoy comiarroz con pollo
    AI: {"Alimento":"arroz con pollo"}
    
    Usuario: Hoy me dieron de comerpan conpollo
    AI: {"Alimento":"pan con pollo"}
    
    Usuario: Comi una torta de chocolate para el desayuno
    AI: {"Alimento":"torta de chocolate"}
    
    Usuario: Para la cena me alimente con un rico choclito con queso
    AI: {"Alimento":"choclito con queso"}

    Usuario: %s
    AI: """%(query)
    
    response = openai.Completion.create(
        model='text-curie-001',
        prompt=prompt,
        temperature=0,
        max_tokens= 256
    )

    result = response.choices[0]["text"]
    print(result)
    
    ans = {}
    try:
        ans = json.loads(result)
    except Exception as e:
        ans = {}
    
    #print(ans)
    return ans

def existe_keyword(mensaje):
    for i in mensaje:
        if i in keyWords_especificos:
            return True
    return False

async def insertar_o_actualizar(usuario_existe, numero_usuario, fecha, alimento, mensaje, temprano, tarde, noche):
    if usuario_existe:
        arreglo_temprano = await recuperar_comida_temprano(numero_usuario, fecha)
        arreglo_tarde = await recuperar_comida_tarde(numero_usuario, fecha)
        arreglo_noche = await recuperar_comida_noche(numero_usuario, fecha)
        if temprano:
            arreglo_temprano.append({"Alimento":alimento})
        elif tarde:
            arreglo_tarde.append({"Alimento":alimento})
        elif noche:
            arreglo_noche.append({"Alimento":alimento})
        await update_user_history(numero_usuario, 0.0, 0.0, mensaje, arreglo_temprano, arreglo_tarde, arreglo_noche)
        return "Actualizado"
    else:
        arr_temprano = []
        arr_tarde = []
        arr_noche= []
        if temprano:
            arr_temprano.append({"Alimento":alimento})
        elif tarde:
            arr_tarde.append({"Alimento":alimento})
        elif noche:
            arr_noche.append({"Alimento":alimento})
        await insertar_user_history(id_numero=numero_usuario, calorias=0.0, litros=0.0, chat=mensaje, temprano=arr_temprano, tarde=arr_tarde, noche=arr_noche)
        return "Insertado"

async def identificar_comida(sender_number, message):

    existe = await existe_usuario(int(sender_number[10:]))
    
    if existe:
        incoming_msg = message
        
        #print(message_body)
        #print(incoming_msg)
        
        arreglo_mensaje = incoming_msg.split(" ")
        arreglo_mensaje_minuscula = [elemento.lower() for elemento in arreglo_mensaje]
        alimento = recuperar_alimento_texto(incoming_msg)
        
        if(alimento == {}):
            return "No hay alimento"
        
        keyword = existe_keyword(arreglo_mensaje_minuscula)
        fecha_hoy = datetime.date.today()
        usuario_existe = await existe_user_history_en_fecha(int(sender_number[10:]), fecha_hoy)
        
        if keyword:
            for palabra in arreglo_mensaje_minuscula:
                if palabra in desayuno_palabras:
                    print("Es Desayuno")
                    #Agregar a la base de datos en el apartado de desayuno
                    await insertar_o_actualizar(usuario_existe, int(sender_number[10:]), fecha_hoy, alimento["Alimento"], incoming_msg, True, False, False)
                    return ["El usuario existe", {"Comida": alimento["Alimento"].lower()}]
                
                elif palabra in almuerzo_palabras:
                    print("Es Almuerzo")
                    #Agregar a la base de datos en el apartado de almuerzo
                    await insertar_o_actualizar(usuario_existe, int(sender_number[10:]), fecha_hoy, alimento["Alimento"], incoming_msg, False, True, False)
                    return ["El usuario existe", {"Comida": alimento["Alimento"].lower()}]
                
                elif palabra in cena_palabras:
                    print("Es Cena")
                    #Agregar a la base de datos en el apartado de cena
                    await insertar_o_actualizar(usuario_existe, int(sender_number[10:]), fecha_hoy, alimento["Alimento"], incoming_msg, False, False, True)
                    return ["El usuario existe", {"Comida": alimento["Alimento"].lower()}]
        else:
            for palabra in arreglo_mensaje_minuscula:
                if palabra in keyWords_confusos:
                    hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
                    if hora_actual > "5:00:00" and hora_actual <= "12:00:00":
                        #Se tiene que meter la fecha, hora y comida en el campo de desayuno
                        print("Es Desayuno")
                        await insertar_o_actualizar(usuario_existe, int(sender_number[10:]), fecha_hoy, alimento["Alimento"], incoming_msg, True, False, False)
                        return ["El usuario existe", {"Comida": alimento["Alimento"].lower()}]
                    
                    elif hora_actual > "12:00:00" and hora_actual <= "18:00:00":
                        #Se tiene que meter la fecha, hora y comida en el campo de almuerzo
                        print("Es Almuerzo")
                        await insertar_o_actualizar(usuario_existe, int(sender_number[10:]), fecha_hoy, alimento["Alimento"], incoming_msg, False, True, False)
                        return ["El usuario existe", {"Comida": alimento["Alimento"].lower()}]
                    
                    elif hora_actual > "18:00:00" and hora_actual <= "23:59:59":
                        #Se tiene que meter la fecha, hora y comida en el campo de cena
                        print("Es Cena")
                        await insertar_o_actualizar(usuario_existe, int(sender_number[10:]), fecha_hoy, alimento["Alimento"], incoming_msg, False, False, True)
                        return ["El usuario existe", {"Comida": alimento["Alimento"].lower()}]
                    
                    elif hora_actual >= "00:00:00" and hora_actual <= "4:59:59":
                        #Se tiene que meter la fecha, hora y comida en el campo de cena
                        print("Es Cena")
                        await insertar_o_actualizar(usuario_existe, int(sender_number[10:]), fecha_hoy, alimento["Alimento"], incoming_msg, False, False, True)
                        return ["El usuario existe", {"Comida": alimento["Alimento"].lower()}]
        
    else:
        return ["No existe el usuario", {}]
    
"""
if __name__ == "__main__": 
    loop = asyncio.get_event_loop()

    # Run the async function in the event loop
    loop.run_until_complete(identificar_comida("whatsapp:+51936404731","He desayunado huevo frito con tocino"))

    # Close the event loop
    loop.close() 
"""