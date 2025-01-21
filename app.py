
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fuel_efficiency.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the database model
class FuelEfficiency(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary Key
    date = db.Column(db.String(50), nullable=False)  # Date of the record
    distance_miles = db.Column(db.Float, nullable=False)  # Distance in miles
    fuel_gallons = db.Column(db.Float, nullable=False)  # Fuel in gallons

    def __repr__(self):
        return f"<FuelRecord {self.date} - {self.distance_miles} miles, {self.fuel_gallons} gallons>"

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Fuel efficiency tracker
@app.route('/track', methods=['GET', 'POST'])
def track():
    if request.method == 'POST':
        distance = float(request.form['distance'])
        fuel = float(request.form['fuel'])
        efficiency = distance / fuel  # Calculate efficiency (miles per gallon)

        # Add the entry to the database
        entry = FuelEfficiency(
            date=datetime.now().strftime("%Y-%m-%d"),
            distance_miles=distance,
            fuel_gallons=fuel
        )
        db.session.add(entry)
        db.session.commit()

        return render_template('track.html', efficiency=efficiency)

    return render_template('track.html', efficiency=None)

@app.route('/records')
def records():
    # Fetch all records from the database
    all_records = FuelEfficiency.query.all()
    return render_template('records.html', records=all_records)

if __name__ == '__main__':
    with app.app_context():  # Use Flask app context
        db.create_all()  # Create database tables
        print("Database tables created successfully!")
    print("Current directory:", os.getcwd())
    app.run(debug=True)