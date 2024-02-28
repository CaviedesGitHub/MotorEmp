from flask_restful import Api
from flask_jwt_extended import JWTManager

from flask import Flask
import os
from flask_cors import CORS


def create_app(config_name, settings_module='config.ProductionConfig'):
    app=Flask(__name__)
    app.config.from_object(settings_module)
    return app

settings_module = os.getenv('APP_SETTINGS_MODULE','config.ProductionConfig')
application = create_app('default', settings_module)
app_context=application.app_context()
app_context.push()

CORS(application)

from datetime import datetime
from datetime import timedelta
import math
import random
import uuid
from flask import request, copy_current_request_context
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
import os
import json
from faker import Faker
from time import sleep
import threading
import concurrent.futures
import requests


class VistaEmparejar(Resource):
    def post(self):
        print("Emparejando")
        print(request.json)
        lstPerfiles=request.json.get("ListaPerfiles")
        lstIdPerfiles=[]
        for p in lstPerfiles:
            calificacion=random.randint(70, 100)
            p["Calificacion"]=calificacion
            lstIdPerfiles.append(p.get('id_perfil'))
        
        print(lstIdPerfiles)
        #lstIdPerfiles=[1,3,5,9]
        headers={} 
        body={"lstPerfiles":lstIdPerfiles}
        print(f"{application.config['HOST_PORT_CANDIDATO']}/candidatos/perfiles")
        #response = send_post_request(f"{application.config['HOST_PORT_CANDIDATO']}/candidatos/perfiles",headers=headers, body=body)
        response = solicitud_candidatos(f"{application.config['HOST_PORT_CANDIDATO']}/candidatos/perfiles", body=body, headers=headers)        
        if response==-1 or response is None:
            return {"Mensaje ":"Microservicio Candidatos NO esta disponible.", "Candidatos":[]}, 200
        else:
            if response.get("Candidatos") is None:
                return {"Mensaje ":"Parametro Candidatos Ausente.", "Candidatos":[]}, 200
            else:
                if len(response.get("Candidatos"))==0:
                    return {"Mensaje ":"Parametro Candidatos Vacio.", "Candidatos":[]}, 200

        
        lstCandidatos=response.get("Candidatos")
        for p in lstPerfiles:
            #print(p)
            for c in lstCandidatos:
                #print("c", c)
                if p["id_perfil"]==c["id_perfil"]:
                    c["Calificacion"]=p["Calificacion"]

        #for c in lstCandidatos:
        #    print(c)

        for c in lstCandidatos:
            cal_inf=c["Calificacion"]
            c["Calificacion"]=100 #random.randint(cal_inf, 100)
        #print(lstPerfiles)
        print(sorted(lstCandidatos, key=lambda i: i['Calificacion'], reverse=True))
        lstCandidatos=sorted(lstCandidatos, key=lambda i: i['Calificacion'], reverse=True)
        lstCandidatosCorte=[]
        if len(lstCandidatos)<=20:
            lstCandidatosCorte=lstCandidatos
        else:
            for i in range(20):
                lstCandidatosCorte.append(lstCandidatos[i])

        return {"Candidatos":lstCandidatosCorte}, 200 #{"Mensaje":"Emparejar"}, 200

class VistaPing(Resource):
    def get(self):
        print("pong")
        return {"Mensaje":"Pong"}, 200


def send_post_request(url, headers, body):
    try:
        response = requests.post(url, json=body, headers=headers, timeout=5000)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as inst:
        print(type(inst))
        #print(inst)
        return -1

def solicitud_candidatos(url, body, headers):
    headers=headers #headers = {"Authorization": f"Bearer {os.environ.get('TRUE_NATIVE_TOKEN')}"}
    body=body #body = {"user": user_data, "transactionIdentifier": str(uuid.uuid4()), "userIdentifier": str(id),
        #"userWebhook": f"http://{os.environ.get('USERS_MS')}/users/verification-webhook"}

    for i in range(3):
        response = send_post_request(url, headers=headers, body=body)
        if response==-1:
            print("Error. Miscroservicio Perfiles NO esta disponible.")
        elif response is None:
            print("Error Microservicio Perfiles. Codigo de respuesta diferente de 200.")
        else:
            print("Exito. Respuesta Exitosa desde Microservicio Perfiles.")
            break
    #print(response)
    return response


api = Api(application)
api.add_resource(VistaEmparejar, '/motor/emparejar')
api.add_resource(VistaPing, '/motor/ping')


jwt = JWTManager(application)