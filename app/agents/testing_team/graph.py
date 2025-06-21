import logging

from langgraph.graph import StateGraph
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import PromptTemplate
from langsmith import traceable
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from app.agents.testing_team.schemas import (InputState, OverallState, Testers, TestCasesList,
                                             TestCaseIndex, TestCase, NewInput, FinalOutput)
from app.agents.config.graph_config import Configuration
from app.agents.utils.llm import load_chat_model, create_structured_llm, create_system_message
from app.agents.utils.input import TypeAnnotator
from app.agents.testing_team.prompts import (GENERATE_TESTERS_PROMPT, GENERATE_TEST_CASES_PROMPT, 
                                             SELECT_TEST_CASES_PROMPT, MODIFY_TEST_CASES_PROMPT, NEW_INPUT_PROMPT,
                                             ASSERTION_PROMPT)
from app.config.config import settings
from app.service.db import SQLiteService
from app.agents.graph_analysis.utils import obj_to_str, invoke_graph

db_service = SQLiteService(settings.sqlite_path)

# =====================================================================
# Nodes
def generate_testers(state: InputState, config: RunnableConfig):
    logging.info("Generate testers node invoked")

    configuration = Configuration.from_runnable_config(config)
    model = load_chat_model(configuration.model)
    structured_llm = create_structured_llm(model, Testers)

    prompt = PromptTemplate.from_template(GENERATE_TESTERS_PROMPT)
    prompt = prompt.invoke({
        "graph_description": state["graph_description"],
        "graph_history_sample": state["graph_history_sample"],
        "human_analyst_feedback": state["human_analyst_feedback"],
        "max_analysts": state["max_analysts"]
    }).to_string()

    created_testers = structured_llm.invoke([create_system_message(prompt)])

    for tester in created_testers.testers:
        # Save each tester to the database
        db_service.create(tester)

    return {"testers": created_testers.testers}

def generate_test_cases(state: OverallState, config: RunnableConfig):
    logging.info("Generate test cases node invoked")

    configuration = Configuration.from_runnable_config(config)
    model = load_chat_model(configuration.model)
    structured_llm = create_structured_llm(model, TestCasesList)

    created_test_cases_list = []

    for tester in state["testers"]:
        prompt = PromptTemplate.from_template(GENERATE_TEST_CASES_PROMPT)
        prompt = prompt.invoke({
            "role_description": tester.description,
            "graph_description": state["graph_description"],
            "graph_history_sample": state["graph_history_sample"],
            "existing_test_cases": [test_case.name for test_case in created_test_cases_list],
            "min_test_cases": state["min_test_cases"]
        }).to_string()

        created_test_cases = structured_llm.invoke([create_system_message(prompt)])
        for test_case in created_test_cases.test_cases:
            test_case.tester = tester
            db_service.create(test_case)
            created_test_cases_list.append(test_case)


    return {"test_cases": created_test_cases_list}

def modify_test_case(state: OverallState, config: RunnableConfig):
    logging.info("Modify test case node invoked")

    configuration = Configuration.from_runnable_config(config)
    model = load_chat_model(configuration.model)

    new_test_cases = []

    @traceable
    def tester_modification(state, tester, model):
        no_tester_test_cases = [test_case for test_case in state["test_cases"] if test_case.tester != tester]

        structured_llm = create_structured_llm(model, TestCaseIndex)
        prompt = PromptTemplate.from_template(SELECT_TEST_CASES_PROMPT)
        prompt = prompt.invoke({
            "role_description": tester.description,
            "test_cases_names": [test_case.name for test_case in no_tester_test_cases],
            "number_of_test_cases": 1
        }).to_string()
        selected_test_case = structured_llm.invoke([create_system_message(prompt)])

        structured_llm = create_structured_llm(model, TestCase)
        prompt = PromptTemplate.from_template(MODIFY_TEST_CASES_PROMPT)
        prompt = prompt.invoke({
            "role_description": tester.description,
            "test_case": no_tester_test_cases[selected_test_case.index]
        }).to_string()
        modified_test_case = structured_llm.invoke([create_system_message(prompt)])

        return modified_test_case


    for tester in state["testers"]:
        modified_test_case = tester_modification(state, tester, model)

        modified_test_case.tester = tester
        db_service.create(modified_test_case)
        new_test_cases.append(modified_test_case)

    return {"test_cases": state["test_cases"] + new_test_cases }

def new_input_generation(state: OverallState, config: RunnableConfig):
    logging.info("New input generation node invoked")

    configuration = Configuration.from_runnable_config(config)
    model = load_chat_model(configuration.model)
    structured_llm = create_structured_llm(model, NewInput)

    new_inputs = []

    for test_case in state["test_cases"]:
        prompt = PromptTemplate.from_template(NEW_INPUT_PROMPT)
        prompt = prompt.invoke({
            "test_case_description": test_case,
            "graph_valid_input": obj_to_str(state["graph_valid_input"])
        }).to_string()
        new_input = structured_llm.invoke([create_system_message(prompt)])
        new_input.test_case = test_case
        db_service.create(new_input)
        new_inputs.append(new_input)

    return {"new_inputs": new_inputs}

def run_new_inputs(state: OverallState, config: RunnableConfig):
    logging.info("Run new inputs node invoked")

    new_inputs = state["new_inputs"]

    new_inputs_with_python_input = []

    for new_input in new_inputs:
        test_case = new_input.test_case
        tester = test_case.tester

        try:
            agent_valid_input = eval(new_input.new_input)
            agent_valid_input_type = TypeAnnotator(agent_valid_input).get_type()
            valid_input_type = TypeAnnotator(state["graph_valid_input"]).get_type()

            logging.info(f"Validating new input {agent_valid_input_type} against expected type {valid_input_type} is {agent_valid_input_type == valid_input_type}")

            if agent_valid_input_type == valid_input_type:
                logging.info(f"New input {new_input.new_input} is valid")
                new_input.actual_python_input = agent_valid_input

                config, error, error_message  = invoke_graph(
                    graph=state["compiled_graph"],
                    input=new_input.actual_python_input,
                    thread_id=test_case.id,
                    user_id=tester.id
                )

                new_input.is_successful = not error
                new_input.config = config

                new_inputs_with_python_input.append(new_input)
                db_service.create(new_input)

            else:
                logging.warning(f"New input {new_input.new_input} is not valid. Expected type: {valid_input_type}, got: {agent_valid_input_type}")
                new_input.is_successful = False
                
        except Exception as e:
            logging.error(f"Error evaluating input {new_input}: {e}")

    return {"new_inputs": new_inputs_with_python_input}

def analyze_results(state: OverallState, config: RunnableConfig):
    logging.info("Analyze results node invoked")

    configuration = Configuration.from_runnable_config(config)
    model = load_chat_model(configuration.model)
    structured_llm = create_structured_llm(model, FinalOutput)

    assertions = []

    for input in state["new_inputs"]:
        configuration = {"configurable": input.config}
        tasks = obj_to_str(state["compiled_graph"].get_state(configuration).values)

        prompt = PromptTemplate.from_template(ASSERTION_PROMPT)
        prompt = prompt.invoke({
            "role_description": input.test_case.tester.description,
            "test_case": input.test_case,
            "langgraph_tasks": tasks
        }).to_string()

        assertion = structured_llm.invoke([create_system_message(prompt)])

        assertion.new_input = input
        assertion.task = tasks
        assertions.append(assertion)
        db_service.create(assertion)

    return {"assertions": assertions}


# =====================================================================
# Build the graph
builder = StateGraph(state_schema=OverallState,
                     input=InputState,
                     config_schema=Configuration)

# Add nodes
builder.add_node("generate_testers", generate_testers)
builder.add_node("generate_test_cases", generate_test_cases)
builder.add_node("modify_test_case", modify_test_case)
builder.add_node("new_input_generation", new_input_generation)
builder.add_node("run_new_inputs", run_new_inputs)
builder.add_node("analyze_results", analyze_results)

# Add edges
builder.set_entry_point("generate_testers")
builder.add_edge("generate_testers", "generate_test_cases")
builder.add_edge("generate_test_cases", "modify_test_case")
builder.add_edge("modify_test_case", "new_input_generation")
builder.add_edge("new_input_generation", "run_new_inputs")
builder.add_edge("run_new_inputs", "analyze_results")
builder.set_finish_point("analyze_results")

# Compile workflow
# memory = MemorySaver()
testing_team_app = builder.compile(name="Testing Team Agents")

