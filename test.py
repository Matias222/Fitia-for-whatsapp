from aux_functions import (
    identificar_confirmacion,
    verificar_datos_bd,
    guardar_plan_personalizado,
)
import openai
import os
from dotenv import load_dotenv
import asyncio
import datetime

from openai_calls import (
    plan_personalizado,
    parseo_info,
    parseo_calorias,
    segmentador,
    sugerencias,
)
from identificador import (
    recuperar_alimento_texto,
    segmentar_cantidades_comida,
    identificar_comida,
)
from bd_functions import (
    insertar_usuario,
    update_usuario,
    update_estado,
    existe_usuario,
    insertar_user_history,
    update_user_history,
    existe_user_history_en_fecha,
    recuperar_comida_temprano,
    recuperar_comida_tarde,
    recuperar_comida_noche,
    update_temprano,
    update_tarde,
    update_noche,
    update_calorias,
    get_users_temprano_with_date,
    get_users_tarde_with_date,
    get_users_noche_with_date,
)

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


async def my_async_function():
    return await insertar_usuario(
        "51999999999",
        "Jorge",
        peso=70,
        talla=1.70,
        objetivo="bajar 10kg",
        objetivo_confirmado=False,
        edad=23,
    )


async def my_async_function_2():
    return await update_usuario(
        "51999999999",
        nombre="",
        peso=0.0,
        talla=0.0,
        edad=0,
        objetivo="",
        objetivo_confirmado=False,
        calorias_dia="",
        litros_dia=0.0,
    )


async def my_async_function_2_failed():
    return await update_usuario(
        "51999",
        nombre="",
        peso=0.0,
        talla=0.0,
        edad=0,
        objetivo="",
        objetivo_confirmado=False,
        calorias_dia="",
        litros_dia=0.0,
    )


async def my_sync_update_estado(numero_usuario, estado):
    return await update_estado(numero_usuario, estado)


async def my_async_existe_usuario(numero_usuario):
    return await existe_usuario(numero_usuario)


async def my_async_insertar_user_history(
    id_numero, calorias, litros, chat, temprano, tarde, noche
):
    return await insertar_user_history(
        id_numero, calorias, litros, chat, temprano, tarde, noche
    )


async def my_async_update_user_history(
    id_numero, calorias, litros, chat, temprano, tarde, noche
):
    return await update_user_history(
        id_numero, calorias, litros, chat, temprano, tarde, noche
    )


async def my_async_existe_user_history_en_fecha(numero_usuario, fecha):
    return await existe_user_history_en_fecha(numero_usuario, fecha)


async def my_async_recuperar_comida_temprano(numero_usuario, fecha):
    return await recuperar_comida_temprano(numero_usuario, fecha)


async def my_async_recuperar_comida_tarde(numero_usuario, fecha):
    return await recuperar_comida_tarde(numero_usuario, fecha)


async def my_async_recuperar_comida_noche(numero_usuario, fecha):
    return await recuperar_comida_noche(numero_usuario, fecha)


async def my_async_update_temprano(numero_usuario, fecha, tempra):
    return await update_temprano(numero_usuario, fecha, tempra)


async def my_async_update_tarde(numero_usuario, fecha, tard):
    return await update_tarde(numero_usuario, fecha, tard)


async def my_async_update_noche(numero_usuario, fecha, noch):
    return await update_noche(numero_usuario, fecha, noch)


async def my_async_update_calorias(numero_usuario, calorias):
    return await update_calorias(numero_usuario, calorias)


async def my_async_get_users_temprano_with_date(fecha):
    return await get_users_temprano_with_date(fecha)


async def my_async_get_users_tarde_with_date(fecha):
    return await get_users_tarde_with_date(fecha)


async def my_async_get_users_noche_with_date(fecha):
    return await get_users_noche_with_date(fecha)


async def my_async_guardar_plan_personalizado(
    mensaje_retornar, sender_number, datos_usuario, objetivo
):
    return await guardar_plan_personalizado(
        mensaje_retornar, sender_number, datos_usuario, objetivo
    )


async def my_async_plan_personalizado(nombre, talla, peso, edad, objetivo):
    return plan_personalizado(nombre, talla, peso, edad, objetivo)


async def my_async_identificar_comida(sender_number, message):
    return await identificar_comida(sender_number, message)


def test_login_user():
    # loop = asyncio.get_event_loop()
    user = asyncio.run(my_async_function())
    print("===========================================")
    if user[0] == 0:
        print("usuario no existe,procede a registrarlo")
        print(user)
    elif user[0] == 1:
        print("usuario ya existe, procede a mostrar datos")
        print(user)
    print("===========================================")
    # loop.close()


def test_update_usuario():
    user, count = asyncio.run(my_async_function_2())
    if user[1] != []:
        print("Usuario actualizado exitosamente")
        print(user[1])


def test_failed_update_usuario():
    user, count = asyncio.run(my_async_function_2_failed())
    if user[1] == []:
        print("usuario no encontrado")
        print(user[1])


def test_update_estado():
    user, count = asyncio.run(
        my_sync_update_estado("51999999999", "CAMBIO DE OBJETIVO")
    )
    if user[1] != []:
        print("cambio estado")
        print(user[1])
    else:
        print("usuario no encontrado")


def test_failed_update_estado():
    print("test failed cambio de estado")
    user, count = asyncio.run(my_sync_update_estado("519", "CAMBIO DE OBJETIVO"))
    if user[1] != []:
        print("cambio estado")
        print(user[1])
    else:
        print("usuario no encontrado")


def test_existe_usuario():
    print("test existe usuario")
    response = asyncio.run(my_async_existe_usuario("51999999999"))
    if response:
        print("Usuario existe")
    else:
        print("Usuario no existe")


def test_failed_existe_usuario():
    print("test failed existe usuario")
    response = asyncio.run(my_async_existe_usuario("519"))
    if response:
        print("Usuario existe")
    else:
        print("Usuario no existe")


def test_insertar_user_history():
    print("==============================")
    print("= TEST INSERTAR USER HISTORY =")
    print("==============================")
    response = asyncio.run(
        my_async_insertar_user_history(
            "51999999999",
            1372,
            0.0,
            "",
            [{"cereal": 1, "vaso de yogurt": 1}],
            [{"Lomo saltado": 1, "Coca Cola": 1}],
            [],
        )
    )
    if response[1] != {}:
        print(response)
    print("==============================")
    print("==============================")


def test_update_user_history():
    response, _ = asyncio.run(
        my_async_update_user_history(
            "51999999999",
            1472,
            0.0,
            "",
            [{"cereal": 1, "vaso de yogurt": 1}],
            [{"Lomo saltado": 1, "Coca Cola": 1}],
            [{"Arroz con leche": 2}],
        )
    )
    if response[1] != []:
        print(response[1])


def test_existe_user_history_en_fecha():
    print("==============================")
    print("= TEST EXISTE USER HISTORY EN FECHA =")
    print("==============================")
    response = asyncio.run(
        my_async_existe_user_history_en_fecha("51999999999", datetime.datetime.now())
    )
    if response:
        print("si existe user history")
    else:
        print("no existe user history")


def test_failed_existe_user_history_en_fecha():
    print("==============================")
    print("= TEST FAILED EXISTE USER HISTORY EN FECHA =")
    print("==============================")
    datetime.datetime(month=6, day=30, year=2024)
    response = asyncio.run(
        my_async_existe_user_history_en_fecha(
            "51999999999", datetime.datetime(month=6, day=30, year=2024)
        )
    )
    if response:
        print("si existe user history")
    else:
        print("no existe user history")


def test_recuperar_comida_temprano():
    response = asyncio.run(
        my_async_recuperar_comida_temprano("51999999999", datetime.datetime.now())
    )
    if response != {}:
        print(response)


def test_failed_recuperar_comida_temprano():
    response = asyncio.run(
        my_async_recuperar_comida_temprano(
            "51999999999", datetime.datetime(month=6, day=30, year=2024)
        )
    )
    if response != {}:
        print("no se ha encontrado comida temprano")


def test_recuperar_comida_tarde():
    response = asyncio.run(
        my_async_recuperar_comida_tarde("51999999999", datetime.datetime.now())
    )
    if response != {}:
        print(response)


def test_failed_recuperar_comida_tarde():
    response = asyncio.run(
        my_async_recuperar_comida_tarde(
            "51999999999", datetime.datetime(month=6, day=30, year=2024)
        )
    )
    if response != {}:
        print("no se ha encontrado comida tarde")


def test_recuperar_comida_noche():
    response = asyncio.run(
        my_async_recuperar_comida_noche("51999999999", datetime.datetime.now())
    )
    if response != {}:
        print(response)


def test_failed_recuperar_comida_noche():
    response = asyncio.run(
        my_async_recuperar_comida_noche(
            "51999999999", datetime.datetime(month=6, day=30, year=2024)
        )
    )
    if response == {}:
        print("no se ha encontrado comida noche")


def test_update_temprano():
    print("====== TEST UPDATE TEMPRANO ======")
    response, _ = asyncio.run(
        my_async_update_temprano("51999999999", datetime.datetime.now(), [])
    )
    if response[1] != []:
        print("lista comida temprano actualizada")
        print(response[1])


def test_update_tarde():
    print("====== TEST UPDATE TARDE ======")
    response, _ = asyncio.run(
        my_async_update_tarde("51999999999", datetime.datetime.now(), [])
    )
    if response[1] != []:
        print("lista comida tarde actualizada")
        print(response[1])


def test_update_noche():
    print("====== TEST UPDATE NOCHE ======")
    response, _ = asyncio.run(
        my_async_update_noche("51999999999", datetime.datetime.now(), [])
    )
    if response[1] != []:
        print("lista comida noche actualizada")
        print(response[1])


def test_update_calorias():
    print("====== TEST UPDATE CALORIAS ======")
    response, _ = asyncio.run(my_async_update_calorias("51999999999", 1675.5))
    if response[1] != []:
        print(response[1])


def test_get_users_temprano_with_date():
    print("====== TEST GET USERS TEMPRANO ======")
    response = asyncio.run(
        my_async_get_users_temprano_with_date(datetime.datetime.now())
    )
    if response != []:
        print(response)


def test_failed_get_users_temprano_with_date():
    print("====== TEST FAILED GET USERS TEMPRANO ======")
    response = asyncio.run(
        my_async_get_users_temprano_with_date(
            datetime.datetime(month=6, day=30, year=2024)
        )
    )
    if response == []:
        print("No se encontro ningun usuario")


def test_get_users_tarde_with_date():
    print("====== TEST GET USERS TARDE ======")
    response = asyncio.run(my_async_get_users_tarde_with_date(datetime.datetime.now()))
    if response != []:
        print(response)


def test_failed_get_users_tarde_with_date():
    print("====== TEST FAILED GET USERS TARDE ======")
    response = asyncio.run(
        my_async_get_users_tarde_with_date(
            datetime.datetime(month=6, day=30, year=2024)
        )
    )
    if response == []:
        print("No se encontro ningun usuario")


def test_get_users_noche_with_date():
    print("====== TEST GET USERS NOCHE ======")
    response = asyncio.run(my_async_get_users_noche_with_date(datetime.datetime.now()))
    if response != []:
        print(response)


def test_failed_get_users_noche_with_date():
    print("====== TEST FAILED GET USERS NOCHE ======")
    response = asyncio.run(
        my_async_get_users_noche_with_date(
            datetime.datetime(month=6, day=30, year=2024)
        )
    )
    if response == []:
        print("No se encontro ningun usuario")


def test_identificar_confirmacion():
    response = identificar_confirmacion("aja")
    if (response == "SI") or (response == "NO"):
        print(response)
    else:
        print("test fallido")


def test_failed_identificar_confimacion():
    response = identificar_confirmacion("")
    if (response == "SI") or (response == "NO"):
        print(response)
    else:
        print("test fallido")


def test_verificar_datos_bd():
    datos_user1 = {"nombre": "", "talla": 0, "peso": 0, "edad": 0}
    datos_user_nuevo = {"nombre": "Pedro", "talla": 1.77, "peso": 70, "edad": 23}
    response = verificar_datos_bd(
        datos_usuario=datos_user1, datos_nuevo=datos_user_nuevo
    )
    if response != []:
        print("datos vacios")
    else:
        print("datos ingresados correctamente")


def test_failed_verificar_datos_bd():
    datos_user1 = {"nombre": "", "talla": 0, "peso": 0, "edad": 0}
    datos_user_nuevo = {"nombre": "", "talla": 1.77, "peso": 70, "edad": 23}
    response = verificar_datos_bd(
        datos_usuario=datos_user1, datos_nuevo=datos_user_nuevo
    )
    if response != []:
        print("falta algun dato")
    else:
        print("datos ingresados correctamente")


def test_guardar_plan_personalizado():
    response, _ = asyncio.run(
        my_async_guardar_plan_personalizado(
            "Basándome en los datos que me proporcionaste, para lograr tu objetivo de bajar 10 kilos, deberías consumir alrededor de 2000 calorías al día y tomar al menos 2 litros de agua diariamente. Es importante que tengas en cuenta que estos valores son aproximados y que pueden variar dependiendo de tu nivel de actividad física y otros factores individuales. Además, es recomendable que consultes con un nutricionista para que te brinde una dieta personalizada y adecuada a tus necesidades.F",
            "000000000051999999999",
            {
                "nombre": "Pedro",
                "peso": 70,
                "talla": 1.72,
                "edad": 23,
            },
            "Bajar 10 kg",
        )
    )
    print(response)


def test_plan_personalizado():
    print("===== TEST PLAN PERSONALIZADO =====")
    response = asyncio.run(
        my_async_plan_personalizado("Pedro", 1.77, 73, 25, "bajar 10 kg")
    )
    if len(response) > 0:
        print("plan personalizado generado")


def test_failed_plan_personalizado():
    print("===== TEST PLAN PERSONALIZADO =====")
    response = asyncio.run(my_async_plan_personalizado("Pedro", 1.77, 73, 25, ""))
    indice = str(response).find("necesito")
    if indice == -1:
        print("plan personalizado generado")
    else:
        print("plan personalizado no generado")


def test_parseo_info():
    print("===== TEST PARSEO DE INFORMACION =====")
    response = parseo_info("Mi nomre es Pedro, tengo 25 años, mido 1.77 y peso 73 kg")
    if response != {}:
        print("parseo de los datos exitoso")
        print(response)


def test_failed_parseo_info():
    print("===== TEST FAILED PARSEO DE INFORMACION =====")
    response = parseo_info("")
    if response == {}:
        print("no se ingresaron los datos")


def test_parseo_calorias():
    print("===== TEST PARSEO DE CALORIAS =====")
    response = parseo_calorias(
        "Basándome en los datos que me proporcionaste, para lograr tu objetivo de bajar 10 kilos, deberías consumir alrededor de 2000 calorías al día y tomar al menos 2 litros de agua diariamente. Es importante que tengas en cuenta que estos valores son aproximados y que pueden variar dependiendo de tu nivel de actividad física y otros factores individuales. Además, es recomendable que consultes con un nutricionista para que te brinde una dieta personalizada y adecuada a tus necesidades."
    )
    if response != {}:
        print("parseo de calorias exitoso")


def test_failed_parseo_calorias():
    print("===== TEST PARSEO DE CALORIAS =====")
    response = parseo_calorias("")
    if response == {}:
        print("parseo de calorias fallido")


def test_segmentador():
    print("===== TEST SEGMENTADOR =====")
    response = segmentador("Almorce 1/4 de pollo a la brasa con full papas")
    if len(response) > 0:
        print("segmentacion exitosa")


def test_sugerencias():
    print("===== TEST SUGERENCIAS =====")
    response = sugerencias("Se me antojo tomarme una gaseosa, ¿Deberia tomarla?")
    if len(response) > 0:
        print("sugerencia exitosa")


def test_recuperar_alimento_texto():
    print("===== TEST RECUPERAR ALIMENTO =====")
    response = recuperar_alimento_texto(
        "Hoy he comido arroz con pollo con papa a la huancaina."
    )
    if response != {}:
        print("recuperacion de alimento exitosa")


def test_failed_recuperar_alimento_texto():
    print("===== TEST RECUPERAR ALIMENTO =====")
    response = recuperar_alimento_texto("")
    if response != {}:
        print("recuperacion de alimento exitosa")
    else:
        print("recuperacion de alimento fallida")


def test_segmentar_cantidades_comida():
    print("===== TEST SEGMENTACION CANTIDAD COMIDA =====")
    response = segmentar_cantidades_comida(
        "Hoy comi 2 huevos con jamon, 1 palta y 2 platanos"
    )
    if response != "{}":
        print("segmentacion de cantidades exitosa")


def test_failed_segmentar_cantidades_comida():
    print("===== TEST FAILED SEGMENTACION CANTIDAD COMIDA =====")
    response = segmentar_cantidades_comida("")
    if response != "{}":
        print("segmentacion de cantidades exitosa")
    elif response == "{}":
        print("segmentacion de cantidades fallida")


def test_identificar_comida():
    print("===== TEST IDENTIDICAR COMIDA =====")
    response = asyncio.run(
        my_async_identificar_comida("000000000051999999999", "Cene arroz con leche")
    )
    if response != {}:
        print("comida identificada exitosamente")
    else:
        print("identificacion de comida fallida")


def test_failed_identificar_comida():
    print("===== TEST FAILED IDENTIDICAR COMIDA =====")
    response = asyncio.run(my_async_identificar_comida("000000000051999999999", ""))
    if response != {}:
        print("comida identificada exitosamente")
    else:
        print("identificacion de comida fallida")


test_login_user()
test_update_usuario()
test_failed_update_usuario()
test_update_estado()
test_failed_update_estado()
test_existe_usuario()
test_failed_existe_usuario()
test_insertar_user_history()
test_update_user_history()
test_existe_user_history_en_fecha()
test_failed_existe_user_history_en_fecha()
test_recuperar_comida_temprano()
test_failed_recuperar_comida_temprano()
test_recuperar_comida_tarde()
test_failed_recuperar_comida_tarde()
test_recuperar_comida_noche()
test_failed_recuperar_comida_noche()
test_update_temprano()
test_update_tarde()
test_update_noche()
test_update_calorias()
test_get_users_temprano_with_date()
test_failed_get_users_temprano_with_date()
test_get_users_tarde_with_date()
test_failed_get_users_tarde_with_date()
test_get_users_noche_with_date()
test_failed_get_users_noche_with_date()
test_identificar_confirmacion()
test_failed_identificar_confimacion()
test_verificar_datos_bd()
test_failed_verificar_datos_bd()
test_guardar_plan_personalizado()
test_plan_personalizado()
test_failed_plan_personalizado()
test_parseo_info()
test_failed_parseo_info()
test_parseo_calorias()
test_failed_parseo_calorias()
test_segmentador()
test_sugerencias()
test_recuperar_alimento_texto()
test_failed_recuperar_alimento_texto()
test_segmentar_cantidades_comida()
test_failed_segmentar_cantidades_comida()
test_identificar_comida()
test_failed_identificar_comida()
