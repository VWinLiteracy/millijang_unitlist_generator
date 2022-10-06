import codecs
import yaml

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

def main():
    with codecs.open("millijang_idol_song/idol.yml", "r", "utf-8") as yml:
        idol_dict = yaml.safe_load(yml)
    with codecs.open("millijang_idol_song/song.yml", "r", "utf-8") as yml:
        song_list = yaml.safe_load(yml)
    filterd_song_list = unitfilter.filter(song_list)
    unit_dict = generate_unit_dict(filterd_song_list, idol_dict)
    duo_graph.generate(idol_dict, unit_dict, 'duo')
    unit_list.generate(idol_dict, unit_dict, 'list')

if __name__ == '__main__':
    main()