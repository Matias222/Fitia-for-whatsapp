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
import time

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
        "51",
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
    user = asyncio.run(my_async_function())
    if user[0] == 0:
        assert len(user) != 0
        assert user[1] != {}
    elif user[0] == 1:
        assert len(user) != 0
        assert user[1] != {}


def test_update_usuario():
    user, count = asyncio.run(my_async_function_2())
    if user[1] != []:
        assert len(user) != 0
        assert user[1] != {}


def test_failed_update_usuario():
    user, count = asyncio.run(my_async_function_2_failed())
    if user[1] == []:
        assert user[1] == {}
        assert len(user[1]) == 0


def test_update_estado():
    user, count = asyncio.run(
        my_sync_update_estado("51999999999", "CAMBIO DE OBJETIVO")
    )
    if user[1] != []:
        assert user[1] != {}
        assert len(user[1]) > 0


def test_failed_update_estado():
    user, _ = asyncio.run(my_sync_update_estado("519", "CAMBIO DE OBJETIVO"))
    assert user[1] == []
    assert len(user[1]) == 0


def test_existe_usuario():
    response = asyncio.run(my_async_existe_usuario("51999999999"))
    assert response == True


def test_failed_existe_usuario():
    print("test failed existe usuario")
    response = asyncio.run(my_async_existe_usuario("519"))
    assert response == False


def test_insertar_user_history():
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
    assert response[1] != {}
    assert len(response[1]) > 0


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
    assert response[1] != []
    assert len(response[1]) > 0
    assert str(response[1][0]["user_id"]) == "51999999999"


def test_existe_user_history_en_fecha():
    response = asyncio.run(
        my_async_existe_user_history_en_fecha("51999999999", datetime.datetime.now())
    )
    assert response == True


def test_failed_existe_user_history_en_fecha():
    datetime.datetime(month=6, day=30, year=2024)
    response = asyncio.run(
        my_async_existe_user_history_en_fecha(
            "51999999999", datetime.datetime(month=6, day=30, year=2024)
        )
    )
    assert response == False


def test_recuperar_comida_temprano():
    response = asyncio.run(
        my_async_recuperar_comida_temprano("51999999999", datetime.datetime.now())
    )
    assert response != {}
    assert len(response) > 0


def test_failed_recuperar_comida_temprano():
    response = asyncio.run(
        my_async_recuperar_comida_temprano(
            "51999999999", datetime.datetime(month=6, day=30, year=2024)
        )
    )
    assert response == {}
    assert len(response) == 0


def test_recuperar_comida_tarde():
    response = asyncio.run(
        my_async_recuperar_comida_tarde("51999999999", datetime.datetime.now())
    )
    assert response != {}
    assert len(response) > 0


def test_failed_recuperar_comida_tarde():
    response = asyncio.run(
        my_async_recuperar_comida_tarde(
            "51999999999", datetime.datetime(month=6, day=30, year=2024)
        )
    )
    assert response == {}
    assert len(response) == 0


def test_recuperar_comida_noche():
    response = asyncio.run(
        my_async_recuperar_comida_noche("51999999999", datetime.datetime.now())
    )
    assert response != {}
    assert len(response) > 0


def test_failed_recuperar_comida_noche():
    response = asyncio.run(
        my_async_recuperar_comida_noche(
            "51999999999", datetime.datetime(month=6, day=30, year=2024)
        )
    )
    assert response == {}
    assert len(response) == 0


def test_update_temprano():
    response, _ = asyncio.run(
        my_async_update_temprano("51999999999", datetime.datetime.now(), [])
    )
    assert response[1] != []
    assert len(response[1]) > 0
    assert str(response[1][0]["user_id"]) == "51999999999"


def test_update_tarde():
    response, _ = asyncio.run(
        my_async_update_tarde("51999999999", datetime.datetime.now(), [])
    )
    assert response[1] != []
    assert len(response[1]) > 0
    assert str(response[1][0]["user_id"]) == "51999999999"


def test_update_noche():
    response, _ = asyncio.run(
        my_async_update_noche("51999999999", datetime.datetime.now(), [])
    )
    assert response[1] != []
    assert len(response[1]) > 0
    assert str(response[1][0]["user_id"]) == "51999999999"


def test_update_calorias():
    response, _ = asyncio.run(my_async_update_calorias("51999999999", 1675.5))
    assert response[1] != []
    assert len(response[1]) > 0
    assert str(response[1][0]["user_id"]) == "51999999999"


def test_get_users_temprano_with_date():
    response = asyncio.run(
        my_async_get_users_temprano_with_date(datetime.datetime.now())
    )
    assert response != []
    assert len(response) > 0
    assert str(response[0]["user_id"]) == "51999999999"


def test_failed_get_users_temprano_with_date():
    response = asyncio.run(
        my_async_get_users_temprano_with_date(
            datetime.datetime(month=6, day=30, year=2024)
        )
    )
    assert response == []
    assert len(response) == 0


def test_get_users_tarde_with_date():
    response = asyncio.run(my_async_get_users_tarde_with_date(datetime.datetime.now()))
    assert response != []
    assert len(response) > 0
    assert str(response[0]["user_id"]) == "51999999999"


def test_failed_get_users_tarde_with_date():
    response = asyncio.run(
        my_async_get_users_tarde_with_date(
            datetime.datetime(month=6, day=30, year=2024)
        )
    )
    assert response == []
    assert len(response) == 0


def test_get_users_noche_with_date():
    response = asyncio.run(my_async_get_users_noche_with_date(datetime.datetime.now()))
    assert response != []
    assert len(response) > 0


def test_failed_get_users_noche_with_date():
    response = asyncio.run(
        my_async_get_users_noche_with_date(
            datetime.datetime(month=6, day=30, year=2024)
        )
    )
    assert response == []
    assert len(response) == 0


def test_identificar_confirmacion():
    response = identificar_confirmacion("aja")
    assert response != ""
    assert response == "SI"



def test_failed_identificar_confimacion():
    response = identificar_confirmacion("")
    assert response != "SI"
    assert response != "NO"


def test_verificar_datos_bd():
    datos_user1 = {"nombre": "", "talla": 0, "peso": 0, "edad": 0}
    datos_user_nuevo = {"nombre": "Pedro", "talla": 1.77, "peso": 70, "edad": 23}
    response = verificar_datos_bd(
        datos_usuario=datos_user1, datos_nuevo=datos_user_nuevo
    )
    assert response == []
    assert len(response) == 0


def test_failed_verificar_datos_bd():
    datos_user1 = {"nombre": "", "talla": 0, "peso": 0, "edad": 0}
    datos_user_nuevo = {"nombre": "", "talla": 1.77, "peso": 70, "edad": 23}
    response = verificar_datos_bd(
        datos_usuario=datos_user1, datos_nuevo=datos_user_nuevo
    )
    assert response != []
    assert len(response) > 0


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
    assert response[1] != {}
    assert len(response[1]) > 0
    assert response[1] == [{
        "numero": 51999999999,
        "nombre": "Pedro",
        "peso": 70,
        "talla": 1.72,
        "objetivo": "Bajar 10 kg",
        "objetivo_confirmado": True,
        "calorias_dia": "2000",
        "litros_dia": 2,
        "edad": 23,
        "estado": "CAMBIO DE OBJETIVO",
    }]
    time.sleep(5)
def test_plan_personalizado():
    response = asyncio.run(
        my_async_plan_personalizado("Pedro", 1.77, 73, 25, "bajar 10 kg")
    )
    assert type(response) == str
    assert response != ""
    assert len(response) > 0
    time.sleep(5)

def test_parseo_info():
    response = parseo_info("Mi nomre es Pedro, tengo 25 años, mido 1.77 y peso 73 kg")
    assert response != {}
    assert len(response) > 0
    assert response == {"nombre": "Pedro", "talla": 1.77, "peso": 73, "edad": 25}


def test_failed_parseo_info():
    time.sleep(5)
    response = parseo_info("")
    assert response == {}
    assert len(response) == 0


def test_parseo_calorias():
    response = parseo_calorias(
        "Basándome en los datos que me proporcionaste, para lograr tu objetivo de bajar 10 kilos, deberías consumir alrededor de 2000 calorías al día y tomar al menos 2 litros de agua diariamente. Es importante que tengas en cuenta que estos valores son aproximados y que pueden variar dependiendo de tu nivel de actividad física y otros factores individuales. Además, es recomendable que consultes con un nutricionista para que te brinde una dieta personalizada y adecuada a tus necesidades."
    )
    assert response != {}
    assert len(response) > 0
    time.sleep(5)

def test_failed_parseo_calorias():
    time.sleep(5)
    response = parseo_calorias("")
    assert response == {}
    assert len(response) == 0


def test_segmentador():
    response = segmentador("Almorce 1/4 de pollo a la brasa con full papas")
    assert response != ""
    assert response == "Reporte de comidas"
    assert len(response) > 0
    time.sleep(5)

def test_sugerencias():
    time.sleep(5)
    response = sugerencias("Se me antojo tomarme una gaseosa, ¿Deberia tomarla?")
    print("resposne", response)
    assert type(response) == str
    assert len(response) > 0
    time.sleep(5)

def test_recuperar_alimento_texto():
    time.sleep(5)
    response = recuperar_alimento_texto(
        "Hoy he comido arroz con pollo con papa a la huancaina."
    )
    assert response != {}
    assert len(response) > 0
   

def test_failed_recuperar_alimento_texto():
    response = recuperar_alimento_texto("")
    assert response == {}
    assert len(response) == 0


def test_segmentar_cantidades_comida():
    response = segmentar_cantidades_comida(
        "Hoy comi 2 huevos con jamon, 1 palta y 2 platanos"
    )
    assert response != "{}"
    time.sleep(5)


def test_failed_segmentar_cantidades_comida():
    response = segmentar_cantidades_comida("")
    assert response == "{}"



def test_identificar_comida():
    time.sleep(25)
    response = asyncio.run(
        my_async_identificar_comida("000000000051999999999", "Cene arroz con leche")
    )
    assert response != {}
    assert len(response) > 0
    assert response == {"arroz con leche": 1}


def test_failed_identificar_comida():
    time.sleep(25)
    response = asyncio.run(my_async_identificar_comida("000000000051999999999", ""))
    assert response == {}
    assert len(response) == 0
