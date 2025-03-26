from typing import Type

from cdp import Wallet
from pydantic import BaseModel, Field

from abstracts.skill import SkillStoreABC
from skills.base import IntentKitSkill

api_url = "https://api.brianknows.org"

class BrianBaseSkill(IntentKitSkill):
    """Base class for Brian tools."""

    api_key: str = Field(description="Brian API key")
    name: str = Field(description="The name of the tool")
    wallet: Wallet | None = Field(None, description="The wallet of the agent")
    description: str = Field(description="A description of what the tool does")
    args_schema: Type[BaseModel]
    skill_store: SkillStoreABC = Field(
        description="The skill store for persisting data"
    )

    @property
    def category(self) -> str:
        return "brian"
