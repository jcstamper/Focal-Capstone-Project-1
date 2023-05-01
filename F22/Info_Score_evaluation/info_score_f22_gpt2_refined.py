import pandas as pd

df = pd.read_csv("C:/Users/dell/Desktop/generated_questions/output/f22_short_answer_e2e_qg.csv")
# df=df[:200]
print(df.columns)
import spacy
import numpy as np

nlp = spacy.load('en_core_web_sm')

# Define a function to extract key concepts for a given row
def extract_key_concepts(row):
    text = row['Paragraph']
    if not isinstance(text, str):
        text = ''
        # or raise an exception
    doc = nlp(text) # create a spaCy document from the Text column
    key_concepts = set()
    for token in doc:
        if token.pos_ in ['NOUN', 'VERB', 'ADJ']: # filter out non-important POS tags
            if not token.is_stop: # filter out stop words
                key_concepts.add(token.lemma_) # add the lemma of the token to key_concepts
    return list(key_concepts)

# Define a function to calculate the information score for a given question based on the key concepts
def information_score(question, key_concepts):
    if not isinstance(question, str):
        return 0 # or raise an exception
    tokens = set(question.lower().split()) # extract tokens from the question
    score = 0
    for concept in key_concepts:
        concept_tokens = set(concept)
        num_coincidences = len(tokens.intersection(concept_tokens))
        score += num_coincidences / len(tokens)
    return score

# Apply the extract_key_concepts function to each row and store the results in a new column
df['Key Concepts'] = df.apply(extract_key_concepts, axis=1)

# Apply the information_score function to each question in the Generated Question column and store the results in a new column
df['Information Score'] = df.apply(lambda row: information_score(row['Generated Question'], row['Key Concepts']), axis=1)

print(df.head(5))

df.to_csv('f22_short_answer_e2e_qg_info_score.csv')
