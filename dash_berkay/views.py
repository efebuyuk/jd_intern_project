from django.shortcuts import render
from django.http import HttpResponse, request, response
# Create your views here.
from tkinter.constants import Y
import pandas as pd
import os
import re

from flask import Flask
from flask import render_template

import plotly.express as px
import pandas as pd

import tkinter as tk
from tkinter import filedialog



def extension_check(extension): #Classifies the file according to the extension of the file.
    if(extension == '.ipynb'):
        name_type = "PYTHON"
    if(extension == '.py'):
        name_type = "PYTHON"
    if(extension == '.R'):
        name_type = "PYTHON"
    if(extension == '.Rmd'):
        name_type = "R"
    if(extension == '.csv'):
        name_type = "CSV" 
    if(extension == '.html'):
        name_type = "HTML" 
    if(extension == '.txt'):
        name_type = "TXT" 

    return name_type

def read_file(file_path): #Reads and returns the content of the files as text.
    with open(file_path, "r") as current_file:
        current_text = current_file.read()
    return current_text

def create_report_python(current_text, file_name, file_type): #Storing all the valuable information about the PYTHON files.
    comment_number = 0
    code_cell_number = 0
    libraries_counter = 0

    report = current_text
    
    code_cells = re.findall('"cell_type": "code"', report) #Code Cells of the file
    code_cell_number = len(code_cells) #Number of Code Cells of the file

    markdown_cells = re.findall('"cell_type": "markdown"', report) #Markdown Cells of the file
    comment_number = len(markdown_cells) #Number of Markdown Cells of the file

    
    #Section to find the dataset used in PYTHON files.
    dataset_used = re.findall('pd.read.*', report)
    dataset_used_string = ''.join(map(str, dataset_used))
    ending = dataset_used_string.find('.csv') + 4
    dataset_used_string = dataset_used_string[:ending]
    dataset_used_string = dataset_used_string.split("/")[-1]
    
    #Section to find the libraries used in PYTHON files.
    libraries = re.findall('import .*\w+', report)
    libraries = ''.join(map(str, libraries))
    libraries = libraries.replace('import', '')
    libraries = libraries.replace('\\n', '')
    libraries = re.sub(' as \S.', '',libraries)
    libraries = libraries.split(' ')
    for number in range(libraries.count('the')):
        libraries.remove('the')
    for number in range(libraries.count('required')):
        libraries.remove('required')
    for number in range(libraries.count('libraries.')):
        libraries.remove('libraries.')
    for number in range(libraries.count('')):
        libraries.remove('')


    for element in libraries:
        libraries_counter +=1
    
    return file_name, file_type, dataset_used_string, report, comment_number, code_cell_number, libraries_counter, libraries

def create_report_r(current_text, file_name, file_type): #Storing all the valuable information about the R files.
    comment_number = 0
    code_cell_number = 0
    libraries_counter = 0

    report = current_text
    
    code_cells = re.findall('```{r', report) #Code Cells of the file
    code_cell_number = len(code_cells) #Number of Code Cells of the file

    comment_cells = re.findall('#', report) #Markdown Cells of the file
    comment_number = len(comment_cells) #Number of Markdown Cells of the file

    #Section to find the dataset used in R files.
    dataset_used = re.findall('read.csv.*', report)
    dataset_used_string = ''.join(map(str, dataset_used))
    ending = dataset_used_string.find('.csv"') + 4
    dataset_used_string = dataset_used_string[:ending]
    dataset_used_string = dataset_used_string.split("/")[-1]

    #Section to find the libraries used in R files.
    libraries = re.findall('library.*', report)
    libraries_list = []
    for element in libraries:
        libraries_list.append(element[8:-1])
        libraries_counter +=1
    libraries = libraries_list

    return file_name, file_type, dataset_used_string, report, comment_number, code_cell_number, libraries_counter, libraries

def open_files(): #Function used in order to select and open all the files you want. Also uses two other functions in order to classify and read the contents of the file
    root = tk.Tk()

    file_paths = filedialog.askopenfilenames() #Opens the file selecter window.

    dataframe_list = [] #Creating a list in order to store all the information gathered by all the files which are selected.

    python_number = 0
    r_number = 0

    for file_path in file_paths:
        file_name, extension = os.path.splitext(file_path)
        file_name = file_name.split("/")[-1] #Take the name of the files selected. (Character '/' should not be used in the name of the files.)

        file_type = extension_check(extension) #Take the type of the files selected.
        print(file_name, file_type)
        
        current_text = read_file(file_path) #Contents of the files are read as text using the read_file() function.

        if(file_type == "PYTHON"):
            file_name, file_type, dataset_used_string, report, comment_number, code_cell_number, libraries_counter, libraries = create_report_python(current_text, file_name, file_type) #Taking and storing all the information about the files of PYTHON.
            print("Name of the dataset:", dataset_used_string, "Number of Comments:", comment_number, "Number of Code Cells:", code_cell_number, "Libraries used:", libraries_counter, libraries)
            python_number +=1

            example_list = [file_name, file_type, dataset_used_string, comment_number, code_cell_number, libraries_counter, libraries] #Storing the information in a list format to make it easy to operate with later on.
            dataframe_list.append(example_list) #Adding the temporary list used by the current file to the cumulative list which will store all information of all the datasets.
        elif(file_type == "R"):
            file_name, file_type, dataset_used_string, report, comment_number, code_cell_number, libraries_counter, libraries  = create_report_r(current_text, file_name, file_type) #Taking and storing all the information about the files of PYTHON.
            print("Name of the dataset:", dataset_used_string, "Number of Comments:", comment_number, "Number of Code Cells:", code_cell_number, "Libraries used:", libraries_counter, libraries)
            r_number +=1

            example_list = [file_name, file_type, dataset_used_string, comment_number, code_cell_number, libraries_counter, libraries] #Storing the information in a list format to make it easy to operate with later on.
            dataframe_list.append(example_list) #Adding the temporary list used by the current file to the cumulative list which will store all information of all the datasets.

    #In order to create dataframe of the files selected using tuples, we store all same category information on different lists.
    list_file_names = [x[0] for x in dataframe_list]
    list_file_types = [x[1] for x in dataframe_list]
    list_file_datasets = [x[2] for x in dataframe_list]
    list_file_comment_numbers = [x[3] for x in dataframe_list]
    list_file_code_numbers = [x[4] for x in dataframe_list]
    list_file_libraries_number = [x[5] for x in dataframe_list]
    list_file_libraries = [x[6] for x in dataframe_list]

    #Use of tuples and zip functions in order to make the data suitable for the the dataframe.
    list_tuples = list(zip(list_file_names, list_file_types, list_file_datasets, list_file_comment_numbers, list_file_code_numbers, list_file_libraries_number, list_file_libraries))
    
    #Creation of the dataframe using the tuple above.
    dataframe = pd.DataFrame(list_tuples, columns=['File Names', 'File Types', 'Dataset Used', 'Comment Numbers', 'Code Numbers', 'Library Numbers', 'Libraries'])
    
    dataframe = dataframe.values.tolist()

    root.destroy()
    return dataframe, python_number, r_number


app = Flask(__name__, template_folder='.../templates')

@app.route("/")
def startapp(request):
    list_file_types_number = [] #First index will be the number of python files, second one R files.
    dataframe, python_number, r_number = open_files()
    list_file_names = [x[0] for x in dataframe]
    list_file_types = [x[1] for x in dataframe]
    list_file_datasets = [x[2] for x in dataframe]
    list_file_comment_numbers = [x[3] for x in dataframe]
    list_file_code_numbers = [x[4] for x in dataframe]
    list_file_libraries_number = [x[5] for x in dataframe]
    list_file_libraries = [x[6] for x in dataframe]
    list_file_types_number.append(python_number)
    list_file_types_number.append(r_number)
    # with app.app_context(), app.test_request_context():
      #  template = render_template("berkay.html", dataframe=dataframe, list_file_names=list_file_names, list_file_types=list_file_types, list_file_datasets= list_file_datasets, list_file_comment_numbers=list_file_comment_numbers, list_file_code_numbers=list_file_code_numbers, list_file_libraries_number=list_file_libraries_number, list_file_libraries=list_file_libraries, list_file_types_number=list_file_types_number)
    # return template

    return render(request, 'berkay.html', {'dataframe':dataframe, 'list_file_names':list_file_names, 'list_file_types':list_file_types, 'list_file_datasets':list_file_datasets, 'list_file_comment_numbers':list_file_comment_numbers, 'list_file_code_numbers':list_file_code_numbers, 'list_file_libraries_number':list_file_libraries_number, 'list_file_libraries':list_file_libraries, 'list_file_types_number':list_file_types_number })

if __name__ == "__main__":
    app.run(debug=True)