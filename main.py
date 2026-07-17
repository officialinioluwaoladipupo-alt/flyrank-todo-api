from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

app = FastAPI()

# Your in-memory "database"
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read a book", "done": False},
    {"id": 3, "title": "Go for a walk", "done": True},
]

@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

@app.post("/tasks", status_code=201)
async def create_task(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})
    
    if not isinstance(body, dict) or "title" not in body:
        return JSONResponse(status_code=400, content={"error": "Title is missing"})
        
    title = body.get("title")
    if not isinstance(title, str) or not title.strip():
        return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})
        
    new_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {
        "id": new_id,
        "title": title.strip(),
        "done": False
    }
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{id}")
async def update_task(id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body"})
    
    if not isinstance(body, dict) or ("title" not in body and "done" not in body):
        return JSONResponse(status_code=400, content={"error": "Nothing to update"})
    
    if "title" in body:
        title = body["title"]
        if not isinstance(title, str) or not title.strip():
            return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})
            
    if "done" in body:
        done = body["done"]
        if not isinstance(done, bool):
            return JSONResponse(status_code=400, content={"error": "Done must be a boolean"})
            
    for task in tasks:
        if task["id"] == id:
            if "title" in body:
                task["title"] = body["title"].strip()
            if "done" in body:
                task["done"] = body["done"]
            return task
            
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

@app.delete("/tasks/{id}")
def delete_task(id: int):
    for i, task in enumerate(tasks):
        if task["id"] == id:
            tasks.pop(i)
            return Response(status_code=204)
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})