# -*- coding: utf-8 -*-
"""Creates oemof energy system components.

Functions for the creation of oemof energy system objects from a
given set of object parameters.

---
Contributors:
- Christian Klemm - christian.klemm@fh-muenster.de
- Gregor Becker - gb611137@fh-muenster.de
"""

from oemof import solph
import logging
import os
import pandas as pd
from feedinlib import *
import demandlib.bdew as bdew
import datetime
import numpy


def buses(nodes_data, nodes):
    """
    Creates bus objects.
    Creates bus objects with the parameters given in 'nodes_data' and
    adds them to the list of components 'nodes'.
    ----

    Keyword arguments:

        nodes_data : obj:'dict'
            -- dictionary containing parameters of the buses to be
            created. The following parameters have to be provided:
                - label,
                - active,
                - excess,
                - shortage,
                - shortage costs /(CU/kWh),
                - excess costs /(CU/kWh)
                
        nodes : obj:'list'
            -- list of components created before (can be empty)
        
    ----
    
    Returns:
        busd : obj:'dict'
            -- dictionary containing all buses created
        
    ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 13.02.2020
    """
    # creates a list of buses
    busd = {}
    
    # Creates components, which are defined within the "buses"-sheet of
    # the original excel-file
    for i, b in nodes_data['buses'].iterrows():
        # Create a bus object for every bus, which is marked as "active"
        if b['active']:
            # creates an oemof-bus object
            bus = solph.Bus(label=b['label'])
            # adds the bus object to the list of components "nodes"
            nodes.append(bus)
            busd[b['label']] = bus
            # returns logging info
            logging.info('   ' + 'Bus created: ' + b['label'])
        
            # Create an sink for every bus, which is marked with
            # "excess"
            if b['excess']:
                # creates the oemof-sink object and
                # directly adds it to the list of components "nodes"
                inputs = {
                    busd[b['label']]:
                        solph.Flow(variable_costs=b['excess costs /(CU/kWh)'],
                                   emission_factor=b[
                                    'variable excess constraint costs /(CU/kWh)'])}
                nodes.append(
                        solph.Sink(
                                label=b['label'] + '_excess',
                                inputs=inputs))
            
            # Create a source for every bus, which is marked with
            # "shortage"
            if b['shortage']:
                # creates the oemof-source object and
                # directly adds it to the list of components "nodes"
                outputs = {
                    busd[b['label']]:
                        solph.Flow(
                            variable_costs=b['shortage costs /(CU/kWh)'],
                            emission_factor=b[
                                'variable shortage constraint costs /(CU/kWh)'])}
                nodes.append(
                        solph.Source(
                                label=b['label'] + '_shortage',
                                outputs=outputs))
        
    # Returns the list of buses as result of the function
    return busd


class Sources:
    """Creates source objects.
    
    There are four options for labeling source objects to be created:
    - 'commodity' : a source with flexible time series
    - 'timeseries' : a source with predefined time series
    - 'photovoltaic' : a photovoltaic component
    - 'wind power' : a wind power component
    - 'solar_thermal_heat' : a solar thermal heat component. Can be
    a flat plate or a parabolic through collector.
    """
    
    def create_source(self, so, timeseries_args, output=None):
        """Creates an oemof source with fixed or unfixed timeseries
        
        ----
        Keyword arguments:
        
            so : obj:'dict'
                -- dictionary containing all information for the
                creation of an oemof source. At least the following
                key-value-pairs have to be included:
                   'label'
                   'output'
                   'periodical costs /(CU/(kW a))'
                   'min. investment capacity /(kW)'
                   'max. investment capacity /(kW)'
                   'existing capacity /(kW)'
                   'Non-Convex Investment'
                   'Fix Investment Costs /(CU/a)'
                   'variable costs /(CU/kWh)'
            
            timeseries_args: dict
                --  dictionary rather containing the 'fix-attribute' or
                the 'min-' and 'max-attribute' of a source

            output: obj: class 'oemof.solph.network.Bus'
                -- bus component which is output bus of the source

        ---
        Contributors:
        - Christian Klemm - christian.klemm@fh-muenster.de
        
        """
        # output default
        if output is None:
            output = self.busd[so['output']]
        # sets checklist for fill in variables
        checklist = ['X', 'x', '', '0', 'None', 'none', 'nan']
        # set variables minimum, maximum and existing
        if str(so['input']) in checklist:
            minimum = so['min. investment capacity /(kW)']
            maximum = so['max. investment capacity /(kW)']
            existing = so['existing capacity /(kW)']
        # set variables minimum, maximum and existing for solar thermal heat
        # sources
        else:
            minimum = so['min. investment capacity /(kW)'] * \
                so['Conversion Factor /(sqm/kW) (Solar Heat)']
            maximum = so['max. investment capacity /(kW)'] * \
                so['Conversion Factor /(sqm/kW) (Solar Heat)']
            existing = so['existing capacity /(kW)'] * \
                so['Conversion Factor /(sqm/kW) (Solar Heat)']
        # Creates a oemof source and appends it to the nodes_sources
        # (variable of the create_sources-class) list
        self.nodes_sources.append(
                solph.Source(
                        label=so['label'],
                        outputs={output: solph.Flow(
                                investment=solph.Investment(
                                        ep_costs=so[
                                            'periodical costs /(CU/(kW a))'],
                                        periodical_constraint_costs=so[
                                            'periodical constraint costs /(CU/(kW a))'],
                                        minimum=minimum,
                                        maximum=maximum,
                                        existing=existing,
                                        nonconvex=True if
                                        so['Non-Convex Investment'] == 1
                                        else False,
                                        offset=so[
                                            'Fix Investment Costs /(CU/a)']),
                                **timeseries_args,
                                variable_costs=so['variable costs /(CU/kWh)'],
                                emission_factor=so[
                                    'variable constraint costs /(CU/kWh)']
                        )}
                ))
    
    def commodity_source(self, so):
        """ Creates an oemof source object with flexible time series
        (no maximum or minimum) with the use of the
        create_source method.
        
        ----
        Keyword arguments:
        
            so : obj:'dict'
                -- dictionary containing all information for the
                    creation of an oemof source. At least the
                    following key-value-pairs have to be included:
                        'label'
        """
        # starts the create_source method with the parameters
        # min = 0 and max = 1
        self.create_source(so, {'min': 0, 'max': 1})
        
        # Returns logging info
        logging.info('   ' + 'Commodity Source created: ' + so['label'])
    
    def timeseries_source(self, so, filepath):
        """Creates an oemof source object from a pre-defined
        timeseries with the use of the create_source
        method.
        
        ---
        Keyword arguments:
        
        so : obj:'dict'
        --  dictionary containing all information for the
        creation of an oemof source. At least the following
        key-value-pairs have to be included:
           'label'
           'output'
           'periodical costs /(CU/(kW a))'
           'min. investment capacity /(kW)'
           'max. investment capacity /(kW)'
           'existing capacity /(kW)'
           'Non-Convex Investment'
           'Fix Investment Costs /(CU/a)'
           'variable costs /(CU/kWh)'
        
        filepath: String
        --  path to .xlsx scenario-file containing a
        "time_series" sheet
        """
        # reads the timeseries sheet of the scenario file
        time_series = pd.read_excel(filepath, sheet_name='time_series')
        
        if so['fixed'] == 1:
            # sets the timeseries attribute for a fixed source
            args = {'fix': time_series[so['label'] + '.fix'].tolist()}
        elif so['fixed'] == 0:
            # sets the timeseries attributes for an unfixed source
            args = {'min': time_series[so['label'] + '.min'].tolist(),
                    'max': time_series[so['label'] + '.max'].tolist()}
        else:
            raise SystemError(so['label'] + " Error in fixed attribute")
        
        # starts the create_source method with the parameters set before
        self.create_source(so, args)
        
        # Returns logging info
        logging.info('   ' + 'Timeseries Source created: ' + so['label'])
        
    def pv_source(self, so, my_weather_pandas_dataframe):
        """Creates an oemof photovoltaic source object.
        
        Simulates the yield of a photovoltaic system using feedinlib and
        creates a source object with the yield as time series and the
        use of the create_source method.
        
        ---
        
        Keyword arguments:
        
            so : obj:'dict'
                --  dictionary containing all information for the
                creation of an oemof source. At least the following
                key-value-pairs have to be included:
                    - 'label'
                    - 'fixed'
                    - 'Azimuth (PV ONLY)'
                    - 'Surface Tilt (PV ONLY)'
                    - 'Modul Model (PV ONLY)'
                    - 'Inverter Model (PV ONLY)'
                    - 'Albedo (PV ONLY)'
                    - 'Latitude (PV ONLY)'
                    - 'Longitude (PV ONLY)'
        """
        
        # reads pv system parameters from parameter dictionary
        # nodes_data
        parameter_set = {
            'azimuth': so['Azimuth (PV ONLY)'],
            'tilt': so['Surface Tilt (PV ONLY)'],
            'module_name': so['Modul Model (PV ONLY)'],
            'inverter_name': so['Inverter Model (PV ONLY)'],
            'albedo': so['Albedo (PV ONLY)']}
        
        # sets pv system parameters for pv_module
        pv_module = powerplants.Photovoltaic(**parameter_set)
        
        # calculates global horizontal irradiance from diffuse (dhi)
        # and direct irradiance and adds it to the weather data frame
        my_weather_pandas_dataframe['ghi'] = \
            (my_weather_pandas_dataframe.dirhi
             + my_weather_pandas_dataframe.dhi)
        
        # changes names of data columns,
        # so it fits the needs of the feedinlib
        name_dc = {'temperature': 'temp_air', 'windspeed': 'v_wind'}
        my_weather_pandas_dataframe.rename(columns=name_dc)
        
        # calculates time series normed on 1 kW pv peak performance
        feedin = pv_module.feedin(
                weather=my_weather_pandas_dataframe,
                location=(so['Latitude (PV ONLY)'], so['Longitude (PV ONLY)']),
                scaling='peak_power')
        
        # Prepare data set for compatibility with oemof
        for i in range(len(feedin)):
            # Set negative values to zero
            # (requirement for solving the model)
            if feedin[i] < 0:
                feedin[i] = 0
            # Set values greater 1 to 1
            # (requirement for solving the model)
            if feedin[i] > 1:
                feedin[i] = 1
            # Replace 'nan' value with 0
            feedin = feedin.fillna(0)
        if so['fixed'] == 1:
            # sets the attribute for a fixed pv_source
            args = {'fix': feedin}
        elif so['fixed'] == 0:
            # sets the attributes for an unfixed pv_source
            args = {'min': 0, 'max': feedin}
        else:
            raise SystemError(so['label'] + " Error in fixed attribute")
        
        # starts the create_source method with the parameters set before
        self.create_source(so, args)
        
        # returns logging info
        logging.info('   ' + 'Source created: ' + so['label'])
    
    def windpower_source(self, so, weather_df_wind):
        """Creates an oemof windpower source object.
        
        Simulates the yield of a windturbine using feedinlib and
        creates a source object with the yield as time series and the
        use of the create_source method.
        
        ---
        Keyword arguments:
        
        so : obj:'dict'
        -- dictionary containing all information for the
        creation of an oemof source. At least the following
        key-value-pairs have to be included:
            - 'label'
            - 'fixed'
            - 'Turbine Model (Windpower ONLY)'
            - 'Hub Height (Windpower ONLY)'
        """
        
        # set up wind turbine using the wind turbine library.
        # The turbine name must correspond to an entry in the turbine
        # data-base of the feedinlib. Unit of the hub height is m.
        turbine_data = {
            'turbine_type': so['Turbine Model (Windpower ONLY)'],
            'hub_height': so['Hub Height (Windpower ONLY)']}
        wind_turbine = WindPowerPlant(**turbine_data)

        # change type of index to datetime and set time zone
        weather_df_wind.index = \
            pd.to_datetime(weather_df_wind.index).tz_convert('Europe/Berlin')
        data_height = {'pressure': 0, 'temperature': 2, 'wind_speed': 10,
                       'roughness_length': 0}
        weather_df_wind = \
            weather_df_wind[['windspeed', 'temperature', 'z0', 'pressure']]
        weather_df_wind.columns = \
            [['wind_speed', 'temperature', 'roughness_length', 'pressure'],
             [data_height['wind_speed'], data_height['temperature'],
              data_height['roughness_length'], data_height['pressure']]]
        
        # calculate scaled feed-in
        feedin_wind_scaled = wind_turbine.feedin(
                weather=weather_df_wind, scaling='nominal_power')
        if so['fixed'] == 1:
            # sets the attribute for a fixed windpower_source
            args = {'fix': feedin_wind_scaled}
        
        elif so['fixed'] == 0:
            # sets the attribute for an unfixed windpower_source
            args = {'min': 0, 'max': feedin_wind_scaled}
        else:
            raise SystemError(so['label'] + " Error in fixed attribute")
        
        # starts the create_source method with the parameters set before
        self.create_source(so, args)
        
        # returns logging info
        logging.info('   ' + 'Source created: ' + so['label'])

    def solar_heat_source(self, so, data):
        """
            Creates a solar thermal collector source object.

            Calculates the yield of a solar thermal flat plate collector
            or a concentrated solar power collector as time series by
            using oemof.thermal and the create_source method.

            The following key-value-pairs have to be included in the
            keyword arguments:

            :param so: has to contain the following keyword arguments:

                - 'label'
                - 'active'
                - 'fixed'
                - 'output'
                - 'input'
                - 'technology':
                    - 'solar_thermal_flat_plate' or
                    - 'concentrated_solar_power'
                - 'variable costs /(CU/kWh)'
                - 'variable constraint costs /(CU/kWh)'
                - 'existing capacity /(kW)'
                - 'min. investment capacity /(kW)'
                - 'max. investment capacity /(kW)'
                - 'periodical costs /(CU/(kW a))'
                - 'periodical constraint costs /(CU/(kW a))'
                - 'Non-Convex Investment'
                - 'Fix Investment Cost / (CU/a)'
                - 'Latitude (Solar Heat)'
                - 'Longitude (Solar Heat)'
                - 'Surface Tilt (Solar Heat)'
                - 'Azimuth (Solar Heat)'
                - 'Cleanliness (Solar Heat)'
                - 'ETA 0 (Solar Heat)'
                - 'A1 (Solar Heat)'
                - 'A2 (Solar Heat)'
                - 'C1 (Solar Heat)'
                - 'C2 (Solar Heat)'
                - 'Temperature Inlet /deg C (Solar Heat)'
                - 'Temperature Difference /deg C (Solar Heat)'
                - 'Conversion Factor /(sqm/kW) (Solar Heat)'
                - 'Peripheral Losses (Solar Heat)'
                - 'Electric Consumption (Solar Heat)'

            :type so: dict

            :param data: weather data
            :type data: dict

            Yannick Wittor - yw090223@fh-muenster.de, 27.11.2020
        """

        # import oemof.thermal in order to calculate collector heat output
        from oemof.thermal.solar_thermal_collector import flat_plate_precalc
        from oemof.thermal.concentrating_solar_power import csp_precalc
        import numpy

        # creates an oemof-bus object for solar thermal collector
        col_bus = solph.Bus(label=so['label'] + '_bus')
        # adds the bus object to the list of components "nodes"
        self.nodes_sources.append(col_bus)
        self.busd[so['label'] + '_bus'] = col_bus
        output = col_bus

        # calculates global horizontal irradiance from diffuse (dhi)
        # and direct irradiance (dirhi) and adds it to the weather data frame
        data['ghi'] = (data.dirhi + data.dhi)

        # precalculations for flat plate collectors, calculates total
        # irradiance on collector, efficiency and heat output
        if so['technology'] == 'solar_thermal_flat_plate':
            precalc_results = flat_plate_precalc(
                lat=so['Latitude (Solar Heat)'],
                long=so['Longitude (Solar Heat)'],
                collector_tilt=so['Surface Tilt (Solar Heat)'],
                collector_azimuth=so['Azimuth (Solar Heat)'],
                eta_0=so['ETA 0 (Solar Heat)'],
                a_1=so['A1 (Solar Heat)'],
                a_2=so['A2 (Solar Heat)'],
                temp_collector_inlet=
                so['Temperature Inlet /deg C (Solar Heat)'],
                delta_temp_n=
                so['Temperature Difference /deg C (Solar Heat)'],
                irradiance_global=(data['ghi']),
                irradiance_diffuse=(data['dhi']),
                temp_amb=data['temperature'])
            # set variables collectors_heat and irradiance and conversion
            # from W/sqm to kW/sqm
            collectors_heat = precalc_results.collectors_heat/1000
            irradiance = precalc_results.col_ira/1000

        # set parameters for precalculations for concentrating solar power
        elif so['technology'] == 'concentrated_solar_power':
            temp_collector_outlet = \
                so['Temperature Inlet /deg C (Solar Heat)'] + \
                so['Temperature Difference /deg C (Solar Heat)']
            latitude = so['Latitude (Solar Heat)']
            longitude = so['Longitude (Solar Heat)']
            collector_tilt = so['Surface Tilt (Solar Heat)']
            collector_azimuth = so['Azimuth (Solar Heat)']
            cleanliness = so['Cleanliness (Solar Heat)']
            eta_0 = so['ETA 0 (Solar Heat)']
            c_1 = so['C1 (Solar Heat)']
            c_2 = so['C2 (Solar Heat)']
            temp_collector_inlet = \
                so['Temperature Inlet /deg C (Solar Heat)']
            temp_collector_outlet = temp_collector_outlet
            a_1 = so['A1 (Solar Heat)']
            a_2 = so['A2 (Solar Heat)']
            e_dir_hor = data['dirhi']

            # precalculation with parameter set, ambient temperature and
            # direct horizontal irradiance. Calculates total irradiance on
            # collector, efficiency and heat output
            precalc_results = csp_precalc(latitude, longitude,
                                          collector_tilt, collector_azimuth,
                                          cleanliness, eta_0, c_1, c_2,
                                          temp_collector_inlet,
                                          temp_collector_outlet,
                                          data['temperature'], a_1, a_2,
                                          E_dir_hor=e_dir_hor)
            # set variables collectors_heat and irradiance and conversion
            # from W/sqm to kW/sqm
            collectors_heat = precalc_results.collector_heat/1000
            irradiance = precalc_results.collector_irradiance/1000

        # set collector heat as timeseries as argument for source
        if so['fixed'] == 1:
            # sets the attribute for a fixed solar heat source
            args = {'fix': collectors_heat}
        elif so['fixed'] == 0:
            # sets the attributes for an unfixed solar heat source
            args = {'min': 0, 'max': collectors_heat}
        else:
            raise SystemError(so['label'] + " Error in fixed attribute")

        # starts the create_source method with the parameters set before
        self.create_source(so, args, output)

        self.nodes_sources.append(solph.Transformer(
            label=so['label'] + '_collector',
            inputs={self.busd[so['label'] + '_bus']:
                    solph.Flow(variable_costs=0),
                    self.busd[so['input']]: solph.Flow(variable_costs=0)},
            outputs={self.busd[so['output']]: solph.Flow(variable_costs=0)},
            conversion_factors={
                self.busd[so['label'] + '_bus']: 1,
                self.busd[so['input']]:
                    so['Electric Consumption (Solar Heat)'] *
                    (1 - so['Peripheral Losses (Solar Heat)']),
                self.busd[so['output']]:
                    1 - so['Peripheral Losses (Solar Heat)']
            }))

        # returns logging info
        logging.info('   ' + 'Source created: ' + so['label']
                     + ", Max Heat power output per year and m²: {:2.2f}".
                     format(numpy.sum(collectors_heat)) + ' kWh/(m²a)'
                     + ", Irradiance on collector per year and m²: "
                       "{:2.2f}".format(numpy.sum(irradiance)) + ' kWh/(m²a)')

    def __init__(self, nodes_data, nodes, busd, filepath):
        """
        Inits the source class
        ---
        Keyword arguments:

        nodes_data: obj:'dict'
        --  dictionary containing parameters of sources to be
        created.The following data have to be provided:
             - 'label'
             - 'active'
             - 'fixed'
             - 'output'
             - 'input' (Only solar thermal flat plate)
             - 'technology'
             - 'variable costs / (CU / kWh)'
             - 'existing capacity / (kW)'
             - 'min.investment capacity / (kW)'
             - 'max.investment capacity / (kW)'
             - 'periodical costs / (CU / (kW a))'
             - 'Non-Convex Investment'
             - 'Fix Investment Cost / (CU/a)'
             - 'Turbine Model (Windpower ONLY)'
             - 'Hub Height (Windpower ONLY)'
             - 'technology database(PV ONLY)'
             - 'inverter database(PV ONLY)'
             - 'Modul Model(PV ONLY)'
             - 'Inverter Model(PV ONLY)'
             - 'Azimuth(PV ONLY)'
             - 'Surface Tilt(PV ONLY)'
             - 'Albedo(PV ONLY)'
             - 'Altitude(PV ONLY)'
             - 'Latitude(PV ONLY)'
             - 'Longitude(PV ONLY)'
             - 'Latitude (Solar Heat)'
             - 'Longitude (Solar Heat)'
             - 'Surface Tilt (Solar Heat)'
             - 'Azimuth (Solar Heat)'
             - 'Cleanliness (Solar Heat)'
             - 'ETA 0 (Solar Heat)'
             - 'A1 (Solar Heat)'
             - 'A2 (Solar Heat)'
             - 'C1 (Solar Heat)'
             - 'C2 (Solar Heat)'
             - 'Temperature Inlet /deg C (Solar Heat)'
             - 'Temperature Difference /deg C (Solar Heat)'
             - 'Conversion Factor /(sqm/kW) (Solar Heat)'
             - 'Peripheral Losses (Solar Heat)'
             - 'Electric Consumption (Solar Heat)'

        nodes: obj:'list'
             -  list of components created before(can be empty)

        busd: obj:'dict'
        --  dictionary containing the buses of the energy system

        filepath: obj:'str'
        -- path to .xlsx scenario-file containing a
        "weather data" sheet with timeseries for
            -   "dhi"(diffuse horizontal irradiation)
                W / m ^ 2
            -   "dirhi"(direct horizontal irradiance)
                W / m ^ 2
            -   "pressure" in Pa
            -   "temperature" in °C
            -   "windspeed" in m / s
            -   "z0"(roughness length) in m

        ---
        Other variables:

        nodes_sources: obj:'list'
        -- class intern list of sources that are already created

        ---
        Contributors:
        - Christian Klemm - christian.klemm@fh-muenster.de
        - Gregor Becker - gregor.becker@fh-muenster.de
        """
        # Delete possible residues of a previous run from the class
        # internal list nodes_sources
        self.nodes_sources = []
        # Initialise a class intern copy of the bus dictionary
        self.busd = busd.copy()

        # Import weather Data
        data = pd.read_csv(
                os.path.join(os.path.dirname(__file__))
                + '/interim_data/weather_data.csv', index_col=0,
                date_parser=lambda idx: pd.to_datetime(idx, utc=True))

        # Create Source from "Sources" Table
        for i, so in nodes_data['sources'].iterrows():
            # Create a source object for every source,
            # which is marked as "active"
            if so['active']:
                # Create Commodity Sources
                if so['technology'] == 'other':
                    self.commodity_source(so)
                
                # Create Photovoltaic Sources
                elif so['technology'] == 'photovoltaic':
                    self.pv_source(so, data)
                
                # Create Windpower Sources
                elif so['technology'] == 'windpower':
                    self.windpower_source(so, data)
                
                # Create Time-series Sources
                elif so['technology'] == 'timeseries':
                    self.timeseries_source(so, filepath)

                # Create flat plate solar thermal Sources
                elif so['technology'] == 'solar_thermal_flat_plate' or \
                        'concentrated_solar_power':
                    self.solar_heat_source(so, data)
            
        # appends created sources and other objects to the list of nodes
        for i in range(len(self.nodes_sources)):
            nodes.append(self.nodes_sources[i])


class Sinks:
    """Creates sink objects.
    
    There are four options for labeling source objects to be
    created:
    - 'unfixed' : a source with flexible time series
    - 'timeseries' : a source with predefined time series
    -  SLP : a VDEW standard load profile component
    - 'richardson' : a component with stochastically generated
    timeseries
    """
    # intern variables
    busd = None
    nodes_sinks = []
    
    def create_sink(self, de, timeseries_args):
        """Creates an oemof sink with fixed or unfixed timeseries.
        
        ----
        Keyword arguments:
            de : obj:'dict'
                --  dictionary containing all information for the
                    creation of an oemof sink. At least the
                    following key-value-pairs have to be included:
                        - 'label'
                        - 'input'
            
            timeseries_args : obj:'dict'
                --  dictionary rather containing the 'fix-attribute'
                    or the 'min-' and 'max-attribute' of a sink
        
        ---
        Contributors:
        - Christian Klemm - christian.klemm@fh-muenster.de
        """
        # creates an omeof Sink and appends it to the class intern list
        # of created sinks
        self.nodes_sinks.append(
                solph.Sink(label=de['label'],
                           inputs={
                               self.busd[de['input']]:
                                   solph.Flow(**timeseries_args)}))
    
    def unfixed_sink(self, de):
        """ Creates a sink object with an unfixed energy input and the
        use of the create_sink method.
        ----
        Keyword arguments:
            de : obj:'dict'
                --  dictionary containing all information for
                the creation of an oemof sink. For this function
                the following key-value-pairs have to
                be included:
                    - 'label'
                    - 'nominal value /(kW)'
        
        ---
        Contributors:
        - Christian Klemm - christian.klemm@fh-muenster.de
        """
        
        # set static inflow values
        inflow_args = {'nominal_value': de['nominal value /(kW)']}
        # starts the create_sink method with the parameters set before
        self.create_sink(de, inflow_args)
        # returns logging info
        logging.info('   ' + 'Sink created: ' + de['label'])
    
    def timeseries_sink(self, de, filepath):
        """ Creates a sink object with a fixed input. The input must be
        given as a time series in the scenario file.
        In this context the method uses the create_sink method.
        ----
        Keyword arguments:
            de : obj:'dict'
                --  dictionary containing all information for
                the creation of an oemof sink. At least the
                following key-value-pairs have to be included:
                    - 'label'
                    - 'nominal value /(kW)'
            
            filepath: String
                -- path to .xlsx scenario-file containing a
                "time_series" sheet
        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """
        # imports the time_series sheet of the scenario file
        time_series = pd.read_excel(filepath, sheet_name='time_series')
        # sets the nominal value
        args = {'nominal_value': de['nominal value /(kW)']}
        if de['fixed'] == 0:
            # sets the attributes for an unfixed time_series sink
            args.update({'min': time_series[de['label'] + '.min'].tolist(),
                         'max': time_series[de['label'] + '.max'].tolist()})
        elif de['fixed'] == 1:
            # sets the attributes for a fixed time_series sink
            args.update({'fix': time_series[de['label'] + '.fix'].tolist()})
        # starts the create_sink method with the parameters set before
        self.create_sink(de, args)
        
        # returns logging info
        logging.info('   ' + 'Sink created: ' + de['label'])
    
    def slp_sink(self, de, filepath):
        """ Creates a sink with a residential or commercial
        SLP time series.
        
        Creates a sink with inputs according to VDEW standard
        load profiles, using oemofs demandlib.
        Used for the modelling of residential or commercial
        electricity demand.
        In this context the method uses the create_sink method.
        ----
        Keyword arguments:
            de : obj:'dict'
                --  dictionary containing all information for
                the creation of an oemof sink. At least the
                following key-value-pairs have to be included:
                    - 'label'
                    - 'load profile'
                    - 'annual demand /(kWh/a)'
                    - 'building class [HEAT SLP ONLY]'
                    - 'wind class [HEAT SLP ONLY]'
        
        
            filepath : String
                -- -- path to .xlsx scenario-file containing a
                "energysystem" sheet
        
        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """
        heat_slps = ['efh', 'mfh']
        heat_slps_commercial = \
            ['gmf', 'gpd', 'ghd', 'gwa', 'ggb', 'gko', 'gbd', 'gba',
             'gmk', 'gbh', 'gga', 'gha']
        electricity_slps = \
            ['h0', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'l0', 'l1', 'l2']
        # Import weather Data
        data = pd.read_csv(os.path.join(
            os.path.dirname(__file__)) + '/interim_data/weather_data.csv')
        # Importing timesystem parameters from the scenario
        nd = pd.read_excel(filepath, sheet_name='energysystem')
        ts = next(nd.iterrows())[1]
        temp_resolution = ts['temporal resolution']
        periods = ts["periods"]
        start_date = str(ts['start date'])
        
        # Converting start date into datetime format
        start_date = \
            datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        
        # Create DataFrame
        demand = pd.DataFrame(
                index=pd.date_range(pd.datetime(start_date.year,
                                                start_date.month,
                                                start_date.day,
                                                start_date.hour),
                                    periods=periods, freq=temp_resolution))
        # creates time series
        if de['load profile'] in heat_slps_commercial \
                or de['load profile'] in heat_slps:
            # sets the parameters of the heat slps
            args = {'temperature': data['temperature'],
                    'shlp_type': de['load profile'],
                    'wind_class': de['wind class [HEAT SLP ONLY]'],
                    'annual_heat_demand': 1,
                    'name': de['load profile']}
            if de['load profile'] in heat_slps:
                # adds the building class which is only necessary for
                # the non commercial slps
                args.update(
                    {'building_class': de['building class [HEAT SLP ONLY]']})
            demand[de['load profile']] = bdew.HeatBuilding(
                demand.index, **args).get_bdew_profile()
        elif de['load profile'] in electricity_slps:
            year = datetime.datetime.strptime(str(ts['start date']),
                                              '%Y-%m-%d %H:%M:%S').year
            # Imports standard load profiles
            e_slp = bdew.ElecSlp(year)
            demand = e_slp.get_profile({de['load profile']: 1})
            # creates time series based on standard load profiles
            demand = demand.resample(temp_resolution).mean()
        # sets the nominal value
        args = {'nominal_value': de['annual demand /(kWh/a)']}
        if de['fixed'] == 1:
            # sets the parameters for a fixed sink
            args.update({'fix': demand[de['load profile']]})
        elif de['fixed'] == 0:
            # sets the parameters for an unfixed sink
            args.update({'max': demand[de['load profile']]})
        # starts the create_sink method with the parameters set before
        self.create_sink(de, args)
        # returns logging info
        logging.info('   ' + 'Sink created: ' + de['label'])
    
    def richardson_sink(self, de, filepath):
        """Creates a sink with stochastically timeseries.
        
        Creates a sink with stochastically generated input, using
        richardson.py. Used for the modelling of residential electricity
        demands. In this context the method uses the create_sink method.
        ----
        Keyword arguments:
            de : obj:'dict'
                --  dictionary containing all information for
                the creation of an oemof sink. At least the
                following key-value-pairs have to be included:
                    - 'label'
                    - 'fixed'
                    - 'annual demand /(kWh/a)'
                    - 'occupants [RICHARDSON]'
        
            filepath : String
                -- path to .xlsx scenario-file containing a
                "energysystem" sheet
        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """
    
        import richardsonpy.classes.occupancy as occ
        import richardsonpy.classes.electric_load as eload
        # Import Weather Data
        dirhi_csv = pd.read_csv(
            os.path.join(os.path.dirname(__file__))
            + '/interim_data/weather_data.csv', usecols=['dirhi'], dtype=float)
        dirhi = dirhi_csv.values.flatten()
        dhi_csv = pd.read_csv(
            os.path.join(os.path.dirname(__file__))
            + '/interim_data/weather_data.csv', usecols=['dhi'], dtype=float)
        dhi = dhi_csv.values.flatten()
        
        # Conversion of irradiation from W/m^2 to kW/m^2
        dhi = dhi / 1000
        dirhi = dirhi / 1000
        
        # Reads the temporal resolution from the scenario file
        nd = pd.read_excel(filepath, sheet_name='energysystem')
        ts = next(nd.iterrows())[1]
        temp_resolution = ts['temporal resolution']
        
        # sets the occupancy rates
        nb_occ = de['occupants [RICHARDSON]']
        
        # Workaround, because richardson.py only allows a maximum
        # of 5 occupants
        if nb_occ > 5:
            nb_occ = 5
        
        # sets the temporal resolution of the richardson.py time series,
        # depending on the temporal resolution of the entire model (as
        # defined in the input spreadsheet)
        if temp_resolution == 'H':
            timestep = 3600  # in seconds
        elif temp_resolution == 'h':
            timestep = 3600  # in seconds
        elif temp_resolution == 'min':
            timestep = 60  # in seconds
        elif temp_resolution == 's':
            timestep = 1  # in seconds
        else:
            raise SystemError('Invalid Temporal Resolution')
        
        #  Generate occupancy object
        #  (necessary as input for electric load gen)
        occ_obj = occ.Occupancy(number_occupants=nb_occ)
        
        #  Generate stochastic electric power object
        el_load_obj = eload.ElectricLoad(occ_profile=occ_obj.occupancy,
                                         total_nb_occ=nb_occ, q_direct=dirhi,
                                         q_diffuse=dhi, timestep=timestep)
        
        # creates richardson.py time series
        load_profile = el_load_obj.loadcurve
        richardson_demand = (sum(el_load_obj.loadcurve)
                             * timestep / (3600 * 1000))
        annual_demand = de['annual demand /(kWh/a)']
        
        # Disables the stochastic simulation of the total yearly demand
        # by scaling the generated time series using the total energy
        # demand of the sink generated in the spreadsheet
        demand_ratio = annual_demand / richardson_demand
        # sets nominal value
        args = {'nominal_value': 0.001 * demand_ratio}
        if de['fixed'] == 1:
            # sets attributes for a fixed richardson sink
            args.update({'fix': load_profile})
        elif de['fixed'] == 0:
            # sets attributes for an unfixed richardson sink
            args.update({'max': load_profile})
        # starts the create_sink method with the parameters set before
        self.create_sink(de, args)
        # returns logging info
        logging.info('   ' + 'Sink created: ' + de['label'])
    
    def __init__(self, nodes_data, busd, nodes, filepath):
        """ Inits the sink class.
        ----
        Keyword arguments:
        
            nodes_data: obj:'dict'
                --  dictionary containing parameters of sinks to be
                created.The following data have to be provided:
                    - 'label'
                    - 'active'
                    - 'fixed'
                    - 'input'
                    - 'load profile'
                    - 'nominal value /(kW)'
                    - 'annual demand /(kWh/a)'
                    - 'occupants [Richardson]'
                    - 'building class [HEAT SLP ONLY]'
                    - 'wind class [HEAT SLP ONLY]'
            
            
            busd: obj:'dict'
                --  dictionary containing the buses of the energy system
            
            nodes: obj:'list'
                --  list of components created before(can be empty)
            
            filepath: obj:'str'
                -- path to .xlsx scenario-file containing a
                "weather data" sheet with timeseries for
                    -   "dhi"(diffuse horizontal irradiation)
                        W / m ^ 2
                    -   "dirhi"(direct horizontal irradiance)
                        W / m ^ 2
                    -   "pressure" in Pa
                    -   "temperature" in °C
                    -   "windspeed" in m / s
                    -   "z0"(roughness length) in m
            
        ---
        Other variables:
        
            nodes_sinks: obj:'list'
                -- class intern list of sinks that are already created
        
        ---
        Contributors:
        - Christian Klemm - christian.klemm@fh-muenster.de
        - Gregor Becker - gregor.becker@fh-muenster.de
        """
        
        # Delete possible residues of a previous run from the class
        # internal list nodes_sinks
        self.nodes_sinks = []
        # Initialise a class intern copy of the bus dictionary
        self.busd = busd.copy()
        
        # richardson.py and demandlib can only read .csv data sets,
        # so the weather data from the .xlsx scenario file have to be
        # converted into a .csv data set and saved
        read_file = pd.read_excel(filepath, sheet_name='weather data')
        read_file.to_csv(
            os.path.join(os.path.dirname(__file__))
            + '/interim_data/weather_data.csv', index=None, header=True)
        
        # Create sink objects
        for i, de in nodes_data['demand'].iterrows():
            slps = \
                ['efh', 'mfh', 'gmf', 'gpd', 'ghd', 'gwa', 'ggb', 'gko', 'gbd',
                 'gba', 'gmk', 'gbh', 'gga', 'gha', 'h0', 'g0', 'g1', 'g2',
                 'g3', 'g4', 'g5', 'g6', 'l0', 'l1', 'l2']
            
            if de['active']:
            
                # Create Sinks un-fixed time-series
                if de['load profile'] == 'x':
                    self.unfixed_sink(de)
                
                # Create Sinks with Time-series
                elif de['load profile'] == 'timeseries':
                    self.timeseries_sink(de, filepath)
                
                # Create Sinks with SLP's
                elif de['load profile'] in slps:
                    self.slp_sink(de, filepath)
                
                # Richardson
                elif de['load profile'] == 'richardson':
                    self.richardson_sink(de, filepath)
        
        # appends created sinks on the list of nodes
        for i in range(len(self.nodes_sinks)):
            nodes.append(self.nodes_sinks[i])


class Transformers:
    """
    Creates a transformer object.
    Creates transformers objects as defined in 'nodes_data' and adds
    them to the list of components 'nodes'.
    ----
    Keyword arguments:
        nodes_data : obj:'dict'
            -- dictionary containing data from excel scenario file. The
            following data have to be provided:
                - label,
                - active,
                - transformer type,
                - input,
                - output,
                - output2,
                - efficiency,
                - efficiency2,
                - variable input costs /(CU/kWh),
                - variable output costs /(CU/kWh),
                - existing capacity /(kW),
                - max. investment capacity /(kW),
                - min. investment capacity /(kW),
                - periodical costs /(CU/(kW a))
        busd : obj:'dict'
            -- dictionary containing the buses of the energy system
        nodes : obj:'list'
            -- list of components
    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 13.02.2020
    """
    # intern variables
    nodes_transformer = []
    busd = None
    
    def create_transformer(self, tf, inputs, outputs, conversion_factors):
        self.nodes_transformer.append(solph.Transformer(
                label=tf['label'], **inputs, **outputs, **conversion_factors))
        logging.info('   ' + 'Transformer created: ' + tf['label'])
    
    def generic_transformer(self, tf):
        """
        Creates a Generic Transformer object.
        Creates a generic transformer with the parameters given in
        'nodes_data' and adds it to the list of components 'nodes'.
        ----
        Keyword arguments:
            tf : obj:'dict'
            -- dictionary containing all information for thecreation of
            an oemof transformer.
            At least the following key-value-pairs have to be included:
                - 'label'
                - 'input'
                - 'output'
                - 'output2'
                - 'efficiency'
                - 'efficiency2'
                - 'variable input costs / (CU/kWh)'
                - 'variable output costs / (CU/kWh)'
                - 'variable output costs 2 / (CU/kWh)'
                - 'periodical costs / (CU/kWh)'
                - 'min. investment capacity / (kW)'
                - 'max. investment capacity / (kW)'
                - 'existing capacity / (kW)'
                - 'Non-Convex Investment'
                - 'Fix Investment Costs / (CU/a)'
        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """
        outputs = \
            {self.busd[tf['output']]: solph.Flow(
                    variable_costs=tf['variable output costs /(CU/kWh)'],
                    emission_factor=tf[
                        'variable output constraint costs /(CU/kWh)'],
                    investment=solph.Investment(
                        ep_costs=tf['periodical costs /(CU/(kW a))'],
                        periodical_constraint_costs=tf[
                            'periodical constraint costs /(CU/(kW a))'],
                        minimum=tf['min. investment capacity /(kW)'],
                        maximum=tf['max. investment capacity /(kW)'],
                        existing=tf['existing capacity /(kW)'],
                        nonconvex=True if
                        tf['Non-Convex Investment'] == 1 else False,
                        offset=tf['Fix Investment Costs /(CU/a)']))}
        conversion_factors = {self.busd[tf['output']]: tf['efficiency']}
        # Defines Capacity values for the second transformer output
        if tf['output2'] not in ['None', 'none', 'x']:
            existing_capacity2 = \
                ((float(tf['efficiency2']) / float(tf['efficiency']))
                 * float(tf['existing capacity /(kW)']))
            minimum_capacity2 = ((float(tf['efficiency2'])
                                  / float(tf['efficiency']))
                                 * float(tf['min. investment capacity /(kW)']))
            maximum_capacity2 = ((float(tf['efficiency2'])
                                  / float(tf['efficiency']))
                                 * float(tf['max. investment capacity /(kW)']))
            # Creates transformer object and adds it to the list of
            # components
            outputs.update(
                    {self.busd[tf['output2']]: solph.Flow(
                        variable_costs=tf['variable output costs 2 /(CU/kWh)'],
                        emission_factor=tf[
                            'variable output constraint costs 2 /(CU/kWh)'],
                        investment=solph.Investment(
                            ep_costs=0,
                            existing=existing_capacity2,
                            minimum=minimum_capacity2,
                            maximum=maximum_capacity2,
                            nonconvex=True if
                            tf['Non-Convex Investment'] == 1 else False,
                            offset=tf['Fix Investment Costs /(CU/a)']))})
            conversion_factors.update(
                    {self.busd[tf['output2']]: tf['efficiency2']})
        outputs = {"outputs": outputs}
        
        conversion_factors = {"conversion_factors": conversion_factors}
        inputs = {"inputs": {self.busd[tf['input']]: solph.Flow(
                variable_costs=tf['variable input costs /(CU/kWh)'],
                emission_factor=tf['variable input constraint costs /(CU/kWh)'])
        }}
        self.create_transformer(tf, inputs, outputs, conversion_factors)
        
    def compression_heat_transformer(self, tf, data):
        """
            Creates a Compression Heat Pump or Compression Chiller by using
            oemof.thermal and adds it to the list of components 'nodes'.
            Parameters are given in 'nodes_data' are used .


            :param tf: has to contain the following keyword arguments

                - 'label'
                - 'active'
                - 'transformer type': 'compression_heat_transformer'
                - 'mode':
                    - 'heat_pump' or
                    - 'chiller'
                - 'input'
                - 'output'
                - 'efficiency'
                - 'variable input costs /(CU/kWh)'
                - 'variable output costs /(CU/kWh)'
                - 'variable input constraint costs /(CU/kWh)'
                - 'variable output constraint costs /(CU/kWh)'
                - 'existing capacity /(kW)'
                - 'min. investment capacity /(kW)'
                - 'max. investment capacity /(kW)'
                - 'periodical costs /(CU/(kW a))'
                - 'periodical constraint costs /(CU/(kW a))'
                - 'Non-Convex Investment'
                - 'Fix Investment Costs /(CU/a)'
                - 'heat source (CHT)'
                - 'temperature high /deg C (CHT)'
                - 'temperature low /deg C (CHT)'
                - 'quality grade (CHT)'
                - 'area /(sq m) (CHT)'
                - 'length of the geoth. probe /m (CHT)'
                - 'heat extraction /(kW/(m*a)) (CHT)'
                - 'min. borehole area /(sq m) (CHT)'
                - 'temp threshold icing (CHT)'
                - 'factor icing (CHT)'

            :type tf: dict

            :param data: weather data
            :type data: dict

            Janik Budde - Janik.Budde@fh-muenster.de, 30.07.2020
            Yannick Wittor - yw090223@fh-muenster.de, 07.01.2021
        """
        
        # import oemof.thermal in order to calculate the cop
        import oemof.thermal.compression_heatpumps_and_chillers \
            as cmpr_hp_chiller
        import math

        # creates one oemof-bus object for compression heat transformers
        # depending on mode of operation
        if tf['mode'] == 'heat_pump':
            temp = '_low_temp'
        elif tf['mode'] == 'chiller':
            temp = '_high_temp'
        bus = solph.Bus(label=tf['label'] + temp + '_bus')
        
        # adds the bus object to the list of components "nodes"
        self.nodes_transformer.append(bus)
        self.busd[tf['label'] + temp + '_bus'] = bus
        
        # returns logging info
        logging.info('   ' + 'Bus created: ' + tf['label'] + temp + '_bus')
        
        # differentiation between heat sources under consideration of mode
        # of operation
        # ground as a heat source referring to vertical-borehole
        # ground-coupled compression heat transformers
        if tf['heat source (CHT)'] == "Ground":
        
            # borehole that acts as heat source for the transformer
            cmpr_heat_transformer_label = tf['label'] + \
                                          temp + '_ground_source'
            
            # the capacity of a borehole is limited by the area
            heatsource_capacity = \
                tf['area /(sq m) (CHT)'] * \
                (tf['length of the geoth. probe /m (CHT)']
                 * tf['heat extraction /(kW/(m*a)) (CHT)']
                 / tf['min. borehole area /(sq m) (CHT)'])
        # ground water as a heat source
        elif tf['heat source (CHT)'] == "GroundWater":
        
            # ground water that acts as heat source for the transformer
            cmpr_heat_transformer_label = tf['label'] + \
                                          temp + '_groundwater_source'
            
            # the capacity of ambient ground water is not limited
            heatsource_capacity = math.inf
        
        # ambient air as a heat source
        elif tf['heat source (CHT)'] == "Air":
        
            # ambient air that acts as heat source for the transformer
            cmpr_heat_transformer_label = tf['label'] + temp + '_air_source'
            
            # the capacity of ambient air is not limited
            heatsource_capacity = math.inf
        
        # surface water as a heat source
        elif tf['heat source (CHT)'] == "Water":
        
            # ambient air that acts as heat source for the transformer
            cmpr_heat_transformer_label = tf['label'] + temp + '_water_source'
            
            # the capacity of ambient water is not limited
            heatsource_capacity = math.inf
        else:
            raise SystemError(tf['label'] + " Error in heat source attribute")
        maximum = heatsource_capacity
        # Creates heat source for transformer. The heat source costs are
        # considered by the transformer.
        self.nodes_transformer.append(
            solph.Source(label=cmpr_heat_transformer_label,
                         outputs={self.busd[
                             tf['label'] + temp + '_bus']: solph.Flow(
                                 investment=solph.Investment(ep_costs=0,
                                                             minimum=0,
                                                             maximum=maximum,
                                                             existing=0),
                                 variable_costs=0)}))
        
        # Returns logging info
        logging.info(
                '   ' + 'Heat Source created: ' + tf['label']
                + temp + '_source')
        
        # set temp_high and temp_low and icing considering different
        # heat sources and the mode of operation
        if tf['heat source (CHT)'] == "Ground":
            if tf['mode'] == 'heat_pump':
                temp_low = data['ground_temp']
            elif tf['mode'] == 'chiller':
                temp_high = data['ground_temp']
        elif tf['heat source (CHT)'] == "GroundWater":
            if tf['mode'] == 'heat_pump':
                temp_low = data['groundwater_temp']
            elif tf['mode'] == 'chiller':
                temp_high = data['groundwater_temp']
        elif tf['heat source (CHT)'] == "Air":
            if tf['mode'] == 'heat_pump':
                temp_low = data['temperature']
            elif tf['mode'] == 'chiller':
                temp_high = data['temperature'].copy()
                temp_low_value = tf['temperature low /deg C (CHT)']
                # low temperature as formula to avoid division by zero error
                for index, value in enumerate(temp_high):
                    if value == temp_low_value:
                        temp_high[index] = temp_low_value + 0.1
        elif tf['heat source (CHT)'] == "Water":
            if tf['mode'] == 'heat_pump':
                temp_low = data['water_temp']
            elif tf['mode'] == 'chiller':
                temp_high = data['water_temp']
        else:
            raise SystemError('problem with HeatSource')
        
        if tf['mode'] == 'heat_pump':
            temp_threshold_icing = tf['temp threshold icing (CHT)']
            factor_icing = tf['factor icing (CHT)']
            temp_high = [tf['temperature high /deg C (CHT)']]
        elif tf['mode'] == 'chiller':
            # variable "icing" is not important in cooling mode
            temp_threshold_icing = None
            factor_icing = None
            temp_low = [tf['temperature low /deg C (CHT)']]
        # calculation of COPs with set parameters
        cops_hp = cmpr_hp_chiller.calc_cops(
                temp_high=temp_high,
                temp_low=temp_low,
                quality_grade=tf['quality grade (CHT)'],
                temp_threshold_icing=temp_threshold_icing,
                factor_icing=factor_icing,
                mode=tf['mode'])
        logging.info('   ' + tf['label']
                     + ", Average Coefficient of Performance (COP): {:2.2f}"
                     .format(numpy.mean(cops_hp)))

        # Creates transformer object and adds it to the list of components
        inputs = {"inputs": {self.busd[tf['input']]: solph.Flow(
                variable_costs=tf['variable input costs /(CU/kWh)'],
                emission_factor=
                tf['variable input constraint costs /(CU/kWh)']),
                self.busd[tf['label'] + temp + '_bus']: solph.Flow(
                variable_costs=0)}}
        outputs = {"outputs": {self.busd[tf['output']]: solph.Flow(
                variable_costs=tf['variable output costs /(CU/kWh)'],
                emission_factor=tf[
                    'variable output constraint costs /(CU/kWh)'],
                investment=solph.Investment(
                        ep_costs=tf['periodical costs /(CU/(kW a))'],
                        minimum=tf['min. investment capacity /(kW)'],
                        maximum=tf['max. investment capacity /(kW)'],
                        periodical_constraint_costs=tf[
                            'periodical constraint costs /(CU/(kW a))'],
                        existing=tf['existing capacity /(kW)']))}}
        conversion_factors = {
            "conversion_factors": {
                self.busd[tf['label'] + temp + '_bus']:
                    [((cop - 1) / cop)/tf['efficiency']
                     for cop in cops_hp],
                self.busd[tf['input']]: [1 / cop for cop in cops_hp]}}
        self.create_transformer(tf, inputs, outputs, conversion_factors)
    
    def genericchp_transformer(self, tf, nd):
        """
            Creates a Generic CHP transformer object.
            Creates a generic chp transformer with the parameters given
            in 'nodes_data' and adds it to the list of components
            'nodes'.
            ----
            Keyword arguments:
            tf : obj:'dict'
                -- dictionary containing all information for
                the creation of an oemof transformer.
                At least the following key-value-pairs have to be included:
                    - 'label'
                    - 'input'
                    - 'output'
                    - 'output2'
                    - 'efficiency'
                    - 'efficiency2'
                    - 'variable input costs / (CU/kWh)'
                    - 'variable output costs / (CU/kWh)'
                    - 'variable output costs 2 / (CU/kWh)'
                    - 'periodical costs / (CU/kWh)'
                    - 'min. investment capacity / (kW)'
                    - 'max. investment capacity / (kW)'
                    - 'existing capacity / (kW)'
                    - 'Non-Convex Investment'
                    - 'Fix Investment Costs / (CU/a)'
            @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """
        # counts the number of periods within the given datetime index
        # and saves it as variable
        # (number of periods is required for creating generic chp transformers)
        # Importing timesystem parameters from the scenario
        ts = next(nd['energysystem'].iterrows())[1]
        periods = ts['periods']
        # creates genericCHP transformer object and adds it to the
        # list of components
        self.nodes_transformer.append(solph.components.GenericCHP(
                label=tf['label'],
                fuel_input={
                    self.busd[tf['input']]: solph.Flow(
                            H_L_FG_share_max=[
                                tf['share of flue gas loss at max heat '
                                   'extraction [GenericCHP]']
                                for p in range(0, periods)],
                            H_L_FG_share_min=[
                                tf['share of flue gas loss at min heat '
                                   'extraction [GenericCHP]']
                                for p in range(0, periods)],
                            variable_costs=tf[
                                'variable input costs /(CU/kWh)'],
                            emission_factor=
                            tf['variable input constraint costs /(CU/kWh)'])},
                electrical_output={
                    self.busd[tf['output']]: solph.Flow(
                            investment=solph.Investment(
                                    ep_costs=tf[
                                        'periodical costs /(CU/(kW a))'],
                                    periodical_constraint_costs=tf[
                                        'periodical constraint costs /(CU/(kW a))'],
                                    minimum=tf[
                                        'min. investment capacity /(kW)'],
                                    maximum=tf[
                                        'max. investment capacity /(kW)'],
                                    existing=tf['existing capacity /(kW)']),
                            P_max_woDH=[
                                tf['max. electric power without district '
                                   'heating [GenericCHP]']
                                for p in range(0, periods)],
                            P_min_woDH=[tf['min. electric power without '
                                           'district heating [GenericCHP]']
                                        for p in range(0, periods)],
                            Eta_el_max_woDH=[
                                tf['el. eff. at max. fuel flow w/o distr. '
                                   'heating [GenericCHP]']
                                for p in range(0, periods)],
                            Eta_el_min_woDH=[
                                tf['el. eff. at min. fuel flow w/o distr. '
                                   'heating [GenericCHP]']
                                for p in range(0, periods)],
                            variable_costs=tf[
                                'variable output costs /(CU/kWh)'],
                            emission_factor=tf[
                                'variable output constraint costs /(CU/kWh)']
                            )
                        },
                heat_output={self.busd[tf['output2']]: solph.Flow(
                    Q_CW_min=[tf['minimal therm. condenser load to '
                                 'cooling water [GenericCHP]']
                              for p in range(0, periods)],
                    variable_costs=tf[
                        'variable output costs 2 /(CU/kWh)'],
                    emission_factor=tf[
                        'variable output constraint costs 2/(CU/kWh)']
                )},
                Beta=[tf['power loss index [GenericCHP]']
                      for p in range(0, periods)],
                # fixed_costs=0,
                back_pressure=tf['back pressure [GenericCHP]'],
                ))

        # returns logging info
        logging.info('   ' + 'Transformer created: ' + tf['label'])

    def absorption_heat_transformer(self, tf, data):
        """
            Creates an absorption heat transformer object with the parameters
            given in 'nodes_data' and adds it to the list of components 'nodes'


            :param tf: has to contain the following keyword arguments

                - 'label'
                - 'active'
                - 'transformer type': 'absorption_heat_transformer'
                - 'mode': 'chiller'
                - 'input'
                - 'output'
                - 'efficiency'
                - 'variable input costs /(CU/kWh)'
                - 'variable output costs /(CU/kWh)'
                - 'variable input constraint costs /(CU/kWh)'
                - 'variable constraint costs /(CU/kWh)'
                - 'existing capacity /(kW)'
                - 'min. investment capacity /(kW)'
                - 'max. investment capacity /(kW)'
                - 'periodical costs /(CU/(kW a))'
                - 'periodical constraint costs /(CU/(kW a))'
                - 'Non-Convex Investment'
                - 'Fix Investment Costs /(CU/a)'
                - 'name (AbsCH)'
                    - name refers to models of absorption heat transformers
                      with different equation parameters. See documentation
                      for possible inputs.
                - 'high temperature /deg C (AbsCH)'
                - 'chilling temperature /deg C (AbsCH)'
                - 'electrical input conversion factor (AbsCH)'
                - 'recooling temperature difference /deg C (AbsCH)'

            :type tf: dict

            :param data: weather data
            :type data: dict

            Yannick Wittor - yw090223@fh-muenster.de, 07.01.2021
        """
        # import oemof.thermal in order to calculate COP
        import oemof.thermal.absorption_heatpumps_and_chillers \
            as abs_hp_chiller
        from math import inf
        import numpy as np

        # Import characteristic equation parameters
        char_para = pd.read_csv(os.path.join(
            os.path.dirname(__file__)) +
                            '/technical_data/characteristic_parameters.csv')

        # creates one oemof-bus object for compression heat transformers
        # depending on mode of operation
        if tf['mode'] == 'heat_pump':
            temp = '_low_temp'
        elif tf['mode'] == 'chiller':
            temp = '_high_temp'

        bus_label = tf['label'] + temp + '_bus'
        source_label = tf['label'] + temp + '_source'
        bus = solph.Bus(label=bus_label)

        # adds the bus object to the list of components "nodes"
        self.nodes_transformer.append(bus)
        self.busd[bus_label] = bus

        # returns logging info
        logging.info('   ' + 'Bus created: ' + bus_label)

        # creates a source object as high temperature heat source
        self.nodes_transformer.append(
            solph.Source(label=source_label,
                         outputs={self.busd[
                             bus_label]:
                                solph.Flow(variable_costs=
                                           tf['variable input costs /(CU/kWh)']
                                           )}))

        # Returns logging info
        logging.info(
            '   ' + 'Heat Source created:' + source_label)

        # Calculates cooling temperature in absorber/evaporator depending on
        # ambient temperature of recooling system
        data_np = np.array(data['temperature'])
        t_cool = data_np + \
            tf['recooling temperature difference /deg C (AbsCH)']
        t_cool = list(map(int, t_cool))

        # Calculation of characteristic temperature difference
        chiller_name = tf['name (AbsCH)']
        ddt = abs_hp_chiller.calc_characteristic_temp(
            t_hot=[tf['high temperature /deg C (AbsCH)']],
            t_cool=t_cool,
            t_chill=[tf['chilling temperature /deg C (AbsCH)']],
            coef_a=char_para[(char_para['name'] ==
                              chiller_name)]['a'].values[0],
            coef_e=char_para[(char_para['name'] ==
                              chiller_name)]['e'].values[0],
            method='kuehn_and_ziegler')
        # Calculation of cooling capacity
        q_dots_evap = abs_hp_chiller.calc_heat_flux(
            ddts=ddt,
            coef_s=char_para[(char_para['name'] ==
                              chiller_name)]['s_E'].values[0],
            coef_r=char_para[(char_para['name'] ==
                              chiller_name)]['r_E'].values[0],
            method='kuehn_and_ziegler')
        # Calculation of driving heat
        q_dots_gen = abs_hp_chiller.calc_heat_flux(
            ddts=ddt,
            coef_s=char_para[(char_para['name'] ==
                              chiller_name)]['s_G'].values[0],
            coef_r=char_para[(char_para['name'] ==
                              chiller_name)]['r_G'].values[0],
            method='kuehn_and_ziegler')
        # Calculation of COPs
        cops_abs = \
            [Qevap / Qgen for Qgen, Qevap in zip(q_dots_gen, q_dots_evap)]

        logging.info('   ' + tf['label']
                     + ", Average Coefficient of Performance (COP): {:2.2f}"
                     .format(numpy.mean(cops_abs)))

        # Set in- and outputs with conversion factors and creates transformer
        # object and adds it to  the list of components
        inputs = {"inputs": {self.busd[tf['input']]: solph.Flow(
                 variable_costs=tf['variable input costs /(CU/kWh)'],
                 emission_factor=
                 tf['variable input constraint costs /(CU/kWh)']),
                 self.busd[tf['label'] + temp + '_bus']: solph.Flow(
                 variable_costs=0)}}
        outputs = {"outputs": {self.busd[tf['output']]: solph.Flow(
                variable_costs=tf['variable output costs /(CU/kWh)'],
                emission_factor=tf['variable output constraint costs /(CU/kWh)'],
                investment=solph.Investment(
                        ep_costs=tf['periodical costs /(CU/(kW a))'],
                        minimum=tf['min. investment capacity /(kW)'],
                        maximum=tf['max. investment capacity /(kW)'],
                        existing=tf['existing capacity /(kW)']))}}
        conversion_factors = {
            "conversion_factors": {
                self.busd[tf['output']]:
                    [cop for cop in cops_abs],
                self.busd[tf['input']]:
                    tf['electrical input conversion factor (AbsCH)']
                }}
        self.create_transformer(tf, inputs, outputs, conversion_factors)

    def __init__(self, nodes_data, nodes, busd):
    
        # renames variables
        self.busd = busd
        self.nodes_transformer = []

        # Import weather Data
        data = pd.read_csv(os.path.join(
            os.path.dirname(__file__)) + '/interim_data/weather_data.csv')

        # creates a transformer object for every transformer item within nd
        for i, t in nodes_data['transformers'].iterrows():
            if t['active']:
        
                # Create Generic Transformers
                if t['transformer type'] == 'GenericTransformer':
                    self.generic_transformer(t)
                
                # Create Compression Heat Transformer
                elif t['transformer type'] == 'compression_heat_transformer':
                    self.compression_heat_transformer(t, data)
                
                # Create Extraction Turbine CHPs
                elif t['transformer type'] == 'ExtractionTurbineCHP':
                    logging.info('   ' + 'WARNING: ExtractionTurbineCHP are'
                                         ' currently not a part of this model '
                                         'generator, but will be added later.')
                
                # Create Generic CHPs
                elif t['transformer type'] == 'GenericCHP':
                    self.genericchp_transformer(t, nodes_data)
                
                # Create Offset Transformers
                elif t['transformer type'] == 'OffsetTransformer':
                    logging.info(
                        '   ' + 'WARNING: OffsetTransformer are currently'
                        + ' not a part of this model generator, but will'
                        + ' be added later.')

                # Create Absorption Chiller
                elif t['transformer type'] == 'absorption_heat_transformer':
                    self.absorption_heat_transformer(t, data)

                # Error Message for invalid Transformers
                else:
                    logging.info('   ' + 'WARNING: \''
                                 + t['label']
                                 + '\' was not created, because \''
                                 + t['transformer type']
                                 + '\' is no valid transformer type.')
        
        # appends created transformers to the list of nodes
        for i in range(len(self.nodes_transformer)):
            nodes.append(self.nodes_transformer[i])


class Storages:
    """
    Creates oemof storage objects as defined in 'nodes_data' and adds them to
    the list of components 'nodes'.
    """
    def generic_storage(self, s):
        """
            Creates a generic storage object with the parameters
            given in 'nodes_data' and adds it to the list of components 'nodes


            :param s: has to contain the following keyword arguments

                - 'label'
                - 'active'
                - 'storage type': 'Generic'
                - 'bus'
                - 'existing capacity /(kWh)'
                - 'min. investment capacity /(kWh)'
                - 'max. investment capacity /(kWh)'
                - 'periodical costs /(CU/(kWh a))'
                - 'periodical constraint costs /(CU/(kWh a))'
                - 'Non-Convex Investments'
                - 'Fix Investment Costs /(CU/a)'
                - 'input/capacity ratio (invest)'
                - 'output/capacity ratio (invest)'
                - 'capacity loss (Generic only)'
                - 'efficiency inflow'
                - 'efficiency outflow'
                - 'initial capacity'
                - 'capacity min'
                - 'capacity max'
                - 'variable input costs'
                - 'variable output costs'
                - 'variable input constraint costs /(CU/kWh)'
                - 'variable output constraint costs /(CU/kWh)'

            :type s: dict

            Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """

        # creates storage object and adds it to the
        # list of components
        self.nodes.append(
            solph.components.GenericStorage(
                label=s['label'],
                inputs={self.busd[s['bus']]: solph.Flow(
                    variable_costs=s[
                        'variable input costs'],
                    emission_factor=s[
                        'variable input constraint costs /'
                        '(CU/kWh)']
                )},
                outputs={self.busd[s['bus']]: solph.Flow(
                    variable_costs=s[
                        'variable output costs'],
                    emission_factor=s[
                        'variable output constraint costs /'
                        '(CU/kWh)']
                )},
                loss_rate=s['capacity loss (Generic only)'],
                inflow_conversion_factor=s[
                    'efficiency inflow'],
                outflow_conversion_factor=s[
                    'efficiency outflow'],
                invest_relation_input_capacity=s[
                    'input/capacity ratio (invest)'],
                invest_relation_output_capacity=s[
                    'output/capacity ratio (invest)'],
                investment=solph.Investment(
                    ep_costs=s[
                        'periodical costs /(CU/(kWh a))'],
                    periodical_constraint_costs=s[
                        'periodical constraint costs /(CU/(kWh a))'],
                    existing=s[
                        'existing capacity /(kWh)'],
                    minimum=s[
                        'min. investment capacity /(kWh)'],
                    maximum=s[
                        'max. investment capacity /(kWh)'],
                    nonconvex=True if
                    s['Non-Convex Investment'] == 1 else False,
                    offset=s['Fix Investment Costs /(CU/a)'])))

        # returns logging info
        logging.info('   ' + 'Storage created: ' + s['label'])

    def stratified_thermal_storage(self, s, data):
        """
            Creates a stratified thermal storage object with the parameters
            given in 'nodes_data' and adds it to the list of components 'nodes'


            :param s: has to contain the following keyword arguments:

                - 'label'
                - 'active'
                - 'storage type': 'Stratified'
                - 'bus'
                - 'existing capacity /(kWh)'
                - 'min. investment capacity /(kWh)'
                - 'max. investment capacity /(kWh)'
                - 'periodical costs /(CU/(kWh a))'
                - 'periodical constraint costs /(CU/(kWh a))'
                - 'Non-Convex Investments'
                - 'Fix Investment Costs /(CU/a)'
                - 'input/capacity ratio (invest)'
                - 'output/capacity ratio (invest)'
                - 'efficiency inflow'
                - 'efficiency outflow'
                - 'initial capacity'
                - 'capacity min'
                - 'capacity max'
                - 'variable input costs'
                - 'variable output costs'
                - 'variable input constraint costs /(CU/kWh)'
                - 'variable output constraint costs /(CU/kWh)'
                - 'diameter /(m) (Stratified Storage)'
                - 'temperature high /(deg C) (Stratified Storage)'
                - 'temperature low /(deg C) (Stratified Storage)'
                - 'U value /(W/(sqm*K)) (Stratified Storage)'

            :type s: dict

            Yannick Wittor - yw090223@fh-muenster.de, 26.01.2021
        """
        # import functions for stratified thermal storages from oemof thermal
        from oemof.thermal.stratified_thermal_storage import calculate_losses

        # calculations for stratified thermal storage
        loss_rate, fixed_losses_relative, fixed_losses_absolute = \
            calculate_losses(
                s['U value /(W/(sqm*K)) (Stratified Storage)'],
                s['diameter /m (Stratified Storage)'],
                s['temperature high /deg C (Stratified Storage)'],
                s['temperature low /deg C (Stratified Storage)'],
                data['temperature'])

        # creates storage object and adds it to the
        # list of components
        self.nodes.append(
            solph.components.GenericStorage(
                label=s['label'],
                inputs={self.busd[s['bus']]: solph.Flow(
                    variable_costs=s[
                        'variable input costs'],
                    emission_factor=s[
                        'variable input constraint costs /'
                        '(CU/kWh)']
                )},
                outputs={self.busd[s['bus']]: solph.Flow(
                    variable_costs=s[
                        'variable output costs'],
                    emission_factor=s[
                        'variable output constraint costs /'
                        '(CU/kWh)']
                )},
                min_storage_level=s['capacity min'],
                max_storage_level=s['capacity max'],
                loss_rate=loss_rate,
                fixed_losses_relative=fixed_losses_relative,
                fixed_losses_absolute=fixed_losses_absolute,
                inflow_conversion_factor=s[
                    'efficiency inflow'],
                outflow_conversion_factor=s[
                    'efficiency outflow'],
                invest_relation_input_capacity=s[
                    'input/capacity ratio (invest)'],
                invest_relation_output_capacity=s[
                    'output/capacity ratio (invest)'],
                investment=solph.Investment(
                    ep_costs=s[
                        'periodical costs /(CU/(kWh a))'],
                    periodical_constraint_costs=s[
                        'periodical constraint costs /(CU/(kWh a))'],
                    existing=s[
                        'existing capacity /(kWh)'],
                    minimum=s[
                        'min. investment capacity /(kWh)'],
                    maximum=s[
                        'max. investment capacity /(kWh)'],
                    nonconvex=True if
                    s['Non-Convex Investment'] == 1 else False,
                    offset=s['Fix Investment Costs /(CU/a)'])))
        # returns logging info
        logging.info('   ' + 'Storage created: ' + s['label'])

    def __init__(self, nodes_data, nodes, busd):
        """
            Inits the storage class.


            :param nodes_data: The following data have to be provided:

                - 'label'
                - 'active'
                - 'storage type':
                    - 'Generic' or
                    - 'Stratified'
                - 'bus'
                - 'existing capacity /(kWh)'
                - 'min. investment capacity /(kWh)'
                - 'max. investment capacity /(kWh)'
                - 'periodical costs /(CU/(kWh a))'
                - 'periodical constraint costs /(CU/(kWh a))'
                - 'Non-Convex Investments'
                - 'Fix Investment Costs /(CU/a)'
                - 'input/capacity ratio (invest)'
                - 'output/capacity ratio (invest)'
                - 'capacity loss (Generic only)'
                - 'efficiency inflow'
                - 'efficiency outflow'
                - 'initial capacity'
                - 'capacity min'
                - 'capacity max'
                - 'variable input costs'
                - 'variable output costs'
                - 'diameter /(m) (Stratified Storage)'
                - 'temperature high /(deg C) (Stratified Storage)'
                - 'temperature low /(deg C) (Stratified Storage)'
                - 'U value /(W/(sqm*K)) (Stratified Storage)'

            :type nodes_data: dict

            :param busd: dictionary containing the busses of the energy system
            :type busd: dict

            :param nodes: list of components created before (can be empty)
            :type nodes: list

            Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
        """
        # renames variables
        self.busd = busd
        self.nodes = []

        # Import weather Data
        data = pd.read_csv(os.path.join(
            os.path.dirname(__file__)) + '/interim_data/weather_data.csv')

        # creates storage object for every storage element in nodes_data
        for i, s in nodes_data['storages'].iterrows():
            if s['active']:

                # Create Generic Storage
                if s['storage type'] == 'Generic':
                    self.generic_storage(s)

                # Create Generic Storage
                if s['storage type'] == 'Stratified':
                    self.stratified_thermal_storage(s, data)

        # appends created storages to the list of nodes
        for i in range(len(self.nodes)):
            nodes.append(self.nodes[i])


class Links:
    """
    Creates links objects as defined in 'nodes_data' and adds them to
    the list of components 'nodes'.
    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 05.03.2020
    """
    # intern variables
    busd = None
    
    def __init__(self, nodes_data, nodes, bus):
        """
        Inits the Links class.
        ----
        
        Keyword arguments:
        nodes_data: obj:'dict'
        -- dictionary containing data from excel scenario file. The
        following data have to be provided:
        - 'active'
        - 'label'
        - '(un)directed'
        
        bus : obj:'dict'
        -- dictionary containing the buses of the energy system
        
        nodes : obj:'list'
        -- list of components created before (can be empty)
        """
        # renames variables
        self.busd = bus
        # creates link objects for every link object in nd
        for i, link in nodes_data['links'].iterrows():
            if link['active']:
                if link['(un)directed'] == 'directed':
                    ep_costs = link['periodical costs /(CU/(kW a))']
                elif link['(un)directed'] == 'undirected':
                    ep_costs = link['periodical costs /(CU/(kW a))'] / 2
                else:
                    raise SystemError('Problem with periodical costs')
                nodes.append(solph.custom.Link(
                    label=link['label'],
                    inputs={self.busd[link['bus_1']]: solph.Flow(),
                            self.busd[link['bus_2']]: solph.Flow()},
                    outputs={self.busd[link['bus_2']]: solph.Flow(
                                variable_costs=
                                link['variable output costs /(CU/kWh)'],
                                emission_factor=
                                link['variable constraint costs /(CU/kWh)'],
                                investment=solph.Investment(
                                    ep_costs=ep_costs,
                                    periodical_constraint_costs=link[
                                        'periodical constraint costs /(CU/(kW a))'],
                                    minimum=link[
                                        'min. investment capacity /(kW)'],
                                    maximum=link[
                                        'max. investment capacity /(kW)'],
                                    existing=link[
                                        'existing capacity /(kW)'],
                                    nonconvex=True if
                                    link['Non-Convex Investment'] == 1
                                    else False,
                                    offset=link[
                                        'Fix Investment Costs /(CU/a)'])),
                             self.busd[link['bus_1']]: solph.Flow(
                                 variable_costs=
                                 link['variable output costs /(CU/kWh)'],
                                 emission_factor=
                                 link['variable constraint costs /(CU/kWh)'],
                                 investment=solph.Investment(
                                     ep_costs=ep_costs,
                                     periodical_constraint_costs=link[
                                         'periodical constraint costs /(CU/(kW a))'],
                                     minimum=link[
                                         'min. investment capacity /(kW)'],
                                     maximum=link[
                                         'max. investment capacity /(kW)'],
                                     existing=link[
                                         'existing capacity /(kW)'],
                                     nonconvex=True if
                                     link['Non-Convex Investment'] == 1
                                     else False,
                                     offset=link[
                                         'Fix Investment Costs /(CU/a)'])), },
                    conversion_factors={
                        (self.busd[link['bus_1']],
                         self.busd[link['bus_2']]): link['efficiency'],
                        (self.busd[link['bus_2']],
                         self.busd[link['bus_1']]):
                             (link['efficiency']
                              if link['(un)directed'] == 'undirected' else 0)}
                ))
                # returns logging info
                logging.info('   ' + 'Link created: ' + link['label'])
