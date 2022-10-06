from graphviz import Graph

def generate_graph(g, idol_dict, unit_dict):
    g = add_idol_node(g, idol_dict)
    for bin in unit_dict:
        if len(unit_dict[bin][0].get('member', [])) == 2:
            extend_unit_list = []
            for bin2 in unit_dict:
                if bin == bin2:
                    continue
                if (unit_dict[bin][0]['member_bin'] & unit_dict[bin2][0]['member_bin']) == unit_dict[bin][0]['member_bin']:
                    extend_unit_list.append(unit_dict[bin2])
            extend_size_list = []
            for ex in extend_unit_list:
                extend_size_list.append(len(ex[0].get('member', [])))
            g = add_duo_edge(g, unit_dict[bin][0].get('member', []), extend_size_list)
    return g

def add_idol_node(g, idol_dict):
    for idol in idol_dict:
        if idol_dict[idol]['type'] == 'Princess Stars':
            g.node(idol, style='filled', fillcolor='pink')
        elif idol_dict[idol]['type'] == 'Fairy Stars':
            g.node(idol, style='filled', fillcolor='lightblue')
        elif idol_dict[idol]['type'] == 'Angel Stars':
            g.node(idol, style='filled', fillcolor='yellow')
    return g

def add_duo_edge(g, duo, extend_size_list):
    if len(extend_size_list) > 0:
        sorted_extend_size_list = sorted(extend_size_list)
        label = ','.join(map(str, sorted_extend_size_list))
        g.edge(duo[0], duo[1], label, style='bold', color='orange')
    else:
        g.edge(duo[0], duo[1])
    return g

def generate(idol_dict, unit_dict, filename):
    g = Graph(format='pdf', 
              directory='output',
              filename=filename, 
              graph_attr={'rankdir': 'LR'},
              node_attr={'fontname': 'Meiryo UI'})
    g = generate_graph(g, idol_dict, unit_dict)
    g.render()
