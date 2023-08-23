# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurements = Base.classes.measurement
stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
def last_year():
    session = Session(engine)
    recent = session.query(measurements.date).order_by(measurements.date.desc()).first()
    last_12 = (dt.datetime.strptime(recent[0],'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    session.close()

    return(last_12)


@app.route("/")
def welcome():
    """Available routes."""
    return(
         f"<b>Welcome to the homepage!</b><br/>"
        f"Available routes:<br/>"
        f"Precipitation measurement over the last 12 months: /api/v1.0/precipitation<br/>"
        f"The following list contains all active stations: /api/v1.0/stations<br/>"
        f"Temperature of the most active stations in the past 12 months: /api/v1.0/tobs<br/>"
        f"Enter a start date to retreive the minimum, maximum, and average temperatures after specified dates: /api/v1.0/<start><br/>"
        f"Enter both a start and end date to retreive the minimum, maximum and average temperatures between dates: /api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")   
def precipitation():
    session =Session(engine)

    query = session.query(measurements.date, measurements.prcp).\
    filter(measurements.date>=last_year).all()

    session.close()

    p_list = []
    for date, prcp in query:
        dict1 ={}
        dict1["date"]=date
        dict1["prcp"]=prcp
        p_list.append(dict1)


    return jsonify(p_list)


@app.route("/api/v1.0/stations")
def stations():

    session =Session(engine)

    allstations=session.query(stations.station, stations.name).all()

    session.close()

    stations_list=list(np.ravel(allstations))

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    tobs_data = session.query(measurements.date, measurements.tobs).\
            filter(measurements.date >= last_year()).\
            filter(measurements.station == "USC00519281").\
            order_by(measurements.date).all()
    
    tobs_dict = dict(tobs_data)

    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end=None):

    if end == None:

        s_temp= session.query(func.min(measurements.tobs), func.max(measurements.tobs), func.round(func.avg(measurements.tobs), 2)).\
                            filter(measurements.date >= start).all()
        
        s_list = list(np.ravel(s_temp))
        s_list2 = {"Temp min:": s_list[0],"Temp max:": s_list[1], "Temp avg:": s_list[2]}

        return jsonify(s_list2)
    else:
        start_end_temp = session.query(func.min(measurements.tobs), func.max(measurements.tobs), func.round(func.avg(measurements.tobs), 2)).\
                            filter(measurements.date >= start).\
                            filter(measurements.date <= end).all()
     
        s_end_list = list(np.ravel(start_end_temp))
        s_end_list2 = {"Temp min:": s_end_list[0],"Temp max:": s_end_list[1], "Temp avg:": s_end_list[2]}

        return jsonify(s_end_list2)
                
session.close()


if __name__ == '__main__':
    app.run(debug=True)