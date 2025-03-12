import logging
import requests

#URL de la API de metricas
metrics_report_api = 'https://prevebsabackend.azurewebsites.net/api/RequestBlocks'

def metricas(id, peticion, status_code, blocked):
    #Creamos el json con la informacion de la metrica
    json = {
        "UserId": id,
        "RequestType": peticion,
        "StatusCode": status_code,
        "Blocked": blocked
    }

    #Enviamos metricas a la URL de la API
    send_metrics(json)

def send_metrics(message_body):
    try:
        response = requests.post(metrics_report_api, json = message_body)
        logging.info(f"Metrics sent - Status: {response.status_code}")

    except Exception as e:
        logging.error(f"An error occurred while sending metrics: {e}")