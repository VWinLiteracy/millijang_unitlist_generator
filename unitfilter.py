def filter(song_list: list[dict[str, any]]) -> list[dict[str, any]]:
    filterd_song_list: list[dict[str, any]] = []
    for song in song_list:
        if not('mltd' in song) and 'cover' in song:
            continue
        filterd_song_list.append(song)
    return filterd_song_list