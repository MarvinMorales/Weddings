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
            token = Encode_jwt({"user": f"{datetime.now()}-{adminFound[0][0]}", 'exp': datetime.now() + timedelta(days=1)})
            response = Response(json.dumps({"success": True, "user_ID": adminFound[0][0]}))
            response.headers["Authorization"] = token
            response.headers['Access-Control-Expose-Headers'] = '*'
            response.status = 200
            return response
        elif len(adminFound) != 1: return {"success": True, "reason": "no user found!"}, 200

@app.route("/upload/file/video", methods=["POST"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"], max_age=300)
def uploadFile_api_route() -> dict:
    if request.method == "POST":
      validation = Validate_token(request.headers['Authorization'])
      if validation['response'] == "Valid":
          file = request.files['image']
          files_path = os.getcwd() + '/files/'
          folder = [x for x in file.filename.split(".")][0]
          if not os.path.exists(f'{files_path}/{folder}'): os.makedirs(f'{files_path}/{folder}')
          file.save(files_path + f'{folder}/' + file.filename)
          _1080p  = Representation(Size(1920, 1080), Bitrate(2048 * 1024, 320 * 1024))
          video = ffmpeg_streaming.input(f'{files_path}/{folder}/{file.filename}')
          hls = video.hls(Formats.h264())
          hls.representations(_1080p)
          hls.output(f'{files_path}/{folder}/index.m3u8')
          os.remove(f'{files_path}/{folder}/{file.filename}')
          response = Response(json.dumps({"success": True, "fileUpload": file.filename}))
          return response, 200
      else: return {"success": False, "reason": "token expired!"}, 200

@app.route("/load/video/streaming/hls/<string:folder>/<string:video>", methods=["GET"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"], max_age=300)
def request_for_video_streaming(folder: str, video: str) -> send_from_directory:
    if request.method == "GET":
      file_path = os.getcwd() + '/files/' + folder
      return send_from_directory(file_path, path=video, as_attachment=False)

@app.route("/admin/create/project", methods=["POST"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"], max_age=300)
def crrate_project() -> dict:
      if request.method == "POST":
          pass
      return 200

@app.route("/<int:admin_id>/retrieve/projects", methods=["GET"])
@cross_origin(origins="*", allow_headers=["Authorization"], max_age=300)
def retrieve_projects(admin_id: int) -> Response:
      if request.method == "GET":
          #validation = Validate_token(request.headers['Authorization'])
          #if validation['response'] == "Valid":
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

@app.route("/<int:admin_id>/delete/projects/<string:projects_list>", methods=["GET"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"], max_age=300)
def delete_projects(projects_list: str, admin_id: int) -> Response:
      if request.method == "GET":
          #validation = Validate_token(request.headers['Authorization'])
          #if validation['response'] == "Valid":
          conn = connectDataBase()
          cursor = conn.cursor()
          for project in json.loads(projects_list):
              shutil.rmtree(os.getcwd() + f'/proyectos/{project}')
              cursor.execute(f"Delete from `projects` where `project_name` = '{project}';")
          cursor.execute(f"Select `project_name`, `project_info` from `projects`;")
          projects, result = dict(), cursor.fetchall()
          for project in result: projects[project[0]] = json.loads(project[1])
          response = Response(json.dumps({"success": True, "root_projects": projects}))
          response.headers['Content-Type'] = "application/json"
          response.status = 200
          return response
          #else: return Response(status=401)
              

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=12000)