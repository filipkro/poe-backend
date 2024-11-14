import os
# import boto3
#from configparser import ConfigParser
# from botocore.exceptions import NoCredentialsError, ClientError
# from dateutil import tz
# from datetime import date
# import re
# import datetime
from rq import Queue
import redis
import pipeline

if os.environ.get("REDIS_URL") is not None:
    r = redis.from_url(os.environ.get("REDIS_URL"))
else:
    r = redis.from_url('redis://redis:6379')

q = Queue(connection=r)

BASE = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
#config = ConfigParser()

#config.read(os.path.join(BASE, 'configs/config'))
#ACCESS_KEY = config.get('aws', 'access')
#SECRET_KEY = config.get('aws', 'secret')

#del config, ConfigParser
def check_ongoing(vid):
    path = vid.split('.')[0] + '-ONGOING'
    return os.path.exists(os.path.join('/data', path))

def check_completed(vid):
    path = vid.split('.')[0] + '.json'
    return os.path.exists(os.path.join('/data', path))

def get_variable_from_req(request, key):
    var = request.form.get(key)
    print(var)
    if var is None:
        print('args')
        var = request.args.get(key)
    if var is None:
        print('values')
        var = request.values.get(key)

    return var


def get_attempt_nbr(id):

    return 2

def file_on_aws(file):
    return True
# def file_on_aws(file):
#     s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
#                       aws_secret_access_key=SECRET_KEY)

#     return 'Contents' in s3.list_objects(Bucket='poe-uploads', Prefix=file)


def check_user_exist(id):
    return file_on_aws(f'users/{id}')


def check_result_available(id, attempt):
    return file_on_aws(f'users/{id}/ATTEMPT{attempt}/results.pkl')

def delete_from_aws(file):
    print("Delete Successful")
    return True

# def delete_from_aws(file):
#     s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
#                       aws_secret_access_key=SECRET_KEY)

#     bucket='poe-uploads'
#     try:
#         s3.delete_object(Bucket=bucket, Key=file)
#         print("Delete Successful")
#         return True
#     except FileNotFoundError:
#         print("The file was not found")
#         return False
#     except NoCredentialsError:
#         print("Credentials not available")
#         return False


def get_result_for_user(id):
    return 0


def predict(file_path, leg, debug=None):
    # vid = '/app/dummy-data/950203/ATTEMPT1/vid.mts'
    job = q.enqueue(pipeline.pipe, args=(file_path, leg, debug),
                    job_timeout=-1)

    return (f"Prediction for {file_path} started!\nTask ({job.id})" +
            " added to queue at {job.enqueued_at}")


if __name__ == '__main__':

    print(check_user_exist('950203/ATTEMPT1/vid'))
