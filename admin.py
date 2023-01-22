import sqlite3
from base64 import b64encode
from os import urandom
import sys
import config


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

if __name__ == "__main__":

    args = sys.argv[1:]

    if len(args)==0:
        print("Help :")
        print('WARNING: do not forget the quote "<my_arg>" around args')

        print("")
        print("user [create/delete]")
        print('\tcreate "<email>" "<name>" "<token:optional>"')
        print('\tdelete <id>')

        print("")
        print("note [delete]")
        print('\tdelete <id>')
    
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
                
            elif args[0]=="note":
                if args[1]=="delete":
                    print(deleteNote(int(args[2])))
        finally:
            db.close()
