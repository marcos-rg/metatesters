GENERATE_TESTERS_PROMPT: str = """
You are a LangChain and langgraph expert in python.
You are tasked with creating a set of AI tester personas.
Those are going to test an agentic system in python.
Those must have a grasp of the LLM and LangGraph frameworks.
Follow these instructions carefully:
1. First, review the general graph description:
{graph_description}

2. Review the graph history sample:
{graph_history_sample}

3. Examine any security team feedback that has been optionally provided to guide creation of the testers:
{human_analyst_feedback}

4. Determine the most critical kind of testing needed based upon the feedback above.
Max number of analysts: {max_analysts}

5. Identify the most relevant testing roles focusing on this business context.
6. For each role, provide a detailed description of the tester's expertise, focus, concerns, and motives. This will be use to create system messages for the AI testers
7. Ensure that the testers are diverse and cover a wide range of testing aspects.
8. Testers should be able to work independently and focus on their specific areas of expertise.
9. Each tester must be excellent in test case generation for odd behaviors, edge cases, and fault injection.
"""

GENERATE_TEST_CASES_PROMPT: str = """
{role_description}
You must generate test cases for this agent system. The below is the langgraph information:

Graph description:
{graph_description}

Graph history sample:
{graph_history_sample}

existing test cases:
{existing_test_cases}

Take your time to think about the test cases you want to create:
Give at least {min_test_cases} test cases.
Apply fault injection as much as you can
Avoid repeating an existing test case.
Must Avoid putting values in the test cases.
acceptance_criteria is required and will be used to verify if the test case passed or not by an LLM tester.
You must focus on your role and generate the test cases only in your area of expertise.
Try to be very creative  
Avoid being too obvious with the test cases.
You will receive a huge rewared if you create a test case that spots a bug in the graph.
"""

SELECT_TEST_CASES_PROMPT: str = """
{role_description}
You must select A test cases from the below list.

Test case names list:
{test_cases_names}

You must select {number_of_test_cases} test cases to modify them. 
You must select the test cases that you think are the most relevant to your role.
Give the index of the test cases you want to modify (0-based).
"""

MODIFY_TEST_CASES_PROMPT: str = """
{role_description}
Your task is to modify the test case below to make it more relevant to your role.

Test case information:
{test_case}

Try to be creative and not too obvious with the test cases.
You must focus on your role and generate the test cases only in your area of expertise.
Try to figure out what could be missing by a human tester and add it to the test case.
"""

NEW_INPUT_PROMPT: str = """
You are a LangChain and LangGraph python developer. Your are focused on testing a graph of LangGraph.
Some senior testers have provided you with a test case for the graph.
The test case is as follows:

- test case information:
{test_case_description}

- sample graph valid input:
{graph_valid_input}

you must follow this instructions:
1. Review the test case description.
2. Validate if the test case can be tested with an input using the valid input structure.
3. take graph valid input only as reference, you can modify it.
4. Apply fault injection as much as you can
5. If it can't be tested, return an empty string.
6. If it can be tested, create a new imput for the test case.
7. verify carefully the new input format. Every open bracket must have a closing bracket and so on.
8. For each property in the input, you MUST make sure it is the same type as it is in valid input.
9. For any message object, the content must be a string.
10. Make sure the string could be passed to the 'eval' python function. For example, if the input has 'null' it should be 'None'.
11. You must verify carefully the new input format to ensure is a valid python object.
"""
ASSERTION_PROMPT: str = """
{role_description}

A test case has been run on the graph and here you have the results:
You must validate the results using the test case description, acceptance criteria, and the output of the test case:

test case: 
{test_case}

Actual langgraph tasks:
{langgraph_tasks}

You must validate the output. If the output is as described in the test case acceptance criteria, return 'True'. Otherwise, return 'False'.
Identify also run time errors and mention them even if the output is as expected.
Finally, if the output is as expected, the comments should be a description of the behavior of the graph.
But if the output is not as expected, write a comment of how to solve the issue if the output is not as expected.
The comment contains possible fixes as bullet points with action items to implement such as:
1. LangGraph python code modification: add, remove, or modify nodes, edges, or properties base on Actual langgraph tasks information.
2. Prompt modifications.
"""