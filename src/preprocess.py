import os
import pandas as pd
from openpyxl import load_workbook
from pyprojroot import here

'''
This program expects 
1. a DATA_FILE in excel containing column headers: Participant ID, Current Job Title, Current Industry, NOC code in no 
particular order
2. a preprocessing file PREPROCESS_CANDIDATE_FILE with two sheets where:
One sheet contains column headers: Current Job Title, Preferred Job Title, Preferred NOC code
The other contains column headers: Current Industry, Preferred Industry, Preferred NOC code
For each sheet with the expected column headers, the program generates and adds a processed sheet with a prefix p_ in 
the DATA_FILE. 
The option 'no_replace_if_industry_exist = True' , when set, only replaces the 'Current Job Title' if there is no 
'Current Industry' assigned for that Job Title. Setting 'False' replaces even if there is an assigned Current Industry.
'''

# project directory
#os.chdir(r'/home/sadnan/work/unb/noccodeproject-master/')

# Excel Data file to pre-process. Pre-processing involves creating a new Sheet from a current sheet
# DATA_FILE = 'data/v_0_6/NOC-NAICS-coded.xlsx'


DATA_FILE = here() / 'data' / 'NOC-spreadsheet.xlsx'

# Exeel file where the candidates for Current Job Title, Current Industry are tabulated
# PREPROCESS_CANDIDATE_FILE = 'data/v_0_6/preprocessing_candidates.xlsx'


PREPROCESS_CANDIDATE_FILE = here() / 'data' / 'preprocessing_candidates.xlsx'

# Replace Current Job Title only if there is NO Current Industry assigned (True), replace (False)
no_replace_if_industry_exist = True

# Ensures these column headers are present before preprocessing
data_file_col_headers = ['Current Job Title', 'Current Industry', 'NOC code']
cand_jobtitle_col_headers = ['Current Job Title', 'Preferred Job Title', 'Preferred NOC code']
cand_industry_col_headers = ['Current Industry', 'Preferred Industry', 'Preferred NOC code']

# writer = pd.ExcelWriter(DATA_FILE, engine='xlsxwriter') #wipes out existing sheet, overwrites

# Keeps adding new sheets to the processed EXCEL file rather than replacing
book = load_workbook(DATA_FILE)
print(book)

writer = pd.ExcelWriter(DATA_FILE, engine='openpyxl')
writer.book = book



def preprocess_jobtitle_sheet(df_excel, df_preprocess_jobtitle, exist_current_industry):
    '''
    Replace Current Job Title with the Preferred Job Title from a separate Sheet of candidates.
    Currently, replacement occurs if there is no Current Industry for the title to be replaced.
    Also replace NOC code with the Preferred NOC code, if it is different from the original.
    '''
    df_excel_processed = df_excel.copy()
    num_rows_processed = 0
    for i in range(len(df_preprocess_jobtitle)):
        prepr_current_job_title = df_preprocess_jobtitle.loc[df_preprocess_jobtitle.index[i], 'Current Job Title'].lower()
        prepr_preferred_job_title = df_preprocess_jobtitle.loc[df_preprocess_jobtitle.index[i], 'Preferred Job Title'].lower()
        prepr_preferred_noc_code = df_preprocess_jobtitle.loc[df_preprocess_jobtitle.index[i], 'Preferred NOC code'].lower()
        for j in range(len(df_excel)):
            if prepr_current_job_title == df_excel.loc[df_excel.index[j], 'Current Job Title'].lower():
                if exist_current_industry:  # current industry exists
                    if df_excel.loc[df_excel.index[j], 'Current Industry']:  # not empty
                        print('[JobTitle] Replacing row ', (j+1), ': ', df_excel.loc[df_excel.index[j], 'Current Job Title'], ' => ', prepr_preferred_job_title)
                        df_excel_processed.loc[df_excel_processed.index[j], 'Current Job Title'] = prepr_preferred_job_title
                        if df_excel_processed.loc[df_excel_processed.index[j], 'NOC code']:  # not empty
                            if df_excel_processed.loc[df_excel_processed.index[j], 'NOC code'] != prepr_preferred_noc_code:
                                print('Replacing: NOC code',
                                      df_excel_processed.loc[df_excel_processed.index[j], 'NOC code'],
                                      ' == Preferred NOC code ==> ', prepr_preferred_noc_code)
                                df_excel_processed.loc[df_excel_processed.index[j], 'NOC code'] = prepr_preferred_noc_code
                        num_rows_processed += 1
                else:
                    print('[JobTitle] Replacing row ', (j + 1), ': ',
                          df_excel.loc[df_excel.index[j], 'Current Job Title'], ' => ', prepr_preferred_job_title)
                    #print(df_excel_processed.loc[df_excel_processed.index[j], 'Current Job Title'])
                    df_excel_processed.loc[df_excel_processed.index[j], 'Current Job Title'] = prepr_preferred_job_title
                    #print(df_excel_processed.loc[df_excel_processed.index[j], 'Current Job Title'])
                    if df_excel_processed.loc[df_excel_processed.index[j], 'NOC code']:
                        if df_excel_processed.loc[df_excel_processed.index[j], 'NOC code'] != prepr_preferred_noc_code:
                            print('Replacing: NOC code', df_excel_processed.loc[df_excel_processed.index[j], 'NOC code'], ' == Preferred NOC code ==> ', prepr_preferred_noc_code)
                            df_excel_processed.loc[df_excel_processed.index[j], 'NOC code'] = prepr_preferred_noc_code
                    num_rows_processed += 1

    return num_rows_processed, df_excel_processed


def preprocess_industry_sheet(df_excel, df_preprocess_industry):
    '''
    Replace Current Industry with the Preferred Industry from a separate Sheet of candidates.
    Also replace NOC code with the Preferred NOC code, if it is different from the original.
    '''
    df_excel_processed = df_excel.copy()
    num_rows_processed = 0
    for i in range(len(df_preprocess_industry)):
        prepr_current_industry = df_preprocess_industry.loc[df_preprocess_industry.index[i], 'Current Industry'].lower()
        prepr_preferred_industry = df_preprocess_industry.loc[df_preprocess_industry.index[i], 'Preferred Industry'].lower()
        prepr_preferred_noc_node = df_preprocess_industry.loc[df_preprocess_industry.index[i], 'Preferred NOC code'].lower()
        for j in range(len(df_excel)):
            if prepr_current_industry == df_excel.loc[df_excel.index[j], 'Current Industry'].lower():
                print('[Industry] Replacing row ', (j + 1), ': ', df_excel.loc[df_excel.index[j], 'Current Industry'], ' => ',
                      prepr_preferred_industry)
                df_excel_processed.loc[df_excel_processed.index[j], 'Current Industry'] = prepr_preferred_industry
                if df_excel_processed.loc[df_excel_processed.index[j], 'NOC code']:
                    if df_excel_processed.loc[df_excel_processed.index[j], 'NOC code'] != prepr_preferred_noc_node:
                        df_excel_processed.loc[df_excel_processed.index[j], 'NOC code'] = prepr_preferred_noc_node
                num_rows_processed += 1

    return num_rows_processed, df_excel_processed


def preprocess(DATA_FILE, PREPROCESS_CANDIDATE_FILE, exist_current_industry):
    '''
    Traverses each rows in each Sheet of the data file and replaces Current Job Title, Current Industry, NOC code
    based on the if they are candidates present in the candidate file
    '''
    num_jobtitle_processed = 0
    num_industry_processed = 0

    data_file_sheet_names = pd.ExcelFile(DATA_FILE).sheet_names
    prepr_cand_file_sheet_names = pd.ExcelFile(PREPROCESS_CANDIDATE_FILE).sheet_names
    print('Data Sheet Names: ', data_file_sheet_names)
    print('Preprocessing Sheet Names: ', prepr_cand_file_sheet_names)

    for data_file_sheet_name in data_file_sheet_names:
        print('\nProcessing Sheet: ', data_file_sheet_name)
        if all(df_col_header in pd.read_excel(DATA_FILE, sheet_name=data_file_sheet_name, header=0).columns.ravel() for df_col_header in data_file_col_headers):
            df_excel = pd.read_excel(DATA_FILE, sheet_name=data_file_sheet_name, header=0,
                                     converters={'NOC code': str, 'Current Job Title': str, 'Current Industry': str},
                                     na_filter=False)
            for prepr_cand_file_sheet_name in prepr_cand_file_sheet_names:
                if all(cj_col_header in pd.read_excel(PREPROCESS_CANDIDATE_FILE, sheet_name=prepr_cand_file_sheet_name, header=0).columns.ravel() for cj_col_header in cand_jobtitle_col_headers):
                    df_preprocess_jobtitle = pd.read_excel(PREPROCESS_CANDIDATE_FILE, sheet_name=prepr_cand_file_sheet_name, header=0,
                                                  converters={'Current Job Title': str, 'Preferred Job Title': str,
                                                              'Preferred NOC code': str},
                                                  na_filter=False)


                    num_jobtitle_processed, df_result_sheet = preprocess_jobtitle_sheet(df_excel, df_preprocess_jobtitle, exist_current_industry)
                    #if num_jobtitle_processed > 0:
                    #    processed_jobtitle_sheet.to_excel(writer, sheet_name='p_' + data_file_sheet_name, index=False)
                    #else:
                    #    print('Number of rows processed: ', num_jobtitle_processed)

                if all(ci_col_header in pd.read_excel(PREPROCESS_CANDIDATE_FILE, sheet_name=prepr_cand_file_sheet_name, header=0).columns.ravel() for ci_col_header in cand_industry_col_headers):
                    df_preprocess_industry = pd.read_excel(PREPROCESS_CANDIDATE_FILE, sheet_name=prepr_cand_file_sheet_name, header=0,
                                                           converters={'Current Industry': str,
                                                                       'Preferred Industry': str,
                                                                       'Preferred NOC code': str},
                                                           na_filter=False)
                    num_industry_processed, df_result_sheet = preprocess_industry_sheet(df_result_sheet, df_preprocess_industry)
                    #if num_industry_processed > 0:
                    #    processed_industry_sheet.to_excel(writer, sheet_name='p_' + data_file_sheet_name, index=False)
                    #else:
                    #    print('Number of rows processed: ', num_industry_processed)

            if num_jobtitle_processed + num_industry_processed > 0:
                print('Job Title replaced: ', num_jobtitle_processed)
                print('Industry replaced: ', num_industry_processed)
                df_result_sheet.to_excel(writer, sheet_name='p_' + data_file_sheet_name, index=False)
            else:
                print('No items were replaced during preprocessing steps')

        else:
            print('Sheet cannot be processed due to incompatible column headers')

    writer.save()



preprocess(DATA_FILE, PREPROCESS_CANDIDATE_FILE, no_replace_if_industry_exist)

writer.close()