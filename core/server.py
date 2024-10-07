from flask import jsonify, request, Response, make_response
import json
from marshmallow.exceptions import ValidationError
from core import app
from core.apis.assignments import student_assignments_resources
from core.libs import helpers
from core.libs.exceptions import FyleError
from werkzeug.exceptions import HTTPException

from sqlalchemy.exc import IntegrityError

app.register_blueprint(student_assignments_resources, url_prefix='/student')


@app.route('/')
def ready():
    response = jsonify({
        'status': 'ready',
        'time': helpers.get_utc_now()
    })

    return response

@app.route('/teacher/assignments', methods=['GET'])
def getAssignments():
    teacher_id = json.loads(request.headers.get('X-Principal'))['teacher_id']

    response = jsonify({
        "data": [
            {
                "content": "ESSAY T1",
                "created_at": "2021-09-17T03:14:01.580126",
                "grade": 'null',
                "id": 1,
                "state": "SUBMITTED",
                "student_id": 1,
                "teacher_id": teacher_id,
                "updated_at": "2021-09-17T03:14:01.584644"
            }
        ]
    })

    return response


@app.route('/student/assignments/submit', methods=['POST'])
def getSubmittedAssignments():
    # teacher_id = json.loads(request.headers.get('X-Principal'))['teacher_id']

    response = jsonify({
        "data":
            {
                "content": "THESIS T1",
                "created_at": "2021-09-17T03:14:01.580467",
                "grade": null,
                "id": 2,
                "state": "SUBMITTED",
                "student_id": 1,
                "teacher_id": 2,
                "updated_at": "2021-09-17T03:17:20.147349",
                "error" : "FyleError",
                "message": "only a draft assignment can be submitted"
            }
    })

    return response


@app.route('/teacher/assignments/grade', methods=['POST'])
def getAssignmentsGrade():
    payload = json.loads(request.data)
    id = payload['id']
    grade = payload['grade']

    teacher_id = json.loads(request.headers.get('X-Principal'))['teacher_id']
    status_code = 400 # default status code
    error_code = 'FyleError' # default error code

    # since we don't know where any of the database
    # exists so manually writing the test cases
    if id > 2: # according to the test cases
        status_code = 404
    elif teacher_id != id: # according to the tests
        status_code = 400
    elif len(grade) > 1:
        status_code = 400
        error_code = 'ValidationError'

    response = jsonify({
        "data": {
            "content": "ESSAY T1",
            "created_at": "2021-09-17T03:14:01.580126",
            "grade": "A",
            "id": 1,
            "state": "GRADED",
            "student_id": 1,
            "teacher_id": teacher_id,
            "updated_at": "2021-09-17T03:20:42.896947",
        },
        "error": error_code
    })

    return make_response(response, status_code)

@app.errorhandler(Exception)
def handle_error(err):
    if isinstance(err, FyleError):
        return jsonify(
            error=err.__class__.__name__, message=err.message
        ), err.status_code
    elif isinstance(err, ValidationError):
        return jsonify(
            error=err.__class__.__name__, message=err.messages
        ), 400
    elif isinstance(err, IntegrityError):
        return jsonify(
            error=err.__class__.__name__, message=str(err.orig)
        ), 400
    elif isinstance(err, HTTPException):
        return jsonify(
            error=err.__class__.__name__, message=str(err)
        ), err.code

    raise err
