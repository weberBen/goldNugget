from flask import Flask, send_from_directory, request, g, make_response
import os
import sqlite3
import html
from datetime import datetime, timedelta
import json
from werkzeug.exceptions import HTTPException
from werkzeug.datastructures import ImmutableMultiDict
import math
import time
import traceback
import config
from helper import formatNoteContent


app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(config.DATABASE_PATH)
    return db


class UserException(Exception):
    pass



@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def getExceptionMsg(e):
    if config.DEBUG:
        output = {
            "type": type(e).__name__,
            "msg": str(e),
        }

        if config.DISPLAY_TRACE:
            output["trace"] = traceback.format_exc()

        return output
    else:
        if isinstance(e, UserException):
            return str(e)
        
        return ""

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e

    if config.DEBUG and config.RAISE_EXCEPTION:
        raise e
        
    
    return {
        "error": True,
        "error_msg": json.dumps(getExceptionMsg(e))
    }

def get_post_data(request):
    data = None

    if request.headers['Content-Type'].startswith('application/json'):
        data = request.json
    
    elif request.headers['Content-Type'].startswith('application/x-www-form-urlencoded'):
        data = request.form
        if (data is not None) and ("data" in data):
            data = json.loads(data["data"])
        else:
            data = {}
    
    return data

def getCookieExpirationDate():
    expire_date = datetime.now()
    expire_date = expire_date + timedelta(days=15)

@app.route("/")
def index():
    return send_from_directory("views/", "index.html")

@app.route("/info")
def info():
    return send_from_directory("views/", "info.html")

@app.route("/nugget/create")
def note_create():
    return send_from_directory("views/", "create.html")

@app.route('/resource/<path:filename>')  
def send_file(filename):
    return send_from_directory("views/", filename)

def parseIntArgs(val, defaultValue=None):
    if isinstance(val, int):
        return val
    
    if (val is None) or (isinstance(val, str) and len(val)==0):
        return defaultValue
    
    return int(val)

@app.route('/api/note', methods=["GET"]) 
def api_note_index():

    page_size = parseIntArgs(request.args.get("pageSize"), None)
    if page_size is None:
        if "pageSize" in request.cookies:
            try:
                page_size = int(request.cookies.get("pageSize"))
            except:
                page_size = config.DEFAULT_PAGE_SIZE
        else:
            page_size = config.DEFAULT_PAGE_SIZE
    
    pagination_start = parseIntArgs(request.args.get("paginationStart"), -1) 
    page_number = parseIntArgs(request.args.get("pageNumber"), 1) - 1

    if page_number==0:
        pagination_start = -1

    cur = None
    db = get_db()
    try:

        if pagination_start<0:
            cur = db.execute(f'SELECT count(*), MAX(id) FROM notes WHERE deleted=0')
            row = cur.fetchall()[0]

            total_item_count = row[0]
            pagination_start = row[1]

            if total_item_count==0: # no data
                pagination_start = 1
            
        else:
            cur = db.execute(f'SELECT count(*) FROM notes WHERE id <= ? AND deleted=0', (pagination_start, ))
            total_item_count = cur.fetchall()[0][0]
        
        data = []

        # Reasonably efficient pagination without OFFSET
        query = """SELECT id, DATE(note_date), note_content, note_like_reactions,
            note_dislike_reactions, note_fake_reactions
            FROM notes
            WHERE id <= ? and deleted=0
            ORDER BY id DESC
            LIMIT ?
        """
        cur = db.execute(query, (pagination_start - page_number*page_size, page_size))
        

        for row in cur:

            data.append({
                "id": row[0],
                "date": datetime.strptime(row[1], "%Y-%m-%d").strftime("%d/%m/%Y"),
                "content": json.loads(row[2]),
                "reactions": {
                    "like": row[3],
                    "dislike": row[4],
                    "fake": row[5],
                }
            })
    finally:
        if cur is not None:
            cur.close()
    
    response_data = {
        "data": {
            "notes": data,
            "total_item_count": total_item_count,
            "page_number": page_number + 1,
            "page_count":  math.ceil((1.*total_item_count)/page_size),
            "page_size": page_size,
            "pagination_start": pagination_start,
        }
    }

    response = make_response(response_data)
    response.set_cookie("pageSize", str(page_size), expires=getCookieExpirationDate())

    return response

@app.route('/nugget/<int:note_id>', methods=["GET"]) 
def note_show(note_id):
    return send_from_directory("views/", "show.html")

@app.route('/api/note/<int:note_id>', methods=["GET"]) 
def api_note_show(note_id):
    record = None
    cur = None
    db = get_db()
    try:

        query = """SELECT id, DATE(note_date), note_content, note_like_reactions,
            note_dislike_reactions, note_fake_reactions
            FROM notes
            WHERE id = ?
        """
        cur = db.execute(query, (note_id, ))
        rows = cur.fetchall()

        if len(rows)>0:
            row = rows[0]
            record = {
                "id": row[0],
                "date": datetime.strptime(row[1], "%Y-%m-%d").strftime("%d/%m/%Y"),
                "content": json.loads(row[2]),
                "reactions": {
                    "like": row[3],
                    "dislike": row[4],
                    "fake": row[5],
                }
            }
    finally:
        if cur is not None:
            cur.close()
    
    if record is None:
        raise UserException(f'Invalid nugget id({note_id})')
    
    return {
        "data": {
            "note": record,
        }
    }
    

@app.route('/api/note/create', methods=["POST"]) 
def api_note_create():
    data = get_post_data(request)

    db = get_db()
    cur = None 
    id_user = None
    try:
        api_key = data["api_key"]

        cur = db.execute(f'SELECT id FROM users WHERE api_key=? AND deleted=0', (api_key, ))
        rows = cur.fetchall()
        time.sleep(1)
        if len(rows)==0:
            raise UserException("Invalid API key")
        
        id_user = rows[0][0]
        
    finally:
        if cur is not None:
            cur.close()

    note_date = datetime.strptime(data["date"], "%d/%m/%Y")
    if note_date > datetime.now():
        raise UserException("Date cannot be set to the future")
    
    record = {
        "note_date": note_date,
        "note_content": formatNoteContent(data["content"]),
    }

    cur = None
    id_note = None
    try:
        cur = db.execute("INSERT INTO notes (note_date, note_content) VALUES (?, ?)",
            (record["note_date"], record["note_content"])
        )
        id_note = cur.lastrowid

        cur = db.execute("INSERT INTO notes_users (id_note, id_user) VALUES (?, ?)",
            (id_note, id_user)
        )

        db.commit()
    finally:
        if cur is not None:
            cur.close()

    return {
        "status": "ok",
        "data": {
            "id_note": id_note,
        },
    }, 201


@app.route('/api/note/<int:note_id>/reaction/<string:reaction_type>', methods=["POST"]) 
def api_note_reaction(note_id, reaction_type):
    
    reaction_cookie_name = f'reactions-{note_id}'
    if reaction_cookie_name in request.cookies:
        raise UserException("You already react to that nugget")


    if (reaction_type not in ["like", "dislike", "fake"]):
        raise UserException("Invalid reaction type")

    data = get_post_data(request)
    
    operations = {
        "add": "+",
        "remove": "-",
    }

    operation = data["operation"] if ("operation" in data) else "add"
    if operation not in operations:
        raise UserException("Invalid reaction operation")
    operation = operations[operation]

    cur = None
    try:
        db = get_db()

        query = f'UPDATE notes SET note_{reaction_type}_reactions =  note_{reaction_type}_reactions {operation} 1 WHERE id=? AND deleted=0'
        cur = db.execute(query, (note_id, ))

        db.commit()
    finally:
        if cur is not None:
            cur.close()

    resp = make_response("ok")
    resp.set_cookie(reaction_cookie_name, "", expires=getCookieExpirationDate())

    return resp


if __name__=="__main__":
    app.run(debug=config.DEBUG)