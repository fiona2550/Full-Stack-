from flask import Flask, request

app = Flask(__name__)

@app.route('/headers')
def headers():
    temp = request.headers.get('Authorization',None)
    if temp:
        print('missing')
    else:
        print('not missing')
        #print(temp['Authorization'])
 #   auth_header = request.headers['Authorization']
 #   print(auth_header)
 #   return request.headers