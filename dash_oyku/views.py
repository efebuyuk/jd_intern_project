from django.shortcuts import render
from django.http import HttpResponse

import pandas as pd
from os import listdir
from os.path import isfile, join
import re
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import plotly
from plotly.subplots import make_subplots
from .models import notebook
from django.db import connection
import urllib, json


an_files = [f for f in listdir("data") if isfile(join("data", f))]
route = ["data/" + sub for sub in an_files]
read_list = [open(route[x], encoding="utf8") for x in range(len(route))]
read_list = [x.read() for x in read_list]
read_list = [x.replace("false", "False") for x in read_list]
read_list = [x.replace("true", "True") for x in read_list]
read_list = [x.replace("null", "None") for x in read_list]
ntb_list = [eval(x) for x in read_list]# ntb_list is the list of notebooks in dict form

cell_count = [len(x["cells"]) for x in ntb_list]

# getting code cells
def find_code_cells(s):
    return [x for x in s["cells"] if x["cell_type"] == "code"]


ntb_list_code = list(map(find_code_cells, ntb_list))

code_cell_count = [len(x) for x in ntb_list_code]

an_files = [re.sub('.ipynb',"", x) for x in an_files]

# id creation
for x in range(len(ntb_list)):
    ntb_list[x]["id"] = x

for x in range(len(ntb_list_code)):
    ntb_list_code[x].insert(0, x)

# python code selection
re_is_python = re.compile(r'pd.read_')
is_python = [x[0] for x in ntb_list_code for y in range(1,len(x)) for z in x[y]["source"] if re_is_python.search(z) != None]

# function to get unique values
def unique(list1):
    x = np.array(list1)
    return(np.unique(x))

is_python = unique(is_python)
is_r = range(len(ntb_list_code))
is_r = [item for item in is_r if item not in is_python]

for x in is_python:
    ntb_list_code[x].insert(1, "python")
for x in is_r:
    ntb_list_code[x].insert(1, "r")

df_code = pd.DataFrame(ntb_list_code)

# package list for python
pklf = open("dash_oyku/package_list.txt", "r")
package_list=[]
for line in pklf:
  stripped_line = line.strip()
  package_list.append(stripped_line)
pklf.close()

# libraries
def reg_apply(r, x):
    return [a["source"] for a in x if a != None and r.search(str(a["source"])) != None]
def reg_sub_apply(r, x):
    return [re.sub(r,"", a) for a in x]
def pull(r, x):
    return [r.search(i[a]).group() for i in x for a in range(len(i)) if r.search(i[a]) != None]
def is_exist(real, x):
    imports_as_set = set(x)
    intersection = imports_as_set.intersection(real)
    intersection_as_list = list(intersection)
    return intersection_as_list
def out(x, r):
    return [a for a in x if r.search(a) == None]

# python libraries
regimport = re.compile(r'from.[^ \t\n\r\f\v.]*|import.[^ \t\n\r\f\v.]*')
libpy =  df_code[df_code[1]=="python"].iloc[:,2:].apply(lambda x: reg_apply(regimport, x), axis=1)
libpy = libpy.apply(lambda x: pull(regimport, x))
libpy = pd.DataFrame({"id":df_code[df_code[1]=="python"][0], "library": libpy})
libpy["library"] = libpy["library"].apply(lambda x: reg_sub_apply('import|from| ', x))
libpy["library"] = libpy["library"].apply(lambda x: is_exist(package_list, x))

# r libraries
regimport = re.compile(r'library\([^ \t\n\r\f\v]*\)')
libr =  df_code[df_code[1]=="r"].iloc[:,2:].apply(lambda x: reg_apply(regimport, x), axis=1)
libr = libr.apply(lambda x: pull(regimport, x))
libr = libr.apply(lambda x: reg_sub_apply('library|\(|\)', x))
libr = pd.DataFrame({"id":df_code[df_code[1]=="r"][0], "library": libr})

# used datasets
regdataset = re.compile(r'read[^ \t\n\r\f\v]*\(.*\)|.*/kaggle/input/[^ \t\n\r\f\v]*/"|.*/kaggle/input/[^ \t\n\r\f\v]*/\'')
datasets =  df_code.iloc[:,2:].apply(lambda x: reg_apply(regdataset, x), axis=1)
datasets = datasets.apply(lambda x: pull(regdataset, x))
datasets = datasets.apply(lambda x: reg_sub_apply('read[^ \t\n\r\f\v]*\([^ \t\n\r\f\v]*/input/|"|\'|\)|,.*\)|.* = \'/kaggle/input/', x))
datasets = pd.DataFrame({"id":df_code[0], "dataset": datasets})
datasets["dataset"] = datasets["dataset"].apply(lambda x: out(x, re.compile(r'(.*os.path.join.*)')))


ntb_data = pd.DataFrame({"id": range(len(an_files)), "name": an_files, "cell_count": cell_count,
 "code_cell_count": code_cell_count, "language": df_code[1]})

# funtions used
refunc = re.compile(r'[^ \t\n\r\f\v=\.\"\'-]*\(.*\)|[^ \t\n\r\f\v=\.\"\'-]*\(\)')
functions =  df_code.iloc[:,2:].apply(lambda x: reg_apply(refunc, x), axis=1)
functions = functions.apply(lambda x: pull(refunc, x))
functions = functions.apply(lambda x: reg_sub_apply('\(.*\)| |[.*]|\"[a-zA-Z0-9_\']*\"|\[|\]', x))
functions = pd.DataFrame({"id":df_code[0], "function": functions})

# opening lists
def open_list(df, column):
    return pd.DataFrame({
        col:np.repeat(df[col].values, df[column].str.len())
        for col in df.columns.difference([column])
    }).assign(**{column:np.concatenate(df[column].values)})[df.columns.tolist()]

nlibr = open_list(libr, "library")
nlibpy = open_list(libpy, "library")
ndatasets = open_list(datasets, "dataset")

ndatasets = ndatasets.groupby(["dataset"]).count().reset_index().rename(columns={'id': 'value'}).sort_values(["value"],ascending=False)
ndatasets = ndatasets.iloc[:10]

#create a full dataset for displaying
fun1 = open_list(functions.merge(ntb_data[["language", "id"]]), "function")
fun1 = fun1[fun1.function != ""]
fun1 = fun1.groupby("id")["function"].apply(list).reset_index(name='function')
libs = libpy.append(libr)
full_set = ntb_data.merge(datasets, on='id')
full_set = full_set.merge(fun1, on='id')
full_set = full_set.merge(libs, how='left', on='id').iloc[:,1:]

def horizontal_bar_labels(categories):
    subplots = make_subplots(
        rows=len(categories),
        cols=1,
        subplot_titles=[x["dataset"] for x in categories],
        shared_xaxes=True,
        print_grid=False,
        vertical_spacing=(0.45 / len(categories)),
    )
    subplots['layout'].update(
        width=550,
        plot_bgcolor='#fff',
    )

    # add bars for the categories
    for k, x in enumerate(categories):
        subplots.add_trace(dict(
            type='bar',
            orientation='h',
            y=[x["dataset"]],
            x=[x["value"]],
            text=["{:,.0f}".format(x["value"])],
            hoverinfo='text',
            textposition='auto',
            marker=dict(
                color="#A3BCB6",
                ),
        ), k+1, 1)

    # update the layout
    subplots['layout'].update(
        showlegend=False,
    )
    for x in subplots["layout"]['annotations']:
        x['x'] = 0
        x['xanchor'] = 'left'
        x['align'] = 'left'
        x['font'] = dict(
            size=12,
        )

    # update the margins and size
    subplots['layout']['margin'] = {
        'l': 0,
        'r': 0,
        't': 20,
        'b': 1,
    }
    for axis in subplots['layout']:
        if axis.startswith('yaxis') or axis.startswith('xaxis'):
            subplots['layout'][axis]['visible'] = False
    height_calc = 25 * len(categories)
    height_calc = max([height_calc, 350])
    subplots['layout']['height'] = height_calc
    subplots['layout']['width'] = 500

    return subplots

full_set_store = full_set
full_set_store["dataset"] = [json.dumps(x) for x in full_set_store["dataset"]]
full_set_store["function"] = [json.dumps(x) for x in full_set_store["function"]]
full_set_store["library"] = [json.dumps(x) for x in full_set_store["library"]]

query_results = notebook.objects.all()


if(len(query_results)==0):
# Iterate through all the data items
    for i in range(len(full_set_store)):
            # Insert in the database
        notebook.objects.create(name = full_set_store.iloc[i,:]["name"], cell_count = full_set_store.iloc[i,:]["cell_count"],
        code_cell_count = full_set_store.iloc[i,:]["code_cell_count"], language = full_set_store.iloc[i,:]["language"], 
        dataset = full_set_store.iloc[i,:]["dataset"], function = full_set_store.iloc[i,:]["function"],
        library = full_set_store.iloc[i,:]["library"])
elif(len(full_set_store) != len(query_results)):
    names = [item.name for item in query_results]
    existing = is_exist(full_set_store["name"], names)
    for i in range(len(full_set_store)):
        
        if is_exist(existing, full_set_store.iloc[i,:][["name"]]) == []:
            notebook.objects.create(name = full_set_store.iloc[i,:]["name"], cell_count = full_set_store.iloc[i,:]["cell_count"],
            code_cell_count = full_set_store.iloc[i,:]["code_cell_count"], language = full_set_store.iloc[i,:]["language"], 
            dataset = full_set_store.iloc[i,:]["dataset"], function = full_set_store.iloc[i,:]["function"],
            library = full_set_store.iloc[i,:]["library"])

query_results = str(query_results.query)
all_dt = pd.read_sql_query(query_results, connection)
all_dt["function"] = all_dt["function"].apply(json.loads)
all_dt["dataset"] = all_dt["dataset"].apply(json.loads)
all_dt["library"] = all_dt["library"].apply(json.loads)

width = 310

def language_graph():
    fig_language = px.pie(ntb_data.iloc[:, 3:5].groupby(["language"]).count().reset_index().rename(columns={'code_cell_count': 'count'}),
    values='count', names='language', title='Language Distrubition', height=width, color_discrete_sequence=px.colors.sequential.Tealgrn)
    
    graphJSON = json.dumps(fig_language, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def cell_count_plot(flag_language):
    
    ntb_data["markdown_cell_count"] = ntb_data["cell_count"]-ntb_data["code_cell_count"]
    cldata = ntb_data.sort_values(["cell_count"],ascending=False)
    
    if flag_language == "r":
        cldata = cldata[cldata["language"]=="r"]
    elif flag_language =="python":
        cldata = cldata[cldata["language"]=="python"]
    
    cell_count_fig = go.Figure(go.Bar(x=cldata["name"].iloc[:10], y=cldata["code_cell_count"], name='Code Cells', marker=dict(color="rgb(37, 125, 152)")))
    cell_count_fig.add_trace(go.Bar(x=cldata["name"].iloc[:10], y=cldata["markdown_cell_count"], name='Markdown Cells', marker=dict(color="#39603D")))
    cell_count_fig.update_layout(barmode='stack', height=340, xaxis_tickangle=40, margin={
        "l": 60,
        "r": 10,
        "b": 10,
        "t": 20,
        })
    cell_count_fig.update_xaxes(categoryorder='array', categoryarray= cldata["name"])
    
    
    data = cell_count_fig
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON  

def dataset_plot():
    dataset_fig = horizontal_bar_labels(ndatasets.to_dict("records"))
    graphJSON = json.dumps(dataset_fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def func(flag_language):
    fun = open_list(functions.merge(ntb_data[["language", "id"]]), "function")
    fun = fun[fun.function != ""]
    fun = fun.groupby(["function","language"]).count().reset_index().rename(columns={
        'id': 'count'}).sort_values(["count"],ascending=False)
    if flag_language == "r":
        fun = fun[fun["language"]=="r"]#language choice line
        fig = go.Figure(go.Bar(x=fun["function"].iloc[:10], y=fun["count"]))
        fig.update_layout(width=1210)
        fig.update_traces(marker=dict(color="#39603D"))


    elif flag_language =="python":
        fun = fun[fun["language"]=="python"]#language choice line
        fig = go.Figure(go.Bar(x=fun["function"].iloc[:10], y=fun["count"]))
        fig.update_layout(width=1210)
        fig.update_traces(marker=dict(color="#39603D"))

    else:
        fig = go.Figure(go.Bar(x=fun[fun["language"]=="r"]["function"], y=fun[fun["language"]=="r"]["count"], name='r', marker=dict(color="rgb(137, 232, 172)")))
        fig.add_trace(go.Bar(x=fun[fun["language"]=="python"]["function"], y=fun[fun["language"]=="python"]["count"], name='python', marker=dict(color="#39603D")))
        fig.update_layout(barmode='stack', width=1210)
        fig.update_xaxes(categoryorder='total descending',range=(-0.5, 20))
        
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def libr_plot():
    lrdata = nlibr.groupby(["library"]).count().reset_index().rename(columns={'id': 'count'})
    lrdata = lrdata.sort_values(["count"],ascending=False).iloc[:10]
    lr_fig = go.Figure(go.Bar(x=lrdata["library"], y=lrdata["count"]))
    lr_fig = lr_fig.update_layout(height=width, title="R Libraries")
    lr_fig.update_traces(marker=dict(color="rgb(37, 125, 152)"))

    graphJSON = json.dumps(lr_fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def libpy_plot():
    lpdata = nlibpy.groupby(["library"]).count().reset_index().rename(columns={'id': 'count'})
    lpdata = lpdata.sort_values(["count"],ascending=False).iloc[:10]
    lp_fig = go.Figure(go.Bar(x=lpdata["library"], y=lpdata["count"]))
    lp_fig = lp_fig.update_layout(height=width, title="Python Libraries")
    lp_fig.update_traces(marker=dict(color="rgb(37, 125, 152)"))
    graphJSON = json.dumps(lp_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def change_features(request):
    feature = request.GET.get('selected')
    graphJSON= cell_count_plot(feature)

    return HttpResponse(graphJSON)

def change_language(request):

    feature = request.GET.get('selected')
    graphJSON= func(feature)

    return HttpResponse(graphJSON)


def startapp(request):
    feature = "both"
    df = all_dt.to_html(table_id="example")
    return render(request, 'odash_template.html', {
        'func': func(feature),
        'language_graph': language_graph(),
        'cell_count_plot': cell_count_plot(feature),
        'dataset_plot': dataset_plot(),
        'libr_plot': libr_plot(),
        'libpy_plot': libpy_plot(),
        'df': df
        })

