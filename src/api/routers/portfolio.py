import pandas as pd
from fastapi import APIRouter

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)


@router.get("/stats")
def portfolio_stats():
    """portfolio_stats function."""

    df = pd.read_csv("output/portfolio_stats.csv")

    return df.to_dict(
        orient="records"
    )