import os

# Import database and ORM
import supabase
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

#Get credentials
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase_client = supabase.create_client(supabase_url, supabase_key)

async def insertar_usuario(numero_usuario,nombre="",peso=0.0,talla=0.0,objetivo="",objetivo_confirmado=False):

    db_item, count = supabase_client.table('Usuarios').select('*').eq('numero', numero_usuario).execute()
    
    
    arr_retornar=[1,{}]

    if len(db_item[1]) == 0:
        new_user = {'numero': numero_usuario, 'nombre':nombre,'peso':peso,'talla':talla,'objetivo':objetivo,'objetivo_confirmado':objetivo_confirmado}
        supabase_client.table('Usuarios').insert(new_user).execute()
        
        arr_retornar[0]=0
        arr_retornar[1]=new_user
    else:
        arr_retornar[1]=db_item[1][0]

    return arr_retornar


async def update_usuario(numero_usuario,nombre="",peso=0.0,talla=0.0,objetivo="",objetivo_confirmado=False):
    new_user = {'numero': numero_usuario, 'nombre':nombre,'peso':peso,'talla':talla,'objetivo':objetivo,'objetivo_confirmado':objetivo_confirmado}
    supabase_client.table("Usuarios").update(new_user).eq("numero", numero_usuario).execute()







async def insertar_user_history(id_numero,dia="",calorias=0.0,litros=0.0,chat="",comidas=[]):

    db_item, count = supabase_client.table('user_history').select('*').eq('user_id', id_numero).execute()
    
    
    arr_retornar=[1,{}]
    print("DBITEM",db_item)
    if len(db_item[1]) == 0:
        new_user = {'user_id': id_numero, 'dia':dia,'calorias':calorias,'litros':litros,'chat':chat,'comidas':comidas}
        supabase_client.table('user_history').insert(new_user).execute()
        
        arr_retornar[0]=0
        arr_retornar[1]=new_user
    else:
        arr_retornar[1]=db_item[1][0]

    return arr_retornar


async def update_user_history(id_numero,dia="",calorias=0.0,litros=0.0,chat="",comidas=[]):
    new_user = {'user_id': id_numero, 'dia':dia,'calorias':calorias,'litros':litros,'chat':chat,'comidas':comidas}
    supabase_client.table("user_history").update(new_user).eq("user_id", id_numero).execute()
