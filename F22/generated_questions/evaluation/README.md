### GPT-3 Generated Question Classification

File: GPT3_finetune.ipynb
This file demonstrated the method for finetuning a GPT-3 model for generated question classification using the LearningQ dataset (https://github.com/AngusGLChen/LearningQ). User must have access to the OPEN AI API with their own API Key. 

File: GPT3_evaluation.ipynb
This file is used for evaluating questions using the fine-tuned GPT-3 Classification created by GPT3_finetune.ipynb. Data is expected to be in the form of a csv file where the final column contains model generated questions. All questions should end with a ? to match the format of the fine-tuning. 