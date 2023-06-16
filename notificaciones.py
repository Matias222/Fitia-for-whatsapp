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
schedule.every().day.at("06:00").do(asyncio.run, send_notification_temprano("6:00 AM"))
schedule.every().day.at("07:00").do(asyncio.run, send_notification_temprano("7:00 AM"))
schedule.every().day.at("08:00").do(asyncio.run, send_notification_temprano("8:00 AM"))
schedule.every().day.at("09:00").do(asyncio.run, send_notification_temprano("9:00 AM"))
schedule.every().day.at("10:00").do(asyncio.run, send_notification_temprano("10:00 AM"))
schedule.every().day.at("11:00").do(asyncio.run, send_notification_temprano("11:00 AM"))

# TARDE
schedule.every().day.at("13:00").do(asyncio.run, send_notification_tarde("13:00 PM"))
schedule.every().day.at("14:00").do(asyncio.run, send_notification_tarde("14:00 PM"))
schedule.every().day.at("15:00").do(asyncio.run, send_notification_tarde("15:00 PM"))
schedule.every().day.at("16:00").do(asyncio.run, send_notification_tarde("16:00 PM"))
schedule.every().day.at("17:00").do(asyncio.run, send_notification_tarde("17:00 PM"))

# NOCHE
schedule.every().day.at("19:00").do(asyncio.run, send_notification_noche("19:00 PM"))
schedule.every().day.at("20:06").do(asyncio.run, send_notification_noche("20:00 PM"))
schedule.every().day.at("21:00").do(asyncio.run, send_notification_noche("21:00 PM"))
schedule.every().day.at("22:00").do(asyncio.run, send_notification_noche("22:00 PM"))
schedule.every().day.at("23:00").do(asyncio.run, send_notification_noche("23:00 PM"))
schedule.every().day.at("00:00").do(asyncio.run, send_notification_noche("00:00 AM"))
schedule.every().day.at("01:00").do(asyncio.run, send_notification_noche("1:00 AM"))
schedule.every().day.at("02:00").do(asyncio.run, send_notification_noche("2:00 AM"))
schedule.every().day.at("03:00").do(asyncio.run, send_notification_noche("3:00 AM"))


if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)
