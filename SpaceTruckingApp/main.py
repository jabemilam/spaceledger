from fastapi import FastAPI, Depends
import models
from database import engine
from routers import auth, runs, users
from starlette.staticfiles import StaticFiles
from starlette import status
from starlette.responses import RedirectResponse

app = FastAPI()  # Where it all starts

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/runs", status_code=status.HTTP_302_FOUND)

# Router files
app.include_router(auth.router)
app.include_router(runs.router)
app.include_router(users.router)
