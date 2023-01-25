import sqlite3
from base64 import b64encode
from os import urandom
import sys
import config
import json
import ftfy
from helper import formatNoteContent

def addUser(email, name, api_key=None):
    token = None
    if api_key is not None:
        token = api_key
    else:
        random_bytes = urandom(64)
        token = b64encode(random_bytes).decode('utf-8')

    cur = None
    try:
        cur = db.execute("INSERT INTO users (email, name, api_key) VALUES (?, ?, ?)",
            (email, name, token)
        )

        db.commit()

        return token
    finally:
        if cur is not None:
            cur.close()

def getRecord(sql_table, id):
    cur = None
    try:
        cur = db.execute("SELECT * FROM " + sql_table + " where id=?",
            (id, )
        )

        rows = cur.fetchall()
        if len(rows)==0:
            raise Exception(f'Invalid record with id({id}) on table {sql_table}')
        
        return rows[0]
    finally:
        if cur is not None:
            cur.close()

def deleteUser(id):
    cur = None
    try:
        getRecord("users", id)

        cur = db.execute("UPDATE users SET deleted=1 WHERE id=?",
            (id, )
        )

        db.commit()

        return "ok"
    finally:
        if cur is not None:
            cur.close()

def findUser(id, type="id"):
    cur = None
    try:
        if type=="id":
            cur = db.execute("SELECT id, name, email, api_key, deleted FROM users WHERE id=?",
                (id, )
            )
        elif type=="email":
            cur = db.execute("SELECT id, name, email, api_key, deleted FROM users WHERE email=?",
                (id, )
            )
        elif type=="api_key":
            cur = db.execute("SELECT id, name, email, api_key, deleted FROM users WHERE api_key=?",
                (id, )
            )

        rows = cur.fetchall()
        if len(rows)==0:
            raise Exception(f'Invalid record with id({id}, type={type}) on table users')

        row = rows[0]

        return json.dumps({
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "api_key": row[3],
            "deleted": False if (row[4]==0) else True,
        }, sort_keys=True, indent=4)
    
    finally:
        if cur is not None:
            cur.close()

def deleteNote(id):
    cur = None
    try:
        getRecord("notes", id)

        cur = db.execute("UPDATE notes SET deleted=1 WHERE id=?",
            (id, )
        )

        db.commit()

        return "ok"
    finally:
        if cur is not None:
            cur.close()

def getContentNote(id):
    cur = None
    try:
        cur = db.execute("SELECT id, deleted, note_content deleted FROM notes WHERE id=?",
            (id, )
        )

        rows = cur.fetchall()
        if len(rows)==0:
            raise Exception(f'Invalid record with id({id}) on table notes')

        row = rows[0]

        data = json.loads(row[2])

        return json.dumps({
            "id": row[0],
            "deleted": False if (row[1]==0) else True,
            "content": {
                "header": ftfy.ftfy(data["header"]),
                "body": ftfy.ftfy(data["body"]),
                "footer": ftfy.ftfy(data["footer"]),
            }
        }, sort_keys=False, indent=4, ensure_ascii=False)
    
    finally:
        if cur is not None:
            cur.close()

def setContentNote(id, data):
    data = json.loads(data)

    if data["id"]!=id:
        raise Exception("Note data id does not match given id")

    cur = None
    try:
        cur = db.execute("UPDATE notes SET note_content=? WHERE id=?",
            (formatNoteContent(data["content"]), id, )
        )

        db.commit()
    
    finally:
        if cur is not None:
            cur.close()

if __name__ == "__main__":

    args = sys.argv[1:]

    if len(args)==0:
        print("Help :")
        print('WARNING: do not forget the quote "<my_arg>" around args')

        print("")
        print("user [create/delete/find]")
        print('\tcreate "<email>" "<name>" "<token:optional>"')
        print('\tdelete <id>')
        print('\tfind [Do not enter user personal data here, wait for the prompt]"')

        print("")
        print("note")
        print('\tdelete <id>')
        print('\tcontent [get/set] <id>')
    
    else:
        db = sqlite3.connect(config.DATABASE_PATH)
        try:
            if args[0]=="user":
                if args[1]=="create":
                    if len(args)>=5:
                        token = args[4]
                    else:
                        token = None
                    
                    print("API key :")
                    print(addUser(args[2], args[3], api_key=token))
                
                elif args[1]=="delete":
                    print(deleteUser(int(args[2])))
                
                elif args[1]=="find":
                    type = input("<type=[id, email, api_key]>: ")
                    id = input("<id>: ")

                    print(findUser(id, type))
                
            elif args[0]=="note":
                if args[1]=="delete":
                    print(deleteNote(int(args[2])))
                if args[1]=="content":
                    if args[2]=="get":
                        print(getContentNote(int(args[3])))
                    elif args[2]=="set":
                        data = input('data minified { ..., content: {...} }: ')
                        print(setContentNote(int(args[3]), data))

            else:
                print("Command not found")
        finally:
            db.close()
