from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from github import Client, ContributionsRequestParams

client = Client()
app = FastAPI()


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.post("/contributions")
async def fetch_contributions(params: ContributionsRequestParams):
    return client.fetch_contributions(params)
