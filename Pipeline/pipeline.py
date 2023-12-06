import openai
from xml.etree import ElementTree as ET
import os, glob
import pandas as pd
import argparse
import time
import re 

openai.api_key = os.getenv('OPENAI_API_KEY') #Replace with your openAI API key

def extract_text_from_xml(filename):
    with open(filename, 'rb') as f:
        xml_bytes = f.read()
        xml_str = xml_bytes.decode('UTF-8')
        # Extract text from <p> tags
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', xml_str, re.DOTALL)
        return(" ").join(paragraphs)
    
def extract_concepts(file_text, course_type="data science"):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
    {
      "role": "user",
      "content": f"extract key concepts from the following text such that we can assess {course_type} knowledge based on them and put them in a numbered list with no header: {file_text}"
    }
        ],
        temperature=0.2,
        max_tokens=256,
        top_p=0.1,
        frequency_penalty=0,
        presence_penalty=0
    )
    concepts = response["choices"][0]["message"]["content"]
    return [",".join(i[2:] for i in concepts.split("\n"))], concepts

def write_questions(concepts, file_text):
    response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[
      {
        "role": "user",
        "content": f"create a why, what, when or how type question for each concept in list using the text content: {concepts}{file_text}"
      }
      ],
    temperature=0.2,
    max_tokens=500,
    top_p=0.1,
    frequency_penalty=0,
    presence_penalty=0
    )
    questions = response["choices"][0]["message"]["content"]
    return [ind_q[3:]+"?" for ind_q in response["choices"][0]["message"]["content"].split("?")][:-1], questions

def evaluate_questions(questions, concepts, full_rubric=False, course_type="data science"):
    results = []

    iwfs = [{"criteria": "gramatical accuracy",
        "definition": "question text is grammatically accurate and logical to reader"},
        {"criteria": "ambiguous or unclear information ",
        "definition": "questions is written in clear, unambiguous language. It is clear what is being asked and what is expected in the answer"}, 
        {"criteria": "gratuious information",
        "definition": "avoids unnecessary information in the stem that is not required to answer the question"}, 
        {"criteria": "pedagogical value",
        "definition": "question is of educational value to students in a data science course"}, #update to reflect course you are interested in
        {"criteria": "covers key concept",
        "definition": "question relates closely to an identified key concept for the given block of text"},
        ]
    done = False
    error_counter = 0

    if full_rubric:
        for i in iwfs:
            #Run this as a while loop with error handling code, as sometimes the GPT-4 API goes down, returning an error, in which 
            #we'll need to wait and retry our call
            while(done == False):
                try:
                    o = openai.ChatCompletion.create(
                    model="gpt-4", 
                    messages=[
                        {"role": "user", "content": f'Begin your response with yes or no, does this question satisfy the criteria relating to {i["criteria"]}: {i["definition"]}? Explain why. {q}'},
                    ],
                    max_tokens=100
                    )
                    time.sleep(1)
                    done = True 
                except Exception as e:
                    error_counter += 1
                    print(f'Error: {error_counter}, Message: {str(e)}')
                    time.sleep(15)
            done = False
            results.append(o)
        while(done == False):
            try:
                o = openai.ChatCompletion.create(
                model="gpt-4", 
                messages=[
                    {"role": "user", "content": f'Start your answer with the concept. Given this list of concepts: {concepts}, which is most closely related, if any, to this question: {q}'},
                    ],
                    max_tokens=100
                )
                time.sleep(1)
                done = True 
            except Exception as e:
                error_counter += 1
                print(f'Error: {error_counter}, Message: {str(e)}')
                time.sleep(15)
        done = False
        results.append(o)
        while(done == False):
            try:
                o = openai.ChatCompletion.create(
                model="gpt-4", 
                #update with current course selection
                messages=[
                    {"role": "user", "content": f'Begin your response with either good, fair, or poor, how well is this question written for testing a students understanding in a {course_type} course. Explain why. {q}'},
                    ],
                    max_tokens=100
                )
                time.sleep(1)
                done = True 
            except Exception as e:
                error_counter += 1
                print(f'Error: {error_counter}, Message: {str(e)}')
                time.sleep(15)
        done = False
        results.append(o)
        rows = []
        r = []
        indz = 0
        for res in results :
            try:
                r.append(res.choices[0].message.content)
            except:
                r.append(res)
        
            #Once we've created a row, r, that contains the question text and criteria, append it to our greater rows list
            if indz == 1:
                rows.append(r)
                r = []
                indz = 0
            else:
                indz = indz + 1


        columns = [
            'question',
            'gramatical_accuracy',
            'ambiguous_or_unclear',
            'gratuitous_information',
            'pedagogical_value',
            'covers_key_concept',
            'concept_covered',
            'question_grade'
            ]
        pd_results = pd.DataFrame(rows, columns=columns)
        return pd_results
    else:
        for q in questions:
            while(done == False):
                try:
                    o = openai.ChatCompletion.create(
                    model="gpt-4", 
                    #update with current course selection
                    messages=[
                        {"role": "user", "content": f'Begin your response with either good, fair, or poor, how well is this question written for testing a students understanding in a {course_type} course. Explain why. {q}'},
                        ],
                        max_tokens=100
                    )
                    time.sleep(1)
                    done = True 
                except Exception as e:
                    error_counter += 1
                    print(f'Error: {error_counter}, Message: {str(e)}')
                    time.sleep(1)
            done = False
            grade = o["choices"][0]["message"]["content"]
            if grade.startswith('Good') or grade.startswith('Fair') or grade.startswith('Poor'):
                results.append(grade[0:4])
            else:
                results.append("Error")
    return results

def generate_answers(questions, file_text):
  answers = []
  done = False
  for q in questions:
    while(done == False):
      try:
        o = openai.ChatCompletion.create(
        model="gpt-4", 
        #update with current course selection
        messages=[
        {
          "role": "user",
          "content": f"generate a short answer for a graduate or undergraduate student using the question {q} and the context {file_text}"
        }
        ],
        temperature=0.2,
        max_tokens=500,
        top_p=0.1,
        frequency_penalty=0,
        presence_penalty=0
        )
        time.sleep(1)
        done = True 
      except Exception as e:
        error_counter += 1
        print(f'Error: {error_counter}, Message: {str(e)}')
        time.sleep(1)
    done = False
    answer = o["choices"][0]["message"]["content"]
    answers.append(answer)
  return answers

def create_file(input_file_path, questions, answers, concepts, reviews, output_file_path):
    df = pd.DataFrame({'Question':questions, 'Question Evaluation':reviews, 'Answer': answers, 'Concepts':[concepts]*len(answers), 'Original File':input_file_path})
    df = df[df['Question Evaluation']!='Poor']
    df.to_csv(output_file_path)

def main():
    print(" ____   ____   ____   ____   __")
    print("|  __| |    | |  __| |    | |  |")
    print("| |__  | |  | | |    | |  | |  |")
    print("|  __| | |  | | |    |    | |  |")
    print("| |    | |  | | |__  | |  | |  |__")
    print("|_|    |____| |____| |_|__| |_____|")
    filename = input("Please enter filepath you would like questions for: ")
    course_type = input("What is the primary domain of this course text?: ")
    file_text = extract_text_from_xml(filename)
    print("*****Text Extracted*****")
    print("*****Extracting Concepts*****")
    concepts, concepts_for_print = extract_concepts(file_text, course_type)
    print(f'Extracted Key Concepts: \n{concepts_for_print}')
    print("*****Generating Questions*****")
    questions, questions_for_print = write_questions(concepts, file_text)
    print(f'Generated Questions Concepts: \n{questions_for_print}')
    print("*****Evaluating Questions*****")
    reviews = evaluate_questions(questions, concepts, course_type=course_type)
    print("*****Question Evaluation Successful*****")
    print("*****Generating Answers*****")
    answers = generate_answers(questions, file_text)
    print("*****Answer Generation Successful*****")
    output_path = input("Please write the name of the file you would like to write these questions to: ")
    create_file(filename, questions, answers, concepts, reviews, output_path)
    print("*****File Written Successfully*****")

if __name__ == "__main__":
    main()