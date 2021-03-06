Using the Scenario File
*************************************************

For the modeling and optimization of an energy system, parameters for all system components must be given in the model 
generator using the enclosed .xlsx file (editable with Excel, LibreOffice, …). The .xlsx file is divided into nine 
input sheets. In the "energysystem" sheet, general parameters are defined for the time horizon to be examined, in the 
sheets "buses", "sinks", "sources", "transformers", "storages" and "links" corresponding components are defined. In 
the sheet "time series", the performance of individual components can be stored. In the "weather data" sheet, the 
required weather data is stored. When completing the input file, it is recommended to enter the energy system step by 
step and to perform test runs in between, so that potential input errors are detected early and can be localized more 
easily. In addition to the explanation of the individual input sheets, an example energy system is built step by step 
in the following subchapters. The input file for this example is stored in the program folder "examples" and viewed on 
`GitHub <https://github.com/chrklemm/SESMG/tree/master/examples>`_. The following units are used throughout:

- capacity/performance in kW,
- energy in kWh,
- angles in degrees, and
- costs in cost units (CU).

Cost units are any scalable quantity used to optimize the energy system, such as euros or grams of carbon dioxide emissions.


Energysystem
=================================================

Within this sheet, the time horizon and the temporal resolution of the model is defined. The following parameters have to be entered:

- **start date**: Start of the modelling time horizon. Format: "YYYY-MM-DD hh:mm:ss";
- **end date**: End date of the modelling time horizon. Format: "YYYY-MM-DD hh:mm:ss"; and
- **temporal resolution**: For the modelling considered temporal resolution. Possible inputs: "a" (years), "d" (days), "h" (hours) "min" (minutes), "s" (seconds), "ms" (mili seconds).
- **periods**: Number of periods within the time horizon (one year with hourly resolution equals 8760 periods).
- **constraint costs /(CU)**: Value in order to set a limit for the whole energysystem, e.g. carbon dioxide emissions. Set this field to "None" in order to ignore the limit. If you want to set a limit, you have to set specific values for each components seen below.

   
.. csv-table:: Exemplary input for the energy system
   :header: start date,end date,temporal resolution,periods,constraint costs /(CU)

   2012-01-01 00:00:00,2012-12-30 23:00:00,h,8760,None
   
 

Buses
=================================================

Within this sheet, the buses of the energy system are defined. The following parameters need to be entered:

- **label**: Unique designation of the bus. The following format is recommended: "ID_energy sector_bus".
- **comment**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **active**: Specifies whether the bus shall be included to the model. 0 = inactive, 1 = active. 
- **excess**: Specifies whether a sink is to be generated, which consumes excess energy. 0 = no excess sink will be generated; 1 = excess sink will be generated.
- **shortage**: Specifies whether to generate a shortage source that can compensate energy deficits or not. 0 = no shortage source will be generated; 1 = shortage source will be generated.
- **shortage costs/(CU/kWh)**: Assigns a price per kWh to the purchase of energy from the shortage source. If the shortage source was deactivated, the fill character "x" is used. 
- **excess costs/(CU/kWh)**: Assigns a price per kWh to the release of energy to the excess sink. If the excess sink was deactivated, the fill character "x" is used.
- **variable shortage constraint costs /(CU/kWh)**: Only if considering constraints. Assigns a price per kWh to the purchase of energy from the shortage source referring to the constraint limit set in the "energysystem" sheet. If the shortage source was deactivated, the fill character "x" is used.
- **variable excess constraint costs /(CU/kWh)**: Only if considering constraints. Assigns a price per kWh to the release of energy to the excess sink referring to the constraint limit set in the "energysystem" sheet. If the excess sink was deactivated, the fill character "x" is used.

.. csv-table:: Exemplary input for the buses sheet
   :header: label,comments,active,excess,shortage,shortage costs /(CU/kWh),excess costs /(CU/kWh),variable shortage constraint costs /(CU/kWh),variable excess constraint costs /(CU/kWh)

   bus001_electricity_bus,,1,0,1,0.300,x,0.10,-0.10
   bus002_electricity_bus,,1,1,0,x,-0.01,0.10,-0.10
   
   
.. figure:: ../images/BSP_Graph_Bus.png
   :width: 60 %
   :alt: Bus_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components. Two buses, a shortage source, and an excess sink were created by the input.


Sinks
=================================================

Within this sheet, the sinks of the energy system are defined. The following parameters need to be entered:

- **label**: Unique designation of the sink. The following format is recommended: "ID_energy sector_sinks".
- **comment**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **active**: Specifies whether the sink shall be included to the model. 0 = inactive, 1 = active.
- **fixed**: Indicates whether it is a fixed sink or not. 0 = not fixed; 1 = fixed.
- **input**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **load profile**: Specifies the basis onto which the load profile of the sink is to be created. If the Richardson tool is to be used, "richardson" has to be inserted. For standard load profiles, its acronym is used. If a time series is used, "timeseries" must be entered. If the source is not fixed, the fill character "x" has to be used.
- **nominal value/(kW)**: Nominal performance of the sink. Required when "time series" has been entered into the "load profile". When SLP or Richardson is used, use the fill character "x" here.
- **annual demand/(kWh/a)**: Annual energy demand of the sink. Required when using the Richardson Tool or standard load profiles. When using time series, the fill character "x" is used. 
- **occupants [RICHARDSON]**: Number of occupants living in the respective building. Only required when using the Richardson tool, use fill character "x" for other load profiles.
- **building class [HEAT SLP ONLY]**: BDEW-building class.
- **wind class [HEAT SLP ONLY]**: wind classification for building location (0=not windy, 1=windy)
 
.. csv-table:: Exemplary input for the sinks sheet
   :header: label,comment,active,fixed,input,load profile,nominal value /(kW),annual demand /(kWh/a),occupants [RICHARDSON],building class [HEAT SLP ONLY],wind class [HEAT SLP ONLY]

   building001_electricity_sink,H0 standard load profile sink,1,1,electricity_bus,h0,x,1000.0,x,x,x

   
  

	
.. figure:: ../images/BSP_Graph_sink.png
   :width: 60 %
   :alt: Sink_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components. By the input in the sinks sheet, a photovoltaic source has been created.

Sources
=================================================

Within this sheet, the sources of the energy system are defined. Properties with the addition "PV ONLY" have only to be 
defined if the parameter "technology" is set on "photovoltaic". The following parameters have to be entered:

- **label**: Unique designation of the source. The following format is recommended: "ID_energy sector_source".
- **comment**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **active**: Specifies whether the source shall be included to the model. 0 = inactive, 1 = active.
- **fixed**: Indicates whether it is a fixed source or not. 0 = not fixed; 1 = fixed.
- **output**: Specifies which bus the source is connected to.
- **technology**: Technology type of source. Input options: "photovoltaic", "windpower", "timeseries". Time series are automatically generated for photovoltaic systems and wind turbines. If "timeseries" is selected, a time series must be provided in the "time_series" sheet.
- **variable costs/(CU/kWh)**: Defines the variable costs incurred for a kWh of energy drawn from the source.
- **variable constraint costs /(CU/kWh)**: Only if considering constraints. Defines the variable costs incurred for a kWh of energy drawn from the source referring to the constraint limit set in the "energysystem" sheet.
- **existing capacity/(kW)**: Existing capacity of the source before possible investments.
- **min. investment capacity/(kW)**: Minimum capacity to be installed in case of an investment.
- **max. investment capacity/(kW)**: Maximum capacity that can be added in the case of an investment. If no investment is possible, enter the value "0" here.
- **periodical costs/(CU/(kW a))**: Costs incurred per kW for investments within the time horizon.
- **periodical constraint costs/(CU/(kW a))**: Only if considering constraints. Costs incurred per kW for investments within the time horizon referring to the constraint limit set in the "energysystem" sheet.
- **Non-Convex Investment**: Specifies whether the investment capacity should be defined as a mixed-integer variable, i.e. whether the model can decide whether NOTHING OR THE INVESTMENT should be implemented.
- **Fix Investment Costs /(CU/a)**: Fixed costs of non-convex investments (in addition to the periodic costs).
- **Turbine Model (Windpower ONLY)**: Reference wind turbine model. Possible turbine types are listed `here <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_. 
- **Hub Height (Windpower ONLY)**: Hub height of the wind turbine. Which hub heights are possible for the selected reference turbine can be viewed `here <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_.
- **technology database (PV ONLY)**: Database, from where module parameters are to be obtained. Recommended Database: "SandiaMod".
- **inverter database (PV ONLY)**: Database, from where inverter parameters are to be obtained. Recommended Database: "sandiainverter".
- **Modul Model (PV ONLY)**: Module name, according to the database used.
- **Inverter Model (PV ONLY)**: Inverter name, according to the database used.
- **Azimuth (PV ONLY)**: Specifies the orientation of the PV module in degrees. Values between 0 and 360 are permissible (0 = north, 90 = east, 180 = south, 270 = west). Only required for photovoltaic sources, use fill character "x" for other technologies.
- **Surface Tilt (PV ONLY)**: Specifies the inclination of the module in degrees (0 = flat). Only required for photovoltaic sources, use fill character "x" for other technologies.
- **Albedo (PV ONLY)**: Specifies the albedo value of the reflecting floor surface. Only required for photovoltaic sources, use fill character "x" for other technologies.
- **Altitude (PV ONLY)**: Height (above mean sea level) in meters of the photovoltaic module. Only required for photovoltaic sources, use fill character "x" for other technologies.
- **Latitude (PV ONLY)**: Geographic latitude (decimal number) of the photovoltaic module. Only required for photovoltaic sources, use fill character "x" for other technologies.
- **Longitude (PV ONLY)**: Geographic longitude (decimal number) of the photovoltaic module. Only required for photovoltaic sources, use fill character "x" for other technologies.


.. csv-table:: Exemplary input for the sources sheet
   :header: label,Comment,active,fixed,output,technology,variable costs /(CU/kWh),variable constraint costs /(CU/kWh),existing capacity /(kW),min. investment capacity /(kW),max. investment capacity /(kW),periodical costs /(CU/(kW a)),periodical constraint costs /(CU/(kW a)),Non-Convex Investment,Fix Investment Costs /(CU/a),Turbine Model (Windpower ONLY),Hub Height (Windpower ONLY),technology database (PV ONLY),inverter database (PV ONLY),Modul Model (PV ONLY),Inverter Model (PV ONLY),Azimuth (PV ONLY),Surface Tilt (PV ONLY),Albedo (PV ONLY),Altitude (PV ONLY),Latitude (PV ONLY),Longitude (PV ONLY)

   pv001_electricity_source,fixed photovoltaic source,1,1,bus001_electricity_bus,photovoltaic,0,0.1,10,0,10,90,0.1,0,0,x,x,SandiaMod,sandiainverter,Panasonic_VBHN235SA06B__2013_,ABB__MICRO_0_25_I_OUTD_US_240__240V_,180.00,35,0.18,60.000,52.13,7.36


  

	
.. figure:: ../images/BSP_Graph_source.png
   :width: 60 %
   :alt: Source_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components. By the input in the sources-sheet one sink has been created.
   
Transformers
=================================================

Within this sheet, the transformers of the energy system are defined. Properties with the addition “HP ONLY” have only to be defined if the parameter “transformer type” is set on “HeatPump”. With other transformers, these fields can be left empty or filled with any placeholder. 

The following parameters have to be entered:


- **label**: Unique designation of the transformer. The following format is recommended: "ID_energy sector_transformer".
- **comment**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **active**: Specifies whether the transformer shall be included to the model. 0 = inactive, 1 = active.
- **transformer type**: Indicates what kind of transformer it is. Possible entries: "GenericTransformer" for linear transformers with constant efficiencies; "GenericCHP" for transformers with varying efficiencies.
- **input**: Specifies the bus from which the input to the transformer comes from.
- **output**: Specifies bus to which the output of the transformer is forwarded to.
- **output2**: Specifies the bus to which the output of the transformer is forwarded to, if there are several outputs. If there is no second output, the fill character "x" must be entered here.
- **efficiency**: Specifies the efficiency of the first output. Values between 0 and 1 are allowed entries.
- **efficiency2**: Specifies the efficiency of the second output, if there is one. Values  between 0 and 1 are entered. If there is no second output, the fill character "x" must be entered here.
- **variable input costs/(CU/kWh)**: Variable costs incurred per kWh of input energy supplied.
- **variable output costs/(CU/kWh)**: Variable costs incurred per kWh of output energy supplied.
- **variable output costs 2/(CU/kWh)**: Variable costs incurred per kWh of output 2 energy supplied.
- **variable input constraint costs/(CU/kWh)**: Only if considering constraints. Variable constraint costs incurred per kWh of input energy supplied referring to the constraint limit set in the "energysystem" sheet.
- **variable output constraint costs/(CU/kWh)**: Only if considering constraints. Variable constraint costs incurred per kWh of output energy supplied referring to the constraint limit set in the "energysystem" sheet.
- **variable output constraint costs 2/(CU/kWh)**: Only if considering constraints. Variable constraint costs incurred per kWh of output 2 energy supplied referring to the constraint limit set in the "energysystem" sheet.
- **existing capacity/(kW)**: Already installed capacity of the transformer.
- **min investment capacity/(kW)**: Minimum transformer capacity to be installed.
- **max investment capacity/(kW)**: Maximum  installable transformer capacity in addition to the previously existing one.
- **periodical costs /(CU/a)**: Costs incurred per kW for investments within the time horizon.
- **Non-Convex Investment**: Specifies whether the investment capacity should be defined as a mixed-integer variable, i.e. whether the model can decide whether NOTHING OR THE INVESTMENT should be implemented.
- **Fix Investment Costs /(CU/a)**: Fixed costs of non-convex investments (in addition to the periodic costs)
- **heat source (HP ONLY)**: Specifies the heat source. At the moment are "GroundWater", "Ground", "Air" and "Water" possible.
- **temperature high /(deg C) (HP ONLY)**: Temperature of the high temperature heat reservoir
- **quality grade (HP ONLY)**: To determine the COP of a real machine a scale-down factor (the quality grade) is applied on the Carnot efficiency (see `oemof.thermal <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_).
- **area /(sq m) (HP ONLY)**: Open spaces for ground-coupled heat pumps (GCHP).
- **length of the geoth. probe (m) (HP ONLY)**: Length of the vertical heat exchanger, only for GCHP.
- **heat extraction (kW/(m*a)) (HP ONLY)**: Heat extraction for the heat exchanger referring to the location, only for GCHP.
- **min. borehole area (sq m) (HP ONLY)**: Limited space due to the regeneation of the ground source, only for GCHP.
- **temp threshold icing (HP ONLY)**: Temperature below which icing occurs (see `oemof.thermal <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_).
- **factor icing (HP ONLY)**: COP reduction caused by icing (see `oemof.thermal <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_).

  
.. csv-table:: Exemplary input for the transformers sheet
   :header: label,comment,active,transformer type,input,output,output2,efficiency,efficiency2,variable input costs /(CU/kWh),variable output costs /(CU/kWh),variable output costs 2 /(CU/kWh),variable input constraint costs /(CU/kWh),variable output constraint costs /(CU/kWh),variable output constraint costs 2 /(CU/kWh),existing capacity /(kW),min. investment capacity /(kW),max. investment capacity /(kW),periodical costs /(CU/(kW a)),periodical constraint costs /(CU/(kW a)),Non-Convex Investment,Fix Investment Costs /(CU/a),heat source,temperature high /(deg C),quality grade,area /(sq m),length of the geoth. probe (m),heat extraction (kW/(m*a)),min. borehole area (sq m),temp threshold icing,factor icing

   tr0001_electricity_transformer,,1,GenericTransformer,bus002_electricity_bus,bus001_electricity_bus,x,0.85,x,0.01,0,0,0.1,0.2,0,1000,0,1000,60,0.1,0,0,x,x,x,x,x,x,x,x,x
   
 

	
.. figure:: ../images/BSP_Graph_transformer.png
   :width: 60 %
   :alt: Transformer_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components. One transformer has been created by including the transformers sheet 

Storages
=================================================

Within this sheet, the sinks of the energy system are defined. The following parameters have to be entered:

- **label**: Unique designation of the storage. The following format is recommended: "ID_energy sector_storage".
- **comment**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **active**: Specifies whether the storage shall be included to the model. 0 = inactive, 1 = active.
- **bus**: Specifies which bus the storage is connected to.
- **existing capacity/(kW)**: Previously installed capacity of the storage.
- **min. investment capacity/(kW)**: Minimum storage capacity to be installed.
- **max. investment capacity/(kW)**: Maximum in addition to existing capacity, installable storage capacity.
- **periodical costs /(CU/a)**: Costs incurred per kW for investments within the time horizon.
- **periodical constraint costs /(CU/a)**: Only if considering constraints. Costs incurred per kW for investments within the time horizon referring to the constraint limit set in the "energysystem" sheet.
- **Non-Convex Investment**: Specifies whether the investment capacity should be defined as a mixed-integer variable, i.e. whether the model can decide whether NOTHING OR THE INVESTMENT should be implemented.
- **Fix Investment Costs /(CU/a)**: Fixed costs of non-convex investments (in addition to the periodic costs)
- **input/capacity ratio (invest)**: Indicates the performance with which the memory can be charged.
- **output/capacity ratio (invest)**: Indicates the performance with which the memory can be discharged.
- **capacity loss**: Indicates the storage loss per time unit.
- **efficiency inflow**: Specifies the charging efficiency.
- **efficiency outflow**: Specifies the discharging efficiency.
- **initial capacity**: Specifies how far the memory is loaded at time 0 of the simulation. Value must be between 0 and 1.
- **capacity min**: Specifies the minimum amount of memory that must be loaded at any given time. Value must be between 0 and 1.
- **capacity max**: Specifies the maximum amount of memory that can be loaded at any given time. Value must be between 0 and 1.
- **variable input costs**: Indicates how many costs arise for charging with one kWh.
- **variable output costs**: Indicates how many costs arise for charging with one kWh.
- **variable input constraint costs**: Only if considering constraints. Indicates how many costs arise for charging with one kWh referring to the constraint limit set in the "energysystem" sheet.
- **variable output constraint costs**: Only if considering constraints. Indicates how many costs arise for charging with one kWh referring to the constraint limit set in the "energysystem" sheet.


.. csv-table:: Exemplary input for the storages sheet
   :header: label,comment,active,bus,existing capacity /(kWh),min. investment capacity /(kWh),max. investment capacity /(kWh),periodical costs /(CU/(kWh a)),periodical constraint costs /(CU/(kWh a)),Non-Convex Investment,Fix Investment Costs /(CU/a),input/capacity ratio (invest),output/capacity ratio (invest),capacity loss,efficiency inflow,efficiency outflow,initial capacity,capacity min,capacity max,variable input costs,variable output costs,variable input constraint costs /(CU/kWh),variable output constraint costs /(CU/kWh)

   battery001_electricity_storage,,1,bus001_electricity_bus,1000,0,1000,70,0.1,0,0,0.17,0.17,0,1,0.98,0,0.1,1,0,0,0.1,0.1


	
.. figure:: ../images/BSP_Graph_Storage.png
   :width: 60 %
   :alt: Transformer_Graph
   :align: center

   Graph of the energy system, which is created after entering the example components. One storage has been created by the storage sheet.
   
Links
=================================================

Within this sheet, the links of the energy system are defined. The following parameters have 
to be entered:

- **label**: Unique designation of the link. The following format is recommended: "ID_energy sector_transformer"
- **comment**: Space for an individual comment, e.g. an indication of  which measure this component belongs to.
- **active**: Specifies whether the link shall be included to the model. 0 = inactive, 1 = active. 
- **bus_1**: First bus to which the link is connected. If it is a directed link, this is the input bus.
- **bus_2**: Second bus to which the link is connected. If it is a directed link, this is the output bus.
- **(un)directed**: Specifies whether it is a directed or an undirected link. Input options: "directed", "undirected".
- **efficiency**: Specifies the efficiency of the link. Values between 0 and 1 are allowed entries.
- **variable output costs/(CU/kWh)**: Specifies the efficiency of the first output. Values between 0 and 1 are allowed entries.
- **variable constraint costs/(CU/kWh)**: Only if considering constraints. Costs incurred per kWh referring to the constraint limit set in the "energysystem" sheet.
- **existing capacity/(kW)**: Already installed capacity of the link.
- **min. investment capacity/(kW)**: Minimum, in addition to existing capacity, installable capacity.
- **max. investment capacity/(kW)**: Maximum capacity to be installed.
- **periodical costs/(CU/(kW a))**: Costs incurred per kW for investments within the time horizon.
- **Non-Convex Investment**: Specifies whether the investment capacity should be defined as a mixed-integer variable, i.e. whether the model can decide whether NOTHING OR THE INVESTMENT should be implemented.
- **Fix Investment Costs /(CU/a)**: Fixed costs of non-convex investments (in addition to the periodic costs)

.. csv-table:: Exemplary input for the link sheet
   :header: label,Comment,active,bus_1,bus_2,(un)directed,efficiency,variable output costs /(CU/kWh),variable constraint costs /(CU/kWh),existing capacity /(kW),min. investment capacity /(kW),max. investment capacity /(kW),periodical costs /(CU/(kW a)),periodical constraint costs /(CU/(kW a)),Non-Convex Investment,Fix Investment Costs /(CU/a)

   pl001_electricity_link,,1,bus001_electricity_bus,bus002_electricity_bus,directed,0.85,0,0.1,0,0,1000,1,0.1,0,0  

	
.. figure:: ../images/BSP_Graph_link.png
   :width: 60 %
   :alt: bsp-graph-link
   :align: center

   Graph of the energy system, which is created by entering the example components. One link has been created by the addition of the links sheet
   
Time Series
=================================================

Within this sheet, time series of components of which no automatically created time series exist, are stored. More 
specifically, these are sinks to which the property "load profile" have been assigned as "timeseries" and sources 
with the "technology" property "timeseries". The following parameters have to be entered:

- **timestamp**: Points in time to which the stored time series are related. Should be within the time horizon defined in the sheet "timesystem".
- **timeseries**: Time series of a sink or a source  which has been assigned the property "timeseries" under the attribute "load profile" or "technology. Time series contain a value between 0 and 1 for each point in time, which indicates the proportion of installed capacity accounted for by the capacity produced at that point in time. In the header line, the name must rather be entered in the format "componentID.fix" if the component enters the power system as a fixed component or it requires two columns in the format "componentID.min" and "componentID.max" if it is an unfixed component. The columns "componentID.min/.max" define the range that the solver can use for its optimisation.

 
 
.. csv-table:: Exemplary input for time series sheet
   :header: timestamp,residential_electricity_demand.actual_value,fixed_timeseries_electricty_source.fix, unfixed_timeseries_electricty_source.min,unfixed_timeseries_electricty_source.max,fixed_timeseries_electricity_sink.fix,unfixed_timeseries_electricity_sink.min,unfixed_timeseries_electricity_sink.max

   2012-01-01 00:00:00,0.559061982,0.000000,0.000000,1.000000,0.000000,0.000000,1.000000
   2012-01-01 01:00:00,0.533606486,0.041667,0.000000,0.500000,0.041667,0.000000,0.500000
   2012-01-01 02:00:00,0.506058757,0.083333,0.000000,0.333333,0.083333,0.000000,0.333333
   2012-01-01 03:00:00,0.504140877,0.125000,0.000000,0.250000,0.125000,0.000000,0.250000
   2012-01-01 04:00:00,0.507104873,0.166667,0.000000,0.200000,0.166667,0.000000,0.200000
   2012-01-01 05:00:00,0.511376515,0.208333,0.000000,0.166667,0.208333,0.000000,0.166667
   2012-01-01 06:00:00,0.541801064,0.250000,0.000000,0.142857,0.250000,0.000000,0.142857
   2012-01-01 07:00:00,0.569261616,0.291667,0.000000,0.125000,0.291667,0.000000,0.125000
   2012-01-01 08:00:00,0.602998867,0.333333,0.000000,0.111111,0.333333,0.000000,0.111111
   2012-01-01 09:00:00,0.629064598,0.375000,0.000000,0.100000,0.375000,0.000000,0.100000






Weather Data
=================================================

If electrical load profiles are simulated with the Richardson tool, heating load profiles with the demandlib or 
photovoltaic systems with the feedinlib, weather data must be stored here. The weather 
data time system should be in conformity with the model’s time system, defined in the sheet "timesystem".

- **timestamp**: Points in time to which the stored weather data are related. 
- **dhi**: diffuse horizontal irradiance in W/m\ :sup:`2`
- **dirhi**: direct horizontal irradiance in W/m\ :sup:`2`
- **pressure**: air pressure in Pa
- **windspeed**: wind speed, measured at 10 m height, in unit m/s
- **z0**: roughness length of the environment in units m
- **ground_temp**: constant ground temperature at 100 m depth
- **water_temp**: varying water temperature of a river depending on the air temperature
- **groundwater_temp**: constant temperatur of the ground water at 6 - 10 m depth in North Rhine-Westphalia

.. csv-table:: Exemplary input for weather data
   :header: ,dhi,dirhi,pressure,temperature,windspeed,z0,ground_temp,water_temp,groundwater_temp

   2012-01-01 00:00:00,0.00,0.00,98405.70,10.33,7.2,0.15,13.7,14.62,13.06
   2012-01-01 01:00:00,0.00,0.00,98405.70,10.33,7.8,0.15,13.7,14.62,13.06
   2012-01-01 02:00:00,0.00,0.00,98405.70,10.48,7.7,0.15,13.7,14.71,13.06
   2012-01-01 03:00:00,0.00,0.00,98405.70,10.55,7.7,0.15,13.7,14.75,13.06
   2012-01-01 04:00:00,0.00,0.00,98405.70,10.93,7.8,0.15,13.7,14.99,13.06
   2012-01-01 05:00:00,0.00,0.00,98405.70,10.90,8.5,0.15,13.7,14.97,13.06
   2012-01-01 06:00:00,0.00,0.00,98405.70,10.88,8.5,0.15,13.7,14.96,13.06
   2012-01-01 07:00:00,0.00,0.00,98405.70,11.22,7.9,0.15,13.7,15.17,13.06
   2012-01-01 08:00:00,0.00,0.00,98405.70,11.68,8.7,0.15,13.7,15.46,13.06
   2012-01-01 09:00:00,0.56,0.56,98405.70,11.87,8.6,0.15,13.7,15.57,13.06
   2012-01-01 10:00:00,13.06,13.06,98405.70,11.65,8.0,0.15,13.7,15.44,13.06


