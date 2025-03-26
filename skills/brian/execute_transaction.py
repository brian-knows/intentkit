from typing import Type

from cdp import Wallet, wallet_action_provider
import httpx
from pydantic import BaseModel, Field

from abstracts.skill import SkillStoreABC
from skills.brian.base import BrianBaseSkill, api_url


class BrianExecuteTransactionInput(BaseModel):
    """Input for BrianExecuteTransaction skill."""

    prompt: str = Field(
        description="The prompt/thought to get the transaction for"
    )


class BrianExecuteTransaction(BrianBaseSkill):
    """Skill for executing a transaction from a prompt/thought.

    This skill uses the Brian API to get the transaction data from a prompt/thought.

    Attributes:
        name: The name of the skill.
        description: A description of what the skill does.
        args_schema: The schema for the skill's input arguments.
    """

    agent_id: str
    skill_store: SkillStoreABC
    api_key: str
    wallet: Wallet | None = None

    name: str = "execute_transaction"
    description: str = (
        "This skill will execute a transaction from a given prompt/thought.",
        "The prompt/thought should be a description of the transaction you want to execute.",
        "Some example of prompts/thoughts are: 'Swap 10 USDC for ETH on Base', 'Deposit 1 ETH into AAVE on Ethereum', 'Bridge 100 USDC from Polygon to Arbitrum'",
        "Always specify the name of the chain you're working on."
    )
    args_schema: Type[BaseModel] = BrianExecuteTransactionInput

    async def _arun(self, prompt: str) -> str:
        """Async implementation of the skill to get transaction.

        Args:
            prompt (str): The prompt/thought to get the transaction for.

        Returns:
            str: A message containing the transaction data or error message.
        """
        try:
            if not self.wallet:
                return "Failed to get wallet."
            if not self.api_key:
                return "Failed to get Brian API key."

            async with httpx.AsyncClient() as client:

                headers = {
                    "accept": "application/json",
                    "x-brian-api-key": self.api_token,
                }

                response = await client.post(
                    f"{api_url}/api/v0/agent/transaction",
                    headers=headers,
                    json={"prompt": prompt, "address": self.wallet.addresses[0].address_id},
                )
                response.raise_for_status()  # Raise HTTPError for non-2xx responses
                json_dict = response.json()
                
                data = json_dict['result']['data']

                for step in data['steps']:
                    # execute each step
                    self.wallet.send_transaction(step)

        except Exception as e:
            return f"Error getting balance: {str(e)}"

    def _run(self, prompt: str) -> str:
        """Sync implementation of the tool.

        This method is deprecated since we now have native async implementation in _arun.
        """
        raise NotImplementedError(
            "Use _arun instead, which is the async implementation"
        )
