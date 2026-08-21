from unittest import result

from flask import Flask, g, render_template, request
import sqlite3

DATABASE = "astronautdatabase.db"

#initialise app
app = Flask(__name__)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def get_astronauts():
#home page - astronaut name, ID
    sql = """
            SELECT astronauts.astronautID, astronauts.name,
            missions.missionID, missions.mission_name FROM astronauts 
            JOIN missions ON missions.missionID=astronauts.astronautID
            JOIN selections ON selections.selectionID=astronauts.astronautID;"""
    results = query_db(sql)
    return results

@app.route('/')
def home():
    results = get_astronauts()
 
    return render_template("Home.html", astronauts=results, search_result=None, query="")
    
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

@app.route("/search")
def search():
   results = get_astronauts()
   query = request.args.get('q', '')
   search_result = None
   if query:
        query = query.lower().strip()
        for astronaut in results:
            astronaut_name = astronaut[1].lower()
            if query in astronaut_name:
                search_result = astronaut
                break
            return render_template("Home.html", astronauts=results, search_result=search_result, query=query)        


@app.route("/credits")
def credits():
    return render_template("Credits.html")

if __name__ == "__main__":
    app.run(debug=True)