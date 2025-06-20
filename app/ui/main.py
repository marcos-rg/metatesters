import logging
import uuid

import gradio as gr
from gradio import themes
import matplotlib.pyplot as plt

from langchain_core.messages import HumanMessage
from app.agents import create_human_message, graph_analysis_app, arithmetic_graph, testing_team_app

graph_analysis_result = None
testers_result = None

def invoke_analyze_graph():
    global graph_analysis_result

    user_description = "This is a react graph. It has one agent and one tool node. This is an assistant that can perform arithmetic operations."

    user_valid_input = {"messages": [create_human_message(message="Add 3 and 4")]}

    graph_before_compile = arithmetic_graph

    configurations = {"configurable": {"model": "azure_openai/gpt-4.1"}}
    # configurations = None

    graph_analysis_result = graph_analysis_app.invoke({"user_description":user_description,
                        "valid_input": user_valid_input,
                        "graph_before_compile": graph_before_compile},
                            config=configurations,
                        )
    

    graph_image_path = "graph_output.png"
    # If draw_mermaid_png doesn't accept output_path parameter, use this alternative approach:
    image_data = graph_analysis_result["compiled_graph"].get_graph().draw_mermaid_png()
    with open(graph_image_path, "wb") as f:
        f.write(image_data)

    graph_analysis_result["graph_image_path"] = graph_image_path

    return "done"

def invoke_generate_testers(suggested_testers):
    global testers_result

    if not graph_analysis_result:
        logging.error("Graph analysis result is not available.")
        return "Graph analysis result is not available."
    
    thread_id = str(uuid.uuid4())

    configuration = {"configurable": {"thread_id": thread_id, "model": "azure_openai/gpt-4.1"}}
    # configuration = {"configurable": {"thread_id": thread_id}}
    
    testers_result = testing_team_app.invoke({
                "graph_description": graph_analysis_result["graph_description"],
                "graph_history_sample": graph_analysis_result["history_to_show"],
                "human_analyst_feedback": suggested_testers,
                "max_analysts": 3,
                "min_test_cases": 6,
                "graph_valid_input": graph_analysis_result["valid_input"], 
                "compiled_graph": graph_analysis_result["compiled_graph"]
            }, config=configuration)

    return "done"

with gr.Blocks(theme=themes.Ocean()) as demo:
    with gr.Tab("Step 1: Analyze Graph"):
        analize_result = gr.State(None)

        gr.Markdown("# Graph Analysis")
        gr.Markdown("This step analyzes the static graph and provides insights into its structure and components.")
        star_analysis_button = gr.Button("Analyze Graph", size="md", variant="primary")

        star_analysis_button.click(fn=invoke_analyze_graph, 
                                      outputs=analize_result,
                                      show_progress="full")
        
        @gr.render(inputs=analize_result)
        def update_analysis_result(analize_result):
            global graph_analysis_result
            gr.Markdown("## Graph Information")
            if graph_analysis_result:
                gr.Markdown(f"## User Graph Description")
                gr.Markdown(graph_analysis_result["user_description"])

                gr.Markdown("---")

                gr.Markdown("## Graph Image")
                gr.Image(value=graph_analysis_result["graph_image_path"], width=700)

                gr.Markdown("---")

                gr.Markdown("## Valid Input")
                gr.Markdown("This is a valid input for the graph, which is used to invoke the graph")
                gr.Code(str(graph_analysis_result["valid_input"]), language="python", label=f"Valid Input", 
                                            container=False, wrap_lines=True, lines=1, show_label=False, scale=2,
                                            show_line_numbers=False)

                gr.Markdown("---")

                gr.Markdown("## History Tasks")
                gr.Code(str(graph_analysis_result["history_to_show"]), language="python", label=f"History", 
                                            container=False, wrap_lines=True, lines=1, show_label=False, scale=2,
                                            show_line_numbers=False)

                gr.Markdown("---")

                gr.Markdown("## Nodes details")
                gr.Markdown("This section provide information about each node in the graph, including its type, description, internal tools, and whether it is runnable or not.")

                with gr.Group():
                    graph = graph_analysis_result["summary_graph"]
                    for node in graph.get_all_nodes():
                        node = graph.get_node_attributes(node)
                        with gr.Accordion(node["name"], open=False):
                            gr.Markdown(f"**Type:** {node['type']} \n")
                            gr.Markdown(f"**Description:** {node['description']} \n")
                            gr.Markdown(f"**Runnable:** {node['runnable']} \n")
                            gr.Markdown(f"**Tools:** {node['tools']} \n")

                gr.Markdown("---")

                gr.Markdown("## Graph Summary")
                gr.Markdown(graph_analysis_result["graph_description"])


            else:
                show_description = gr.Markdown("No graph information available.")

    with gr.Tab("Step 2: Generate Test Cases"):
        testers_result_state = gr.State(None)

        gr.Markdown("# Generate Test Cases")
        gr.Markdown("This step generates test cases based on the analyzed graph to ensure its functionality and correctness.")

        suggested_testers = gr.TextArea(label="User Suggested Testers",
                                       value="""Include: functional tester which is a subject matter expert in the domain of the application, an anti injection and jailbreak LLM engineer, and a vulnerabilities bounty hunter""",
                                         lines=2)

        generate_testers_button = gr.Button("Generate Test Cases", variant="primary")

        generate_testers_button.click(fn=invoke_generate_testers,
                                        inputs=[suggested_testers],
                                        outputs=testers_result_state)
        
        @gr.render(inputs=testers_result_state)
        def update_testers_result(testers_result_state):
            global testers_result
            gr.Markdown("# Testers Information")

            if testers_result:

                 for tester in testers_result["testers"]:
                    gr.Markdown(f"## {tester.role}")
                    gr.Markdown(f"ID: {tester.id}")
                    gr.Markdown(f"**System prompt:** {tester.description}")

                    gr.Markdown("### Test Cases:")
                    with gr.Group():
                        for new_input in testers_result["new_inputs"]:
                            if new_input.test_case.tester.id == tester.id:
                                with gr.Accordion(label=f"{new_input.test_case.name}", open=False):
                                    gr.Markdown(f"ID: {new_input.id}")
                                    gr.Markdown(f"**Test Case Description:** {new_input.test_case.description}")
                                    gr.Markdown(f"**Acceptance Criteria:** {new_input.test_case.acceptance_criteria}")
                                    gr.Markdown(f"**New Input Object:** ")
                                    gr.Code(new_input.new_input, language="python", label=f"New Input Object", 
                                            container=True, wrap_lines=True, lines=1, show_label=False, scale=2,
                                            show_line_numbers=False)
                    gr.Markdown("---")


            else:
                show_description = gr.Markdown("No testers information available.")


    with gr.Tab("Step 3: Results"):

        @gr.render(inputs=testers_result_state)
        def show_testers_result(testers_result_state):
            global testers_result

            if testers_result:
                assertions = testers_result["assertions"]
                passed_assertions = [assertion for assertion in assertions if assertion.assertion]
                failed_assertions = [assertion for assertion in assertions if not assertion.assertion]

                # Create pie chart data
                passed_count = len(passed_assertions)
                failed_count = len(failed_assertions)
                total_count = len(assertions)

                # Create the pie chart
                fig, ax = plt.subplots(figsize=(6, 5))
                sizes = [passed_count, failed_count]
                labels = [f'Passed ({passed_count})', f'Failed ({failed_count})']
                colors = ["#6DE0B8", "#EE709AEE"]  # Green for passed, Red for failed
                explode = (0.03, 0.03)  # Slightly separate the slices

                wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors, 
                                                autopct='%1.1f%%', shadow=False, startangle=90,
                                                textprops={'fontsize': 12, 'fontweight': 'bold'})

                # Customize the chart
                ax.set_title(f'Test Results Summary\n({total_count} Total Assertions)', 
                            fontsize=16, fontweight='bold', pad=20)

                # Make percentage text white for better visibility
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontsize(14)
                    autotext.set_fontweight('bold')

                plt.tight_layout()
                plt.close(fig)

                # Define Unicode symbols for checkmark and cross
                CHECKMARK = "\u2705"  # ✅
                CROSS = "\u274C"      # ❌

                gr.Plot(fig, show_label=False, container=False, format="png")
                
                for assertion in passed_assertions:
                    symbol = CHECKMARK if assertion.assertion else CROSS
                    with gr.Accordion(label=f"{assertion.new_input.test_case.name} {symbol}", open=False):
                        gr.Markdown(f"**Tester:** {assertion.new_input.test_case.tester.role}") 
                        gr.Markdown(f"**Acceptance Criteria:** {assertion.new_input.test_case.acceptance_criteria}")
                        gr.Markdown(f"**Comment:** {assertion.comment}")
                        gr.Markdown(f"**Actual graph output:** ")
                        gr.Code(assertion.task, language="python", label=f"New Input Object", 
                                                    container=True, wrap_lines=True, lines=1, show_label=False, scale=2,
                                                    show_line_numbers=False)
                        
                for assertion in failed_assertions:
                    symbol = CHECKMARK if assertion.assertion else CROSS
                    with gr.Accordion(label=f"{assertion.new_input.test_case.name} {symbol}", open=False):
                        gr.Markdown(f"**Tester:** {assertion.new_input.test_case.tester.role}") 
                        gr.Markdown(f"**Acceptance Criteria:** {assertion.new_input.test_case.acceptance_criteria}")
                        gr.Markdown(f"**Comment:** {assertion.comment}")
                        gr.Markdown(f"**Actual graph output:** ")
                        gr.Code(assertion.task, language="python", label=f"New Input Object", 
                                                    container=True, wrap_lines=True, lines=1, show_label=False, scale=2,
                                                    show_line_numbers=False)
            else:
                show_description = gr.Markdown("No result information available.")
            
        
