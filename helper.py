import json
import html

def formatNoteContent(data):
    return json.dumps({
        "header": html.escape(data["header"], True),
        "body": html.escape(data["body"], True),
        "footer": html.escape(data["footer"], True),
    }, separators=(',', ':'))