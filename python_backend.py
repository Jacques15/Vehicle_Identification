from flask import Flask,flash,redirect,request, url_for, render_template
from werkzeug.utils import secure_filename
import urllib.request
import os
import boto3
import botocore
import pprint

#This script provides the backend for a web application. The application uses a custom AWS Rekognition to guess what type of vehicle is present in an uploaded image

print(os.listdir())

vehicle_description = "" #Used when outputting the name of the vehicle

client = boto3.client('rekognition')
#modelarn = 'arn:aws:rekognition:us-east-2:523448548376:project/VehicleClassifierSimple/version/VehicleClassifierSimple.2021-11-01T17.57.17/1635742453265' 
modelarn = 'arn:aws:rekognition:us-east-1:523448548376:project/VehicleClassifierImproved/version/VehicleClassifierImproved.2021-11-02T22.26.36/1635845010942'

#List allowed extensions
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif'])

#Used to determine is uploaded file is of a type that is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS    

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route("/")
def home():
    return render_template('index.html')

# When an image is posted, this code executes
@app.route('/',methods = ['POST'])
def upload_image():
    if 'file' not in request.files: 
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading') #No image selected
        return(redirect(request.url))
    # If a file is submitted and it is of a type that is allowed
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'],filename)   
        with open(path, 'rb') as image:
            response = client.detect_custom_labels(ProjectVersionArn=modelarn,Image={'Bytes': image.read()})

        vehicle = response['CustomLabels'][0]['Name'] #This saves the top name of a vehicle. This corresponds to the vehicle type with the highest confidence
        confidence = round(response['CustomLabels'][0]['Confidence'],2) #Saves the confidence of the vehicle 
        vehicle_description = 'This vehicle is a ' + str(vehicle) + '! (Confidence = ' + str(confidence) + ')' #This is displayed after an image is uploaded
        return render_template('index.html',path=path,vehicle_description=vehicle_description) #This updates the message
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif') #Dispalyed if type of file uploaded is not allowed
        return redirect(request.url)

if __name__ == "__main__":
    app.run() 