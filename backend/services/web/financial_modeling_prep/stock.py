def find_all(
    sector: str | None = None,
    industry: str | None = None,
    symbol: str | None = None,
    exchange: str | None = None,
):
    # WARNING: The `screener` API call from FPM seems to limit us to ~1k results
    # at a time. This is a known limitation we're accepting for now
    pass


def profile(symbol: str):
    pass
