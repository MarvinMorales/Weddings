from audioop import cross
from msilib.schema import Directory
from sqlite3 import Cursor
from tokenize import String
from urllib import response
from flask import Flask, request, Response, send_from_directory, jsonify
from flask_cors import CORS, cross_origin
from ffmpeg_streaming import Representation, Size, Bitrate, Formats
from datetime import datetime, timedelta
import ffmpeg_streaming
from dotenv import load_dotenv
import mysql.connector
import hashlib
import jwt
import json
import shutil
import os

app = Flask(__name__)
CORS(app)

def Encode_jwt(__payload:str) -> str:
  token_bytes = jwt.encode(__payload, key=os.getenv('SECRET'), algorithm='HS512')
  return token_bytes

def Validate_token(__token:str) -> str:
  try:
    jwt.decode(__token, key=os.getenv('SECRET'), algorithms=['HS256', 'HS512'])
    return {"response": "Valid"}
  except jwt.exceptions.DecodeError as err:
    return {"response": "__TOKEN NOT VALID__", "err": str(err)}
  except jwt.ExpiredSignatureError as err:
    return {"response": "__TOKEN EXPIRED__", "err": str(err)}
  except jwt.InvalidTokenError as err:
    return {"response": "__TOKEN NOT VALID__", "err": str(err)}

#___ Connection to DataBase ___#
def connectDataBase() -> mysql.connector:
    conn = mysql.connector.connect(
        host="localhost",
        database="gabrielstreaming",
        user=os.getenv('dbuser'),
        passwd=os.getenv('dbpassword'))
    return conn

def get_project_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for i in filenames:
            f = os.path.join(dirpath, i)
            total_size += os.path.getsize(f)
    return total_size

"""Middleware declaration to start using environment vars"""
@app.before_first_request
def enable_DotEnv():
    load_dotenv()

#Be carefull with the expiration days token
#it can be a bug while testing phase
@app.route("/auth", methods=["POST"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"], max_age=300)
def auth_api_route() -> Response:
    if request.method == "POST":
        data = json.loads(request.data)
        conn = connectDataBase()
        cursor = conn.cursor()
        hashed_string = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
        sql_statement = f"""Select * from `admins` where `email` = 
        '{data['email']}' and `password` = '{hashed_string}';"""
        cursor.execute(sql_statement)
        adminFound = cursor.fetchall()
        if len(adminFound) == 1:
            token = Encode_jwt({"user": f"{datetime.now()}-{adminFound[0][0]}", 'exp': datetime.now() + timedelta(days=10)})
            response = Response(json.dumps({"success": True, "user_name":adminFound[0][4], "user_ID": adminFound[0][0]}))
            response.headers["Authorization"] = token
            response.headers['Access-Control-Expose-Headers'] = '*'
            response.headers['Content-Type'] = "application/json"
            response.status = 200
            return response
        elif len(adminFound) != 1: return {"success": True, "reason": "no user found!"}, 200

@app.route("/<int:admin_ID>/create/project/<string:folder>", methods=["GET"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"], max_age=300)
def create_project_folder(folder: str, admin_ID: int) -> Response:
      if request.method == "GET":
          validation = Validate_token(request.headers['Authorization'])
          if validation['response'] == "Valid":
              conn = connectDataBase()
              cursor, project_info = conn.cursor(), dict()
              if not os.path.exists(os.getcwd() + f'/proyectos/{folder}'): 
                  os.makedirs(os.getcwd() + f'/proyectos/{folder}')
              if os.path.exists(os.getcwd() + f'/proyectos/{folder}'):
                  os.makedirs(os.getcwd() + f'/proyectos/{folder}/fotos')
                  os.makedirs(os.getcwd() + f'/proyectos/{folder}/videos')
                  cursor = conn.cursor()
                  cursor.execute(f"Select `name` from `admins` where `ID` = {admin_ID}")
                  project_info["project_rating"] = [0,0,0,0,0]
                  project_info["project_creator"] = cursor.fetchall()[0][0]
                  project_info["project_creation_date"] = str(datetime.now())
                  project_info["videos"] = dict()
                  project_info["fotos"] = dict()
                  project_info["project_size"] = ""
                  cursor.execute(f"Insert into `projects` (`project_name`, `project_info`) values ('{folder}', '{json.dumps(project_info)}');")
                  conn.commit()
                  cursor.close()
                  conn.close()
                  response = Response(json.dumps({"success": True}))
                  response.headers['Content-Type'] = "application/json"
                  response.headers['Access-Control-Expose-Headers'] = '*'
                  response.status = 200 
                  return response 
              else: return {"success": False, "reason": "Folder not created"}, 200   
          else: return {"success":False, "reason":"no valid token!"}, 401  

@app.route("/upload/file/video", methods=["POST"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"], max_age=300)
def uploadFile_api_route_Video() -> Response:
    if request.method == "POST":
        validation = Validate_token(request.headers['Authorization'])
        if validation['response'] == "Valid":
            conn = connectDataBase()
            cursor = conn.cursor(dictionary=True)
            file = request.files['video']
            projectName = json.loads(request.form.get('projectName'))
            files_path = os.getcwd() + f"/proyectos/{projectName['name']}/videos/"
            folder = [x for x in file.filename.split(".")][0]
            file.save(files_path + f"{request.files['video'].filename}")
            _1080p  = Representation(Size(1920, 1080), Bitrate(2048 * 1024, 320 * 1024))
            video = ffmpeg_streaming.input(f'{files_path}/{folder}/{file.filename}')
            hls = video.hls(Formats.h264())
            hls.representations(_1080p)
            hls.output(f'{files_path}/{folder}/index.m3u8')
            cursor.execute("Select `project_info` from `projects` where `project_name` = '{}';".format(projectName['name']))
            result = json.loads(cursor.fetchall()[0]['project_info'])
            result['videos'][file.filename] = dict()['rating'] = [0,0,0,0,0]
            projectSize = get_project_size(os.getcwd() + f"/proyectos/{projectName['name']}")
            result['project_size'] = round(projectSize * 9.537 * pow(10, -7), 2)
            cursor.execute("""Update `projects` set `project_info` = '{}' where `project_name` = '{}'""".format(json.dumps(result), projectName['name']))
            conn.commit()
            cursor.close()
            conn.close()
            response = Response(json.dumps({"success": True, "fileUpload": file.filename}))
            response.headers['Content-Type'] = "application/json"
            response.status = 200
            return response
        else: return {"success":False, "reason":"no valid token!"}, 401  

@app.route("/upload/file/image", methods=["POST"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"], max_age=300)
def uploadFile_api_route_Image() -> Response:
    if request.method == "POST":
      validation = Validate_token(request.headers['Authorization'])
      if validation['response'] == "Valid":
          file = request.files['image']
          conn = connectDataBase()
          cursor = conn.cursor(dictionary=True)
          projectName = json.loads(request.form.get('projectName'))
          files_path = os.getcwd() + f"/proyectos/{projectName['name']}/fotos/"
          file.save(files_path + f"{request.files['image'].filename}")
          cursor.execute("Select `project_info` from `projects` where `project_name` = '{}';".format(projectName['name']))
          result = json.loads(cursor.fetchall()[0]['project_info'])
          projectSize = get_project_size(os.getcwd() + f"/proyectos/{projectName['name']}")
          result['project_size'] = round(projectSize * 9.537 * pow(10, -7), 2)
          result['fotos'][file.filename] = dict()['rating'] = [0,0,0,0,0]
          cursor.execute("Update `projects` set `project_info` = '{}' where `project_name` = '{}'".format(json.dumps(result), projectName['name']))
          conn.commit()
          cursor.close()
          conn.close()
          response = Response(json.dumps({"success":True}))
          response.headers['Content-Type'] = "application/json"
          response.status = 200
          return response
      else: return {"success":False, "reason":"no valid token!"}, 401  

@app.route("/<int:admin_id>/retrieve/projects", methods=["GET"])
@cross_origin(origins="*", allow_headers=["Authorization"], max_age=300)
def retrieve_projects(admin_id: int) -> Response:
      if request.method == "GET":
            validation = Validate_token(request.headers['Authorization'])
            if validation['response'] == "Valid":
                  conn = connectDataBase()
                  cursor = conn.cursor()
                  cursor.execute(f"Select `project_name`, `project_info` from `projects`;")
                  projects, result = dict(), cursor.fetchall()
                  for project in result: projects[project[0]] = json.loads(project[1])
                  cursor.close()
                  conn.close()
                  response = Response(json.dumps({"success": True, "root_projects": projects}))
                  response.headers['Content-Type'] = "application/json"
                  response.status = 200
                  return response
            else: return {"success":False, "reason":"no valid token!"}, 401  

@app.route("/<int:admin_id>/delete/projects/<string:projects_list>", methods=["GET"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"], max_age=300)
def delete_projects(projects_list: str, admin_id: int) -> Response:
      if request.method == "GET":
          validation = Validate_token(request.headers['Authorization'])
          if validation['response'] == "Valid":
              conn = connectDataBase()
              cursor = conn.cursor()
              for project in json.loads(projects_list):
                  shutil.rmtree(os.getcwd() + f'/proyectos/{project}')
                  cursor.execute(f"Delete from `projects` where `project_name` = '{project}';")
                  conn.commit()
              cursor.execute(f"Select `project_name`, `project_info` from `projects`;")
              cursor.close()
              conn.Close()
              projects, result = dict(), cursor.fetchall()
              for project in result: projects[project[0]] = json.loads(project[1])
              response = Response(json.dumps({"success": True, "root_projects": projects}))
              response.headers['Content-Type'] = "application/json"
              response.status = 200
              return response
          else: return {"success":False, "reason":"no valid token!"}, 401  

@app.route("/load/video/streaming/hls/<string:folder>/<string:video>", methods=["GET"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"], max_age=300)
def request_for_video_streaming(folder: str, video: str) -> send_from_directory:
    if request.method == "GET":
      file_path = os.getcwd() + '/files/' + folder
      return send_from_directory(file_path, path=video, as_attachment=False)
              

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=12000)