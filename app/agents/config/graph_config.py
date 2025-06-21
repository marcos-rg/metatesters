"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Optional

from langchain_core.runnables import RunnableConfig, ensure_config



@dataclass(kw_only=True)
class Configuration:
    """The configuration for the agent."""

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="azure_openai/gpt-4o-mini",
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "Should be in the form: provider/model-name."
        },
    )

    thread_id: Annotated[Optional[str], {"__template_metadata__": {"kind": "thread_id"}}] = field(
        default=None,
        metadata={
            "description": "The thread ID for the agent. If not provided"
        },
    )

    user_id: Annotated[Optional[str], {"__template_metadata__": {"kind": "user_id"}}] = field(
        default=None,
        metadata={
            "description": "The user ID for the agent. If not provided"
        },
    )


    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> Configuration:
        """Create a Configuration instance from a RunnableConfig object."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})