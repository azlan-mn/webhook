import sqlite_utils
import json

from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def webhook():
    out = []
    if request.method == 'POST':
        out.append(str(request.json))
    else:
        try:
            sqliteConnection = sqlite3.connect('sql.db')
            cursor = sqliteConnection.cursor()
            out.append('DB Init')
            query = 'select sqlite_version();'
            cursor.execute(query)
            result = cursor.fetchall()
            out.append('SQLite Version is {}'.format(result))
            cursor.close()
        except sqlite3.Error as error:
            print('Error occurred - ', error)
        finally:
            if sqliteConnection:
                sqliteConnection.close()
        out.append('SQLite Connection closed')
    print('\n'.join(out))
    return '\n'.join(out)

#@app.route('register/<webhook_id>', methods=['POST'])
#def register(webhook_id):
#    out = []
#    for 
#    db = sqlite_utils.Database("sql.db")
#    db['hooks'].insert
#    return webhook_id

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

