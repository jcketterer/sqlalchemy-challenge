import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- Dates and Temps from last year<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- Temp observations from last year<br/>"
        f"<br/>"
        f"/api/v1.0/<start> <br/>"
        f"Input start date in 'YYYY-MM-DD' format<br/>"
        f"<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Input dates in 'YYYY-MM-DD/YYYY-MM-DD' format<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of percipitation from last year"""
    last_day = session.query(measurement.date).order_by(measurement.date.desc()).first()

    year_2016 = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date > year_2016).\
        order_by(measurement.date).all()

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def station_list():

    active_stations = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    return jsonify(active_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    active_stations = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    most_active_station = active_stations[0][0]

    most_active_station = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.station == most_active_station).all()

    return jsonify(most_active_station)

@app.route("/api/v1.0/<start>")
def start(start):

    first_date = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).group_by(measurement.date).all()
    
    from_first_date = list(first_date)

    return jsonify(from_first_date)


@app.route("/api/v1.0/<start>/<end>")
def range_temp(start, end):

    range_date = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()

    range_date_list = list(range_date)

    return jsonify(range_date_list)


if __name__ == '__main__':
    app.run(debug=True)