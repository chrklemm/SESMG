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
   bus001_heat_bus,,1,1,1,0.1,-0.05,0.1,-0.1
   bus001_cooling_bus,,1,0,1,0.3,x,0.1,-0.1
   
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
   building001_fixed_timeseries_cooling_demand,,1,1,bus001_cooling_bus,timeseries,1,x,x,x,x
   building001_heat_demand,EFH standard load profile sink,1,1,bus001_heat_bus,efh,x,1000,x,1,0
   
  

	
.. figure:: ../images/BSP_Graph_sink.png
   :width: 60 %
   :alt: Sink_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components. By the input in the sinks sheet, a photovoltaic source has been created.

Sources
=================================================

Within this sheet, the sources of the energy system are defined. Properties with the addition "PV ONLY" have only to be 
defined if the parameter "technology" is set on "photovoltaic", if the parameter "technology" is "solar_thermal_flat_plate" or "concentrated_solar_power" the
properties with the addition "Solar Heat" have to be filled.

- **label**: Unique designation of the source. The following format is recommended: "ID_energy sector_source".
- **comment**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **active**: Specifies whether the source shall be included to the model. 0 = inactive, 1 = active.
- **fixed**: Indicates whether it is a fixed source or not. 0 = not fixed; 1 = fixed.
- **output**: Specifies which bus the source is connected to.
- **input**: Has to be an electricity bus, if "technology" is set to "concentrated_solar_power" or "solar_thermal_flat_plate". Otherwise has to be set to "x", "X", "None", "none", "0" or just blank.
- **technology**: Technology type of source. Input options: "photovoltaic", "windpower", "timeseries", "concentrated_solar_power", "solar_thermal_flat_plate". Time series are automatically generated for photovoltaic systems and wind turbines. If "timeseries" is selected, a time series must be provided in the "time_series" sheet.
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
- **Azimuth (PV and Solar Heat)**: Specifies the orientation of the PV or solar thermal module in degrees. Values between 0 and 360 are permissible (0 = north, 90 = east, 180 = south, 270 = west). Only required for photovoltaic and solar thermal sources, use fill character "x" for other technologies.
- **Surface Tilt (PV and Solar Heat)**: Specifies the inclination of the module in degrees (0 = flat). Only required for photovoltaic and solar thermal sources, use fill character "x" for other technologies.
- **Albedo (PV ONLY)**: Specifies the albedo value of the reflecting floor surface. Only required for photovoltaic sources, use fill character "x" for other technologies.
- **Altitude (PV ONLY)**: Height (above mean sea level) in meters of the photovoltaic module. Only required for photovoltaic sources, use fill character "x" for other technologies.
- **Latitude (PV and Solar Heat)**: Geographic latitude (decimal number) of the photovoltaic or solar thermal module. Only required for photovoltaic and solar thermal sources, use fill character "x" for other technologies.
- **Longitude (PV and Solar Heat)**: Geographic longitude (decimal number) of the photovoltaic or solar thermal module module. Only required for photovoltaic and solar thermal sources, use fill character "x" for other technologies.
- **Cleanliness (Solar Heat)**: Cleanliness of a parabolic through collector. Only required if "technology" is set to "concentrated_solar_power".
- **ETA 0 (Solar Heat)**: Optical efficiency of the collector. Only required if "technology" is "concentrated_solar_power" or "solar_thermal_flate_plate".
- **A1 (Solar Heat)**: Collector specific linear heat loss coefficient. Only required if "technology" is "concentrated_solar_power" or "solar_thermal_flate_plate".
- **A2 (Solar Heat)**: Collector specific quadratic heat loss coefficient. Only required if "technology" is "concentrated_solar_power" or "solar_thermal_flate_plate".
- **C1 (Solar Heat)**: Collector specific thermal loss parameter. Only required if "technology" is "concentrated_solar_power".
- **C2 (Solar Heat)**: Collector specific thermal loss parameter. Only required if "technology" is "concentrated_solar_power".

**Note: Exemlpary values for concentrated_solar_power technology**
The following figure shows examplary values for a parabolic through collector

.. figure:: ../images/CSP_examplary.png
   :width: 100 %
   :alt: CSP_example
   :align: center
   
The parameters refer to `Janotte, N; et al <https://www.sciencedirect.com/science/article/pii/S1876610214004664>`_

- **Temperature Inlet /deg C (Solar Heat)**: Inlet temperature of the solar heat collector module. Only required if "technology" is "concentrated_solar_power" or "solar_thermal_flate_plate".
- **Temperature Difference /deg C (Solar Heat)**: Temperature Difference between in- and outlet temperature of the solar heat collector module. Only required if "technology" is "concentrated_solar_power" or "solar_thermal_flate_plate".
- **Conversion Factor /(sqm/kW) (Solar Heat)**: Collector specific factor. Further information in documentation on "Structure of Energy System".
- **Peripheral Losses (Solar Heat)**: Heat loss coefficient for losses in the collector's peripheral system. Only required for "technology" "concentrated_solar_power" and "solar_thermal_flate_plate".
- **Electric Consumption (Solar Heat)**: Electric consumption of the collector system. Example: If value is set to 0,05, the electric consumption is 5 % of the energy output. Only required for "technology" "concentrated_solar_power" and "solar_thermal_flate_plate".

.. csv-table:: Exemplary input for the sources sheet
   :header: label,Comment,active,fixed,output,input,technology,variable costs /(CU/kWh),variable constraint costs /(CU/kWh),existing capacity /(kW),min. investment capacity /(kW),max. investment capacity /(kW),periodical costs /(CU/(kW a)),periodical constraint costs /(CU/(kW a)),Non-Convex Investment,Fix Investment Costs /(CU/a),Turbine Model (Windpower ONLY),Hub Height (Windpower ONLY),technology database (PV ONLY),inverter database (PV ONLY),Modul Model (PV ONLY),Inverter Model (PV ONLY),Azimuth (PV ONLY),Surface Tilt (PV ONLY),Albedo (PV ONLY),Altitude (PV ONLY),Latitude (PV ONLY),Longitude (PV ONLY),Latitude (Solar Heat),Longitude (Solar Heat),Surface Tilt (Solar Heat),Azimuth (Solar Heat),Cleanliness (Solar Heat),ETA 0 (Solar Heat),A1 (Solar Heat),A2 (Solar Heat),C1 (Solar Heat),C2 (Solar Heat),Temperature Inlet /deg C (Solar Heat),Temperature Difference /deg C (Solar Heat),Conversion Factor /(sqm/kW) (Solar Heat),Peripheral Losses (Solar Heat),Electric Consumption (Solar Heat)

   pv001_electricity_source,fixed photovoltaic source,1,1,bus001_electricity_bus,x,photovoltaic,0,0.1,10,0,10,90,0.1,0,0,x,x,SandiaMod,sandiainverter,Panasonic_VBHN235SA06B__2013_,ABB__MICRO_0_25_I_OUTD_US_240__240V_,180.00,35,0.18,60.000,52.13,7.36,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x
   solar_heat001,thermaldev,1,1,bus001_heat_bus,bus001_electricity_bus,solar_thermal_flat_plate,0,0.1,10,0,100,55,0.1,0,0,x,x,x,x,x,x,x,x,x,x,x,x,52.13,7.36,10,20,x,0.719,1.063,0.005,x,x,40,15,1.6,0.05,0.06
   windpower001_electricity_source,fixed wind power source,1,1,bus001_electricity_bus,x,windpower,0,0.1,0,10,1000,100,0.1,0,0,E-126/4200,135,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x

  

	
.. figure:: ../images/BSP_Graph_source.png
   :width: 60 %
   :alt: Source_Graph
   :align: center

   Graph of the energy system, which is created by entering the example components. By the input in the sources-sheet one sink has been created.
   
Transformers
=================================================

Within this sheet, the transformers of the energy system are defined. 

The following parameters have to be entered:


- **label**: Unique designation of the transformer. The following format is recommended: "ID_energy sector_transformer".
- **comment**: Space for an individual comment, e.g. an indication of which measure this component belongs to.
- **active**: Specifies whether the transformer shall be included to the model. 0 = inactive, 1 = active.
- **transformer type**: Indicates what kind of transformer it is. Possible entries: "GenericTransformer" for linear transformers with constant efficiencies; "GenericCHP" for transformers with varying efficiencies.
- **mode**: Specifies, if a compression or absorption heat transformer is working as "chiller" or "heat_pump". Only required if "transformer type" is set to "compression_heat_transformer" or "absorption_heat_transformer". Otherwise has to be set to "x", "X", "None", "none", "0" or just blank.
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
- **periodical constraint costs /(CU/(kW a))**: Only required if constraint is considered. Constraint costs incurred per kW for investments within the time horizon.
- **Non-Convex Investment**: Specifies whether the investment capacity should be defined as a mixed-integer variable, i.e. whether the model can decide whether NOTHING OR THE INVESTMENT should be implemented.
- **Fix Investment Costs /(CU/a)**: Fixed costs of non-convex investments (in addition to the periodic costs)

**The following parameters are only required, if "transformer type" is set to "compression_heat_transformer"**:

- **heat source (CHT)**: Specifies the heat source. Possible heat sources are "GroundWater", "Ground", "Air" and "Water" possible.
- **temperature high /deg C (CHT)**: Temperature of the high temperature heat reservoir. Only required if "mode" is set to "heat_pump".
- **temperature low /(deg C) (CHT)**: Cooling temperature needed for cooling demand. Only required if "mode" is set to "chiller".
- **quality grade (CHT)**: To determine the COP of a real machine a scale-down factor (the quality grade) is applied on the Carnot efficiency (see `oemof.thermal <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_).
- **area /(sq m) (CHT)**: Open spaces for ground-coupled compression heat transformers (GC-CHT).
- **length of the geoth. probe /m (CHT)**: Length of the vertical heat exchanger, only for GC-CHT.
- **heat extraction /(kW/(m*a)) (CHT)**: Heat extraction for the heat exchanger referring to the location, only for GC-CHT.
- **min. borehole area /(sq m) (CHT)**: Limited space due to the regeneation of the ground source, only for GC-CHT.
- **temp threshold icing (CHT)**: Temperature below which icing occurs (see `oemof.thermal <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_). Only required if "mode" is set to "heat_pump".
- **factor icing (CHT)**: COP reduction caused by icing (see `oemof.thermal <https://github.com/wind-python/windpowerlib/blob/dev/windpowerlib/oedb/turbine_data.csv>`_). Only required if "mode" is set to "heat_pump".

**The following parameters are only required, if "transformer type" is set to "absorption_heat_transformer"**:

- **name (AbsCH)**: Defines the way of calculating the efficiency of the absorption heat transformer. Possible inputs are: "Rotartica", "Safarik", "Broad_01", "Broad_02", and "Kuehn". "Broad_02" refers to a double-effect absorption chiller model, whereas the other keys refer to single-effect absorption chiller models.
- **high temperature /deg C (AbsCH)**: Temperature of the heat source, that drives the absorption heat transformer.
- **chilling temperature /deg C (AbsCH)**: Output temperature which is needed for the cooling demand.
- **electrical input conversion factor (AbsCH)**: Specifies the relation of electricity consumption to energy input. Example: A value of 0,05 means, that the system comsumes 5 % of the input energy as electric energy.
- **recooling temperature difference /deg C (AbsCH)**: Defines the temperature difference between temperature source for recooling and recooling cycle.

  
.. csv-table:: Exemplary input for the transformers sheet
   :header: label,comment,active,transformer type,mode,input,output,output2,efficiency,efficiency2,variable input costs /(CU/kWh),variable output costs /(CU/kWh),variable output costs 2 /(CU/kWh),variable input constraint costs /(CU/kWh),variable output constraint costs /(CU/kWh),variable output constraint costs 2 /(CU/kWh),existing capacity /(kW),min. investment capacity /(kW),max. investment capacity /(kW),periodical costs /(CU/(kW a)),periodical constraint costs /(CU/(kW a)),Non-Convex Investment,Fix Investment Costs /(CU/a),heat source (CHT),temperature high /deg C (CHT),temperature low /deg C (CHT),quality grade (CHT),area /(sq m) (CHT),length of the geoth. probe /m (CHT),heat extraction /(kW/(m*a)) (CHT),min. borehole area /(sq m) (CHT),temp threshold icing (CHT),factor icing (CHT),name (AbsCH),high temperature /deg C (AbsCH),chilling temperature /deg C (AbsCH),electrical input conversion factor (AbsCH),recooling temperature difference /deg C (AbsCH)

   tr0001_electricity_transformer,,1,GenericTransformer,,bus002_electricity_bus,bus001_electricity_bus,x,0.85,x,0.01,0,0,0.1,0.2,0,1000,0,1000,60,0.1,0,0,x,x,x,x,x,x,x,x,x,x,x,x,x,x,x
   tr0002_airsource_heat_pump,,1,compression_heat_transformer,heat_pump,bus001_electricity_bus,bus001_heat_bus,None,0.95,x,10,0,x,0.1,0.1,x,10,10,100,50,0.1,0,0,Air,40,x,0.4,0,0,0,0,3,0.8,x,x,x,x,x
   tr0003_absorption_chiller,,1,absorption_heat_transformer,chiller,bus001_electricity_bus,bus001_cooling_bus,None,0.95,x,5,0,x,0.1,0.1,x,10,10,100,50,0.1,0,0,x,x,x,x,x,x,x,x,x,x,Kuehn,85,10,0.05,6
 

	
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
- **storage type**: Defines whether the storage is a "Generic" or a "Stratified" sorage. These two inputs are possible.
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
- **capacity loss (Generic only)**: Indicates the storage loss per time unit. Only required, if the "storage type" is set to "Generic". 
- **efficiency inflow**: Specifies the charging efficiency.
- **efficiency outflow**: Specifies the discharging efficiency.
- **initial capacity**: Specifies how far the memory is loaded at time 0 of the simulation. Value must be between 0 and 1.
- **capacity min**: Specifies the minimum amount of memory that must be loaded at any given time. Value must be between 0 and 1.
- **capacity max**: Specifies the maximum amount of memory that can be loaded at any given time. Value must be between 0 and 1.
- **variable input costs**: Indicates how many costs arise for charging with one kWh.
- **variable output costs**: Indicates how many costs arise for charging with one kWh.
- **variable input constraint costs**: Only if considering constraints. Indicates how many costs arise for charging with one kWh referring to the constraint limit set in the "energysystem" sheet.
- **variable output constraint costs**: Only if considering constraints. Indicates how many costs arise for charging with one kWh referring to the constraint limit set in the "energysystem" sheet.
- **diameter /m (Stratified Storage)**: Defines the diameter of a stratified thermal storage, which is necessary for the calculation of thermal losses.
- **temperature high /deg C (Stratified Storage)**: Outlet temperature of the stratified thermal storage.
- **temperature low /deg C (Stratified Storage)**: Inlet temperature of the stratified thermal storage.
- **U value /(W/(sqm*K)) (Stratified Storage)**: Thermal transmittance coefficient
- **existing capacity/(kW)**: Previously installed capacity of the storage.
- **periodical costs /(CU/a)**: Costs incurred per kW for investments within the time horizon.
- **max. investment capacity/(kW)**: Maximum in addition to existing capacity, installable storage capacity.
- **min. investment capacity/(kW)**: Minimum storage capacity to be installed.
- **Non-Convex Investment**: Specifies whether the investment capacity should be defined as a mixed-integer variable, i.e. whether the model can decide whether NOTHING OR THE INVESTMENT should be implemented.
- **Fix Investment Costs /(CU/a)**: Fixed costs of non-convex investments (in addition to the periodic costs)


.. csv-table:: Exemplary input for the storages sheet
   :header: label,comment,active,storage type,bus,existing capacity /(kWh),min. investment capacity /(kWh),max. investment capacity /(kWh),periodical costs /(CU/(kWh a)),periodical constraint costs /(CU/(kWh a)),Non-Convex Investment,Fix Investment Costs /(CU/a),input/capacity ratio (invest),output/capacity ratio (invest),capacity loss (Generic only),efficiency inflow,efficiency outflow,initial capacity,capacity min,capacity max,variable input costs,variable output costs,variable input constraint costs /(CU/kWh),variable output constraint costs /(CU/kWh),diameter /(m) (Stratified Storage),temperature high /(deg C) (Stratified Storage),temperature low /(deg C) (Stratified Storage),U value /(W/(sqm*K)) (Stratified Storage)

   battery001_electricity_storage,,1,Generic,bus001_electricity_bus,1000,0,1000,70,0.1,0,0,0.17,0.17,0,1,0.98,0,0.1,1,0,0,0.1,0.1,x,x,x,x
   stratified_thermal_storage001,,1,Stratified,bus001_heat_bus,100,0,500,40,0.1,0,0,0.2,0.2,x,1,0.98,0,0.05,0.95,0,0,0.1,0.1,1,60,45,0.04

	
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
   :header: timestamp,residential_electricity_demand.actual_value,fixed_timeseries_electricty_source.fix, unfixed_timeseries_electricty_source.min,unfixed_timeseries_electricty_source.max,fixed_timeseries_electricity_sink.fix,unfixed_timeseries_electricity_sink.min,unfixed_timeseries_electricity_sink.max,fixed_timeseries_cooling_demand_sink.fix

   2012-01-01 00:00:00,0.559061982,0.000000,0.000000,1.000000,0.000000,0.000000,1.000000,100
   2012-01-01 01:00:00,0.533606486,0.041667,0.000000,0.500000,0.041667,0.000000,0.500000,100
   2012-01-01 02:00:00,0.506058757,0.083333,0.000000,0.333333,0.083333,0.000000,0.333333,100
   2012-01-01 03:00:00,0.504140877,0.125000,0.000000,0.250000,0.125000,0.000000,0.250000,100
   2012-01-01 04:00:00,0.507104873,0.166667,0.000000,0.200000,0.166667,0.000000,0.200000,100
   2012-01-01 05:00:00,0.511376515,0.208333,0.000000,0.166667,0.208333,0.000000,0.166667,100
   2012-01-01 06:00:00,0.541801064,0.250000,0.000000,0.142857,0.250000,0.000000,0.142857,100
   2012-01-01 07:00:00,0.569261616,0.291667,0.000000,0.125000,0.291667,0.000000,0.125000,100
   2012-01-01 08:00:00,0.602998867,0.333333,0.000000,0.111111,0.333333,0.000000,0.111111,100
   2012-01-01 09:00:00,0.629064598,0.375000,0.000000,0.100000,0.375000,0.000000,0.100000,100






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


