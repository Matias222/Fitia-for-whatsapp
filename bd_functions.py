import os

# Import database and ORM
import supabase
from dotenv import load_dotenv
import datetime
import asyncio

load_dotenv()

#Get credentials
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase_client = supabase.create_client(supabase_url, supabase_key)

async def insertar_usuario(numero_usuario,nombre="",peso=0.0,talla=0.0,objetivo="",objetivo_confirmado=False,edad=0):

    db_item, count = supabase_client.table('Usuarios').select('*').eq('numero', numero_usuario).execute()
    
    arr_retornar=[1,{}]

    if len(db_item[1]) == 0:
        new_user = {'numero': numero_usuario, 'nombre':nombre,'peso':peso,'talla':talla,'edad':edad,'objetivo':objetivo,'objetivo_confirmado':objetivo_confirmado}
        supabase_client.table('Usuarios').insert(new_user).execute()
        
        arr_retornar[0]=0
        arr_retornar[1]=new_user
    else:
        arr_retornar[1]=db_item[1][0]

    return arr_retornar


async def update_usuario(numero_usuario,nombre="",peso=0.0,talla=0.0,edad=0,objetivo="",objetivo_confirmado=False,calorias_dia="",litros_dia=0.0):
    new_user = {'numero': numero_usuario, 'nombre':nombre,'peso':peso,'talla':talla,'edad':edad,'objetivo':objetivo,'objetivo_confirmado':objetivo_confirmado,'calorias_dia':calorias_dia,'litros_dia':litros_dia}
    supabase_client.table("Usuarios").update(new_user).eq("numero", numero_usuario).execute()

async def update_estado(numero_usuario,estado):
    new_user = {'estado':estado}
    supabase_client.table("Usuarios").update(new_user).eq("numero", numero_usuario).execute()


async def existe_usuario(numero_usuario):
    response = supabase_client.table("Usuarios").select("*").eq('numero',numero_usuario).execute()
    
    if len(response.data) > 0:
        return True
    
    return False

async def insertar_user_history(id_numero,calorias=0.0,litros=0.0,chat="", temprano=[], tarde=[], noche=[],fecha=None):
    db_item, _ = supabase_client.table('user_history').select('*').eq('user_id', id_numero).eq('dia',fecha).execute()
    
    fecha_actual = datetime.date.today()
    fecha_actual_str = fecha_actual.strftime('%Y-%m-') + str(fecha_actual.day).zfill(2)
    
    arr_retornar=[1,{}]
 
    if len(db_item[1]) == 0:
        new_user = {'user_id': id_numero, 'dia':fecha_actual_str, 'calorias':calorias, 'litros':litros, 'chat':chat, "temprano":temprano, "tarde":tarde, "noche":noche}
        print(new_user)
        supabase_client.table('user_history').insert(new_user).execute()
        
        arr_retornar[0]=0
        arr_retornar[1]=new_user
    else:
        arr_retornar[1]=db_item[1][0]

    return arr_retornar

async def update_user_history(id_numero,calorias=0.0,litros=0.0,chat="", temprano=[], tarde=[], noche=[]):
    fecha_actual = datetime.date.today()
    fecha_actual_str = fecha_actual.strftime('%Y-%m-') + str(fecha_actual.day).zfill(2)
    
    new_user = {'user_id': id_numero, 'dia':fecha_actual_str, 'calorias':calorias, 'litros':litros, 'chat':chat, "temprano":temprano, "tarde":tarde, "noche":noche}
    supabase_client.table("user_history").update(new_user).eq("user_id", id_numero).execute()
    

async def existe_user_history_en_fecha(numero_usuario, fecha):
    response = supabase_client.table("user_history").select("*").eq('user_id',numero_usuario).eq('dia', fecha).execute()
    
    if(len(response.data) > 0):
        return True;
    return False;

async def recuperar_comida_temprano(numero_usuario, fecha):
    response = supabase_client.table("user_history").select("*").eq('user_id',numero_usuario).eq('dia', fecha).execute()
    
    if(len(response.data) > 0):
        return response.data[0]["temprano"]
    
    #print(response.data[0]["comidas"])
    return {}

async def recuperar_comida_tarde(numero_usuario, fecha):
    response = supabase_client.table("user_history").select("*").eq('user_id',numero_usuario).eq('dia', fecha).execute()
    
    if(len(response.data) > 0):
        return response.data[0]["tarde"]
    
    #print(response.data[0]["comidas"])
    return {}

async def recuperar_comida_noche(numero_usuario, fecha):
    response = supabase_client.table("user_history").select("*").eq('user_id',numero_usuario).eq('dia', fecha).execute()
    
    if(len(response.data) > 0):
        return response.data[0]["noche"]
    
    #print(response.data[0]["comidas"])
    return {}

async def update_temprano(numero_usuario, fecha, tempra=[]):
    new_temprano = {
        'temprano':tempra
    }
    supabase_client.table("user_history").update(new_temprano).eq("user_id",numero_usuario).eq('dia',fecha).execute()

async def update_tarde(numero_usuario, fecha, tard=[]):
    new_tarde = {
        'tarde':tard
    }
    supabase_client.table("user_history").update(new_tarde).eq("user_id",numero_usuario).eq('dia',fecha).execute()

async def update_noche(numero_usuario, fecha, noch=[]):
    new_noche = {
        'noche':noch
    }
    supabase_client.table("user_history").update(new_noche).eq("user_id",numero_usuario).eq('dia',fecha).execute()

async def get_users_temprano_with_date(fecha):
    #Se debe de colocar la fecha actual str y borrar el parametro de fecha de la funcion
    fecha_actual = datetime.date.today()
    fecha_actual_str = fecha_actual.strftime('%Y-%m-') + str(fecha_actual.day).zfill(2)
    
    response = supabase_client.table('user_history').select('user_id, temprano').eq('dia', fecha).execute()
    res = response.data
    # print(res)
    
    return res
    
async def get_users_tarde_with_date(fecha):
    #Se debe de colocar la fecha actual str y borrar el parametro de fecha de la funcion
    fecha_actual = datetime.date.today()
    fecha_actual_str = fecha_actual.strftime('%Y-%m-') + str(fecha_actual.day).zfill(2)
    
    response = supabase_client.table('user_history').select('user_id, tarde').eq('dia', fecha).execute()
    res = response.data
    # print(res)
    
    return res

async def get_users_noche_with_date(fecha):
    #Se debe de colocar la fecha actual str y borrar el parametro de fecha de la funcion
    fecha_actual = datetime.date.today()
    fecha_actual_str = fecha_actual.strftime('%Y-%m-') + str(fecha_actual.day).zfill(2)
    
    response = supabase_client.table('user_history').select('user_id, noche').eq('dia', fecha).execute()
    res = response.data
    # print(res)
    
    return res

"""
if __name__ == "__main__": 
    loop = asyncio.get_event_loop()

    # Run the async function in the event loop
    loop.run_until_complete(update_user_history(51936404731, 0.0, 0.0, "Almorce palta con huevo", [{"Alimento": "torta"}, {"Alimento": "queso"}], [{"Alimento": "palta con huevo"}], []))

    # Close the event loop
    loop.close()
"""

# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()

#     # Run the async function in the event loop
#     loop.run_until_complete(get_users_tarde_with_date('2023-06-09'))

#     # Close the event loop
#     loop.close()
