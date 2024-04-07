from openai import OpenAI
import json
import os
import config
import sys
"""
"Provide a set of numbered steps outlining an effective strategy for completing a homework assignment. The homework assignment is 
described by the text enclosed in single quotes: '{description}'. Write the advice in JSON format, where each step number maps to 
the description for that step of the effective work strategy. Additionally, create a JSON file containing a dictionary of helpful 
websites for completing the assignment. Each entry in the dictionary should have a title as its key and a URL as its value. Finally, 
include another JSON file containing a single integer representing the estimated time, in minutes, to complete this assignment. If 
you encounter any difficulties, such as trouble estimating the time required. Ensure that each JSON file follows a consistent structure. 
If you are unable to find relevant websites, return an empty JSON dictionary for that file instead."
"""


api_key = config.openai_api_key
client = OpenAI(api_key=api_key)

prompt_format = ""
def generate_prompt(text_dic):
    # this function expects a dictionary with a key 'description', holding a text description for an assignment
    # this function returns a prompt to feed the AI
    description = text_dic['description']

    return f"Provide a set of numbered steps outlining an effective strategy for completing a homework assignment. The homework assignment is described by the text enclosed in single quotes: '{description}'. Write the advice in JSON format, where each step number maps to the description for that step of the effective work strategy. Additionally, create a JSON file containing a dictionary of helpful websites for completing the assignment. Each entry in the dictionary should have a title as its key and a URL as its value. Finally, include another JSON file containing a single integer representing the estimated time, in minutes, to complete this assignment. If you encounter any difficulties, such as trouble estimating the time required. Ensure that each JSON file follows a consistent structure. If you are unable to find relevant websites, return an empty JSON dictionary for that file instead. It is absolutely crucial that you do return all 3 JSON dictionaries, they all must be formatted exactly as specified, and you must return absolutely nothing else."

# def generate_prompt2(description): #just to use while we don't have integration w/ Canvas data
#    # description = text_dic['description']

#     return f"Give me a numbered steps to take to complete the following assignment wrapped by single quotes: '{description}' Please write the advice like normal, but put it in json format containing the step number and the description for that step. Also write another JSON file containing URLs and titles of websites which could be helpful for completing the assignment. Also, write another JSON file which contains a single estimated time to complete the assignment. Only return the three JSON files."

def generate_text(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    ) 
    print(chat_completion.choices)  
    return chat_completion.choices[0].message.content

#def retrieve_json(generated_text):
    #generated_response = generated_text
    #response_dict = json.loads(generated_response)
    #return response_dict

def process_chatgpt_output(chatgpt_output, assignment_id):
    # Split the chatgpt_output into individual JSON strings
    json_strings = chatgpt_output.split("\n\n")
    # file_paths as a list because [0] should be steps [1] should be urls, and [2] should be minutes
    keys = {0: 'steps', 1: 'urls', 2: 'minutes'}
    
    assignment_outp_content = {}
    # Process each JSON string separately
    for i, json_string in enumerate(json_strings):
        print(i)
        print(f"\n\n{json_string}\n\n")
        try:
            # Parse the JSON string into a dictionary
            json_data = json.loads(json_string)
            if json_data == {}:
                assignment_outp_content[i] = {}
            else:
                assignment_outp_content[i] = json_data
            

        except json.JSONDecodeError as e:
            print(f"Error loading JSON file {i}: {e}", file=sys.stderr)
        except KeyError as e:
            print(f"GPT returned too many responses : {e}", file=sys.stderr)
    
    # STORE ALL 3 IN ONE DICTIONARY UNDER ASSIGNMENT NAME FILE NAME
    assignment_outp_file_name = f"gpt_output_{assignment_id}.json"
    file_path = "gpt_out/" + assignment_outp_file_name

    # Save the JSON data to a file
    with open(file_path, "w") as json_file:
        json.dump(obj=assignment_outp_content, fp=json_file, indent=4)

    print(f"JSON file {i} saved successfully: {file_path}")
    
    return file_path


def get_json_from_assignment_id(assignment_id):
    # takes in one assignment ID, then asks chatgpt about it, and saves 3 separate documents
    with open("json_out/assignment_ids_to_info.json", "r") as file:
        try:
            info = json.load(file)
            assignment_info = info[assignment_id]
        except KeyError:
            print(f"Assignment ID ' {assignment_id} ' not in database", path=sys.stderr)
            return
        
        prompt = generate_prompt(assignment_info)
        chatgpt_output = generate_text(prompt)
        path = process_chatgpt_output(chatgpt_output=chatgpt_output, assignment_id=assignment_id)
        return path


print(get_json_from_assignment_id("18760000001387025"))
