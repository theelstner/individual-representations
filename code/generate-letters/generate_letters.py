from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY_TEXT_BASED_USER_REPRESENTATIONS"))
models = ["gpt-4.1","gpt-4o","gpt-4","o3"]

def get_response(prompt, model):
  if(model=="o3"):
    response = client.responses.create(
    model=model,
    input=prompt
    )
  else:
    response = client.responses.create(
    model=model,
    top_p=0.9,
    temperature=0.6,
    input=prompt
    )
  return(response)


def get_o3_response_text(response):
  text = ""
  try:
    text = response.output[1].content[0].text
  except (AttributeError, IndexError) as e:
    text = None
  return(text)

def get_response_text(response):
  response_text = ""
  try:
    response_text = response.output[0].content[0].text
    print(f"Extracted text and stored in 'response_text':\n{response_text}")
  except (AttributeError, IndexError) as e:
    print(f"Could not extract text from the response structure. Error: {e}")
    response_text = None # Assign None if extraction fails
  return(response_text)


def transform_string(input_string):
  values = input_string.split(',')
  if len(values) < 20:
      return "Error: Input string does not contain enough values."

  transformed = f"""Status of existing checking account:{values[0]}
Duration in month:{values[1]}
Credit history:{values[2]}
Purpose:{values[3]},
Credit amount:{values[4]},
Savings account/bonds:{values[5]}
Present employment since:{values[6]}
Installment rate:{values[7]}
Personal status and sex:{values[8]}
Other debtors / guarantors:{values[9]}
Present residence since:{values[10]}
Property:{values[11]}
Age:{values[12]}
Other installment plans:{values[13]}
Housing:{values[14]}
Number of existing credits at this bank:{values[15]}
Job:{values[16]}
Dependents:{values[17]}
Telephone:{values[18]}
Foreign worker:{values[19]}
"""
  return transformed


def write_prompt_file(prompt, id):
  file_name = "../prompts/" + str(id) + ".txt"
  try:
    with open(file_name, 'w') as f:
      f.write(prompt)
      print(f"Successfully wrote the string to {file_name}")
  except Exception as e:
    print(f"An error occurred while writing to the file: {e}")



def create_prompts(gcd_profiles_path):
  id = 1
  prompts=[]
  prompt_pre = "Write 5 motivation letters for a bank loan application. Each letter should be written from the perspective of a different person that could be described in the following profile. The letters should explain why the person is applying for the loan, what their financial situation is, and why they are a trustworthy candidate. Invent specific instances of all generic attributes from the profile (e.g. \"scientific research assistant\" instead of \"skilled employee\", \"8 years\" instead of \">= 7 years\", etc.). Keep the letters short and concise. Do not cut off the letter - be sure to write a proper ending! Do not use any formatting on the letter.\n\nProfile:\n"
  prompt_post = "\nWrite the letters."

  try:
    with open(gcd_profiles_path, 'r') as file:

      for line in file:
        gcd_profile = line.strip()
        gcd_profile = transform_string(gcd_profile)
        prompt=prompt_pre + gcd_profile + prompt_post
        write_prompt_file(prompt, id)
        prompts.append(prompt)
        id += 1
  except FileNotFoundError:
    print(f"Error: The file '{gcd_profiles_path}' was not found.")
  except Exception as e:
    print(f"An error occurred: {e}")
  return(prompts)

def write_response_file(response_text, model, prompt_id):
  file_name = "../out/" + model + "_" + str(prompt_id) + ".txt"
  try:
    with open(file_name, 'w') as f:
      f.write(response_text)
      print(f"Successfully wrote the string to {file_name}")
  except Exception as e:
    print(f"An error occurred while writing to the file: {e}")

def main():
  prompts=create_prompts('../../data/german-credit-dataset/gcd_values-decoded.csv')

  for model in models:
    prompt_id = 1 #1 #prompt_id ==out_file_id, == gcd_values-decoded-line_id
    print(f"processing model: {model}")
    for i in range(prompt_id, 1002):
      try:
        response=get_response(prompts[prompt_id-1], model)
        if(model=="o3"):
          response_text = get_o3_response_text(response)
          write_response_file(response_text, model, prompt_id)
        else:
          response_text = get_response_text(response)
          write_response_file(response_text, model, prompt_id)
      except Exception as e:
        print(e)
        prompt_id = prompt_id-1
      prompt_id= prompt_id+1

if __name__ == "__main__":
    main()