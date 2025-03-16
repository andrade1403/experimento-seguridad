import requests
import pandas as pd

if __name__ == '__main__':
    #Definimos flag para volver a traer los datos
    flag = False

    #Definimos la URL para consumir los datos del experimento
    url = 'https://prevebsabackend.azurewebsites.net/api/RequestBlocks'

    #Consumimos los datos del experimento
    try:
        if flag:
            #Hacemos el request a la URL
            respuesta = requests.get(url)

            #Los leemos como JSON
            data_json = respuesta.json()

            #Convertimos los datos a un DataFrame
            data = pd.DataFrame(data_json)

            #Exportamos los datos
            data.to_excel('datos_experimento.xlsx', index = False)

    except requests.exceptions.RequestException as e:
        print(f'Error al obtener los datos: {e}')

    #Importamos datos del experimento como DataFrame para modificar fechas
    data = pd.read_excel('datos_experimento.xlsx')

    #La convertimos en datatime
    data['requestTime'] = pd.to_datetime(data['requestTime'], errors='coerce')

    #Quitamos zonahoraria en columnas de fecha
    data['requestTime'] = data['requestTime'].dt.tz_localize(None)

    #Extraemos la hora de la fecha
    data['hora_request'] = data['requestTime'].dt.strftime('%H:%M:%S')

    #Reorganizamos dataframe
    data = data[['id', 'requestTime', 'hora_request', 'userId', 'requestType', 'statusCode', 'blocked']]
    
    #Volvemos a exportar el archivo
    data.to_excel('datos_experimento.xlsx', index = False)