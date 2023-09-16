import os
import requests

from dotenv import load_dotenv
from inspect import cleandoc
from typing import Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field, SecretStr, model_validator

load_dotenv()

GQL_QUERY = cleandoc(
    """
query($userName:String!, $from: DateTime!, $to: DateTime!) { 
  user(login: $userName){
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""
)

ENDPOINT = "https://api.github.com/graphql"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


class APIError(Exception):
    pass


class ContributionsRequestParams(BaseModel):
    username: str = Field(default="hewliyang")
    # for some reason the GitHub profile heatmap displays data for 1 year + 1 week ago
    from_date: Optional[datetime] = datetime.now() - relativedelta(years=1, weeks=1)
    to_date: Optional[datetime] = datetime.now()

    @model_validator(mode="before")
    def validate_dates(cls, values):
        from_date = values.get("from_date")
        to_date = values.get("to_date")

        if from_date > to_date:
            raise ValueError("from_date must be earlier than to_date!")
        return values


class Client:
    def __init__(
        self, github_api_key: SecretStr = f"Bearer {os.environ['GITHUB_API_KEY']}"
    ):
        self.github_api_key = github_api_key

    def fetch_contributions(self, params: ContributionsRequestParams) -> dict:
        resp = requests.post(
            ENDPOINT,
            json={
                "query": GQL_QUERY,
                "variables": {
                    "userName": params.username,
                    "from": params.from_date.strftime(TIME_FORMAT),
                    "to": params.to_date.strftime(TIME_FORMAT),
                },
            },
            headers={"Authorization": self.github_api_key},
        )

        if resp.status_code == 200:
            return resp.json()
        else:
            raise APIError(f"Request failed with error: {resp.status_code}") from None
