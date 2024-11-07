from flask import Flask, request
import os
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
    raise NotImplementedError("Ongoing is not implemented yet")
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



@app.route("/")
def hello_world():
    return "<p>Hello, World!\nLOL1</p>"



if __name__ == '__main__':
    # app.run(host='0.0.0.0')
    # app.run()
    # get_results('950203', 1, with_reps=True)

    print(backend_utils.check_user_exist('950203/ATTEMPT1/vid'))
