"""Functions for returning optimization results in several forms.

----
@ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
"""

import logging
import pandas as pd
from oemof import solph
from matplotlib import pyplot as plt
import os


def xlsx(nodes_data, optimization_model, filepath):
    """Returns model results as xlsx-files.
    Saves the in- and outgoing flows of every bus of a given,
    optimized energy system as .xlsx file
    
    ----
    
    Keyword arguments:
    
        nodes_data : obj:'dict'
            -- dictionary containing data from excel scenario file
        
        optimization_model
            -- optimized energy system
        
        filepath : obj:'str'
            -- path, where the results will be stored
    
    ----
    
    Returns:
        results : obj:'.xlsx'
            -- xlsx files containing in and outgoing flows of the energy
            systems' buses.
    
    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
    """
    results = solph.processing.results(optimization_model)

    # Writes a spreadsheet containing the input and output flows into
    # every bus of the energy system for every timestep of the
    # timesystem
    for i, b in nodes_data['buses'].iterrows():
        if b['active']:
            file_path = \
                os.path.join(filepath, 'results_' + b['label'] + '.xlsx')
            node_results = solph.views.node(results, b['label'])
            df = node_results['sequences']
            df.head(2)
            with pd.ExcelWriter(file_path) as writer:  # doctest: +SKIP
                df.to_excel(writer, sheet_name=b['label'])
            # returns logging info
            logging.info('   ' + 'Results saved as xlsx for ' + b['label'])


def charts(nodes_data, optimization_model, energy_system):
    """Plots model results.
    
    Plots the in- and outgoing flows of every bus of a given, optimized energy
    system
    
    ----
    
    Keyword arguments:
    
        nodes_data : obj:'dict'
            -- dictionary containing data from excel scenario file
        
        optimization_model
            -- optimized energy system
        
        energy_system : obj:
            -- original (unoptimized) energy system
    
    ----
    
    Returns:
        plots
            -- plots displaying in and outgoing flows of the energy
            systems' buses.
    
    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
    """
    # rename variables
    esys = energy_system
    results = solph.processing.results(optimization_model)

    for i, b in nodes_data['buses'].iterrows():
        if b['active']:
            logging.info('   ' + "******************************************"
                         + "***************")
            logging.info('   ' + 'RESULTS: ' + b['label'])

            bus = solph.views.node(results, b['label'])
            logging.info('   ' + bus['sequences'].sum())
            fig, ax = plt.subplots(figsize=(10, 5))
            bus['sequences'].plot(ax=ax)
            ax.legend(loc='upper center', prop={'size': 8},
                      bbox_to_anchor=(0.5, 1.4), ncol=2)
            fig.subplots_adjust(top=0.7)
            plt.show()

    esys.results['main'] = solph.processing.results(optimization_model)
    esys.results['meta'] = solph.processing.meta_results(optimization_model)
    esys.dump(dpath=None, filename=None)


class Results:
    """
    Class for preparing Plotly results and logging the results of
    Cbc-Solver
    """
    results = None
    esys = None

    def get_flow(self, comp_label, comp_type):
        """
            Calculates the flow and performance of the given component,
            then logs it in the output and returns it to the statistics
            method.
            ----
            Keyword arguments:
                
                comp_label: obj:'str'
                    -- label of component to be calculated
                comp_type: obj:'str'
                    -- type of component to be calculated
            ----
            Returns:
                flow_sum: -- sum of the of the calculated flow
                flow_max: -- maximum of the calculated flow
                df_component: -- component_performance(input or output)
        """
        logging.info('   ' + comp_label)
        # creates component by component_label
        component = solph.views.node(self.results, comp_label)
        # reads the flows of the given component
        flow_sum = component['sequences'].sum()
        flow_max = component['sequences'].max()
        # sets the performance of the given component
        component_performance = component['sequences'].columns.values
        df_component1 = component['sequences'][component_performance[0]]
        # Dictionary for the information of components to be logged
        comp_log = {'demand': [0, 0, 'Total Energy Demand: '],
                    'source': [0, 0, 'Total Energy Input: ']}
        if comp_type == 'demand' or comp_type == 'source':
            logging.info('   ' + comp_log[comp_type][2]
                         + str(round(flow_sum[[comp_log[comp_type][0]]
                                              [comp_log[comp_type][1]]], 2))
                         + 'kWh')
        if comp_type == 'source':
            logging.info('   ' + 'Max. Capacity: '
                         + str(round(flow_max[[0][0]], 2)) + ' kW')
        # returns the parameters to the statistics method
        if comp_type == 'demand' or comp_type == 'source' \
                or comp_type == 'shortage':
            return flow_sum[[0][0]], df_component1
        elif comp_type == 'link' or comp_type == 'storage':
            return flow_sum, flow_max, component['sequences']

    def get_investment(self, component, comp_type):
        """
        Calculates the investment to be made and the resulting periodical
        costs.
        ----
        Keyword arguments:
            component: obj
                -- one component of the energy system with
                'max. investment' > 0
            comp_type: obj: 'str'
                -- type of the component to be calculated
        ----
        Returns:
            component_investment: obj: 'float'
                -- investment to be made
            periodical_costs: obj: 'float'
                -- periodic_costs resulting from the investment decision
        """
        component_node = self.esys.groups[component['label']]
        # defines bus_node for different components
        if comp_type == 'source':
            bus_node = self.esys.groups[component['output']]
        elif comp_type == 'solar_heat':
            label = component['label'] + '_bus'
            bus_node = self.esys.groups[label]
        elif comp_type == 'storage':
            bus_node = None
        elif comp_type == 'link':
            bus_node = self.esys.groups[component['bus_2']]
        else:
            raise SystemError('Wrong type chosen!')
        # sets component investment
        component_investment = \
            (self.results[component_node, bus_node]
             ['scalars']['invest'])
        if comp_type == 'solar_heat':
            # considers area conversion factor on investment for
            # solar heat sources
            component_investment = \
                component_investment / \
                component['Conversion Factor /(sqm/kW) (Solar Heat)']
        # returns logging info
        logging.info('   ' + 'Investment Capacity: '
                     + str(round(component_investment, 2)) + ' kW')
        if comp_type == 'storage':
            # calculates the periodical costs
            periodical_costs = (component['periodical costs /(CU/(kWh a))'] *
                                component_investment)
        else:
            # calculates the periodical costs
            periodical_costs = (component['periodical costs /(CU/(kW a))'] *
                                component_investment)
        # logs periodical costs in system output
        logging.info('   ' + 'Periodical costs: '
                     + str(round(periodical_costs, 2))
                     + ' cost units p.a.')
        return component_investment, periodical_costs

    def statistics(self, nodes_data, optimization_model, energy_system,
                   result_path):
        """
        Returns a list of all defined components with the following
        information:
        
        component   |   information
        ----------------------------------------------------------------
        sinks       |   Total Energy Demand
        sources     |   Total Energy Input, Max. Capacity,
                        Variable Costs, Periodical Costs,
                        Electricity Input (Solar Heat only),
        transformers|   Total Energy Output, Max. Capacity,
                        Variable Costs, Investment Capacity,
                        Periodical Costs
        storages    |   Energy Output, Energy Input, Max. Capacity,
                        Total variable costs, Investment Capacity,
                        Periodical Costs
        links       |   Total Energy Output
        
        Furthermore, a list of recommended investments is printed.
        ----
        Keyword arguments:
        
            nodes_data : obj:'dict'
               -- dictionary containing data from excel scenario file
        
            optimization_model
                -- optimized energy system
        
            energy_system : obj:
                -- original (unoptimized) energy system
            
            result_path : obj: 'str'
                -- Path where the results are saved.
        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """

        # renames input variables
        nd = nodes_data
        self.esys = energy_system
        om = optimization_model
        self.results = solph.processing.results(om)
        # columns of list of components
        columns = ['ID', 'type', 'input 1/kWh', 'input 2/kWh', 'output 1/kWh',
                   'output 2/kWh', 'capacity/kW', 'variable costs/CU',
                   'periodical costs/CU', 'investment/kW', 'constraints/CU']
        # sets checklist for fill in variables
        checklist = ['X', 'x', '', '0', 'None', 'none', 'nan']

        df_list_of_components = pd.DataFrame(columns=columns)
        df_result_table = pd.DataFrame()
        log_end = \
            '   ' + '--------------------------------------------------------'

        ###################
        # Analyze Results #
        ###################
        total_usage = 0
        total_demand = 0
        total_costs = 0
        total_periodical_costs = 0
        total_constraint_costs = 0
        investments_to_be_made = {}
        # logs the next type of components(sinks)
        log("SINKS********")
        # creates and returns results for sinks defined in the
        # sinks-sheet of the input spreadsheet
        for i, comp in nd['demand'].iterrows():
            if comp['active']:
                # gets the flow for the given sink
                (flow_sum, df_demand) = self.get_flow(comp['label'], 'demand')
                total_demand = total_demand + flow_sum
                df_result_table[comp['label']] = df_demand
                # adds the sink to the list of components
                df_list_of_components = \
                    df_list_of_components.append(
                        pd.DataFrame([[comp['label'], 'sink',
                                       round(flow_sum, 2), '---', '---', '---',
                                       round(df_demand.max(), 2), '---', '---',
                                       '---','---']], columns=columns))
                # returns logging info
                logging.info(log_end)
        # creates and returns results for excess buses defined in the
        # buses-sheet of the input spreadsheet (excess sinks)
        for i, comp in nd['buses'].iterrows():
            if comp['active']:
                if comp['excess']:
                    (flow_sum, df_excess) = \
                        self.get_flow(comp['label'] + '_excess', 'demand')
                    total_usage = total_usage + flow_sum
                    # calculates the total variable costs of the sink
                    variable_costs = comp['excess costs /(CU/kWh)'] * flow_sum
                    # adds the variable costs to the total_costs variable
                    total_costs = total_costs + variable_costs
                    # calculates the constraint costs
                    constraint_costs = \
                        flow_sum * comp['variable excess constraint costs /(CU/kWh)']
                    total_constraint_costs += constraint_costs
                    df_result_table[comp['label'] + '_excess'] = df_excess
                    # adds the bus to the list of components
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'] + '_excess',
                                           'sink', round(flow_sum, 2), '---',
                                           '---', '---',
                                           round(df_excess.max(), 2),
                                           round(variable_costs, 2), '---',
                                           '---', round(constraint_costs,2)]],
                                           columns=columns))
                    # returns logging info
                    logging.info('   ' + 'Variable Costs: '
                                 + str(round(variable_costs, 2))
                                 + ' cost units')
                    logging.info(log_end)
        # logs the next type of components(sources)
        log("SOURCES******")
        # creates and returns results for sources defined in the
        # sources-sheet of the input spreadsheet
        for i, comp in nd['sources'].iterrows():
            if comp['active']:
                if str(comp['input']) in checklist:
                    (flow_sum, df_source) = self.get_flow(comp['label'], 'source')
                    # adds the flowsum to the total_usage variable
                    total_usage = total_usage + flow_sum
                    # Adds the components time series to the
                    # df_component_flows data frame for further usage
                    df_result_table[comp['label']] = df_source
                # creates and returns results if source is a solar thermal
                # collector (flat plate or concentrated)
                elif str(comp['input']) not in checklist:
                    # reference to transformer and solar bus component
                    transformer = comp['label'] + '_collector'
                    col_bus = comp['label'] + '_bus'
                    transformer_investment = 0
                    variable_costs = 0
                    periodical_costs = 0
                    # sets in- and output variables for solar heat transformer
                    # and logs results
                    (flow_sum_tf, flow_max, dfcomponent) = \
                        self.get_flow(transformer, 'link')
                    for index, value in flow_sum_tf.items():
                        if index == ((comp['input'], transformer), 'flow'):
                            input = value
                            df_input1 = dfcomponent[index]
                        elif index == ((col_bus, transformer), 'flow'):
                            input2 = value
                            # flow_sum = input2
                            df_input2 = dfcomponent[index]
                        elif index == ((transformer, comp['output']), 'flow'):
                            output1 = value
                            flow_sum = output1
                            df_output1 = dfcomponent[index]
                    logging.info('   ' + 'Input from '
                                 + comp['input'] + ': '
                                 + str(round(input, 2)) + ' kWh')
                    logging.info('   ' + 'Ambient Energy Input to '
                                 + transformer + ': '
                                 + str(round(input2, 2)) + ' kWh')
                    logging.info('   ' + 'Energy Output to '
                                 + comp['output'] + ': '
                                 + str(round(output1, 2)) + ' kWh')
                    total_usage = total_usage + output1
                    # Adds the components time series for solar heat sources
                    # to the df_component_flows data frame for further usage
                    df_result_table[comp['label'] + '_el_input'] = df_input1
                    df_result_table[comp['label'] + '_solar_input'] = df_input2
                    df_result_table[comp['label'] + '_heat_output'] =\
                        df_output1
                # continues, if the model decided to take a investment
                # decision for this source
                constraint_costs = \
                    flow_sum * comp['variable constraint costs /(CU/kWh)']

                if comp['max. investment capacity /(kW)'] > 0:
                    # sources except solar heat
                    if str(comp['input']) in checklist:
                        # gets the investment for the given source
                        (component_investment, periodical_costs) = \
                            self.get_investment(comp, 'source')
                        # adds the investment to the investments_to_be_made
                        # list
                        investments_to_be_made[comp['label']] = \
                            (str(round(component_investment, 2)) + ' kW')
                    # solar heat sources
                    elif str(comp['input']) not in checklist:
                        # gets the investment for the given source
                        (component_investment, periodical_costs) = \
                            self.get_investment(comp, 'solar_heat')
                        # adds the investment to the investments_to_be_made
                        # list
                        investments_to_be_made[comp['label']] = \
                            (str(round(component_investment, 2)) + ' kW')

                    if component_investment > 0:
                        total_periodical_costs = (total_periodical_costs
                                                  + periodical_costs)
                        investments_to_be_made[comp['label']] = \
                            (str(round(component_investment, 2))
                             + ' kW; ' + str(round(periodical_costs, 2))
                             + ' cost units (p.a.)')
                        constraint_costs += \
                            component_investment \
                            * comp['periodical constraint costs /(CU/(kW a))']
                else:
                    periodical_costs = 0
                    component_investment = 0
                total_constraint_costs += constraint_costs
                # Calculates Variable Costs, adds it to the total_cost
                # variable and returns logging info
                variable_costs = comp['variable costs /(CU/kWh)'] * flow_sum
                total_costs = total_costs + variable_costs
                logging.info('   ' + 'Variable costs: '
                             + str(round(variable_costs, 2)) + ' cost units')
                # adds the source to the list of components (except solar heat)
                if str(comp['input']) in checklist:
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'], 'source', '---',
                                           '---', round(df_source.sum(), 2),
                                           '---', round(df_source.max(), 2),
                                           round(variable_costs, 2),
                                           round(periodical_costs, 2),
                                           round(component_investment, 2),
                                           round(constraint_costs, 2)]],
                                         columns=columns))
                # adds solar heat sources to the list of components
                if str(comp['input']) not in checklist:
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[transformer, 'source',
                                           round(input, 2), round(input2, 2),
                                           round(output1, 2), '---',
                                           round(df_input2.max(), 2),
                                           round(variable_costs, 2),
                                           round(periodical_costs, 2),
                                           round(component_investment, 2),
                                           round(constraint_costs, 2)]],
                                         columns=columns))
                logging.info(log_end)
        for i, comp in nd['buses'].iterrows():
            if comp['active']:
                if comp['shortage']:
                    (flow_sum, df_shortage) = \
                        self.get_flow(comp['label'] + '_shortage', 'shortage')
                    total_usage = total_usage + flow_sum
                    constraint_costs = \
                        flow_sum * comp['variable shortage constraint costs /(CU/kWh)']
                    total_constraint_costs += constraint_costs
                    # Variable Costs
                    variable_costs = \
                        comp['shortage costs /(CU/kWh)'] * flow_sum
                    total_costs = total_costs + variable_costs
                    logging.info('   ' + 'Variable Costs: '
                                 + str(round(variable_costs, 2))
                                 + ' cost units')
                    # adds the bus to the list of components
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'] + '_shortage',
                                           'source', '---', '---',
                                           round(flow_sum, 2), '---',
                                           round(df_shortage.max(), 2),
                                           round(variable_costs, 2), '---',
                                           '---', round(constraint_costs, 2)]],
                                           columns=columns))
                    df_result_table[comp['label'] + '_shortage'] = df_shortage
                    logging.info(log_end)
        # logs the next type of components
        log("TRANSFORMERS*")
        for i, comp in nd['transformers'].iterrows():
            variable_costs = 0
            max_transformer_flow = 0
            constraint_costs = 0
            if comp['active']:
                (flow_sum, flow_max, dfcomponent) = \
                    self.get_flow(comp['label'], 'link')
                for index, value in flow_sum.items():
                    if index == ((comp['input'], comp['label']), 'flow'):
                        input = value
                        df_input1 = dfcomponent[index]
                    elif index == ((comp['label'] + '_low_temp_bus',
                                    comp['label']), 'flow'):
                        input2 = value
                        df_input2 = dfcomponent[index]
                    elif index == ((comp['label'] + '_high_temp_bus',
                                    comp['label']), 'flow'):
                        input2 = value
                        df_input2 = dfcomponent[index]
                    elif index == ((comp['label'], comp['output']), 'flow'):
                        output1 = value
                        df_output1 = dfcomponent[index]
                    elif index == ((comp['label'], comp['output2']), 'flow'):
                        output2 = value
                        df_output2 = dfcomponent[index]
                for index, value in flow_max.items():
                    if index == ((comp['label'], comp['output']), 'flow'):
                        max_transformer_flow = value
                if comp['transformer type'] == 'GenericTransformer' or \
                        comp['transformer type'] == 'GenericCHP':
                    if comp['output2'] != 'None':
                        logging.info('   '
                                     + 'Total Energy Output to '
                                     + comp['output'] + ': '
                                     + str(round(output1, 2)) + ' kWh')
                        output = comp['output2']
                    else:
                        output = comp['output']
                    logging.info('   '
                                 + 'Total Energy Output to ' + output + ':'
                                 + str(round(
                                            (output2 if
                                             output == comp['output2']
                                             else output1), 2)) + ' kWh')

                elif comp['transformer type'] == 'ExtractionTurbineCHP':
                    logging.info('   ' + 'WARNING: ExtractionTurbineCHP are'
                                 ' currently not a part of this model '
                                 'generator, but will be added later.')
                # sets logging info for compression or absorption heat
                # transformers
                elif str(comp['mode']) not in checklist:
                    logging.info('   ' + 'Electricity Energy Input to '
                                 + comp['label'] + ': '
                                 + str(round(input, 2)) + ' kWh')
                    if comp['transformer type'] == \
                            'absorption_heat_transformer':
                        logging.info('   ' + 'Heat Input to '
                                     + comp['label'] + ': '
                                     + str(round(input2, 2)) + ' kWh')
                    if comp['transformer type'] == \
                            'compression_heat_transformer':
                        logging.info('   ' + 'Ambient Energy Input to '
                                     + comp['label'] + ': '
                                     + str(round(input2, 2)) + ' kWh')
                    logging.info('   ' + 'Total Energy Output to '
                                 + comp['output'] + ': '
                                 + str(round(output1, 2)) + ' kWh')

                elif comp['transformer type'] == 'OffsetTransformer':
                    logging.info('   ' + 'WARNING: OffsetTransformer are '
                                 + 'currently not a part of this model '
                                 + 'generator, but will be added later.')

                logging.info('   ' + 'Max. Capacity: '
                             + str(round(max_transformer_flow, 2)) + ' kW')
                if comp['output2'] != 'None':
                    variable_costs = (comp['variable output costs 2 /(CU/kWh)']
                                      * df_output2.sum())
                    constraint_costs += \
                        output2 * comp['variable output constraint costs 2 /(CU/kWh)']
                    total_costs = total_costs + variable_costs
                variable_costs += (comp['variable input costs /(CU/kWh)']
                                   * df_input1.sum())
                constraint_costs += \
                    output1 * comp['variable output constraint costs /(CU/kWh)']
                constraint_costs += \
                    input * comp['variable input constraint costs /(CU/kWh)']
                variable_costs += \
                    (comp['variable output costs /(CU/kWh)']
                     * df_output1.sum())
                total_costs += variable_costs
                logging.info('   ' + 'Variable Costs: '
                             + str(round(variable_costs, 2)) + ' cost units')

                # Investment Capacity
                if comp['max. investment capacity /(kW)'] > 0:
                    # gets investment for given transformer
                    (transformer_investment, periodical_costs) = \
                        self.get_investment(comp, 'source')
                    logging.info('   ' + 'Investment Capacity: '
                                 + str(round(transformer_investment, 2))
                                 + ' kW')
                else:
                    transformer_investment = 0

                # Periodical Costs
                if transformer_investment > 0:
                    # max investment capacity * periodical costs
                    periodical_costs = (comp['periodical costs /(CU/(kW a))']
                                        * transformer_investment)
                    total_periodical_costs = (total_periodical_costs
                                              + periodical_costs)
                    investments_to_be_made[comp['label']] = \
                        (str(round(transformer_investment, 2)) + ' kW; '
                         + str(round(periodical_costs, 2))
                         + ' cost units (p.a.)')
                    constraint_costs += \
                        transformer_investment\
                        * comp['periodical constraint costs /(CU/(kW a))']
                else:
                    periodical_costs = 0
                total_constraint_costs += constraint_costs
                logging.info('   ' + 'Periodical costs (p.a.): '
                             + str(round(periodical_costs, 2))
                             + ' cost units p.a.')
                if comp['transformer type'] == 'GenericTransformer':
                    df_result_table[comp['label'] + '_input1'] = df_input1
                    df_result_table[comp['label'] + '_output1'] = df_output1
                    if comp['output2'] == 'None':
                        # adds Generic transformer with one given
                        # outputs to the list of components
                        df_list_of_components = \
                            df_list_of_components.append(
                                pd.DataFrame([[comp['label'], 'transformer',
                                               round(input, 2), '---',
                                               round(output1, 2), '---',
                                               round(df_input1.max(), 2),
                                               round(variable_costs, 2),
                                               round(periodical_costs, 2),
                                               round(transformer_investment, 2),
                                               round(constraint_costs, 2)]],
                                               columns=columns))
                    else:
                        # adds Generic transformer with two given
                        # outputs to the list of components
                        df_result_table[comp['label'] + '_output2'] = \
                            df_output2
                        df_list_of_components = \
                            df_list_of_components.append(
                                pd.DataFrame([[comp['label'], 'transformer',
                                               round(input, 2), '---',
                                               round(output1, 2),
                                               round(output2, 2),
                                               round(df_input1.max(), 2),
                                               round(variable_costs, 2),
                                               round(periodical_costs, 2),
                                               round(transformer_investment, 2),
                                               round(constraint_costs, 2)]],
                                               columns=columns))
                # adds compression or absorption heat transformer to the
                # list of results
                elif str(comp['mode']) not in checklist:
                    df_result_table[comp['label'] + '_el_input'] = df_input1
                    if comp['transformer type'] ==\
                            'absorption_heat_transformer':
                        df_result_table[comp['label'] + '_heat_input'] =\
                            df_input2
                    if comp['transformer type'] ==\
                            'compression_heat_transformer':
                        df_result_table[comp['label'] + '_ambient_input'] =\
                            df_input2
                    if comp['mode'] == 'chiller':
                        df_result_table[comp['label'] + '_cooling_output'] =\
                            df_output1
                    if comp['mode'] == 'heat_pump':
                        df_result_table[comp['label'] + '_heat_output'] =\
                            df_output1
                    # adds compression or absorption heat transformer to the
                    # list of components
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'], 'transformer',
                                           round(input, 2), round(input2, 2),
                                           round(output1, 2), '---',
                                           round(df_output1.max(), 2),
                                           round(variable_costs, 2),
                                           round(periodical_costs, 2),
                                           round(transformer_investment, 2),
                                           round(constraint_costs, 2)]],
                                           columns=columns))

                elif comp['transformer type'] == 'GenericCHP':
                    # adds genericchp transformer to the list of
                    # components
                    df_result_table[comp['label'] + '_input'] = df_input1
                    df_result_table[comp['label'] + '_output1'] = df_output1
                    df_result_table[comp['label'] + '_output2'] = df_output2
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'], 'transformer',
                                           round(input, 2), '---',
                                           round(output1, 2),
                                           round(output2, 2),
                                           round(df_output1.max(), 2),
                                           round(variable_costs, 2),
                                           round(periodical_costs, 2),
                                           round(transformer_investment, 2),
                                           round(constraint_costs, 2)]],
                                           columns=columns))
                logging.info(log_end)
        # logs the next type of components
        log("STORAGES*****")
        for i, comp in nd['storages'].iterrows():
            if comp['active']:
                # gets component flow and performance for given storages
                (flow_sum, flow_max, dfcomponent) = \
                    self.get_flow(comp['label'], 'link')
                for index, value in flow_sum.items():
                    if index == ((comp['bus'], comp['label']), 'flow'):
                        input = value
                        df_input = dfcomponent[index]
                    elif index == ((comp['label'], comp['bus']), 'flow'):
                        output = value
                        df_output = dfcomponent[index]
                    elif index == ((comp['label'], 'None'), 'storage_content'):
                        df_capacity = dfcomponent[index]
                for index, value in flow_max.items():
                    if index == ((comp['label'], 'None'), 'storage_content'):
                        maxcapacity = value
                logging.info('   ' + 'Energy Output from ' + comp['label'] + ':'
                             + str(round(output, 2)) + 'kWh')
                logging.info('   ' + 'Energy Input to ' + comp['label'] + ': '
                             + str(round(input, 2)) + ' kWh')
                constraint_costs = \
                    comp['variable input constraint costs /(CU/kWh)'] * input
                constraint_costs += \
                    comp['variable output constraint costs /(CU/kWh)'] * output
                variable_costs = comp['variable input costs'] * input
                variable_costs += comp['variable output costs'] * output
                logging.info('   ' + 'Total variable costs for: '
                             + str(round(variable_costs, 2))
                             + ' cost units')
                total_costs = total_costs + variable_costs
                # Investment Capacity
                if comp['max. investment capacity /(kWh)'] > 0:
                    # gets investment and periodical cost for given
                    # storage
                    (storage_investment, periodical_costs) = \
                        self.get_investment(comp, 'storage')
                else:
                    # if no investment decision has been taken
                    storage_investment = 0
                    periodical_costs = 0
                # Periodical Costs
                if storage_investment \
                        > float(comp['existing capacity /(kWh)']):
                    total_periodical_costs = (total_periodical_costs
                                              + periodical_costs)
                    investments_to_be_made[comp['label']] = \
                        (str(round(storage_investment, 2)) + ' kWh; '
                         + str(round(periodical_costs, 2)) +
                         ' cost units (p.a.)')
                    constraint_costs += \
                        comp['periodical constraint costs /(CU/(kWh a))'] \
                        * storage_investment
                total_constraint_costs += constraint_costs
                df_list_of_components = \
                    df_list_of_components.append(
                        pd.DataFrame([[comp['label'], 'storage',
                                       round(input, 2), '---',
                                       round(output, 2), '---',
                                       round(maxcapacity, 2),
                                       round(variable_costs, 2),
                                       round(periodical_costs, 2),
                                       round(storage_investment, 2),
                                       round(constraint_costs, 2)]],
                                     columns=columns))
                df_result_table[comp['label'] + '_capacity'] = df_capacity
                df_result_table[comp['label'] + '_input'] = df_input
                df_result_table[comp['label'] + '_output'] = df_output
                logging.info(log_end)
        # logs the next type of components (links
        log("LINKS********")
        for i, comp in nd['links'].iterrows():
            variable_costs = 0
            constraint_costs = 0
            if comp['active']:
                (flow_sum, flow_max, dfcomponent) = \
                    self.get_flow(comp['label'], 'link')
                for index, value in flow_sum.items():
                    if index == ((comp['bus_1'], comp['label']), 'flow'):
                        df_linkinput1 = dfcomponent[index]
                    elif index == ((comp['bus_2'], comp['label']), 'flow'):
                        df_linkinput2 = dfcomponent[index]
                    elif index == ((comp['label'], comp['bus_1']), 'flow'):
                        output2 = value
                        df_linkoutput2 = dfcomponent[index]
                    elif index == ((comp['label'], comp['bus_2']), 'flow'):
                        output1 = value
                        df_linkoutput1 = dfcomponent[index]
                for index, value in flow_max.items():
                    if index == ((comp['label'], comp['bus_1']), 'flow'):
                        outputmax1 = value
                    elif index == ((comp['label'], comp['bus_2']), 'flow'):
                        outputmax2 = value
                if comp['(un)directed'] == 'directed':
                    logging.info('   ' + 'Total Energy Output to '
                                 + comp['bus_2'] + ': '
                                 + str(round(output1, 2)) + ' kWh')
                    logging.info('   ' + 'Max. Capacity to ' + comp['bus_2']
                                 + ': ' + str(round(outputmax2, 2)) + ' kW')
                else:
                    logging.info('   ' + 'Total Energy Output to '
                                 + comp['bus_2'] + ': '
                                 + str(round(output1, 2)) + ' kWh')
                    logging.info('   ' + 'Total Energy Output to '
                                 + comp['bus_1'] + ': '
                                 + str(round(output2, 2)) + ' kWh')
                    logging.info('   ' + 'Max. Capacity to ' + comp['bus_2']
                                 + ': ' + str(round(outputmax2, 2)) + ' kW')
                    logging.info('   ' + 'Max. Capacity to ' + comp['bus_1']
                                 + ': ' + str(round(outputmax1, 2)) + ' kW')
                    variable_costs += \
                        comp['variable output costs /(CU/kWh)'] \
                        * output2
                    constraint_costs += \
                        comp['variable constraint costs /(CU/kWh)'] * output2
                variable_costs += \
                    comp['variable output costs /(CU/kWh)'] * output1
                constraint_costs = \
                    comp['variable constraint costs /(CU/kWh)'] * output1

                total_costs = total_costs + variable_costs
                logging.info('   ' + 'Variable Costs: '
                             + str(round(variable_costs, 2))
                             + ' cost units')

                # Investment Capacity
                if comp['max. investment capacity /(kW)'] > 0:
                    # get investment for the given link
                    (link_investment, periodical_costs) = \
                        self.get_investment(comp, 'link')
                else:
                    # if no investment decision has been taken
                    link_investment = 0
                    periodical_costs = 0

                # Periodical Costs
                if link_investment > 0:
                    constraint_costs += \
                        (comp['periodical constraint costs /(CU/(kW a))']
                         * link_investment)
                    total_periodical_costs = \
                        (total_periodical_costs + periodical_costs)
                    investments_to_be_made[comp['label']] = \
                        (str(round(link_investment, 2)) + ' kW; '
                         + str(round(periodical_costs, 2))
                         + ' cost units (p.a.)')
                total_constraint_costs += constraint_costs
                df_result_table[comp['label'] + '_input1'] = df_linkinput1
                df_result_table[comp['label'] + '_output1'] = df_linkoutput1
                if comp['(un)directed'] == 'directed':
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'], 'link',
                                           round(df_linkinput1.sum(), 2),
                                           '---',
                                           round(df_linkoutput1.sum(), 2),
                                           '---',
                                           round(df_linkinput1.max(), 2),
                                           round(variable_costs, 2),
                                           round(periodical_costs, 2),
                                           round(link_investment, 2),
                                           round(constraint_costs, 2)]],
                                         columns=columns))
                else:
                    df_result_table[comp['label'] + '_input2'] = df_linkinput2
                    df_result_table[comp['label'] + '_output2'] = \
                        df_linkoutput2
                    df_list_of_components = \
                        df_list_of_components.append(
                            pd.DataFrame([[comp['label'], 'link',
                                           round(df_linkinput1.sum(), 2),
                                           round(df_linkinput2.sum(), 2),
                                           round(df_linkoutput1.sum(), 2),
                                           round(df_linkoutput2.sum(), 2),
                                           round(max(df_linkinput1.max(),
                                                     df_linkinput2.max()), 2),
                                           round(variable_costs, 2),
                                           round(periodical_costs, 2),
                                           round(link_investment, 2),
                                           round(constraint_costs, 2)]],
                                         columns=columns))
            logging.info(log_end)
        log("SUMMARY")
        meta_results = solph.processing.meta_results(om)
        meta_results_objective = meta_results['objective']
        logging.info('   ' + 'Total System Costs:             '
                     + str(round(meta_results_objective, 1))
                     + ' cost units')
        logging.info('   ' + 'Total Constraint Costs:         '
                     + str(round(total_constraint_costs)) + ' cost units')
        logging.info('   ' + 'Total Variable Costs:           '
                     + str(round(total_costs)) + ' cost units')
        logging.info('   ' + 'Total Periodical Costs (p.a.):  '
                     + str(round(total_periodical_costs))
                     + ' cost units p.a.')
        logging.info('   ' + 'Total Energy Demand:            '
                     + str(round(total_demand)) + ' kWh')
        logging.info('   ' + 'Total Energy Usage:             '
                     + str(round(total_usage)) + ' kWh')
        logging.info('   ' + '------------------------------------------------'
                     + '---------')
        logging.info('   ' + 'Investments to be made:')

        investment_objects = list(investments_to_be_made.keys())
        # Importing timesystem parameters from the scenario
        ts = next(nd['energysystem'].iterrows())[1]
        temp_resolution = ts['temporal resolution']
        start_date = ts['start date']
        end_date = ts['end date']

        df_summary = pd.DataFrame([[start_date,
                                    end_date,
                                    temp_resolution,
                                    round(meta_results_objective, 2),
                                    round(total_constraint_costs, 2),
                                    round(total_costs, 2),
                                    round(total_periodical_costs, 2),
                                    round(total_demand, 2),
                                    round(total_usage, 2)
                                    ]],
                                  columns=['Start Date',
                                           'End Date',
                                           'Resolution',
                                           'Total System Costs',
                                           'Total Constraint Costs',
                                           'Total Variable Costs',
                                           'Total Periodical Costs',
                                           'Total Energy Demand',
                                           'Total Energy Usage'])
        for i in range(len(investment_objects)):
            logging.info('   ' + investment_objects[i] + ': '
                         + investments_to_be_made[investment_objects[i]])
        logging.info(
            '   ' + '-----------------------------------------------------'
            + '----')
        logging.info(
            '   ' + "*****************************************************"
            + "****\n")
        # Dataframes are exported as csv for further processing
        df_list_of_components.to_csv(result_path + '/components.csv',
                                     index=False)

        df_result_table = df_result_table.rename_axis('date')
        df_result_table.to_csv(result_path + '/results.csv')

        df_summary.to_csv(result_path + '/summary.csv', index=False)

        logging.info('   ' + 'Successfully prepared results...')

    def __init__(self, nodes_data, optimization_model, energy_system,
                 result_path):
        """
            Inits the Results class for preparing Plotly results and
            logging the results of Cbc-Solver.
            
            ----
            Keyword arguments:
                
                nodes_data: obj:'dict'
                    -- dictionary containing data from excel scenario
                    file.
                optimization_model: -- optimized energy system
                energy_system: obj:
                    -- original (unoptimized) energy system
                result_path:
                    -- Path where the results are saved.
        """
        self.statistics(nodes_data, optimization_model, energy_system,
                        result_path)


def log(component):
    """
    Returns logging info for type of given components.
    ----
    Keyword arguments:
         component: obj: 'str'
         -- component type
    """
    # returns logging infos
    logging.info(
        '   ' + "********************************************************")
    logging.info(
        '   ' + "***" + component + "****************************************")
    logging.info(
        '   ' + "********************************************************")
    logging.info(
        '   ' + '--------------------------------------------------------')
