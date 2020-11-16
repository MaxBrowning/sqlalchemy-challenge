# Import dependencies
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

import datetime as dt

#################################################
# Database setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

inspector = inspect(engine)
print(inspector.get_table_names())

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask setup
#################################################
app = Flask(__name__)


#################################################
# Flask routes
#################################################

# Home page that lists all routes available.
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App!<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"----------------------------<br/>"
        f"<br/>"
        f"Additionally, you can choose a date range<br/>"
        f"or simply a starting date to see information<br/>"
        f"maximum, minimum, and average temperatures.<br/>"
        f"<br/>"
        f"Simply use routes:<br/>"
        f"/api/v1.0/start_date to query all dates after a date<br/>"
        f"/api/v1.0/start_date/end_date to query all dates in a range<br/>"
        f"<br/>"
        f"Dates should be formatted as YYYY-MM-DD."
    )

# Convert query results into a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    prcp_query = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    all_prcp = []
    for Measurement.date, Measurement.prcp in prcp_query:
        prcp_dict = {}
        prcp_dict['date'] = Measurement.date
        prcp_dict['prcp'] = Measurement.prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations_query = session.query(Station.elevation, Station.latitude, Station.name, Station.id, Station.longitude, Station.station).all()

    session.close()

    all_stations = []
    for elevation, latitude, name, id, longitude, station in stations_query:
        stations_dict = {}
        stations_dict['elevation'] = elevation
        stations_dict['latitude'] = latitude
        stations_dict['name'] = name
        stations_dict['id'] = id
        stations_dict['longitude'] = longitude
        stations_dict['station'] = station
        all_stations.append(stations_dict)
    
    return jsonify(all_stations)

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Calculate the most active station.
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    tobs_query = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.station == most_active_station)

    session.close()

    all_tobs = []
    for date, station, tobs in tobs_query:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['station'] = station
        tobs_dict['tobs'] = tobs
        all_tobs.append(tobs_dict)
    
    return jsonify(all_tobs)

# Return a JSON list of the minimum, average, and maximum temperature for all dates greater
# than or equal to the start date.
@app.route(f"/api/v1.0/<start>")
def tobs_by_start_date(start):
    session = Session(engine)

    lowest_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= f'{start}').all()[0][0]
    highest_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= f'{start}').all()[0][0]
    average_temp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= f'{start}').all()[0][0]

    session.close()

    return(
        f'The minimum temperature after {start} was {lowest_temp}.<br/>'
        f'The maximum temperature after {start} was {highest_temp}.<br/>'
        f'The average temperature after {start} was {average_temp}.'
    )

# Return a JSON list of the minimum, average, and maximum temperature for all dates within
# the provided start and end dates.
@app.route("/api/v1.0/<start>/<end>")
def tobs_by_start_end_date(start, end):
    session = Session(engine)

    lowest_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= f'{start}').\
        filter(Measurement.date <= f'{end}').all()[0][0]
    highest_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= f'{start}').\
        filter(Measurement.date <= f'{end}').all()[0][0]
    average_temp = session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= f'{start}').\
        filter(Measurement.date <= f'{end}').all()[0][0]

    session.close()

    return(
        f'The minimum temperature between {start} and {end} was {lowest_temp}.<br/>'
        f'The maximum temperature between {start} and {end} was {highest_temp}.<br/>'
        f'The average temperature between {start} and {end} was {average_temp}.'
    )

if __name__ == "__main__":
    app.run(debug=True)
