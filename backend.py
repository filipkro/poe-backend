from flask import Flask, request, send_file
import flask
import os
import json
from werkzeug.utils import secure_filename
import boto3
from configparser import ConfigParser
import backend_utils

app = Flask(__name__)

BASE = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
# config = ConfigParser()

# config.read(os.path.join(BASE, 'configs/config'))
# ACCESS_KEY = config.get('aws', 'access')
# SECRET_KEY = config.get('aws', 'secret')

# del config, ConfigParser



@app.route('/ongoing', methods=['GET'])
def get_ongoing():
    '''
        Check if assessment is ongoing for user, specified by id.
        Returns 'Ongoing' if assessment is ongoing and 'Finished' if it is
        completed.
    '''
    id = backend_utils.get_variable_from_req(request, 'id')
    print(f'Check ongoing for user with id {id}')
    if id is None:
        return "No id provided", 400

    if not backend_utils.check_user_exist(id):
        return "User not in database", 404

    attempt = backend_utils.get_attempt_nbr(id) - 1
    if backend_utils.check_ongoing(id, attempt):
        return "Ongoing", 200
    else:
        return "Finished", 201

@app.route('/analyse_video', methods=['POST'])
def analyse_video():
    '''
        Analyse video specified by path
    '''
    path = backend_utils.get_variable_from_req(request, 'path')
    leg = backend_utils.get_variable_from_req(request, 'leg')
    debug = backend_utils.get_variable_from_req(request, 'debug')
    print(path)
    status = backend_utils.predict(path, leg, debug=debug)
    return f"{path} to be analysed,\n{status}", 200


@app.route('/tt', methods=['POST'])
def tt():
    print('writing file??')
    with open('/data/out.txt', 'w') as fo:
        fo.write('lol')

    return "ok", 200

@app.route('/upload', methods=['POST'])
def upload_video():
    '''
        Upload video to assess. Specify id and leg
        (and frames between repetitions, TO BE IMPLEMENTED).
        Video provided as file in files.
    '''
    import cv2
    id = backend_utils.get_variable_from_req(request, 'id')
    print(f'Upload for user with id {id}')
    if id is None:
        print("No id provided")
        return "No id provided", 400
    leg = backend_utils.get_variable_from_req(request, 'leg')
    if leg is None:
        print("No leg provided")
        return "No leg provided", 400

    debug = backend_utils.get_variable_from_req(request, 'debug')
    print(f'DEBUG: {debug}')

    if not backend_utils.check_user_exist(id):
        print("User not in database")
        return "User not in database", 404

    attempt = backend_utils.get_attempt_nbr(id)

    frame_splits = request.form.getlist('frames')
    print(id)

    meta = {'leg': leg, 'frames': tuple(frame_splits)}

    meta_name = 'meta'
    f = open(meta_name, 'w')
    json.dump(meta, f)
    f.close()

    s3_path = f'users/{id}/ATTEMPT{attempt}/meta.json'
    uploaded = backend_utils.upload_to_aws(meta_name, s3_path)

    if not uploaded:
        print("Could not save meta data to S3")
        return "Could not save meta data to S3", 501

    if 'file' not in request.files:
        print(request.url)
        print("no file in files")
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        print("no filename")
        return "No video selected for uploading", 400
    else:
        filename = secure_filename(file.filename)
        print(filename)

        file_path = os.path.join('/app', filename)
        file.save(file_path)
        print(type(file))
        file.close()
        # cap = cv2.VideoCapture(file_path)
        with open(file_path, 'rb') as fi:
            file = fi.read()
        s3_name = f'users/{id}/ATTEMPT{attempt}/vid.'
        s3_name = s3_name + filename.split('.')[-1] if '.' in filename else \
            s3_name + 'mp4'
        print(s3_name)
        uploaded = backend_utils.upload_to_aws(file_path, s3_name)
        os.remove(file_path)
        if uploaded:
            print('upload_video filename: ' + filename)
            status = backend_utils.predict(s3_name, id, leg, file, attempt=attempt,
                                           debug=debug)
            return f"{filename} uploaded,\n{status}", 200
        else:
            print("not uploaded to aws correctly")
            return "File could not be uploaded to S3", 501


@app.route("/")
def hello_world():
    return "<p>Hello, World!\nLOL1</p>"


@app.route("/create_user", methods=["POST"])
def create_user():
    '''
        Create user in database, provide id, injured leg, weight, and length.
    '''
    id = backend_utils.get_variable_from_req(request, 'id')
    print(f'Creating user with id {id}')
    if id is None or id == '':
        return "No id provided", 400
    leg = request.form.get('leg')

    weight = request.form.get('weight')
    length = request.form.get('length')
    name = request.form.get('name')
    injury = request.form.get('injury')
    sex = request.form.get('sex')
    date = request.form.get('date')

    if backend_utils.check_user_exist(id):
        # overwrite previous information??
        return "User already exists", 401

    params = {'id': id, 'leg': leg, 'weight': weight, 'length': length,
              'name': name, 'injury': injury, 'sex': sex, 'date': date}

    f = open('user_params', 'w')
    json.dump(params, f)
    f.close()

    s3_path = f'users/{id}/user_params.json'
    uploaded = backend_utils.upload_to_aws('user_params', s3_path)

    if uploaded:
        return "User successfully created", 200
    else:
        return "Something went wrong when saving to S3, plz view logs", 501


if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    # app.run()
    # get_results('950203', 1, with_reps=True)

    print(backend_utils.check_user_exist('950203/ATTEMPT1/vid'))
