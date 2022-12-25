import codecs
import yaml
import argparse

import unitfilter
import duo_graph
import unit_list

def generate_unit_dict(song_list, idol_dict):
    for song in song_list:
        song['member_bin'] = 0
        member_list = song.get('member', [])
        if len(member_list) <= 1 or len(member_list) >= 7:
            continue
        for idol in member_list:
            if idol_dict.get(idol, []) == []:
                continue
            song['member_bin'] += 2 ** (len(idol_dict) - idol_dict[idol]['id'])
    unit_dict = dict()
    for song in song_list:
        if song['member_bin'] == 0:
            continue
        if song['member_bin'] in unit_dict.keys():
            unit_dict[song['member_bin']].append(song)
        else:
            unit_dict[song['member_bin']] = [song]
    return unit_dict

def main(args):
    if args.suffix is None:
        suffix = ''
    else:
        suffix = f'_{args.suffix}'
    with codecs.open('millijang_idol_song/idol.yml', 'r', 'utf-8') as yml:
        idol_dict = yaml.safe_load(yml)
    with codecs.open('millijang_idol_song/song.yml', 'r', 'utf-8') as yml:
        song_list = yaml.safe_load(yml)
    with codecs.open('millijang_idol_song/team.yml', 'r', 'utf-8') as yml:
        team_list = yaml.safe_load(yml)
    filterd_song_list = unitfilter.filter(song_list)
    unit_dict = generate_unit_dict(filterd_song_list, idol_dict)
    duo_option = {
        'filename': f'duo{suffix}', 
        'engine': 'dot',
        'graph_attr': 
            {
                'rankdir': 'LR',
                'overlap': 'false',
                'splines': 'true',
            },
        'weight': {2: 100, 3: 1, 4: 1, 5: 1, 6: 1},
        'threshold': {'black': 100, 'orange': 101, 'red': 999},
        'label': True}
    duo_graph.generate(idol_dict, unit_dict, duo_option)
    kiteru_option = {
        'filename': f'kiteru{suffix}',
        'engine': 'fdp',
        'graph_attr': 
            {
                'overlap': 'false',
                'splines': 'true',
            },
        'weight': {2: 13, 3: 6, 4: 5, 5: 4, 6: 3},
        'threshold': {'black': 12, 'orange': 17, 'red': 19}}
    duo_graph.generate(idol_dict, unit_dict, kiteru_option)
    unit_option = {'filename': f'unit{suffix}'}
    unit_list.generate(idol_dict, unit_dict, team_list, unit_option)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--suffix', help='出力ファイル名の接尾語')
    parser.add_argument('-e', '--engine', help='Graphvizのエンジン')
    main(parser.parse_args())