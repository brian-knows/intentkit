"""Tool for fetching top cryptocurrencies by market cap via CryptoCompare API."""

from typing import Any, Dict, Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

from skills.cryptocompare.api import FetchTopMarketCapInput, fetch_top_market_cap
from skills.cryptocompare.base import CryptoCompareBaseTool

FETCH_TOP_MARKET_CAP_PROMPT = """
This tool retrieves the top cryptocurrencies ranked by market capitalization.
Customize results with limit and quote currency parameters.
Returns detailed information including current price, market cap, 24h volume, and circulating supply.
"""


class CryptoCompareFetchTopMarketCapOutput(BaseModel):
    result: Dict[str, Any]
    error: str | None = None


class CryptoCompareFetchTopMarketCap(CryptoCompareBaseTool):
    name: str = "cryptocompare_fetch_top_market_cap"
    description: str = FETCH_TOP_MARKET_CAP_PROMPT
    args_schema: Type[BaseModel] = FetchTopMarketCapInput

    async def _arun(
        self, to_symbol: str, config: RunnableConfig, **kwargs
    ) -> CryptoCompareFetchTopMarketCapOutput:
        try:
            # Get agent context if available
            context = self.context_from_config(config)
            agent_id = context.agent.id if context else None
            # Check rate limiting with agent_id
            is_rate_limited, error_msg = await self.check_rate_limit(agent_id=agent_id)
            if is_rate_limited:
                return CryptoCompareFetchTopMarketCapOutput(result={}, error=error_msg)

            limit = 10
            # Fetch top market cap data from API using API key from context
            result = await fetch_top_market_cap(
                context.config.get("api_key"), limit, to_symbol
            )
            return CryptoCompareFetchTopMarketCapOutput(result=result)
        except Exception as e:
            return CryptoCompareFetchTopMarketCapOutput(result={}, error=str(e))
