from bd_functions import get_users_noche_with_date, get_users_temprano_with_date, get_users_tarde_with_date, get_users_historial, insertar_usuario
import schedule
import datetime
import asyncio
import time
import requests
import threading

class SharedObject:
    def __init__(self):
        self.resultado = None
    
    def actualizar_variable(self, valor):
        self.resultado = valor
        
shared_obj = SharedObject()

async def send_notification_temprano(hora):
    usuarios_mandar_notificacion = []
    url = 'http://127.0.0.1:8000/bot'
    fecha_actual = datetime.date.today()
    fecha_actual_str = fecha_actual.strftime('%Y-%m-') + str(fecha_actual.day).zfill(2)
    
    usuarios_temprano = await get_users_temprano_with_date(fecha_actual_str)
    
    for elemento in usuarios_temprano:
        if len(elemento['temprano']) == 0:
                usuarios_mandar_notificacion.append(elemento['user_id'])
                
    if len(usuarios_mandar_notificacion) == 0:
        print('No mandamos notificacion para temprano')
        shared_obj.actualizar_variable(None)
    else:
        shared_obj.actualizar_variable([usuarios_mandar_notificacion, f'Hey, son las {hora} y te olvidaste de reportar tu comida de la mañana'])
        result = {
            "From" : 'SECRETO',
            "numeros" : shared_obj.resultado[0],
            "Body" : shared_obj.resultado[1],
        }
        response = requests.post(url, data=result)
    
    
async def send_notification_tarde(hora):
    usuarios_mandar_notificacion = []
    url = 'http://127.0.0.1:8000/bot'
    fecha_actual = datetime.date.today()
    fecha_actual_str = fecha_actual.strftime('%Y-%m-') + str(fecha_actual.day).zfill(2)
    
    usuarios_tarde = await get_users_tarde_with_date(fecha_actual_str)
    
    for elemento in usuarios_tarde:
        if len(elemento['tarde']) == 0:
                usuarios_mandar_notificacion.append(elemento['user_id'])
    
    if len(usuarios_mandar_notificacion) == 0:
        print('No mandamos notificacion para tarde')
        shared_obj.actualizar_variable(None)
    else:
        shared_obj.actualizar_variable([usuarios_mandar_notificacion, f'Hey, son las {hora} y te olvidaste de reportar tu comida de la tarde'])
        result = {
            "From" : 'SECRETO',
            "numeros" : shared_obj.resultado[0],
            "Body" : shared_obj.resultado[1],
        }
        response = requests.post(url, data=result)
    
    
async def send_notification_noche(hora):
    usuarios_mandar_notificacion = []
    url = 'http://127.0.0.1:8000/bot'
    fecha_actual = datetime.date.today()
    fecha_actual_str = fecha_actual.strftime('%Y-%m-') + str(fecha_actual.day).zfill(2)
    
    usuarios_noche = await get_users_noche_with_date(fecha_actual_str)
    
    for elemento in usuarios_noche:
        if len(elemento['noche']) == 0:
                usuarios_mandar_notificacion.append(elemento['user_id'])
    
    if len(usuarios_mandar_notificacion) == 0:
        print('No mandamos notificacion para noche')
        shared_obj.actualizar_variable(None)
    else:
        shared_obj.actualizar_variable([usuarios_mandar_notificacion, f'Hey, son las {hora} y te olvidaste de reportar tu comida de la noche'])
        result = {
            "From" : 'SECRETO',
            "numeros" : shared_obj.resultado[0],
            "Body" : shared_obj.resultado[1],
        }
        response = requests.post(url, data=result)
        
async def daily_report():
    
    url = 'https://b105-204-199-168-25.ngrok-free.app/bot' #CAMBIAR PARA PRUEBAS
    
    fecha_actual = datetime.date.today()
    fecha_actual_str = fecha_actual.strftime('%Y-%m-') + str(fecha_actual.day).zfill(2)
    
    usuarios_global = await get_users_historial(fecha_actual_str)
    arr_retornar=[]
    
    numeros=[]

    for elemento in usuarios_global:

        usuario_especifico=await insertar_usuario(elemento["user_id"])

        print(usuario_especifico[1])

        limite_calorias=usuario_especifico[1]["calorias_dia"]

        numeros.append(elemento["user_id"])
        calorias=elemento["calorias"]

        desayuno="No reporto"
        almuerzo="No reporto"
        cena="No reporto"

        for i in range(len(elemento["temprano"])):
            if(i==0): desayuno=""
            desayuno=desayuno+str(elemento["temprano"][i])+" "

        for i in range(len(elemento["tarde"])):
            if(i==0): almuerzo=""
            almuerzo=almuerzo+str(elemento["tarde"][i])+" "
        
        for i in range(len(elemento["noche"])):
            if(i==0): cena=""
            cena=cena+str(elemento["noche"][i])+" "
        
        #print(desayuno)
        #print(almuerzo)
        #print(cena)

        limite_calorias_numero=2800

        try:
            limite_calorias_numero=float(limite_calorias)
        except:
            temp_numero=""
            for i in limite_calorias:
                if(i=="-"): break
                temp_numero=temp_numero+i
            limite_calorias_numero=float(temp_numero)

        if(limite_calorias_numero<calorias):
            mensaje=f"Tu limite diario de calorias es de {limite_calorias}, hoy consumiste {calorias}, por lo que no lograste tu objetivo alimenticio 😞.\n Temprano -> {desayuno} \n Tarde -> {almuerzo}\n Cena -> {cena}"
        else:
            mensaje=f"Tu limite diario de calorias es de {limite_calorias}, hoy consumiste {calorias}, por lo que lograste tu objetivo alimenticio 😊.\n Temprano -> {desayuno} \n Tarde -> {almuerzo} \n Cena -> {cena}"
        

        arr_retornar.append(mensaje)

    #shared_obj.actualizar_variable([usuarios_mandar_notificacion, f'Hey, son las {hora} y te olvidaste de reportar tu comida de la noche'])
    result = {
        "From" : 'SECRETO_REPORTE',
        "Mensaje" : arr_retornar,
        "Numeros" : numeros,
        "Body": ""
    }
    print(arr_retornar,numeros)
    response = requests.post(url, data=result)
    

def ejecutar_cronjob():
    # TEMPRANO
    schedule.every().day.at("11:00").do(asyncio.run, send_notification_temprano("11:00 AM")) #Cambiar esto

    # TARDE
    schedule.every().day.at("17:00").do(asyncio.run, send_notification_tarde("17:00 PM"))

    # NOCHE
    schedule.every().day.at("23:00").do(asyncio.run, send_notification_noche("23:00 PM"))
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def cronjob_test():

    cronjob_thread = threading.Thread(target=ejecutar_cronjob)

    cronjob_thread.start()

def example_test():
    #asyncio.run(send_notification_temprano("11:00 PM"))
    asyncio.run(daily_report())

example_test()