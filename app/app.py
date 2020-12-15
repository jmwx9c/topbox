from bson import json_util, ObjectId
from flask import Flask, request, jsonify

from webargs import fields, validate, missing
from webargs.flaskparser import FlaskParser

from app.helpers import mongo_client

API_VERSION = '1.0'

app = Flask(__name__)
db = mongo_client()


class Parser(FlaskParser):
    DEFAULT_VALIDATION_STATUS = 400

# use derived Parser class for default error status = 400, not 422
parser = Parser()
use_kwargs = parser.use_kwargs


@app.route('/')
def root():
    response = {'apiVersion': API_VERSION, 'appName': 'Topbox Backend Take Home Test'}
    return json_util.dumps(response)


@app.route('/clients')
def clients():
    return json_util.dumps(db.clients.find({}))


@app.route('/clients/<client_id>')
def clients_by_id(client_id):
    client_object_id = ObjectId(client_id)
    return json_util.dumps(db.clients.find_one({'_id': client_object_id}))


@app.route('/engagements')
def engagements():
    return json_util.dumps(db.engagements.find({}))


@app.route('/engagements/<engagement_id>')
def engagements_by_id(engagement_id):
    engagement_object_id = ObjectId(engagement_id)
    return json_util.dumps(db.engagements.find_one({'_id': engagement_object_id}))


@app.route('/interactions')
@use_kwargs({'engagementId': fields.Str(required=True, validate=lambda x: ObjectId.is_valid(x)), 'startDate': fields.DateTime(missing=None), 'endDate': fields.DateTime(missing=None)}, location="query")
def interactions(engagementId, startDate, endDate, **kwargs):
    db_query = {}
    db_query['engagementId'] = ObjectId(engagementId)

    # get the date params
    if startDate or endDate:
        date_dict = {}
        if startDate:
            date_dict['$gte'] = startDate
        if endDate:
            date_dict['$lt'] = endDate
        
        db_query['interactionDate'] = date_dict

    return json_util.dumps(db.interactions.find( db_query ))

@app.errorhandler(422)
@app.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code

@app.route('/interactions/<interaction_id>')
def interactions_by_id(interaction_id):
    interaction_object_id = ObjectId(interaction_id)
    return json_util.dumps(db.interactions.find_one({'_id': interaction_object_id}))
