from fastapi import FastAPI 
 

app = FastAPI()

@app.get("/")
def health_endpoint():
    return{"message":"the server is running"}