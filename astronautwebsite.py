from unittest import result

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
    return render_template("Home.html", astronauts=results)

@app.route('/', methods=['GET'])
def search():
    query = request.args.get('q', '')
    results = []

    if query:
        conn = get_db_connection()
        sql_query = "SELECT * FROM astronauts WHERE name LIKE ?"
        search_term = f'%{query}%'

        results = conn.execute(sql_query, (search_term)).fetchall()
        conn.close

    return render_template('Home.html', results=results, query=query)

@app.route("/astronauts/<int:id>")
def astronaut(id):
    #one astronaut based on the ID
    sql = """
             SELECT * FROM astronauts 
             JOIN missions ON missions.missionID=astronauts.astronautID 
             JOIN selections ON selections.selectionID=astronauts.astronautID
             WHERE astronauts.astronautID = ?;"""
    result = query_db(sql,(id,),True)
    return render_template("Astronauts.html", astronaut=result)

@app.route("/credits")
def credits():
    return render_template("Credits.html")

if __name__ == "__main__":
    app.run(debug=True)