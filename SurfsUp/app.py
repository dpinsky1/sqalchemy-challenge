# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import numpy as np
import datetime as dt
from datetime import timedelta
#################################################
# Database Setup
#################################################
Base = automap_base()
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurements = Base.classes.measurement
stations_table = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Landing Page
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Returns precipitation totals for the last year, sorted by\
            date in JSON format.<br/>"
        f"/api/v1.0/stations - Returns a JSON list of stations, their names, and exact \
            locations, as well as elevation.<br/>"
        f"/api/v1.0/tobs - Returns a JSON list of temperature observations for the previous\
              year from the most active station.<br/>"
        f"/api/v1.0/start - Returns a JSON list of the minimum temperature, the average \
            temperature, and the maximum temperature for a specified start date. \
                Dates should be entered as yyyy-mm-dd.<br/> "
        f"/api/v1.0/start/end - Returns a JSON list of the minimum temperature, the average \
            temperature, and the maximum temperature for a specified start-end date range.\
                Dates should be entered as yyyy-mm-dd.<br/>"
    )

# Precipitation
@app.route("/api/v1.0/precipitation")
def precip():
    """Returns precipitation totals for the last year, sorted by date."""
    
    # Get date for last year of data. 
    year = timedelta(days=365)
    latest_date = session.query(func.max(measurements.date)).filter().all()
    latest_date = dt.datetime.strptime(latest_date[0][0], '%Y-%m-%d')
    one_year = latest_date - year
    one_year

    # Get precipitation totals.
    prcp_data = session.query(measurements).with_entities(measurements.date, measurements.prcp)\
    .filter(measurements.date >= one_year).all()
    session.close()

    # Return data.
    dates = list(np.ravel(prcp_data)) 
    return jsonify(dates)

# Stations
@app.route("/api/v1.0/stations")
def stations():
    """Gets list of stations and their locations."""

    # Get station list.
    station_list = session.query(stations_table.station).all()
    session.close()

    # Return data.
    all_stations = list(np.ravel(station_list)) 
    return jsonify(all_stations)

# Temperature Observations
@app.route("/api/v1.0/tobs")
def tobs():
    ''' Gets low, high, and avg temps for most active station over the last year.'''

    # Get date for last year of data. 
    year = timedelta(days=365)
    latest_date = session.query(func.max(measurements.date)).filter().all()
    latest_date = dt.datetime.strptime(latest_date[0][0], '%Y-%m-%d')
    one_year = latest_date - year
    one_year

    # Get most active station. 
    station_values = session.query(measurements.station, func.count(measurements.station))\
    .order_by(func.count(measurements.station).desc()).group_by(measurements.station).all()
    most_active = station_values[0][0]

    # Get data for most active station. 
    active_data = session.query(measurements.date, measurements.prcp, measurements.tobs).filter\
        (measurements.station == most_active, measurements.date >= one_year)\
            .order_by(measurements.date).group_by(measurements.date).all()
    session.close()

    # Return data. 
    tobs_resp = list(np.ravel(active_data))
    return jsonify(tobs_resp)

# Temperature overview with start date
@app.route("/api/v1.0/<start>")
def start_only(start):
    ''' Gets low, high, and avg temps for all stations with a user-provided start date.'''

    # Get date for query of data.
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    # Get data for most active station. 
    start_data = session.query(measurements.date,func.min(measurements.tobs),\
                               func.max(measurements.tobs),func.avg(measurements.tobs) )\
                                .filter(measurements.date >= start_date)\
                                    .order_by(measurements.date).group_by(measurements.date)\
                                        .all()
    session.close()

    # Return data. 
    start_resp = list(np.ravel(start_data))
    return jsonify(start_resp)

# Temperature overview with start and end date
@app.route("/api/v1.0/start/<start>/end/<end>")
def start_end(start, end):
    ''' Gets low, high, and avg temps for all stations with a user-provided start and end date.'''
    # Get dates for query of data.
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    # Get data for most active station.
    start_end_data = session.query(measurements.date,func.min(measurements.tobs),func.max\
                                   (measurements.tobs), func.avg(measurements.tobs)).filter(measurements.date >= start_date,\
                                    measurements.date <= end_date).order_by(measurements.date)\
                                        .group_by(measurements.date).all()
    session.close()

    # Return data. 
    start_end_resp = list(np.ravel(start_end_data))
    return jsonify(start_end_resp)

if __name__ == "__main__":
    app.run(debug=True)