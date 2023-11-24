import codecs
import yaml
import argparse
import glob

import unitfilter
import duo_graph
import unit_list

def generate_unit_dict(
        song_list: list[dict[str, any]], 
        idol_dict: dict[str, dict[str, any]]
    ) -> dict[str, dict[str, any]]:
    for song in song_list:
        song['member_bin'] = 0
        member_list: list[str] = song.get('member', [])
        if len(member_list) <= 1 or len(member_list) >= 7:
            continue
        for idol in member_list:
            listed_idol: dict[str, any] = idol_dict.get(idol)
            if listed_idol is None:
                continue
            song['member_bin'] += 2 ** (len(idol_dict) - listed_idol['id'])
    unit_dict: dict[str, dict[str, any]] = dict()
    for song in song_list:
        if song['member_bin'] == 0:
            continue
        if song['member_bin'] in unit_dict.keys():
            unit_dict[song['member_bin']].append(song)
        else:
            unit_dict[song['member_bin']] = [song]
    return unit_dict

def main(args):
    suffix: str = ''
    if args.suffix:
        suffix = f'_{args.suffix}'
    with codecs.open('idol.yml', 'r', 'utf-8') as yml:
        idol_dict: dict[str, dict[str, any]] = yaml.safe_load(yml)
    song_yaml_list: list[str] = glob.glob('millijang_idol_song/*.yaml')
    song_list: list[dict[str, any]] = []
    for filepath in song_yaml_list:
        with codecs.open(filepath, 'r', 'utf-8') as yml:
            song_list = song_list + yaml.safe_load(yml)
    with codecs.open('team.yml', 'r', 'utf-8') as yml:
        team_list: list[dict[str, any]] = yaml.safe_load(yml)
    filtered_song_list: list[dict[str, any]] = unitfilter.filter(song_list)
    unit_dict: dict[str, dict[str, any]] = generate_unit_dict(filtered_song_list, idol_dict)

    # Generate duo graph
    duo_engine = 'fdp'
    if args.engine:
        duo_engine = args.engine
    duo_option: dict[str, any] = {
        'filename': f'duo{suffix}', 
        'engine': duo_engine,
        'graph_attr': 
            {
                # 'rankdir': 'LR',
                'overlap': 'false',
                'splines': 'true',
            },
        'weight': {2: 100, 3: 1, 4: 1, 5: 1, 6: 1},
        'threshold': {'black': 100, 'orange': 101, 'red': 102},
        'label': True}
    duo_graph.generate(idol_dict, unit_dict, duo_option)

    # Generate kiteru graph
    kiteru_engine = 'fdp'
    if args.engine:
        kiteru_engine = args.engine
    kiteru_option: dict[str, any] = {
        'filename': f'kiteru{suffix}',
        'engine': kiteru_engine,
        'graph_attr': 
            {
                'overlap': 'false',
                'splines': 'true',
            },
        'weight': {2: 13, 3: 6, 4: 5, 5: 4, 6: 3},
        'threshold': {'black': 12, 'orange': 17, 'red': 19}}
    duo_graph.generate(idol_dict, unit_dict, kiteru_option)

    # Generate unit list
    unit_option = {'filename': f'unit{suffix}'}
    unit_list.generate(idol_dict, unit_dict, team_list, unit_option)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--suffix', help='出力ファイル名の接尾語')
    parser.add_argument(
        '-e',
        '--engine',
        help='Graphvizのエンジン (dot, neato, fdp, sfdp, circo, twopi, osage)')
    main(parser.parse_args())