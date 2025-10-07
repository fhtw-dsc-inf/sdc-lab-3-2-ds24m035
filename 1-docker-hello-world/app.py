import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root(name: str = 'name'):
    return {"hello data scientists!!: "+ name}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
