from flask import Flask, request, jsonify

app = Flask(__name__)

services = []
s3 = boto3.client('s3',
	endpoint_url='https://s3.filebase.com',
	aws_access_key_id="filebase-access-key",
	aws_secret_access_key="filebase-secret-key")

@app.route('/register_service', methods=['GET'])
def register_service():
    data = request.get_json()
    service_name = data['name']
    service_url = data['url']
    services.append({'name': service_name, 'url': service_url})
    return jsonify({'message': 'Service registered successfully.'})

@app.route('/list_services', methods=['GET'])
def list_services():
    return jsonify(services)

@app.route('/user/services')
def list_services():
    return jsonify(services)

if __name__ == '__main__':
    app.run(debug=True)


    # to do
    # 1. add address, name(string)

    # to do
    # services offered
