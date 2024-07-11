# Import the dependencies.
#!pip install sqlalchemy
from flask import Flask, jsonify
#import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# Start at homepage, lista all the available routes
@app.route("/")
def home():
    return(
        "<h1>Welcome to the Climate API!</h1>"
        "<h2>Available Routes:</h2>"
        "<ul>"
        "<li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a></li>"
        "<li><a href='/api/v1.0/stations'>/api/v1.0/stations</a></li>"
        "<li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></li>"
        "<li><a href='/api/v1.0/<start>'>/api/v1.0/&lt;start&gt;</a></li>"
        "<li><a href='/api/v1.0/<start>/<end>'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a></li>"
        "</ul>"
          )


# Define what to do when a user hits the /precitpitation route
@app.route("/api/v1.0/precipitation")
def precipitation():


    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Query the last 12 months of precipitation data
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

     # Close the session
    session.close()
    
    # Convert the query results to a dictionary
    precip_dict = {date: prcp for date, prcp in precip_data}
    
    return jsonify(precip_dict)

#station data
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
     # Query all stations
    results = session.query(Station.station).all()

     # Close the session
    session.close()

    # Convert the query results to a list
    stations_list = [result.station for result in results]

    return jsonify(stations_list)

#temperature observations of the most active station
#@app.route("/api/v1.0/tobs")
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Find the most active station ID
    most_active_station = session.query(Measurement.station, func.count(Measurement.station).label('count')).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()

    most_active_station_id = most_active_station.station

    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Query the temperature observations for the most active station for the last 12 months
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station_id).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Close the session
    session.close()


    # Convert the query results to a list of dictionaries
    tobs_list = [{date: tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)

# temperature statistics for a specified start date
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # If no end date is provided, set the end date to the most recent date in the dataset
    if not end:
        end = session.query(func.max(Measurement.date)).scalar()

    # Query for temperature statistics (TMIN, TAVG, TMAX) for the specified date range
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()


     # Close the session
    session.close()


    # Convert the query results to a dictionary
    temp_stats_dict = {
        "Start Date": start,
        "End Date": end,
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
  

    return jsonify(temp_stats_dict)


if __name__ == "__main__":
    app.run(debug=True)
