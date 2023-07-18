from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from pisync.lib.api.info_response import InfoResponse
import settings

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("client-index.html", {"request": request})


@app.get('/info')
def get_server_info():
    return InfoResponse(is_client=True)


def setup():
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    setup()
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
