from flask import Flask, render_template, request, redirect, url_for, flash, send_file , jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user, LoginManager, UserMixin
from collections import Counter
import pandas as pd
import face_recognition
from flask_migrate import Migrate
import base64
import cv2
import numpy as np
import os
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///policeusers.db"
app.config['SECRET_KEY'] = 'your_secret_key'  # Set a secret key for session management
#app.config['SQLALCHEMY_BINDS'] = {'criminal_data': 'sqlite:///criminal_data.db'}



db = SQLAlchemy(app) 
migrate = Migrate(app, db)
login_manager = LoginManager(app)
app.app_context().push()


class User(db.Model, UserMixin):
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), primary_key=True)

    def get_id(self):
        return str(self.password)
    
class CriminalRecord(db.Model):
   # __bind_key__ = 'criminal_data'

    id = db.Column(db.Integer,primary_key = True)
    Name = db.Column(db.String(100))
    Offence = db.Column(db.String(1000))
    Time = db.Column(db.String(100))
    Month = db.Column(db.String(100))
    Year = db.Column(db.Integer)
    Hour = db.Column(db.Integer)
    Location = db.Column(db.String(100))
    Neighborhood = db.Column(db.String(100))
    Longitude = db.Column(db.Float(100))
    Latitude = db.Column(db.Float(100))
    X = db.Column(db.Integer)
    Y = db.Column(db.Integer)
    Photo = db.Column(db.LargeBinary, nullable=False)



@login_manager.user_loader
def load_user(user_password):
    return User.query.get(user_password)

@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to access this page.', 'error')
    return redirect(url_for('login'))

# ... (Your existing code for creating tables and adding initial users)

@app.route("/")
@login_required
def homepage():
    return render_template("home.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_name = request.form['name']
        entered_password = request.form['password']

        # Check if the entered credentials match any user in the database
        user = User.query.get(entered_password)

        if user and user.name == entered_name:
            # Log the user in and redirect to the home page
            login_user(user)
            return redirect(url_for('homepage'))
        else:
            # Authentication failed, render the login page with an error message
            error_message = "Invalid username or password. Please try again."
            return render_template("login.html", error_message=error_message)

    # If the request method is GET, render the login page
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    # Log the user out and redirect to the login page
    logout_user()
    return redirect(url_for('login'))

@app.route("/map")
@login_required
def map():
    return render_template("map.html")

@app.route('/criminal_record')
@login_required
def criminal_record():
    
    return render_template('criminal_report.html')
# ... (Your existing code)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("Name")
    offence = request.form.get("Offence")
    time_reported = request.form.get("Time Reported")
    location = request.form.get("Location or Landmark")
    longitude = request.form.get("Longitude")
    latitude = request.form.get("Latitude")
    x = request.form.get("X")
    y = request.form.get("Y")
    month = request.form.get("Month")
    year = request.form.get("Year")
    hour = request.form.get("Hour")
    neighborhood = request.form.get("Neighborhood")
    photo_file = request.files['photo']
    
   # face_encoding = process_criminal_photo(photo_file)
  #  fe              = face_encoding.tobytes()
    file_data = photo_file.read()
    image = np.frombuffer(file_data,np.uint8)
   
   
    new_record = CriminalRecord(
        Name=name, Offence=offence, Time=time_reported, Location=location,
        Longitude=longitude, Latitude=latitude, X=x, Y=y, Month=month,
        Year=year, Hour=hour, Neighborhood=neighborhood ,  Photo = file_data
    )
    
    # Process the photo and get the face encoding
    #if 'photo' in request.files:
       # photo_file = request.files['photo']
       # face_encoding = process_criminal_photo(photo_file)

        # Save the face encoding to the criminal record in the database
       # new_record.Photo = face_encoding
          # Check if face encoding is available
      #  if face_encoding:
            # Convert the face encoding to bytes for storage in SQLAlchemy
        #    new_record.Photo = face_encoding.tobytes()

    db.session.add(new_record)
    db.session.commit()
    return render_template('view_records.html')
     
# ... (Your existing code)
def process_criminal_photo(photo_file):
    # Read the photo
    image = face_recognition.load_image_file(photo_file)

    # Find the face encoding
    face_encoding = face_recognition.face_encodings(image)
    
    if not face_encoding:
        return None

    # Convert the face encoding to bytes for storage in SQLAlchemy
    face_encoding_bytes = photo_file.tobytes()

    return face_encoding_bytes


import base64

@app.route('/Records')
@login_required
def Records():
    records = CriminalRecord.query.all()

    # Convert the Photo field to Base64-encoded strings
    for record in records:
        
        
        if record.Photo:
           
            record.Photo = convert_image_to_base64(record.Photo)
           

    return render_template('records.html', records=records)

@app.route('/search')
# ... (your existing imports)

@app.route('/search_records')
@login_required
def search_records():
    return render_template('search_records.html')

@app.route('/search_results', methods=['POST'])
@login_required
def search_results():
    offence = request.form.get('offence')
    location = request.form.get('location')

    # Perform your database query based on the entered offence and location
    # Replace this with your actual logic
    records = CriminalRecord.query.filter_by(Offence=offence, Location=location).all()

    return render_template('search_results.html', records=records)

# ... (your existing routes)

# ... (your existing routes)

def search_records():
    if request.method == 'POST':
        offence = request.form.get('offence')
        location = request.form.get('location')

        # Perform your database query based on the entered offence and location
        # Replace this with your actual logic
        records = CriminalRecord.query.filter_by(Offence=offence, Location=location).all()

        # You may want to convert the records to a format suitable for JSON
        records_data = [{'id': record.id, 'Name': record.Name, 'Offence': record.Offence,
                         'Location': record.Location, 'Photo': record.Photo} for record in records]

        return jsonify({'records': records_data})


@app.route('/get_photo/<int:record_id>')
def get_photo(record_id):
    if record_id == None:
        print("hello")


    print(f"Accessing get_photo route for record ID: {record_id}")
   # import pdb; pdb.set_trace()
    #print(f"Accessing get_photo route for record ID: {record_id}")
    record = CriminalRecord.query.get(record_id)
    print("hello")
    if record:
        return send_file(BytesIO(record.Photo), mimetype='image/jpeg')
    else:
        return "Record not found", 404
   # photo_data = BytesIO(record.Photo)
   # print(photo_data.getvalue())
   # return send_file(photo_data, mimetype='image/jpeg' )
    
#@app.route('/Records')
#@login_required
#def Records():
  #  imgg = []
 #   records = CriminalRecord.query.all()
  #  for record in records:
  #      record.Photo = BytesIO(record.Photo)
    #    imgg.append(record.Photo)

   # return render_template('records.html',records = records, mimetype='image/jpeg')

def convert_image_to_base64(image_data):
    if image_data:
        print('hello')
       # if isinstance(image_data, str):
         #  image_data = image_data.encode('utf-8')
        print(image_data)
          # print('hello')
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        return f'data:image/jpeg;base64,{base64_encoded}'
    return None




@app.route('/Dashboard')
@login_required
def Dashboard():
    records = CriminalRecord.query.all()
    # categories = ["a","b","c"]
    # data = [1,2,3]

    offence,offence_count,location,location_count,hour,hour_count,total_crimes = structure()
    new_loc_count = len(location_count)
    new_off_count = len(offence_count)
    new_hour_count = len(hour_count)

    return render_template('dashboard.html',offence= offence,offence_count = offence_count,location = location,location_count = location_count,hour = hour,hour_count = hour_count,total_crimes = total_crimes,new_loc_count = new_loc_count,new_off_count = new_off_count,new_hour_count=new_hour_count)

def structure():
    database = CriminalRecord.query.all()
    total_crimes = len(database)

    temporary = []
    temporary_l = []
    temporary_h = []
    for temp in database:
        temporary.append(temp.Offence)
        temporary_l.append(temp.Location)
        temporary_h.append(temp.Hour)

    Offence = []
    Offence_count = []
    Location = []
    Location_count = []
    Hour = []
    Hour_count = []

    for record in Counter(temporary).keys():
        Offence.append(record)
        Offence_count.append(Counter(temporary)[record])

    for record in Counter(temporary_l).keys():
        Location.append(record)
        Location_count.append(Counter(temporary_l)[record])

    for record in Counter(temporary_h).keys():
        Hour.append(record)
        Hour_count.append(Counter(temporary_h)[record])


    return Offence,Offence_count,Location,Location_count,Hour,Hour_count,total_crimes


@app.route('/offen_track')
@login_required
def offen_track():
    return render_template('offen_track.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'video' in request.files:
        video_file = request.files['video']
        video_path = os.path.join('uploads', 'input_video.mp4')
        video_file.save(video_path)

        # Process the video
        results, frames = process_video(video_path)
        return render_template('results.html', results=results, frames=frames)

    return redirect(url_for('index'))


def process_video(video_path):
    criminals = CriminalRecord.query.all()
    cap = cv2.VideoCapture(video_path)

    results = []
    frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)

        for face_location in face_locations:
            top, right, bottom, left = face_location
            face_roi = frame[top:bottom, left:right]
            rgb_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)

            match = check_criminal_match(rgb_face, criminals)
            results.append({'frame': frame, 'match': match})
            
            # Change encoding to PNG
            frames.append(cv2.imencode('.png', frame)[1].tobytes())

    cap.release()
    cv2.destroyAllWindows()

    return results, frames


def check_criminal_match(rgb_face, criminals):
    face_encoding = face_recognition.face_encodings(rgb_face)

    if not face_encoding:
        return False  # No face found, return False

    for criminal in criminals:
        stored_encoding = criminal.Photo

        if stored_encoding is not None:
            stored_encoding = np.frombuffer(stored_encoding, dtype=np.float64)

            if stored_encoding is not None and len(stored_encoding) > 0:
                match = face_recognition.compare_faces([stored_encoding], face_encoding[0])

                if match[0]:
                    return criminal.Name

    return False

from flask import jsonify

# ... (your existing imports)

@app.route('/get_crime_data')
def get_crime_data():
    with app.app_context():
        crime_data_list = CriminalRecord.query.all()

        time_period = request.args.get('time', 'all')

        if time_period != 'all':
            # Update time period based on the provided conditions
            crime_data_list = [
                crime for crime in crime_data_list
                if (5 <= crime.Hour <= 17 and time_period == 'morning') or
                   ((18 <= crime.Hour <= 24 or 0 <= crime.Hour <= 4) and time_period == 'evening')
            ]

        # Calculate count based on the number of occurrences of each location
        location_count = Counter((crime.Latitude, crime.Longitude) for crime in crime_data_list)

        crime_data_response = [
            {
                'lat': crime.Latitude,
                'lon': crime.Longitude,
                'count': location_count[(crime.Latitude, crime.Longitude)],
                'location': crime.Location
            }
            for crime in crime_data_list
        ]

    return jsonify(crime_data_response)


if __name__ == "__main__":
   

    app.run(debug=True, port=9200)  



