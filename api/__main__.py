from fastapi import FastAPI
from fastapi.responses import FileResponse
import datetime as dt
import os
from datetime import datetime

app = FastAPI()

docpath = 'images/'
doctypes = ['png', 'jpg', 'tif']

@app.get('/doclist')
def doclist() :
    doclist = []
    with os.scandir(docpath) as docs :
        for i, doc in enumerate(docs) :
            if doc.name.split('.')[-1] in doctypes :
                mtime = datetime.fromtimestamp(doc.stat().st_mtime)
                listitem = {'fname' : doc.name, 'mtime' : mtime.strftime('%Y-%m-%d %H:%M')}
                doclist.append(listitem)
    return doclist

@app.get('/doccontent')
def doccontent(fname : str) :
    f = docpath + fname
    return FileResponse(f)

@app.put('/status')
def put_status(source : str, message : str) :
    now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    out = f'"{now}"' + f',"{source}"' + f',"{message}"\n'
    fname = 'logs/remote_log.csv'
    with open(fname, 'a') as f :
        f.write(out)
    return True
