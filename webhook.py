import sqlite_utils
import json

from flask import Flask, request

app = Flask(__name__)

@app.post('/<webhook_id>')
def respond(webhook_id):
    return { 'status': 'success' }

@app.post('/register/<webhook_id>')
def register(webhook_id):
    data = { 'id': webhook_id }
    for key in ['payload', 'extract']:
        if key not in request.json:
            return 'Incorrect input.\nExpected: {extract:str, payload:str}\nReceived: ' + str(request.json), 400
        data[key] = request.json[key]
    #return json.loads(request.json['payload'])

    try:
        db = sqlite_utils.Database('sql.db')
        db['hooks'].insert(data, pk='id', replace=True)
        result = db['hooks'].get(data['id'])
    except BaseException as e:
        return 'Error\n' + str(e), 500

    return { 'status': 'success', 'db': result }

@app.route('/', methods=['POST', 'GET'])
def webhook():
    out = [
        '',
        '# Usage:',
        '',
        '## POST /<webhook_id> - Webhook will respond with preconfigured response.',
        '',
        '- All payloads accepted.',
        '',
        '## POST /register/<webhook_id> - Configure a response to any request send to webhook endpoint.',
        '',
        '- Expected json payload:',
        '   - extract: Comma delimited string of JSON attributes to extract from request, and replace in response payload.',
        '   - payload: JSON string that will be sent back in webhook response.',
    ]
    return '\n'.join(out)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

