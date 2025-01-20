
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fuel_efficiency.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the database model
class FuelEfficiency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    distance = db.Column(db.Float, nullable=False)
    fuel = db.Column(db.Float, nullable=False)
    efficiency = db.Column(db.Float, nullable=False)

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
        efficiency = distance / fuel
        entry = FuelEfficiency(distance=distance, fuel=fuel, efficiency=efficiency)
        db.session.add(entry)
        db.session.commit()
        return render_template('track.html', efficiency=efficiency)
    return render_template('track.html')

if __name__ == '__main__':
    app.run(debug=True)