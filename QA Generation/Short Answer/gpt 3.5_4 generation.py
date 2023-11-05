import openai
from xml.etree import ElementTree as ET
import os, glob
import pandas as pd
import argparse
import time

openai.api_key = '' #Replace with your openAI API key

def extract_text_from_xml(filename):
    with open('/content/a0abc3fa0e6b44aaaf5e70e36602b61e.xml', 'rb') as f:
        xml_bytes = f.read()
        xml_str = xml_bytes.decode('UTF-8')


        # Extract text from <p> tags
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', xml_str, re.DOTALL)

        return(" ").join(paragraphs)

def find_keywords(xml_file_path):
    xml = extract_text_from_xml(xml_file_path)
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
    {
      "role": "user",
      "content": f"extract key concepts from the following xml text such that we can assess data science knowledge based on them and put them in a numbered list with no header: {xml}"
    }
    ],
  temperature=0.2,
  max_tokens=256,
  top_p=0.1,
  frequency_penalty=0,
  presence_penalty=0
  )

    return response
def write_questions(concepts, xml_file_path):
    xml = extract_text_from_xml(xml_file_path)
    response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[
      {
        "role": "user",
        "content": f"create a why, what, when or how type question for each concept in list using the xml content: {concepts}{xml}"
      }
      ],
    temperature=0.2,
    max_tokens=500,
    top_p=0.1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response
def generate_answers(question, xml_file_path):
    xml = extract_text_from_xml(xml_file_path)
    response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[
      {
        "role": "user",
        "content": f"generate a short answer for a graduate or undergraduate student using the question {question} and the context {xml}"
      }
      ],
    temperature=0.2,
    max_tokens=500,
    top_p=0.1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response

def gen_ans_df(df):
  context_file = df["File_name"]
  question = df["Questions"]
  try:
    ans = generate_answers(question,context_file)
  except openai.error.RateLimitError:
    time.sleep(65)
    ans = generate_answers(question,context_file)
  except:
    ans = ""
  return(ans["choices"][0]["message"]["content"])

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--context_path",
        type=str,
        required=True,
        default='/content/data',
        help="Context Path for concept/question generation",
    )
    # parser.add_argument(
    #     "--concept_data",
    #     type=str,
    #     required=True,
    #     help="Path to concept data for question generation",
    # )

    args = parser.parse_args()
    context_path = args.context_path
    df_qs_con = pd.DataFrame(columns=["File_name","Concepts","Questions"])
    for filename in glob.glob(os.path.join(context_path, '*.xml')):
      try:

            response = find_keywords(filename)

            concepts = response["choices"][0]["message"]["content"]
            questions = write_questions(concepts, filename)
            ind_q_list = [ind_q[3:]+"?" for ind_q in questions["choices"][0]["message"]["content"].split("?")]

            filen = [filename]*len(ind_q_list)
            conc = [",".join(i[2:] for i in concepts.split("\n"))]*len(ind_q_list)
            df = pd.DataFrame({'File_name': filen,
                            'Concepts': conc,
                            'Questions': ind_q_list})
            df_qs_con = pd.concat([df_qs_con, df], axis=0)
    
      except:
            print("failed",filename)
            continue
    df_qs_con["Short Answer"] = df_qs_con.apply(gen_ans_df,axis=1)
    df_qs_con.to_csv("gpt_QA_generation.csv")




