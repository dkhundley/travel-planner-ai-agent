# Importing the necessary Python libraries
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Tuple, TextIO
from strands import Agent, tool
from strands.models.openai import OpenAIModel
from strands.telemetry import StrandsTelemetry



## SAMPLE SETUP
## -------------------------------------------------------------------------------------------------
TRACE_FILE = "agent_traces.jsonl"
COUNT_SENTENCE = "Strands is an amazing AI framework"
COUNT_CHAR = "a"
SUMMARY_PROMPT = "Can you summarize our discussion so far?"

def show_actual_datetime() -> None:
    print("Actual Date and Time:")
    print(datetime.now().strftime("%B %d, %Y at %I:%M %p"))


def show_actual_count() -> None:
    print("Actual Count:")
    print(COUNT_SENTENCE.count(COUNT_CHAR))



## TELEMETRY SETUP
## -------------------------------------------------------------------------------------------------
def otel_disabled() -> bool:
    return os.getenv("DISABLE_OTEL_EXPORT", "").strip().lower() in {"1", "true", "yes"}


def configure_tracing(log_path: Path) -> Tuple[StrandsTelemetry, TextIO]:
    telemetry = StrandsTelemetry()
    log_handle = log_path.open("a", encoding="utf-8")
    telemetry.setup_console_exporter(
        out=log_handle,
        formatter=lambda span: span.to_json() + "\n",
    )
    if otel_disabled():
        print("Remote OTLP export disabled via DISABLE_OTEL_EXPORT; writing spans to JSONL only.")
    else:
        try:
            telemetry.setup_otlp_exporter()
        except Exception as exc:
            print(f"Failed to configure OTLP exporter: {exc}")
    return telemetry, log_handle



## MODEL SETUP
## -------------------------------------------------------------------------------------------------
# Setting the Strands-OpenAI model
model_id = 'gpt-5-nano'
model = OpenAIModel(
    client_args = {
        'api_key': os.getenv('OPENAI_API_KEY')
    },
    model_id = model_id
)



## TOOL SETUP
## -------------------------------------------------------------------------------------------------
@tool
def perform_calculation(expr: str):
    '''
    Performs a basic mathematical calculation given as a string expression.

    Inputs:
        - expr (str): A string containing a mathematical expression (e.g., "30 / 5").
    
    Returns:
        - (float or str): The result of the calculation or an error message.
    '''
    try:
        # Setting allowed characters for safety
        allowed_chars = "0123456789+-*/.() "

        # Checking for invalid characters
        if not all(c in allowed_chars for c in expr):
            raise ValueError("Invalid characters in expression.")
        
        # Evaluating the mathematical expression safely
        return eval(expr)
    
    except Exception as e:
        return f"Error: {e}"



@tool
def get_current_datetime():
    '''
    Returns the current date and time in a human-readable format.

    Inputs:
        - N/A

    Returns:
        - (str): The current date and time as a string (e.g., "June 9, 2024 at 3:30 PM").
    '''
    return datetime.now().strftime("%B %d, %Y at %I:%M %p")



@tool
def count_character_occurrences(input_string: str, character: str):
    '''
    Counts the number of occurrences of a specified character / letter in a given string.

    Inputs:
        - input_string (str): The string to search within.
        - character (str): The character / letter to count occurrences of.

    Returns:
        - (int or str): The count of occurrences or an error message.
    '''
    try:
        if len(character) != 1:
            raise ValueError("Please provide a single character to count.")
        return input_string.count(character)
    except Exception as e:
        return f"Error: {e}"



## AGENT INSTANTIATION
## -------------------------------------------------------------------------------------------------
# Instantiating the agent with only the model
no_tools_agent = Agent(model = model)

# Instantiating the agent with the model and tools
tools_agent = Agent(model = model, tools = [perform_calculation, get_current_datetime, count_character_occurrences])

# Instantiating a "Jar Jar Binks" agent with model, tools, and system message
jar_jar_agent = Agent(
    model = model,
    tools = [perform_calculation, get_current_datetime, count_character_occurrences],
    system_prompt = "You are Jar Jar Binks from Star Wars. You speak in a distinctive way, often using phrases like 'Meesa' and 'Yousa'. Answer questions and perform tasks in character, adding a touch of humor and clumsiness to your responses."
)



## SCRIPT INVOCATION
## -------------------------------------------------------------------------------------------------
def main() -> None:
    _telemetry, log_handle = configure_tracing(TRACE_FILE)
    agents = {
        "No Tools Agent": no_tools_agent,
        "Tools Agent": tools_agent,
        "Jar Jar Binks Agent": jar_jar_agent,
    }

    # Setting simple prompts for different scenarios
    simple_prompt = "What is the capital of Illinois?"
    datetime_prompt = "What is the current date and time?"
    count_prompt = (
        f"How many times does the letter '{COUNT_CHAR}' appear in the sentence: '{COUNT_SENTENCE}'?"
    )

    # Defining scenarios for testing different prompts
    scenarios = [
        {"label": "Simple prompt", "prompt": simple_prompt},
        {"label": "Current date/time", "prompt": datetime_prompt, "before": show_actual_datetime},
        {"label": "Character counting", "prompt": count_prompt, "before": show_actual_count},
    ]

    try:
        for name, agent in agents.items():
            session_id = str(uuid.uuid4())
            print(f"\n\n==== {name} | Session: {session_id} ====")
            for scenario in scenarios:
                before = scenario.get("before")
                if callable(before):
                    before()
                print(f"\nScenario: {scenario['label']}")
                output = agent(scenario["prompt"], session_id=session_id)
                print(output)

            print("\nSummary Prompt Response:")
            summary_output = agent(SUMMARY_PROMPT, session_id=session_id)
            print(summary_output)
    finally:
        log_handle.close()
        print(f"\nTrace log written to {TRACE_FILE}")


if __name__ == "__main__":
    main()