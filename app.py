from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import matplotlib.pyplot as plt
import io
import base64

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
    # Default page value
    page = int(request.args.get('page', 1))  # Default to page 1
    per_page = 5  # Number of records per page
    offset = (page - 1) * per_page

    if request.method == 'POST':
        # Process form submission
        distance = float(request.form['distance'])
        fuel = float(request.form['fuel'])
        efficiency = distance / fuel

        # Add a new record to the database
        new_record = FuelEfficiency(
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            distance_miles=distance,
            fuel_gallons=fuel,
        )
        db.session.add(new_record)
        db.session.commit()

    # Fetch the records for the current page
    records = (
        FuelEfficiency.query.order_by(FuelEfficiency.id.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )

    # Check if there's a next page
    total_records = FuelEfficiency.query.count()
    has_next = offset + per_page < total_records
    has_prev = page > 1

    return render_template(
        'track.html',
        records=records,
        efficiency=None,
        page=page,
        has_next=has_next,
        has_prev=has_prev,
    )




@app.route('/visualise')
def visualise():
    records = FuelEfficiency.query.order_by(FuelEfficiency.id.desc()).limit(10).all()  # Get last 10 records

    if not records:
        return render_template('visualise.html', chart_data=None)

    dates = [record.date for record in records]
    efficiencies = [record.distance_miles / record.fuel_gallons for record in records]

    # Create the plot
    plt.figure(figsize=(10, 5))
    plt.plot(dates, efficiencies, marker='o', linestyle='-', color='b')
    plt.xlabel('Date')
    plt.ylabel('Efficiency (MPG)')
    plt.title('Fuel Efficiency Over Time')
    plt.xticks(rotation=45)
    plt.grid()

    # Save plot to a string
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')  # <-- Add bbox_inches='tight'
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template('visualise.html', chart_data=plot_url)



if __name__ == '__main__':
    with app.app_context():  # Use Flask app context
        db.create_all()  # Create database tables
        print("Database tables created successfully!")
    print("Current directory:", os.getcwd())
    app.run(debug=True)