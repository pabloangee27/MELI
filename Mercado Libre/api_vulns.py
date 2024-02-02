from fastapi import FastAPI, Request, Form, Depends, Header, HTTPException
from typing import Optional, Annotated
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, BaseLoader, Template, FileSystemLoader
import jinja2
import sqlite3
from starlette.responses import RedirectResponse, PlainTextResponse, HTMLResponse
from starlette import status
from pydantic import BaseModel


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class Vuln(BaseModel):
    idd: int
    name: str
    description: str
    category: str
    severity: str | None = None
    remediation: str
    image_url: str | None = None

def database_queries(q, data):
    connection = sqlite3.connect("vulns.db")
    cursor = connection.cursor()
    try:
        res = cursor.execute(q, data)
        connection.commit()
        l = res.fetchall()
        return l
    except Exception as e:
        print("Ingrese una consulta SQL correcta")

async def check_token(key: str):
    if key != "secret_token":
        raise HTTPException(status_code=400, detail="key header is invalid")
    return key


@app.get("/list", dependencies=[Depends(check_token)])
async def main():
    l = database_queries("SELECT * FROM vulners;", ())
    json_data = []
    r = {}
    for row in l:
        rem = row[5].split('\n')
        for j in rem:
            r["R" + str(rem.index(j)+1)] = j
        proc = {"id": row[0], "name": row[1], "description": row[2], "category": row[3], "severity": row[4], "remediation":r, "image_url":row[6]}
        json_data.append(proc)
        r = {}
    return json_data

@app.get("/vulnid/{id}", dependencies=[Depends(check_token)])
async def req_vuln(id: str):
    
    l = database_queries(f"SELECT * FROM vulners WHERE id = {id}", ())
    if not l:
        return PlainTextResponse("No data found!", status_code = 404)
    else:
        json_data = []
        r = {}
        for row in l:
            rem = row[5].split('\n')
            for j in rem:
                r["R" + str(rem.index(j)+1)] = j
            proc = {"id": row[0], "name": row[1], "description": row[2], "category": row[3], "severity": row[4], "remediation":r, "image_url":row[6]}
            json_data.append(proc)
            r = {}
        return json_data

@app.post("/create", dependencies=[Depends(check_token)])
async def create_vuln(it: Vuln):
    l = database_queries("INSERT INTO vulners (id, name, description, category, severity, remediation, path) VALUES (?,?,?,?,?,?,?)", (it.idd, it.name, it.description, it.category, it.severity, it.remediation, it.image_url))
    return {"message":"New vulnerability uploaded", "id": it.idd}
        
    

