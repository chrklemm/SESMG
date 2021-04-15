from graphviz import Digraph
import os


def create_graph(filepath, nodes_data, legend=False):
    """Visualizes the energy system as graph.

    Creates, using the library Graphviz, a graph containing all
    components and connections from "nodes_data" and returns this as a
    PNG file.

    ----

    Keyword arguments:

        filepath : obj:'str'
          -- path, where the PNG-result shall be saved

        nodes_data : obj:'dict'
           -- dictionary containing data from excel scenario file.

        legend : obj:'bool'
          -- specifies, whether a legend will be added to the graph or
             not

    ----
    @ Christian Klemm - christian.klemm@fh-muenster.de, 14.04.2020
    """
    
    def linebreaks(text):
        """Adds linebreaks a given string.

         Function which adds a line break to strings every ten
         characters. Up to four strings are added.

         ----

        Keyword arguments:

            text : obj:'str'
              -- string to which line breaks will be added

        ----
        @ Christian Klemm - christian.klemm@fh-muenster.de, 14.04.2020

         """
        text_length = len(text)
        if text_length > 10:
            text = str(text[0:9] + "-\n" + text[9:])
        if text_length > 20:
            text = str(text[0:21] + "-\n" + text[21:])
        if text_length > 30:
            text = str(text[0:33] + "-\n" + text[33:])
        if text_length > 40:
            text = str(text[0:45] + "-\n" + text[45:])
        return text
    
    # Defines the location of Graphviz as path necessary for windows
    os.environ["PATH"] += \
        os.pathsep + 'C:\\Program Files (x86)\\Graphviz2.38\\bin'
    # Creates the Directed-Graph
    dot = Digraph(format='png')
    # Creates a Legend if Legend = True
    if legend:
        component = ['Bus', 'Source', 'Sink', 'Transformer\nLinks', 'Storage']
        shape = {'Bus': ['ellipse'], 'Source': ['trapezium'],
                 'Sink': ['invtrapezium'], 'Transformer\nLinks': ['box'],
                 'Storage': ['box']}
        for i in component:
            dot.node(i, shape=shape[i][0], fontsize="10", fixedsize='shape',
                     width='1.1', height='0.6',
                     style='dashed' if i == 'Storage' else '')
    components = ["buses", "sources", "demand", "transformers", "storages",
                  "links"]
    shapes = {'sources': ['trapezium'], 'demand': ['invtrapezium'],
              'transformers': ['box'], 'storages': ['box'],
              'links': ['box']}
    bus = {'buses': ['label'], 'sources': ['output'], 'demand': ['input'],
           'transformers': ['input'], 'storages': ['bus'], 'links': ['bus_1']}
    # sets checklist for fill in variables
    checklist = ['X', 'x', '', '0', 'None', 'none', 'nan']
    for i in components:
        for j, b in nodes_data[i].iterrows():
            if b['active']:
                # sets component label
                label = b['label']
                if i == 'buses':
                    if b['shortage']:
                        label = b['label'] + '_shortage'
                    elif b['excess']:
                        label = b['label'] + '_excess'
                label = linebreaks(label)
                if i != 'buses':
                    dot.node(label, shape=shapes[i][0], fontsize="10",
                             fixedsize='shape', width='1.1', height='0.6',
                             style='dashed' if i == 'storages' else '')
                    if i == 'sources':
                        # Creates graph elements for solar heat
                        if str(b['input']) not in checklist:
                            # creates additional transformer
                            transformer = b['label'] + '_collector'
                            transformer = linebreaks(transformer)
                            dot.node(transformer, shape='box', fontsize="10",
                                     fixedsize='shape', width='1.1', height='0.6')
                            # creates additional bus
                            c_bus = b['label'] + '_bus'
                            c_bus = linebreaks(c_bus)
                            dot.node(c_bus, shape='ellipse', fontsize="10")
                            # Adds edge for transformer, source and bus to the graph
                            dot.edge(b['input'], transformer)
                            dot.edge(c_bus, transformer)
                            dot.edge(transformer, b['output'])
                            dot.edge(label, c_bus)
                else:
                    if b['shortage']:
                        dot.node(label, shape='trapezium', fontsize="10",
                                 fixedsize='shape', width='1.1', height='0.6')
                        
                    if b['excess'] and not b['shortage']:
                        dot.node(label, shape='invtrapezium', fontsize="10",
                                 fixedsize='shape', width='1.1', height='0.6')
                # creates bus nodes
                dot.node(b[bus[i][0]], shape='ellipse', fontsize="10")
                if i == 'links':
                    dot.node(b['bus_2'], shape='ellipse')
                # creates edges
                if i == 'demand' or i == 'storages' or i == 'links' \
                        or (i == 'buses' and b['excess']
                            and not b['shortage']):
                    dot.edge(b[bus[i][0]], label)
                if (i == 'sources' and str(b['input']) in checklist) \
                        or i == 'storages' or (i == 'buses' and b['shortage']):
                    dot.edge(label, b[bus[i][0]])
                if i == 'links':
                    dot.edge(label, b['bus_2'])
                    if b['(un)directed'] == 'undirected':
                        dot.edge(b['bus_2'], label)
                        dot.edge(label, b['bus_1'])
                elif i == 'transformers':
                    dot.node(b['output'], shape='ellipse', fontsize="10")
                    dot.edge(b[bus[i][0]], label)
                    dot.edge(label, b['output'])
                    if b['output2'] != "None":
                        dot.node(b['output2'], shape='ellipse', fontsize="10")
                        dot.edge(label, b['output2'])
                    if str(b['mode']) not in checklist:
                        # consideration of mode of operation
                        if b['mode'] == 'heat_pump':
                            temp = '_low_temp'
                        elif b['mode'] == 'chiller':
                            temp = '_high_temp'
                        # creates label for source and bus depending on mode
                        cmpr_abs_source = label + temp + '_source'
                        cmpr_abs_bus = label + temp + '_bus'
                        # Linebreaks, so that the labels fit the boxes
                        cmpr_abs_source = linebreaks(cmpr_abs_source)
                        cmpr_abs_bus = linebreaks(cmpr_abs_bus)
                        # Adds a second input and a heat source (node and edge)
                        # for compressionand absorption heat transformers
                        dot.node(cmpr_abs_bus,
                                 shape='ellipse',
                                 fontsize="10")
                        dot.edge(cmpr_abs_bus, label)
                        dot.node(cmpr_abs_source, shape='trapezium',
                                 fontsize="10",
                                 fixedsize='shape', width='1.1', height='0.6')
                        dot.edge(cmpr_abs_source, cmpr_abs_bus)
                elif i == 'buses':
                    if b['excess'] and b['shortage']:
                        label = b['label'] + '_excess'
                        label = linebreaks(label)
                        dot.node(label, shape='invtrapezium', fontsize="10",
                                 fixedsize='shape', width='1.1', height='0.6')
                        dot.node(b[bus[i][0]], shape='ellipse', fontsize="10")
                        dot.edge(b[bus[i][0]], label)
    dot.render(filepath + '/graph.gv', view=True)
