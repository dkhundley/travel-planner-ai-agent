# Importing the necessary Python libraries
import os
from datetime import datetime
from strands import Agent, tool
from strands.models.openai import OpenAIModel

# Setting the Strands-OpenAI model
model = OpenAIModel(
    client_args = {
        'api_key': os.getenv('OPENAI_API_KEY')
    },
    model_id = 'gpt-5-nano'
)

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

# Instantiating the agent with only the model
no_tools_agent = Agent(model = model)

# Instantiating the agent with the model and tools
tools_agent = Agent(model = model, tools = [perform_calculation, get_current_datetime])

# Instantiating a "Jar Jar Binks" agent with model, tools, and system message
jar_jar_agent = Agent(
    model = model,
    tools = [perform_calculation, get_current_datetime],
    system_prompt = "You are Jar Jar Binks from Star Wars. You speak in a distinctive way, often using phrases like 'Meesa' and 'Yousa'. Answer questions and perform tasks in character, adding a touch of humor and clumsiness to your responses."
)

# Testing the agents with a simple sample prompt
simple_prompt = "What is the capital of Illinois?"

print("No Tools Agent Response:")
response = no_tools_agent(simple_prompt)
print("\n\nTools Agent Response:")
response = tools_agent(simple_prompt)
print("\n\nJar Jar Binks Agent Response:")
response = jar_jar_agent(simple_prompt)


# # Testing the agents with a calculation prompt
# calc_prompt = "What is 30586450123124918824 * 85748795938829102938?"

# print("Actual Calculation:")
# print(30586450123124918824 * 85748795938829102938)
# print("\n\nNo Tools Agent Response:")
# response = no_tools_agent(calc_prompt)
# print("\n\nTools Agent Response:")
# response = tools_agent(calc_prompt)
# print("\n\nJar Jar Binks Agent Response:")
# response = jar_jar_agent(calc_prompt)

# Testing the agents with a prompt to get the current date and time
datetime_prompt = "What is the current date and time?"

print("Actual Date and Time:")
print(datetime.now().strftime("%B %d, %Y at %I:%M %p"))
print("\n\nNo Tools Agent Response:")
response = no_tools_agent(datetime_prompt)
print("\n\nTools Agent Response:")
response = tools_agent(datetime_prompt)
print("\n\nJar Jar Binks Agent Response:")
response = jar_jar_agent(datetime_prompt)



