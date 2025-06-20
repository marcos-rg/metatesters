from typing import Any, List, Optional
from typing_extensions import TypedDict
import uuid

from pydantic import BaseModel, Field, PrivateAttr
from langgraph.graph.graph import CompiledGraph
from langchain_core.runnables import RunnableConfig

class InputState(TypedDict):
    """
    Defines the input state for the agent.
    """
    graph_description: str
    graph_history_sample: str
    human_analyst_feedback: str
    max_analysts: int
    min_test_cases: int
    graph_valid_input: str
    compiled_graph: CompiledGraph

class OverallState(InputState):
    """
    Defines additional internal state for the agent.
    """
    testers: list
    test_cases: list
    new_inputs: list
    assertions: list


# =====================================================================
# pydantic models

class SuggestedTester(BaseModel):
    role: str = Field(
        description="Role of the tester in the context of the graph.",
    )
    description: str = Field(
        description="Role description of the tester expertise, focus, concerns, and motives. (you are ...) ",
    )
    _id: str = PrivateAttr(default_factory=lambda: str(uuid.uuid4()))

    @property
    def id(self):
        return self._id

class Testers(BaseModel):
    testers: List[SuggestedTester] = Field(
        description="Comprehensive list of testers with their roles and descriptions",
    )


class TestCase(BaseModel):
    name: str = Field(description="Name of the test case. Do not enumerate the test cases. Just give a descriptive name")

    description: str = Field(description="Test case description.  No specific values in the description")

    acceptance_criteria: str = Field(description="acceptance criteria description to pass the test. No specific values in the test case")

    _tester: Optional[SuggestedTester] = PrivateAttr(default=None)

    _id: str = PrivateAttr(default_factory=lambda: str(uuid.uuid4()))

    @property
    def id(self):
        return self._id
    
    @property
    def tester(self):
        return self._tester
    
    @tester.setter
    def tester(self, tester: SuggestedTester):
        if not isinstance(tester, SuggestedTester):
            raise ValueError("tester must be an instance of SuggestedTester")
        self._tester = tester

class TestCasesList(BaseModel):
    test_cases: List[TestCase] = Field(description="Comprehensive list of test cases with their properties")


class TestCaseIndex(BaseModel):
    index: int = Field(description="Index of the test case in the list")
    

class NewInput(BaseModel):
    new_input : str = Field(description="new input for the test case. It must be only the python script code.")

    _is_successful: Optional[Any] = PrivateAttr(default=None)

    _actual_python_input: Optional[Any] = PrivateAttr(default=None)

    _test_case: Optional[TestCase] = PrivateAttr(default=None)

    _id: str = PrivateAttr(default_factory=lambda: str(uuid.uuid4()))

    _config: Optional[RunnableConfig] = PrivateAttr(default=None)

    @property
    def id(self):
        return self._id

    @property
    def test_case(self):
        return self._test_case

    @test_case.setter
    def test_case(self, test_case: TestCase):
        if not isinstance(test_case, TestCase):
            raise ValueError("test_case must be an instance of NewInput")
        self._test_case = test_case

    @property
    def actual_python_input(self):
        return self._actual_python_input
    
    @actual_python_input.setter
    def actual_python_input(self, actual_python_input: Any):
        if not isinstance(actual_python_input, (str, dict, list)):
            raise ValueError("actual_python_input must be a string, dict or list")
        self._actual_python_input = actual_python_input

    @property
    def is_successful(self):
        return self._is_successful
    
    @is_successful.setter
    def is_successful(self, is_successful: bool):
        if not isinstance(is_successful, bool):
            raise ValueError("is_successful must be a boolean")
        self._is_successful = is_successful

    @property
    def config(self):
        return self._config
    
    @config.setter
    def config(self, config: RunnableConfig):
        self._config = config


class FinalOutput(BaseModel):
    assertion : bool = Field(description="Assertion of the test case")
    comment : str = Field(description="Final comment on the test case output")
    _new_input: Optional[NewInput] =  PrivateAttr(default=None)
    _id: str = PrivateAttr(default_factory=lambda: str(uuid.uuid4()))
    _task: Optional[Any] = PrivateAttr(default=None)

    @property
    def id(self):
        return self._id

    @property
    def new_input(self):
        return self._new_input

    @new_input.setter
    def new_input(self, new_input: NewInput):
        if not isinstance(new_input, NewInput):
            raise ValueError("new_input must be an instance of NewInput")
        self._new_input = new_input

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task: Any):
        self._task = task