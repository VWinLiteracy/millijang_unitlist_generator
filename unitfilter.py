def filter(song_list):
    filterd_song_list = []
    for song in song_list:
        if not('mltd' in song) and 'cover' in song:
            continue
        filterd_song_list.append(song)
    return filterd_song_list