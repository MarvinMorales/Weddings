from flask import Flask, request, Response, send_from_directory
from flask_cors import CORS, cross_origin
from ffmpeg_streaming import Representation, Size, Bitrate, Formats
from datetime import datetime, timedelta
import ffmpeg_streaming
from dotenv import load_dotenv
import mysql.connector
import hashlib
import jwt
import json
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
        host="mysql.pythonanywhere-services.com",
        database="db",
        user="user",
        passwd="pass!")
    return conn

"""Middleware declaration to start using environment vars"""
@app.before_first_request
def enable_DotEnv():
    load_dotenv()

@app.route("/auth", methods=["POST"])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"], max_age=300)
def auth_api_route() -> Response:
    if request.method == "POST":
        data = json.loads(request.data)
        cursor = connectDataBase().cursor()
        hashed_string = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
        sql_statement = f"""Select * from `admins` where `email` = 
        '{data['email']}' and `password` = '{hashed_string}';"""
        cursor.execute(sql_statement)
        adminFound = cursor.fetchall()
        if len(adminFound) == 1:
            token = Encode_jwt({"user": f"{datetime.now()}-{adminFound[0][0]}", 'exp': datetime.now() + timedelta(days=1)})
            response = Response(json.dumps({"success": True}))
            response.headers["Authorization"] = token
            return response, 200
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

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=12000)