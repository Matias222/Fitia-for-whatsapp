from bd_functions import get_users_noche_with_date, get_users_temprano_with_date, get_users_tarde_with_date
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
    usuarios_temprano = await get_users_temprano_with_date('2023-06-09')
    
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
    usuarios_tarde = await get_users_tarde_with_date('2023-06-09')
    
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
    usuarios_noche = await get_users_noche_with_date('2023-06-09')
    
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
        

def ejecutar_cronjob():
    # TEMPRANO
    schedule.every().day.at("11:00").do(asyncio.run, send_notification_temprano("11:00 AM")) #Cambiar esto

    # TARDE
    schedule.every().day.at("17:00").do(asyncio.run, send_notification_tarde("17:00 PM"))

    # NOCHE
    schedule.every().day.at("00:00").do(asyncio.run, send_notification_noche("00:00 PM"))
    
    while True:
        schedule.run_pending()
        time.sleep(1)

cronjob_thread = threading.Thread(target=ejecutar_cronjob)

cronjob_thread.start()