from django.shortcuts import render
from django.http import HttpResponse
from collections import Counter
import numpy as np
import pathlib
import re


# Create your views here.
def index(request):
    ipynb_dir = pathlib.Path(r'./yigit/notebooks').glob('*.ipynb')
    ipynb_files = [x for x in ipynb_dir if x.is_file()]

    print('Number of files: ',len(ipynb_files))
    ipynp_array = []
    for ipynb_file in ipynb_files:
        f = open(ipynb_file, "r")

    number_of_csv = 0
    number_of_xlsx = 0
    number_of_json = 0
    total_number_of_markdown_cells = 0
    total_number_of_code_cells = 0
    list_of_libraries = []
    
    for ipynb_file in ipynb_files:
        list_of_datasets = []
        number_of_commends = 0
        number_of_markdown_cells = 0
        number_of_code_cells = 0
        with open(ipynb_file, 'r') as read_obj:
            for line in read_obj:
                if 'import' in line:
                    #print(line)
                    pattern1 = 'import[ X](.*)[ X]as'
                    pattern2 = 'import[ X](.*)\\n",'
                    pattern3 = 'import[ X](.*)"'
                    pattern4 = 'from[ X](?:.*)[ X]import[ X](.*)'
                    if len(re.findall(pattern1,line)) > 0:
                        list_of_libraries.append(re.findall(pattern1,line)[0])
                    elif len(re.findall(pattern2,line)) > 0:
                        list_of_libraries.append(re.findall(pattern2,line)[0])
                    elif len(re.findall(pattern3,line)) > 0:
                        list_of_libraries.append(re.findall(pattern3,line)[0])
                    elif len(re.findall(pattern4,line)) > 0:
                        list_of_libraries.append(re.findall(pattern4,line)[0])
                if '.read_csv' in line:
                    pattern = 'input\/(.*?)\.csv'
                    if len(re.findall(pattern,line)) > 0:
                        list_of_datasets.append(re.findall(pattern,line)[0])
                        number_of_csv+=1
                if '.read_excel' in line:
                    pattern = 'input\/(.*?)\.xlsx'
                    if len(re.findall(pattern,line)) > 0:
                        list_of_datasets.append(re.findall(pattern,line)[0])
                        number_of_xlsx+=1
                if 'open(' in line:
                    pattern = 'input\/(.*?)\.json'
                    if len(re.findall(pattern,line)) > 0:
                        list_of_datasets.append(re.findall(pattern,line)[0])
                        number_of_json+=1
                if '/*' in line:
                    number_of_commends+=1
                if '#' in line:
                    number_of_commends+=1
                if '"cell_type": "markdown",' in line:
                    number_of_markdown_cells+=1
                    total_number_of_markdown_cells+=1
                if '"cell_type": "code",' in line:
                    number_of_code_cells+=1
                    total_number_of_code_cells+=1
        #print(ipynb_file, list_of_datasets,len(list_of_datasets),number_of_commends,number_of_markdown_cells,number_of_code_cells)
        ipynp_array.append([str(ipynb_file), list_of_datasets,len(list_of_datasets),number_of_commends,number_of_markdown_cells,number_of_code_cells])
        print(ipynp_array)
    #message = """<html>
    #    <head></head>
    #    <body>
    #    <p>Number of notebooks analized: """+ str(len(ipynb_files)) +"""</p>
    #    <p>Total number of with csv datasets used in notebooks: """+ str(number_of_csv) +"""</p>
    #    <p>Total number of with xlsx datasets used in notebooks: """+ str(number_of_xlsx) +"""</p>
    #    </body>
    #    </html>"""
    #return message
    dic_of_libraries = Counter(list_of_libraries)

    libraries_keys = list(dic_of_libraries.keys())
    libraries_values = list(dic_of_libraries.values())
    
    mylist = zip(libraries_keys, libraries_values)
    context = {
                'mylist': mylist,
            }
    
    type_of_dataset = [number_of_csv,number_of_xlsx,number_of_json,0]
    type_of_code_cells = [total_number_of_markdown_cells,total_number_of_code_cells]
    print(ipynp_array)
    return render(request, 'yigit.html', {'galaxies':ipynp_array, 'type_of_dataset' :type_of_dataset, 'type_of_code_cells' :type_of_code_cells, 'dic_of_libraries':context })
