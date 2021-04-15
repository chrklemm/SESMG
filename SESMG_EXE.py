# -*- coding: utf-8 -*-
from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import subprocess
import os
from program_files.Spreadsheet_Energy_System_Model_Generator import sesmg_main


def create_elements(sheet, elements, texts, values, first_row):
    """ Creates a block of tk-inter elements. The elements are created from an input dictionary. The tk-inter output
    has the following structure:

    TEXT 1 | TEXT 2 | TEXT 3 | INPUT FIELD   | TEXT 4
    ...    | ...    | ...    | ...           | ...
           |        |        | UPDATE BUTTON |

    The block will have the number of lines that the input dictionary elements have. By pressing the "UPDATE BUTTON"
    the value "TEXT 2" will be replaced with the input given with the input field.

    ---

    Input variables:

    sheet: sheet within the window, where the element block will be placed

    elements: dictionary containing elements wich will be shown within this tk-inter block. Structure of the dictionary
                has to be as follows: elements = {'rowname':['text 1', 'text 2', 'text 3', 'text 4']}

    texts: list, where the elements of column 3 (TEXT 4) will be saved. Required for data updates.

    values: list, where the elements of column 1 (TEXT 2) will be saved. Required for data updates.

    first_row: top line of the window sheet where the block should be positioned.

    """

    element_keys = [i for i in elements.keys()]

    # Creates the row elements of the time-series-sheet
    for i in range(len(elements)):
        row = i + first_row + 1

        variable_name = Label(sheet, text=elements[element_keys[i]][0], font='Helvetica 10')
        variable_name.grid(column=0, row=row, sticky="W")

        variable_value = Label(sheet, text=str(elements[element_keys[i]][1]), font='Helvetica 10')
        values.append(variable_value)
        values[i].grid(column=1, row=row)

        variable_unit = Label(sheet, text=str(elements[element_keys[i]][2]), font='Helvetica 10')
        variable_unit.grid(column=2, row=row, sticky="W")

        variable_text = Entry(sheet, width=20, font='Helvetica 10')
        texts.append(variable_text)
        texts[i].grid(column=3, row=row)

        variable_format = Label(sheet, text=elements[element_keys[i]][3], font='Helvetica 10')
        variable_format.grid(column=4, row=row, sticky="W")


def create_main_frame_elements(elements, sheet, first_row, file_paths, frame):
    """ Creates a block of tk-inter elements. The elements are created from an input dictionary. The tk-inter output
       has the following structure:

       TEXT 1 | BUTTON | TEXT 2 |
       ...    | ...    | ...    |

       The block will have the number of lines that the input dictionary elements have. By pressing the "BUTTONS"
       stored functions will be executed.

       ---

       Input variables:

       sheet: sheet within the window, where the element block will be placed

       elements: dictionary containing elements wich will be shown within this tk-inter block.
       Structure of the dictionary has to be as follows:
            elements = {'rowname':['text 1', function to be executed, 'text 2'}

       frame: sheet within the window, where the element block will be placed

       file_paths: dictionary where the values of TEXT 2 can be saved. Required for later changes.

       first_row: top line of the window sheet where the block should be positioned.

       """
    element_keys = [i for i in elements.keys()]

    for i in range(len(elements)):
        row = i + first_row + 1

        label_name = Label(sheet, text=elements[element_keys[i]][0], font='Helvetica 10')
        label_name.grid(column=0, row=row, sticky="W")

        button = Button(frame, text=elements[element_keys[i]][2], command=elements[element_keys[i]][1])
        button.grid(column=3, row=row)

        label_comment = Label(sheet, text=elements[element_keys[i]][3], font='Helvetica 10')
        file_paths.append(label_comment)
        file_paths[i].grid(column=4, row=row, sticky="W")


def update_values(texts_input, rows, input_elements, input_values):
    input_element_keys = [i for i in input_elements.keys()]

    for j in range(rows):
        input_text = texts_input[j]
        if len(input_text.get()) > 0:
            input_elements[input_element_keys[j]][1] = input_text.get()
            input_values[j].configure(text=input_text.get())


def data_path():
    print('placeholder')


def getFolderPath():
    """ opens a file dialog and sets the selected path for the variable "scenario_path" """

    path = filedialog.askopenfilename(filetypes=(("Spreadsheet Files", "*.xlsx"), ("all files", "*.*")))
    print(path)

    scenario_path.set(path)
    print(scenario_path.get())

    file_paths[0].configure(text=scenario_path.get())

def getSavePath():
    """ opens a file dialog and sets the selected path for the variable "save_path" """

    path = filedialog.askdirectory()
    save_path.set(path)

    save_paths[0].configure(text=save_path.get())

def show_graph():
    """ creates and shows a graph of the energy system given by a Spreadsheet
        - the created graphs are saved in /results/graphs"""
    import os
    from program_files import (create_energy_system,
                               create_graph)

    # DEFINES PATH OF INPUT DATA
    scenario_file = scenario_path.get()

    # DEFINES PATH OF OUTPUT DATA
    if sys.platform.startswith("win"):
        result_path = os.path.join(os.path.dirname(__file__) + '/results/graphs')
    elif sys.platform.startswith('darwin'):
        result_path = os.path.dirname(os.path.abspath(__file__))
        result_path = result_path + '/results/graphs'
    elif sys.platform.startswith("linux"):
        result_path = os.path.dirname(os.path.abspath(__file__))
        result_path = result_path + '/results/graphs'
        subprocess.call("chmod +x " + result_path, shell=True)

    # IMPORTS DATA FROM THE EXCEL FILE AND RETURNS IT AS DICTIONARY
    nodes_data = create_energy_system.import_scenario(filepath=scenario_file)

    # PRINTS A GRAPH OF THE ENERGY SYSTEM
    create_graph.create_graph(filepath=result_path,
                              nodes_data=nodes_data,
                              legend=False)



def execute_sesmg():
    """ 1. Creates the folder where the results will be saved
        2. Excecutes the optimization algorithm """
    if scenario_path.get() != "No scenario selected.":
        scenario_name = os.path.basename(scenario_path.get())
        save_path.set(str(os.path.join(save_path_directory.get())
                          + '/' + scenario_name[:-5]
                          + str(datetime.now().strftime(
                            '_%Y-%m-%d--%H-%M-%S'))))
        os.mkdir(save_path.get())
        sesmg_main(scenario_file=scenario_path.get(),
                   result_path=save_path.get(),
                   num_threads=1,
                   graph=True,
                   results=True,
                   plotly=True)
        show_results()
    else:
        print('Please select scenario first!')
        comments[2].configure(text='Please select scenario first!')


def get_pid():
    """ Returns the ID of the running process on Port 8050 """
    import socket
    import errno
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Checks if port 8050 can be reached
        s.bind(("127.0.0.1", 8050))
        # If Yes, the program continues in line 225
        closeprocess = False
    # If not, the ID of the running process is returned
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            closeprocess = True
    s.close()
    if closeprocess:
        if sys.platform.startswith("win"):
            command = "netstat -aon| findstr :8050"
        elif sys.platform.startswith("darwin"):
            command = "lsof -i tcp:8050"
        elif sys.platform.startswith("linux"):
            command = "fuser -n tcp 8050"
        pids = subprocess.check_output(command, shell=True)
        pids = str(pids)
        pidslist = pids.split()
        if sys.platform.startswith("win"):
            pid = pidslist[5]
            pid = pid[:-4]
        elif sys.platform.startswith("darwin"):
            pid = pidslist[9]
        elif sys.platform.startswith("linux"):
            pid = pidslist[1]
        return pid
    else:
        return ''


def show_results():
    """ executes the external program, which executes a plotl.dash app for displaying interactive results."""
    if save_path.get() == '':
        raise SystemError('No optimization since the last restart'
                          ' please select a result folder!')

    # Determines the ID of a still running process on port 8050.
    pid = get_pid()
    # Checks if the ID is not an empty return (no process available)
    if pid != '':
        if sys.platform.startswith("win"):
            command = 'taskkill /F /PID ' + pid
        elif sys.platform.startswith("darwin"):
            command = 'kill ' + pid
        elif sys.platform.startswith("linux"):
            command = 'kill ' + pid
        # Kills the still running process on port 8050
        subprocess.call(command, shell=True)
    else:
        if sys.platform.startswith("win"):
            subprocess.call("start http://127.0.0.1:8050", shell=True)
        elif sys.platform.startswith("darwin"):
            subprocess.call("open http://127.0.0.1:8050", shell=True)
        elif sys.platform.startswith("linux"):
            subprocess.call("xdg-open http://127.0.0.1:8050", shell=True)

    # Starts the new Plotly Dash Server for Windows
    if sys.platform.startswith("win"):
        IR_PATH = os.path.join(os.path.dirname(__file__) + '/program_files')
        subprocess.call(IR_PATH + "/Interactive_Results.py "
                        + 'r"'+save_path.get()+'"', timeout=10, shell=True)
    # Starts the new Plotly Dash Server for MACOS
    elif sys.platform.startswith("darwin"):
        IR_PATH = os.path.dirname(os.path.abspath(__file__))
        IR_PATH = IR_PATH + '/program_files'
        subprocess.call("python3 " + IR_PATH + "/Interactive_Results.py "
                        + str(save_path.get()), timeout=10, shell=True)
    elif sys.platform.startswith("linux"):
        IR_PATH = os.path.dirname(os.path.abspath(__file__))
        IR_PATH = IR_PATH + '/program_files'
        subprocess.call("python3 " + IR_PATH + "/Interactive_Results.py "
                        + str(save_path.get()), timeout=10, shell=True)


# Definition of the user interface
window = Tk()
window.title("SESMG - Spreadsheet Energy System Model Generator")
window.geometry('1200x900')
tab_control = ttk.Notebook(window)
tab_control.pack(expand=1, fill='both')
tab_control.pressed_index = None
scenario_path = StringVar(window, str(os.path.join(os.path.dirname(__file__), 'scenario_v0.2.0.xlsx')))
save_path_directory = \
        StringVar(window, str(os.path.join(os.path.dirname(__file__), 'results')))
save_path = StringVar(window, '')
num_threads = 2

############
# MAIN FRAME
############
# Definition of the Main-Frames
# main_frame = ttk.Frame(tab_control)
main_frame = ttk.Frame(window)
tab_control.add(main_frame, text='Home')

# Headline
main_head1 = Label(main_frame, text='Selection Options', font='Helvetica 10 bold')
main_head1.grid(column=0, row=0, sticky="w")

# Erstellung des ersten Element-Blocks
# [label, function to be executed, button label, comment]
selection_elements = {'row1': ['Select scenario file', getFolderPath, 'Change', scenario_path.get()]}
file_paths = []
create_main_frame_elements(elements=selection_elements, sheet=main_frame, first_row=1, file_paths=file_paths,
                           frame=main_frame)

# Headline 2
main_head2 = Label(main_frame, text='Execution Options', font='Helvetica 10 bold')
main_head2.grid(column=0, row=3 + len(selection_elements), sticky="w")

# ERstellung des zweiten Element-Blocks
# [Label, function to be executed, name of the button, comment]
test = StringVar(window)
execution_elements = {'row2': ['Show Graph', show_graph, 'Execute', ''],
                      'row3': ['Optimize Model', execute_sesmg, 'Execute', test.get()],
                      'row4': ['Show Latest Results', show_results, 'Execute', ''],
                      # 'row7':['End Program',end_program,'End',' '],
                      }
comments = []
create_main_frame_elements(elements=execution_elements, sheet=main_frame, first_row=3 + len(selection_elements),
                           file_paths=comments, frame=main_frame)
main_head3 = Label(main_frame, text='Analyzing Options',
                       font='Helvetica 10 bold')
main_head3.grid(column=0, row=7 + len(execution_elements), sticky="w")
analyzing_elements = {'row5': ['Select scenario result folder',
                               getSavePath, 'Change', save_path.get()],
                      'row6': ['Start Plotly', show_results, 'Execute', '']}
save_paths = []
create_main_frame_elements(elements=analyzing_elements, sheet=main_frame,
                           first_row=7 + len(execution_elements),
                           file_paths=save_paths, frame=main_frame)

############
# DEMO FRAME
############
import pandas as pd
import openpyxl
import matplotlib as mlp
import matplotlib.pyplot as plt
import numpy as np
from threading import *
#from program_files.Spreadsheet_Energy_System_Model_Generator import SESMG_DEMO


monetary_costs = StringVar()
monetary_costs.set('--')

emission_costs = StringVar()
emission_costs.set('--')

results_dict = {}

def execute_sesmg_DEMO(demo_file, demo_results):
    """ Excecutes the optimization algorithm """
    print(demo_file)
    print(demo_results)

    # if scenario_path.get() != "No scenario selected.":
    #    scenario_file = scenario_path.get()
    if sys.platform.startswith("win"):
        result_path = os.path.join(os.path.dirname(__file__) + demo_results)
        demo_path = os.path.join(os.path.dirname(__file__) + demo_file)
    elif sys.platform.startswith('darwin'):
        result_path = os.path.dirname(os.path.abspath(__file__))
        result_path = result_path + demo_results
    elif sys.platform.startswith("linux"):
        result_path = os.path.dirname(os.path.abspath(__file__))
        result_path = result_path + demo_results
        subprocess.call("chmod +x " + result_path, shell=True)
    # scenario_file = 'scenario.xlsx'
    # SESMG_DEMO(scenario_file=scenario_file, result_path=result_path)
    sesmg_main(scenario_file=demo_path,
          result_path=result_path,
          graph=False,
          results=False,
          plotly=True)
    # show_results()
    # else:
    #     print('Please select scenario first!')
    #     comments[2].configure(text='Please select scenario first!')

def monetary_demo_scenario():
    '''modifies financial demo scenario'''


    xfile = openpyxl.load_workbook('examples/v0.0.6_demo_scenario/demo_scenario_monetaer.xlsx')

    # WINDPOWER
    sheet = xfile["sources"]
    sheet['H2'] = (int(entry_values['windpower'].get()))
    sheet['I2'] = (int(entry_values['windpower'].get()))
    # PHOTOVOLTAICS
    sheet = xfile["sources"]
    sheet['H3'] = (int(entry_values['photovoltaics'].get()))
    sheet['I3'] = (int(entry_values['photovoltaics'].get()))
    # BATTERY
    sheet = xfile["storages"]
    sheet['F2'] = (int(entry_values['battery'].get()))
    sheet['G2'] = (int(entry_values['battery'].get()))
    # CHP
    sheet = xfile["transformers"]
    sheet['N3'] = (int(entry_values['chp'].get()))
    sheet['O3'] = (int(entry_values['chp'].get()))
    # THERMAL STORAGE
    sheet = xfile["storages"]
    sheet['F3'] = (int(entry_values['thermal storage'].get()))
    sheet['G3'] = (int(entry_values['thermal storage'].get()))
    # District Heating
    sheet = xfile["links"]
    sheet['C2'] = (int(entry_values['district heating'].get()))

    xfile.save('results/demo/financial/scenario.xlsx')
    execute_sesmg_DEMO(demo_file=r"/results/demo/financial/scenario.xlsx",
                       demo_results=r"/results/demo/financial")

    df_summary = pd.read_csv(r"results/demo/financial/summary.csv")
    # monetary_costs = float(df_summary['Total System Costs'])
    monetary_costs.set(str(round(float(df_summary['Total System Costs']/1000000),2)))
    window.update_idletasks()

def emission_demo_scenario():
    '''modifies financial demo scenario'''

    xfile = openpyxl.load_workbook('examples/v0.0.6_demo_scenario/demo_scenario_emissionen.xlsx')

    # WINDPOWER
    sheet = xfile["sources"]
    sheet['H2'] = (int(entry_values['windpower'].get()))
    sheet['I2'] = (int(entry_values['windpower'].get()))
    # PHOTOVOLTAICS
    sheet = xfile["sources"]
    sheet['H3'] = (int(entry_values['photovoltaics'].get()))
    sheet['I3'] = (int(entry_values['photovoltaics'].get()))
    # BATTERY
    sheet = xfile["storages"]
    sheet['F2'] = (int(entry_values['battery'].get()))
    sheet['G2'] = (int(entry_values['battery'].get()))
    # CHP
    sheet = xfile["transformers"]
    sheet['N3'] = (int(entry_values['chp'].get()))
    sheet['O3'] = (int(entry_values['chp'].get()))
    # THERMAL STORAGE
    sheet = xfile["storages"]
    sheet['F3'] = (int(entry_values['thermal storage'].get()))
    sheet['G3'] = (int(entry_values['thermal storage'].get()))
    # District Heating
    sheet = xfile["links"]
    sheet['C2'] = (int(entry_values['district heating'].get()))

    xfile.save('results/demo/emissions/scenario.xlsx')
    execute_sesmg_DEMO(demo_file='/results/demo/emissions/scenario.xlsx',
                       demo_results='/results/demo/emissions')

    df_summary = pd.read_csv(r"results/demo/emissions/summary.csv")

    emission_costs.set(str(round(float(df_summary['Total System Costs'])/1000000,0)))
    window.update_idletasks()

def simulate_scenario():

    for i in range(len(entry_values)):
        print(demo_names[i] + ': ' + entry_values[demo_names[i]].get() + ' ' + demo_unit[demo_names[i]])

    t_monetary = Thread(target=monetary_demo_scenario(), args=())
    t_emission = Thread(target=emission_demo_scenario(), args=())

    t_monetary.start()
    t_emission.start()

    t_monetary.join()
    t_emission.join()

    # monetary_demo_scenario()
    # emission_demo_scenario()

def include_optimized_scenarios():
    results_dict['Status Quo'] = [8.2594606, 18521.2, 0, 0, 0, 0, 0, 0]
    results_dict['Financial Minimum'] = [1.310668, 14400.430112, 29700, 10000, 0, 0, 0, 0]
    results_dict['Emission Minimum'] = [9.825963, 12574.7, 5526, 644, 29680, 2769, 0, 10000]

def save_results():

    interim_results = [float(monetary_costs.get()),
                       float(emission_costs.get()),]

    for i in range(1, len(entry_values)):
        interim_results.append(int(entry_values[demo_names[i]].get()))

    results_dict[entry_values[demo_names[0]].get()] = interim_results
    print(results_dict)



def save_manual_results():
    interim_results2 = [float(entry_monetary_costs_value.get()),
                        float(entry_emission_costs_value.get()),]

    for i in range(1, len(entry_values)):
        interim_results2.append(int(entry_values2[demo_names2[i]].get()))

    results_dict[entry_values2[demo_names2[0]].get()] = interim_results2
    print(results_dict)

def plot_results_scatter():

    plt.xlabel('Mio. EUR/a')
    plt.ylabel('t/a')

    keys = list(results_dict.keys())
    print(keys)
    values = list(results_dict.values())
    print(values)

    for i in range(len(results_dict)):
        plt.scatter(values[i][0],values[i][1],label=keys[i])

    plt.legend()
    # fig2.tight_layout()
    plt.show()

def plot_results_bar():
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np

    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                                   NavigationToolbar2Tk)


    # the figure that will contain the plot
    fig = Figure(figsize=(5, 5),dpi=100)


    labels = list(demo_components.keys())
    labels.pop(0)

    scenario_names = list(results_dict.keys())
    print(scenario_names)

    scenarios = []
    scenario_data = list(results_dict.values())
    print(scenario_data)

    for i in range(len(scenario_data)):
        test_list = scenario_data[i][:]
        test_list.pop(0)
        test_list.pop(0)
        scenarios.append(test_list)



    print(scenarios)

    x = np.arange(len(labels))  # the label locations
    width = 0.5/len(scenarios)  # the width of the bars

    fig, ax = plt.subplots()

    bars = []
    for i in range(len(scenarios)):
        bars.append(ax.bar(x + width*i, scenarios[i], width, label=scenario_names[i]))

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Capacity')
    ax.set_title('Scenarios')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    fig.tight_layout()

    plt.show()


# Definition of the DEMO-Frames
# main_frame = ttk.Frame(tab_control)
demo_frame = ttk.Frame(window)
tab_control.add(demo_frame, text='DEMO')



# DEMO explanation

row = 0
explanation = '''DEMO-Energy System: In this DEMO the financial costs and carbon dioxide emissions of a residential area are simulated. For improvement, the technologies 
                 listed below are available with the parameters below. The simulated scenarios can be compared with the status quo, the financial minimum and the emission minimum.          
                 '''

label_explanation = Label(demo_frame, text=explanation, font=('Helvetica 10 bold'))
label_explanation.grid(column=0, columnspan=7, row=row)

row = row + 1
label_monetary_costs = Label(demo_frame, text='Simulation Input', font=('Helvetica 10 bold'))
label_monetary_costs.grid(column=1, row=row)
label_monetary_costs = Label(demo_frame, text='Manual Result Input', font=('Helvetica 10 bold'))
label_monetary_costs.grid(column=5, row=row)


demo_components = {"name":'name',
                   "windpower":'0',
                   "photovoltaics":'0',
                   "battery":'0',
                   "chp":'0',
                   "thermal storage":'0',
                   "district heating":'0'}

demo_unit = {"name":'',
               "windpower":'kW',
               "photovoltaics":'kW',
               "battery":'kWh',
               "chp":'kW (el.)',
               "thermal storage":'kWh',
               "district heating":'True (1) / False (0)'}

row = row + 1
demo_names = list(demo_components.keys())
demo_values = list(demo_components.values())
entry_values = {}

# Erstellt Eingabefelder für alle variierbaren componenten.
for i in range(len(demo_components)):
    column = 0

    # Defines Label
    label_name = Label(demo_frame, text=demo_names[i], font=('Helvetica 10'))
    label_name.grid(column=column, row=row, sticky="W")
    column = column + 1

    # Defines Entry Field
    entry_values[demo_names[i]] = StringVar()
    entry_values[demo_names[i]].set(demo_values[i])
    entry_values[demo_names[i]] = Entry(demo_frame, text=str(entry_values[demo_names[i]]))
    entry_values[demo_names[i]].grid(column=column, row=row)
    column = column + 1

    # Defines Unit
    label_name = Label(demo_frame, text=demo_unit[demo_names[i]], font=('Helvetica 10'))
    label_name.grid(column=column, row=row, sticky="W")

    row = row + 1


# EXECUTION BUTTONS
# row = row + 1
Button(demo_frame, text='SIMULATE', command=simulate_scenario).grid(column=1, row=row, pady=4)

# RESULTS
row = row + 2
label_monetary_costs = Label(demo_frame, text='RESULTS', font=('Helvetica 10'))
label_monetary_costs.grid(column=0, row=row, sticky="W")

row = row + 1
label_monetary_costs = Label(demo_frame, text='Monetary Costs: ', font=('Helvetica 10'))
label_monetary_costs.grid(column=0, row=row, sticky="W")

label_monetary_costs_value = Label(demo_frame, textvariable=monetary_costs, font=('Helvetica 10'))
label_monetary_costs_value.grid(column=1, row=row, sticky="W")

label_monetary_unit = Label(demo_frame, text=' Mio. EUR/a', font=('Helvetica 10'))
label_monetary_unit.grid(column=2, row=row, sticky="W")

row = row + 1
label_emission_costs = Label(demo_frame, text='CO2 Emissions: ', font=('Helvetica 10'))
label_emission_costs.grid(column=0, row=row, sticky="W")
label_emission_costs_value = Label(demo_frame, textvariable=emission_costs, font=('Helvetica 10'))
label_emission_costs_value.grid(column=1, row=row, sticky="W")
label_emission_unit = Label(demo_frame, text=' t/a', font=('Helvetica 10'))
label_emission_unit.grid(column=2, row=row, sticky="W")

# EXECUTION BUTTONS
row = row + 1
Button(demo_frame, text='SAVE', command=save_results).grid(column=1, row=row, sticky=W, pady=4)

for i in range(15):
    label_placeholder = Label(demo_frame, text=' || ', font=('Helvetica 10'))
    label_placeholder.grid(column=3, row=i+1)


row = 2
demo_names2 = list(demo_components.keys())
demo_values2 = list(demo_components.values())
entry_values2 = {}

# Erstellt Eingabefelder für alle variierbaren componenten.
for i in range(len(demo_components)):
    column = 4

    # Defines Label
    label_name = Label(demo_frame, text=demo_names2[i], font=('Helvetica 10'))
    label_name.grid(column=column, row=row, sticky="W")
    column = column + 1

    # Defines Entry Field
    entry_values2[demo_names2[i]] = StringVar()
    entry_values2[demo_names2[i]].set(demo_values2[i])
    entry_values2[demo_names2[i]] = Entry(demo_frame, text=str(entry_values2[demo_names2[i]]))
    entry_values2[demo_names2[i]].grid(column=column, row=row)
    column = column + 1

    # Defines Unit
    label_name = Label(demo_frame, text=demo_unit[demo_names2[i]], font=('Helvetica 10'))
    label_name.grid(column=column, row=row, sticky="W")

    row = row + 1

# RESULTS



row = row + 2
label_monetary_costs = Label(demo_frame, text='RESULTS', font=('Helvetica 10'))
label_monetary_costs.grid(column=4, row=row, sticky="W")

row = row + 1
label_monetary_costs_2 = Label(demo_frame, text='Monetary Costs', font=('Helvetica 10'))
label_monetary_costs_2.grid(column=0+4, row=row, sticky="W")

entry_monetary_costs_value= IntVar()
entry_monetary_costs_value.set(0)
entry_monetary_costs_value = Entry(demo_frame, text=str(entry_monetary_costs_value))
entry_monetary_costs_value.grid(column=1+4, row=row)

label_monetary_unit_2 = Label(demo_frame, text=' Mio. EUR/a', font=('Helvetica 10'))
label_monetary_unit_2.grid(column=2+4, row=row, sticky="W")

row = row + 1

label_emission_costs_2 = Label(demo_frame, text='CO2 Emissions', font=('Helvetica 10'))
label_emission_costs_2.grid(column=0+4, row=row, sticky="W")

entry_emission_costs_value= IntVar()
entry_emission_costs_value.set(0)
entry_emission_costs_value = Entry(demo_frame, text=str(entry_emission_costs_value))
entry_emission_costs_value.grid(column=1+4, row=row)

label_emission_unit_2 = Label(demo_frame, text=' t/a', font=('Helvetica 10'))
label_emission_unit_2.grid(column=2+4, row=row, sticky="W")

#
#
# EXECUTION BUTTONS
row = 14
Button(demo_frame, text='SAVE', command=save_manual_results).grid(column=1+4, row=row, pady=4)
row = row + 1
label_line = Label(demo_frame, text=14*'===========', font=('Helvetica 10'))
label_line.grid(column=0, row=row, columnspan=7)
row = row + 1
Button(demo_frame, text='SCATTER PLOT', command=plot_results_scatter).grid(column=2, row=row, pady=4)
Button(demo_frame, text='BAR PLOT', command=plot_results_bar).grid(column=4, row=row, pady=4)
Button(demo_frame, text='Include Optimized Scenarios', command=include_optimized_scenarios).grid(column=3, row=row, pady=4)
row = row + 1
label_line = Label(demo_frame, text=14*'===========', font=('Helvetica 10'))
label_line.grid(column=0, row=row, columnspan=7)

row = row + 1
img = PhotoImage(file='examples/v0.0.6_demo_scenario/DEMO_System.png')
img = img.subsample(2,2)
panel = Label(demo_frame, image = img)
panel.grid(column=0,columnspan=4, row=row, rowspan=30)

# panel.pack(side = "bottom", fill = "both", expand = "yes")


demo_assumptions = {'Electricity Demand':'14 000 000 kWh/a, h0 Load Profile',
                    'Heaty Demand':'52 203 000 kWh/a, EFH Load Profile',
                    'Windturbines':'2 000 000 €/MW, 8 g/kWh, 20 a, max. 29.7 MW',
                    'Photovoltaics':'1 140 000 €/MW, 56 g/kWh, 20 a, max. 10 MW',
                    'Battery':'1 000 000 €/MWh, 155 t/MWh (Invest!), 20 a',
                    'CHP':'190 000 €/MWh (el.), 375 g/kWh (el), 165 g/kWh (th.), 20 a',
                    'Thermal Storage':'35 000 €/MWh, 46 g/kWh, 20 a, 3 % loss /d',
                    'district heating':'86 000 000 €, 15 % loss, 40 a',
                    'Gas Import/Heating':'6.4 ct/kWh (gas), 85 % efficiency, 45.62 g/kWh',
                    'Electricity Import':'30.5 ct/kWh, 474 g/kWh'
                    }


assumption_keys = list(demo_assumptions.keys())
assumption_values = list(demo_assumptions.values())

# row = row + 1
rowcount = 0
column = 4

for i in range(len(demo_assumptions)):

    label = Label(demo_frame, text=assumption_keys[i], font=('Helvetica 10 bold'))
    label.grid(column=column, row=row, sticky="W")



    label = Label(demo_frame, text=assumption_values[i], font=('Helvetica 10'))
    label.grid(column=column+1, columnspan=2, row=row, sticky="W")

    row = row + 1



window.mainloop()
