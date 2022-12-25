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

def generate_graph2(g, idol_dict, unit_dict, option):
    g = add_idol_node(g, idol_dict)
    duo_dict = dict()
    idol_list = list(idol_dict.keys())
    for idx1 in range(len(idol_list)):
        for idx2 in range(idx1 + 1, len(idol_list)):
            duo_dict[(idol_list[idx1], idol_list[idx2])] = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    for bin in unit_dict:
        member_list = unit_dict[bin][0].get('member', [])
        for idx1 in range(len(member_list)):
            for idx2 in range(idx1 + 1, len(member_list)):
                if idol_dict[member_list[idx1]]['id'] > idol_dict[member_list[idx2]]['id']:
                    idol1 = member_list[idx2]
                    idol2 = member_list[idx1]
                else:
                    idol1 = member_list[idx1]
                    idol2 = member_list[idx2]
                duo_dict[(idol1, idol2)][len(member_list)] += 1
    g = add_duo_edge2(g, duo_dict, option)
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

def add_duo_edge2(g, duo_dict, option):
    duo_list = duo_dict.keys()
    weight = option.get('weight', {})
    threshold = option.get('threshold', {})
    for duo in duo_list:
        kiteru_val = 0
        kiteru_val += duo_dict[duo][2] * weight.get(2, 100)
        kiteru_val += duo_dict[duo][3] * weight.get(3, 1)
        kiteru_val += duo_dict[duo][4] * weight.get(4, 1)
        kiteru_val += duo_dict[duo][5] * weight.get(5, 1)
        kiteru_val += duo_dict[duo][6] * weight.get(6, 1)
        if kiteru_val >= threshold.get('black', 100):
            if option.get('label') == True:
                label_list = [] + [3] * duo_dict[duo][3] + [4] * duo_dict[duo][4] + [5] * duo_dict[duo][5] + [6] * duo_dict[duo][6]
                label = ','.join(map(str, label_list))
            else:
                label = ''
            if duo_dict[duo][2] > 0:
                style = ''
            else:
                style = 'dashed'
            if kiteru_val >= threshold.get('red', 999):
                color = 'red'
            elif kiteru_val >= threshold.get('orange', 101):
                color = 'orange'
            else:
                color = 'black'
            g.edge(duo[0], duo[1], label=label, style=style, color=color)
    return g

def generate(idol_dict, unit_dict, option={}):
    g = Graph(format='pdf', 
              directory='output',
              filename=option.get('filename', 'duo'), 
              engine=option.get('engine', 'dot'),
              graph_attr=option.get('graph_attr',
                {
                    'rankdir': 'LR',
                    'overlap': 'false',
                    'splines': 'true',
                }),
              node_attr={'fontname': 'Meiryo UI'})
    # g = generate_graph(g, idol_dict, unit_dict)
    g = generate_graph2(g, idol_dict, unit_dict, option)
    g.render()
