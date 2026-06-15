import uvicorn
from fastapi import FastAPI


app = FastAPI(title = "API cargo_delivery")



if __name__ == "__main__":
    uvicorn.run(app=app, reload= True)

    # reload = True для разработки