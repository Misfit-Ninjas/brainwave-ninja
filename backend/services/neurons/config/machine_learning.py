"""machine learning settings"""

from dataclasses import dataclass


class ForecastingApproachEnum:
    ML = "Use machine learning"
    BASELINE = "Use static baseline"


@dataclass
class Config:
    forecasting_approach: ForecastingApproachEnum


def run(config: Config) -> Config:
    return config
