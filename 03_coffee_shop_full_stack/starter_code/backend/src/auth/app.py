from flask import Flask, request

app = Flask(__name__)

@app.route('/headers', methods= ['POST', 'GET'])
def headers():
    #temp = request.get_json()
    temp = request.headers['Authorization']
    heards_parts = auth_header.split(' ')
    if temp:
        print(request.get_json())
        return temp
    else:
        print('missing')
        return 'missing'
        #print(temp['Authorization'])
 #   auth_header = request.headers['Authorization']
 #   print(auth_header)
 #   return request.headers