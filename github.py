import os
import requests

from dotenv import load_dotenv
from inspect import cleandoc
from typing import List, Optional
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


# input schema
class ContributionsRequestParams(BaseModel):
    username: str = Field(default="hewliyang")
    from_date: Optional[datetime] = Field(
        default=datetime.now() - relativedelta(years=1, weeks=1)
    )
    to_date: Optional[datetime] = Field(default=datetime.now())

    @model_validator(mode="before")
    def validate_dates(cls, values):
        from_date = values.get("from_date")
        to_date = values.get("to_date")

        if not from_date or not to_date:
            return values
        if from_date > to_date:
            raise ValueError("from_date must be earlier than to_date!")
        return values


# output schemas


class DailyRecord(BaseModel):
    contributionCount: int = Field(...)
    date: str = Field(...)


class Contributions(BaseModel):
    total: int = Field(...)
    contributions: List[DailyRecord] = Field(...)


def _flatten(resp: dict) -> dict:
    blob = resp["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    total_contribs = blob["totalContributions"]
    weeks = blob["weeks"]

    return {
        "total": total_contribs,
        "contributions": [
            record for week in weeks for record in week["contributionDays"]
        ],
    }


class Client:
    def __init__(
        self, github_api_key: SecretStr = f"Bearer {os.environ['GITHUB_API_KEY']}"
    ):
        self.github_api_key = github_api_key

    def fetch_contributions(self, params: ContributionsRequestParams) -> Contributions:
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
            return Contributions(**_flatten(resp.json()))
        else:
            raise APIError(f"Request failed with error: {resp.status_code}") from None
