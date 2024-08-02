import sqlite_utils
import json

from flask import Flask, request

app = Flask(__name__)

@app.post('/<webhook_id>')
def respond(webhook_id):
    def copy_dict_value(copy_key, req_d, res_d):
        if copy_key in req_d and copy_key in res_d:
            res_d[copy_key] = req_d[copy_key]
        for key in req_d:
            if key in res_d \
                and isinstance(req_d[key], dict) \
                and isinstance(res_d[key], dict):
                copy_dict_value(copy_key, req_d[key], res_d[key])
    try:
        db = sqlite_utils.Database('sql.db')
        # save request
        db['request'].insert({ 'id': webhook_id, 'payload': json.dumps(request.json) }, pk='id', replace=True)
        row = db['hooks'].get(webhook_id)
    except BaseException as e:
        return 'Error\n' + str(e), 500
    response = json.loads(row['payload'])
    tokens = row['extract'].split(',')
    for token in tokens:
        copy_dict_value(token, request.json, response)
    # save response
    db['response'].insert({ 'id': webhook_id, 'payload': json.dumps(response) }, pk='id', replace=True)
    return response

@app.post('/register/<webhook_id>')
def register(webhook_id):
    data = { 'id': webhook_id }
    for key in ['payload', 'extract']:
        if key not in request.json:
            return 'Incorrect input.\nExpected: {extract:str, payload:str}\nReceived: ' + str(request.json), 400
        data[key] = request.json[key]
    try:
        db = sqlite_utils.Database('sql.db')
        db['hooks'].insert(data, pk='id', replace=True)
        result = db['hooks'].get(data['id'])
    except BaseException as e:
        return 'Error\n' + str(e), 500
    return { 'status': 'success', 'db': result }

@app.post('/echo')
def echo():
    return request.json

@app.get('/history/<webhook_id>/<history_type>')
def history(webhook_id, history_type):
    db = sqlite_utils.Database('sql.db')
    if history_type == 'request':
        try:
            return json.loads(db['request'].get(webhook_id)['payload'])
        except BaseException as e:
            return 'Error\n' + str(e), 500
    try:
        return json.loads(db['response'].get(webhook_id)['payload'])
    except BaseException as e:
        return 'Error\n' + str(e), 500

@app.route('/', methods=['POST', 'GET'])
def webhook():
    out = [
        '',
        '# Usage:',
        '',
        '## POST /<webhook_id> - Webhook will respond with preconfigured response.',
        '',
        '- JSON payloads accepted.',
        '',
        '## POST /register/<webhook_id> - Configure a response to any request send to webhook endpoint.',
        '',
        '- Expected json payload:',
        '   - extract: Comma delimited string of JSON attributes to extract from request, and replace in response payload.',
        '   - payload: JSON string that will be sent back in webhook response.',
        '',
        '## GET /history/<webhook_id>/request|response - Get the last request or response seen for the endpdoint.',
        '',
        '- No payload expected',
        '',
    ]
    return '\n'.join(out)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

