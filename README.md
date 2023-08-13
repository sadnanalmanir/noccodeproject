# NOCCodeProject

ACA-NOC: Development of an Automated Coding Algorithm for the Canadian National Occupation 
Classification

## Abstract

### Background

In many research studies examining social determinants is important, occupational information is often needed to augment existing data sets. Such information is usually solicited during interviews with open-ended questions, like “what is your job?” and “what industry sector do you work in?” Before being able to use this information for further analysis, the responses need to be categorized using a coding system, like the Canadian National Occupational Classification (NOC).  Manual coding is the usual method, which is a time-consuming and error prone activity, suitable for automation. 

### Objective
To facilitate automated coding we proposed to introduce a rigorous algorithm that is able to identify the NOC (2016) codes using only a job title and industry information as input. Using manually coded data sets we sought to benchmark and iteratively improve the performance of the algorithm. 

### Methods
We developed the ACA-NOC (Automated Coding Algorithm for the Canadian National Occupation Classification) algorithm, based on the National Occupational Classification (NOC) 2016, which allows users to match NOC codes with job titles and industry titles. We employed several different search strategies in the ACA-NOC algorithm to find the best match, including: Exact Search, Minor Exact Search, Like Search, Near (same order) Search, Near (different order) Search, Any Search, and Weak Match Search. In addition a filtering step based on the hierarchical structure of the NOC data was applied in the algorithm to select the best matching codes.

### Results
ACA-NOC was applied to over 500 manually coded job titles and industry titles. The accuracy rate at the 4-digit NOC code level was 58.66% and improved when broader job-categories were considered (65.01% at the 3-digit NOC code level, 72.26% at the 2-digit NOC code level, 81.63% at the 1-digit NOC code level).

### Conclusions
ACA-NOC is a rigorous algorithm for automatically coding to the Canadian National Occupational Classification system, and has been evaluated using real world data. It allows researchers to code moderate sized data sets with occupation in a timely and cost-efficient manner, so that further analytics are possible. Initial assessments indicate it has state of the art performance and is readily extensible upon further benchmarking on larger data sets.

---

## Project Structure
* The program is coded in python 3.x. Check out https://docs.anaconda.com/anaconda/install/ for installation.
* The `data` directory contains the input data file in a spreadsheet.
* There are three python scripts in `src` directory named `preprocess.py`, `NOC_Code_Auto.py` and `result_analysis.py`.
    1. The preprocessing step
        - either replaces the `Current Job Title` with the `Preferred Job Title` if there is no `Current Industry` specified for that `Current Job Title`. This happens when `no_replace_if_industry_exist = True`.
        - or replaces the `Current Job Title` with the `Preferred Job Title` regardless of `Current Industry` specified for that `Current Job Title`. This happens when `no_replace_if_industry_exist = False`.
    2. `NOC_Code_Auto.py` will generate the NOC Codes in a CSV file called `title_noc_result_byprogram.csv`
    3. `result_analysis.py` will analyse this generated CSV file and print the results of the analysis.
* The Canadian National Occupational Classification (NOC) comprises more than 30,000 occupational titles 
gathered into 500 Unit Groups, organized according to 4 skill levels and 10 skill types. Unit Groups 
are based on similarity of skills, defined primarily by functions and employment requirements. 
Each Unit Group describes main duties and employment requirements as well as detailing examples 
of occupational titles. Each unit group has a unique four-digit code. The first three digits of 
this code indicate the major and minor groups to which the unit group belongs.
    - NOC-2016 is organized in a four level hierarchy, and there are 10 broad occupational categories 
    (first level), 46 major groups (second level), 140 minor groups (third level), and 
    500 unit groups (fourth level).
    - The `resources` directory contains 5 files illustrating such organizations based on NOC-2016. 
    - The `data` directory contains 2 files: `preprocessing_candidates.xlsx` spreadsheet listing the candidates to process and `NOC-spreadsheet.xlsx` as the input data.
```bash
.
+-- src
    +-- preprocess.py
    +-- NOC_Code_Auto.py
    +-- result_analysis.py 
+-- resources
    +-- nocjobtitle.txt
    +-- noc_data_get_byws_dealing_slash.csv
    +-- NOC_skilltype.csv
    +-- NOC_majorgroup.csv
    +-- NOC_minorgroup.csv 
+-- data
    +-- preprocessing_candidates.xlsx
    +-- NOC-spreadsheet_BACKUP.xlsx 
    +-- NOC-spreadsheet.xlsx
+-- README.md
```

## How to run

Go to the project directory:
```bash
$ cd /path/to/noccodeproject
```
---
### Step-1: 

#### Settings for preprocess.py
---
A sample file `NOC-spreadsheet_BACKUP.xlsx` is provided with existing data. Rename it to `NOC-spreadsheet.xlsx` if it does not exist.

Based on the recommended job titles and industries, this step will replace the `Current Job Title` and `Current Industry` inside `NOC-spreadsheet.xlsx`.

Two input files are required:

1.  `DATA_FILE = NOC-spreadsheet.xlsx` containing spreadsheets with column headers `Participant ID`, `Current Job Title`, `Current Industry`, and `NOC code`.
2.  `PREPROCESS_CANDIDATE_FILE = preprocessing_candiadates.xlsx` containing two spreadsheets: 
    - one with column headers `Current Job Title`, `Preferred Job Title`, and `Preferred NOC code`.
    - another with column headers `Current Industry`, `Preferred  Industry`, and  `Preferred NOC code`.
3. Set the flag `no_replace_if_industry_exist = True`. The default is set to be `True`.

For each spreadsheet `NAME_OF_THE_SHEET` in `NOC-spreadsheet.xlsx`, a new `p_NAME_OF_THE_SHEET` will be generated only if a match exists.

---
#### Run preprocess.py

Execute the following command:
```bash
$ python src/preprocess.py
```
Open `NOC-spreadsheet.xlsx` and review the spreadsheets titled `p_NAME_OF_THE_SHEET` to view the results of the preprocessing step.

---
### Step-2

#### Settings for NOC_Code_Auto.py
---
The source data is an Excel file titled `NOC-spreadsheet.xlsx` which contains specific column-headers in no specific order: `Participant ID`, `Current Job Title`, `NOC code`, and `Current Industry`.

#### Run NOC_Code_Auto.py with preprocessed data
---
Edit `NOC_Code_Auto.py` and set `SHEET_TITLE = p_Janitors` to run on the processed `Janitors` spreadsheet.

Run  `NOC_Code_Auto.py` using the following command:
```bash
$ python NOC_Code_Auto.py
```

#### Run NOC_Code_Auto.py with fresh data
--- 
Alternatively, create `NOC-spreadsheet.xlsx` file with the columns:
* Column-1 header: `Participant ID`
* Column-2 header: `Current Job Title`
* Column-3 header: `NOC code`
* Column-4 header: `Current Industry`

Populate the spreadsheet with data.
* When records along the `Current Industry` is left empty, the algorithm only considers Current Job Title.
* `NOC code` cannot be left empty because `result_analysis.py` requires these codes to run the analysis.

Run  `NOC_Code_Auto.py` using the following command:
```bash
$ python NOC_Code_Auto.py
```
---
The results are generated in `title_noc_result_byprogram.csv` file


### Step-3

Run python `result_analysis.py` to analyze the precision of automated coding:
```bash
$ python result_analysis.py
```
---
---
## Run with docker-compose

Install Docker and docker compose. For more information, see [Docker](https://docs.docker.com/get-docker/) and [docker desktop](https://docs.docker.com/desktop/install/windows-install/).

Go to the project directory:
```bash
$ cd /path/to/noccodeproject
```

To run  `preprocess.py`, edit `Dockerfile` and enable the line `CMD [ `"python"`, `"./src/preprocess.py"` ]` by removing `#`, and run the following commands: 
```bash
$ docker compose build
$ docker compose up
```

To run  `NOC_Code_Auto.py`, edit `Dockerfile` and enable the line `CMD [ `"python"`, `"./src/NOC_Code_Auto.py"` ]` by 
removing `#`, and run the following commands: 
```bash
$ docker compose build
$ docker compose up
```
To run  `result_analysis.py`, edit `Dockerfile` and enable the line `CMD [ `"python"`, `"./src/result_analysis.py"` ]` by 
removing `#`, and run the following commands:
```bash
$ docker compose build
$ docker compose up
```