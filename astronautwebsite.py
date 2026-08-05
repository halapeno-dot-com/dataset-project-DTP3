from flask import Flask, g, render_template
import sqlite3

DATABASE = "astronautdatabase.db"

#initialise app
app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def home():
    #home page - astronaut name, ID
    sql = """
            SELECT astronauts.astronautID, astronauts.name,
            missions.missionID, missions.mission_name FROM astronauts 
            JOIN missions ON missions.missionID=astronauts.astronautID
            JOIN selections ON selections.selectionID=astronauts.astronautID;"""
    results = query_db(sql)
    return render_template("Home.html")

@app.route("/astronauts/<int:id>")
def astronaut(id):
    #one astronaut based on the ID
    sql = """
             SELECT * FROM astronauts 
             JOIN missions ON missions.missionID=astronauts.astronautID 
             JOIN selections ON selections.selectionID=astronauts.astronautID
             WHERE astronauts.astronautID = ?;"""
    result = query_db(sql,(id,),True)
    return str(result)

@app.route("/missions/<int:id>")
def mission(id):
    #one mission based on the ID
    sql = """
             SELECT * FROM missions 
             JOIN astronauts ON astronauts.astronautID=missions.missionID 
             JOIN selections ON selections.selectionID=missions.missionID
             WHERE missions.missionID = ?;"""
    result = query_db(sql,(id,),True)
    return str(result)

if __name__ == "__main__":
    app.run(debug=True)