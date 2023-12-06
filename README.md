# Focal
<p align="center">
<img width="440" align= "center" alt="Focal" src="https://github.com/mitali-p42/Focal-Capstone-Project/assets/113000033/e1a7fe39-7fac-4533-9e49-2cd1928dc5bf">
</p>

As education continually trends toward online learning, giving students frequent assessments, both formative and summative, is crucial to their development. These assessments often come at a high price to educators however, as they are forced to create a large bank of questions to provide realistic learning opportunities for students of varied skill levels. In addition to the high cost to produce these assessments, educators likewise must spend a significant amount of time providing students with quality feedback. This feedback helps to ensure the assessments that students are completing enrich their learning experience, but is time consuming to produce. Focal is intended to reduce the burden of these assessments on educators. By automating the assessment creation and evaluation pipeline, educators' time will be freed to focus on their various other responsibilities. 

# Installation
clone:
```
$ git clone https://github.com/mitali-p42/Focal-Capstone-Project.git
$ cd Focal-Capstone-Project
```
create & activate virtual env then install dependency:
with venv/virtualenv + pip:
```
$ python -m venv env  # use `virtualenv env` for Python2, use `python3 ...` for Python3 on Linux & macOS
$ source env/bin/activate  # use `env\Scripts\activate` on Windows
$ pip install -r requirements.txt
```
or with Pipenv:
```
$ pipenv install --dev
$ pipenv shell
```
# Running Pipeline
### Single File:
```
$ export OPENAI_API_KEY="your API key here"
$ cd Pipeline
$ python3 pipeline.py
```
##### Respond to the Following Questions: 

*Questions will be written to a CSV file with the input file name.* 

*Run times:* 

    *No rubric, overall question evaluation only (~5 min. per file)* 

    *Full rubric with overall question evaluation (~15-20 min. per file)*
<p align="center">
<img width="650" alt="questions2" src="https://github.com/mitali-p42/Focal-Capstone-Project/assets/95736002/caf9eb01-ef3f-4892-8fd5-cc3e06f80680">
</p>


### Multiple Files
```
$ export OPENAI_API_KEY="your API key here"
$ cd Pipeline
$ python3 pipeline_directory.py
```
##### Respond to the Following Questions:

*A question csv file will be created for each file in the input directory path. Filenames will be in the format {original filename}_questions.csv*

*Run times:* 

    *No rubric, overall question evaluation only (~5 min. per file)* 
  
    *Full rubric with overall question evaluation (~15-20 min. per file)*
<p align="center">
<img width="650" alt="questions" src="https://github.com/mitali-p42/Focal-Capstone-Project/assets/95736002/567c4d44-2d48-4504-9414-9232eac891d5">
</p>

