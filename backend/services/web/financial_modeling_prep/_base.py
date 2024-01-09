import pathlib

import decouple
from requests_ratelimiter import LimiterSession


class Base:
    def __init__(
        self,
        api_key: str,
        api_endpoint: str,
        session: LimiterSession | None = None,
        session_limit: int | None = None,
    ):
        self.api_key = api_key
        self.api_endpoint = api_endpoint.rstrip("/")
        self.session = session

        if self.session is None:
            if session_limit is None:
                raise ValueError("Either `session` or `session_limit` must be provided")
            self.session = LimiterSession(session_limit, limit_statuses=[429, 504])

    def get(self, url, **kwargs):
        result = self.session.get(f"{self.api_endpoint}/{url.lstrip('/')}", params=kwargs)
        result.raise_for_status()
        return result


_config = decouple.Config(decouple.RepositoryEnv(pathlib.Path(__file__).parent.parent / ".env"))
CONFIG = {
    "api_key": _config("financial_modeling_prep_apikey"),
    "session_limit": _config("financial_modeling_prep_throttle", default=5, cast=int),  # Per second
    "api_endpoint": "https://financial_modeling_prep.com",
}
