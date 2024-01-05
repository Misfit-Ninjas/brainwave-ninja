"""future quarters settings"""

from dataclasses import dataclass


@dataclass
class Config:
    number_of_quarters: int


def run(config: Config) -> Config:
    return config
