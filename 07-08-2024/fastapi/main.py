from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="templates")


app.mount("/static", StaticFiles(directory="static"), name="static")


class Names(BaseModel):
    id: int
    name: str


items: List[Names] = [
    Names(id=1, name="Arun"),
    Names(id=2, name="Kumar")
]

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/users", response_class=HTMLResponse)
def get_users(request: Request):
    return templates.TemplateResponse("user_list.html", {"request": request, "users": items})

@app.get("/users/{userid}", response_class=HTMLResponse)
def get_user(request: Request, userid: int):
    for item in items:
        if item.id == userid:
            return templates.TemplateResponse("user_details.html", {"request": request, "user": item})
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/add_user", response_class=HTMLResponse)
def show_add_user_form(request: Request):
    return templates.TemplateResponse("add_user.html", {"request": request})

@app.post("/add_user")
async def add_user(request: Request):
    form = await request.form()
    try:
        user_id = int(form.get("id"))
        user_name = form.get("name")
        
        new_user = Names(id=user_id, name=user_name)
        
        if any(item.id == new_user.id for item in items):
            raise HTTPException(status_code=400, detail="User with this ID already exists")
        
        items.append(new_user)
        return RedirectResponse(url="/users", status_code=302)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/update_user/{userid}", response_class=HTMLResponse)
def show_update_user_form(request: Request, userid: int):
    for item in items:
        if item.id == userid:
            return templates.TemplateResponse("update_user.html", {"request": request, "user": item})
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/update_user/{userid}")
async def update_user(userid: int, request: Request):
    try:
        form = await request.form()
        new_name = form.get("name")
        
        
        for index, item in enumerate(items):
            if item.id == userid:
                items[index].name = new_name
                return {"message": "User updated"}
        
        raise HTTPException(status_code=404, detail="User not found")
    
    except Exception as e:
       
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/delete_user/{userid}")
async def delete_user(userid: int):
    global items
    items = [item for item in items if item.id != userid]
    return RedirectResponse(url="/users", status_code=302)
