from bd_functions import get_users_noche_with_date, get_users_temprano_with_date, get_users_tarde_with_date
import schedule
import datetime
import asyncio
import time

async def send_notification_temprano(hora):
    usuarios_mandar_notificacion = []
    usuarios_temprano = await get_users_temprano_with_date('2023-06-09')
    
    for elemento in usuarios_temprano:
        if len(elemento['temprano']) == 0:
                usuarios_mandar_notificacion.append(elemento['user_id'])
                
    if len(usuarios_mandar_notificacion) == 0:
        print('No mandamos notificacion para temprano')
        return False
    
    print(usuarios_mandar_notificacion)
    print(f'Hey, son las {hora} y te olvidaste de reportar tu comida de la mañana')
    return True
    
    
async def send_notification_tarde(hora):
    usuarios_mandar_notificacion = []
    usuarios_tarde = await get_users_tarde_with_date('2023-06-09')
    
    for elemento in usuarios_tarde:
        if len(elemento['tarde']) == 0:
                usuarios_mandar_notificacion.append(elemento['user_id'])
    
    if len(usuarios_mandar_notificacion) == 0:
        print('No mandamos notificacion para tarde')
        return False
    
    print(usuarios_mandar_notificacion)
    print(f'Hey, son las {hora} y te olvidaste de reportar tu comida de la tarde')
    return True
    
    
async def send_notification_noche(hora):
    usuarios_mandar_notificacion = []
    usuarios_noche = await get_users_noche_with_date('2023-06-09')
    
    for elemento in usuarios_noche:
        if len(elemento['noche']) == 0:
                usuarios_mandar_notificacion.append(elemento['user_id'])
    
    if len(usuarios_mandar_notificacion) == 0:
        print('No mandamos notificacion para noche')
        return False
    
    print(usuarios_mandar_notificacion)
    print(f'Hey, son las {hora} y te olvidaste de reportar tu comida de la noche')
    return True


# TEMPRANO
schedule.every().day.at("11:00").do(asyncio.run, send_notification_temprano("11:00 AM"))

# TARDE
schedule.every().day.at("17:00").do(asyncio.run, send_notification_tarde("17:00 PM"))

# NOCHE
schedule.every().day.at("00:00").do(asyncio.run, send_notification_noche("00:00 AM"))


if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)
