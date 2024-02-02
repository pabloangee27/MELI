from fastapi import FastAPI, Request, Form, Depends, Header, HTTPException
from typing import Optional
from pydantic import BaseModel, ValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, BaseLoader, Template, FileSystemLoader
import jinja2
from newsapi import NewsApiClient
from typing import Annotated
from starlette.responses import RedirectResponse, PlainTextResponse, HTMLResponse
from starlette import status
import sqlite3

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def get_news(query,source):
    
    news_api = NewsApiClient(api_key = "2780211c5feb44abb10cb744c940074c")
    encabezados = news_api.get_top_headlines(q = query ,sources = source)

    articulos = encabezados['articles']
    
    desc = []
    news = []
    img = []

    for i in range(len(articulos)):
        m = articulos[i]
        news.append(m['title'])
        desc.append(m['description'])
        img.append(m['urlToImage'])

    l = zip(news, desc, img)

    return l

@app.get("/")
async def login_page(request: Request, name: str = None, password: str = None):
    
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, name: str = Form(...), password: str = Form(...)):
    
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    check_input = "SELECT name, password FROM users where name = '"+ name +"' and password = '"+password+"'"

    cursor.execute(check_input)

    data = cursor.fetchall()

    if not data:
         html_temp = f"<h1>Wrong credentials. Please login</h1>"
         env = jinja2.Environment(loader=BaseLoader)

         template = env.from_string(html_temp)
         return HTMLResponse('<html><body><h1>Wrong Credentials, try again</h1></body></html>', status_code = status.HTTP_403_FORBIDDEN)
         #return template.render()
    else:
        return RedirectResponse(url='/bbc', status_code=status.HTTP_302_FOUND)
        
         
        

@app.get("/bbc", response_class=HTMLResponse)
async def home(request: Request):

    l = get_news(None,"bbc-news")
    
    return templates.TemplateResponse(name="bbc.html", request = request, context = {"data": l})

@app.get("/cnn", response_class=HTMLResponse)
async def home(request: Request):

    l = get_news(None, "cnn")
    
    return templates.TemplateResponse(name="cnn.html", request = request, context = {"data": l})

@app.get("/abc-news", response_class=HTMLResponse)
async def home(request: Request):

    l = get_news(None, "abc-news")
    
    return templates.TemplateResponse(name="abc.html", request = request, context = {"data": l})


@app.post("/process_search_bbc", response_class=HTMLResponse)
async def process_search(request: Request, keyword: str = Form(...)):

    l = get_news(keyword, "bbc-news")

    return templates.TemplateResponse(name="bbc.html", context = {"request":request,"data": l})

@app.post("/process_search_cnn", response_class=HTMLResponse)
async def process_search(request: Request, keyword: str = Form(...)):

    l = get_news(keyword, "cnn")

    return templates.TemplateResponse(name="cnn.html", request = request, context = {"data": l})

@app.post("/process_search_abc", response_class=HTMLResponse)
async def process_search(request: Request, keyword: str = Form(...)):

    l = get_news(keyword, "abc-news")

    return templates.TemplateResponse(name="abc.html", request = request, context = {"data": l})

@app.post("/comments", response_class=HTMLResponse)
async def process_search(request: Request, name: str = Form(...), comment: str = Form(...)):
    
    html_template = f"<h1>Hello {name}! Thanks for your contribution</h1>"
    env = jinja2.Environment(loader=BaseLoader)

    template = env.from_string(html_template)
    return template.render()




