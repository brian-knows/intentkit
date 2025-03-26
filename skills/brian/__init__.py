"""Enso skills."""

from typing import List, NotRequired

from cdp import Wallet

from abstracts.agent import AgentStoreABC
from abstracts.skill import SkillStoreABC
from skills.base import SkillConfig
from skills.brian.base import BrianBaseSkill
from skills.brian.execute_transaction import BrianExecuteTransaction
from utils.chain import ChainProvider


class Config(SkillConfig):
    """Configuration for Brian skills."""
    api_key: str
    public_skills: List[str]
    private_skills: NotRequired[List[str]]


def get_skills(
    config: "Config",
    agent_id: str,
    is_private: bool,
    store: SkillStoreABC,
    agent_store: AgentStoreABC,
    wallet: Wallet,
    **_,
) -> list[BrianBaseSkill]:
    """Get all Brian skills."""
    # always return public skills
    resp = [
        get_brian_skill(name, config["api_key"], wallet, store, agent_store, agent_id) for name in config["public_skills"]
    ]
    # return private skills only if is_private
    if is_private:
        resp.extend(
            get_brian_skill(name, config["api_key"], wallet, store, agent_store, agent_id)
            for name in config["private_skills"]
            # remove duplicates
            if name not in config["public_skills"]
        )
    return resp


def get_brian_skill(
    name: str,
    api_key: str,
    wallet: Wallet,
    skill_store: SkillStoreABC,
    agent_store: AgentStoreABC,
    agent_id: str,
) -> BrianBaseSkill:
    if not api_key:
        raise ValueError("Brian API key is empty")

    if name == "execute_transaction":
        return BrianExecuteTransaction(
            api_key=api_key,
            wallet=wallet,
            skill_store=skill_store,
            agent_store=agent_store,
            agent_id=agent_id,
        )

    else:
        raise ValueError(f"Unknown Enso skill: {name}")
