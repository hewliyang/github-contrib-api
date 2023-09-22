from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from github import Client, Contributions, ContributionsRequestParams

client = Client()
app = FastAPI()


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.post("/contributions")
async def fetch_contributions(params: ContributionsRequestParams) -> Contributions:
    return client.fetch_contributions(params)
