from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from pydantic import BaseModel

def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)

    return init_chat_model(model=model, model_provider=provider)


def create_structured_llm(llm: BaseChatModel, structured_output: BaseModel) -> BaseChatModel:
    """
    Creates a language model that outputs structured data according to the given Pydantic model.
    This function wraps a language model to make it return outputs conforming to a
    specified Pydantic BaseModel schema.
    Args:
        llm: The language model to wrap with structured output capability.
        structured_output (BaseModel): A Pydantic BaseModel class that defines the
            structure of the output.
    Returns:
        The language model with structured output capability.
    Raises:
        ValueError: If the provided language model is not valid or doesn't support
            structured output.
    Example:
        ```python
        class Person(BaseModel):
            name: str
            age: int
        structured_model = create_structured_llm(llm, Person)
        ```
    """
    
    try:
        structured_llm = llm.with_structured_output(structured_output)
        return structured_llm
    except:
        raise ValueError("The llm model is not valid")
    
def create_human_message(message: str) -> HumanMessage:
    """
    Creates a HumanMessage object with the given message content.
    Args:
        message (str): The content of the message to be included in the HumanMessage object.
    Returns:
        HumanMessage: A HumanMessage object containing the provided message as its content.
    """
    
    return HumanMessage(content=message)

def create_system_message(message: str) -> SystemMessage:
    """
    Creates a SystemMessage object with the given message content.
    Args:
        message (str): The content of the message to be included in the SystemMessage object.
    Returns:
        SystemMessage: A SystemMessage object containing the provided message as its content.
    """
    return SystemMessage(content=message)

