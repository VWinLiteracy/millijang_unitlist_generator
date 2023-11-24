import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors

A4_HEIGHT = 297*mm
A4_WIDTH = 210*mm
IDOL_NAME_SIZE = 6*mm
ROW_SIZE = 6*mm
INTERVAL_SIZE = 3*mm
MERGIN_LEFT_SIZE = 2*mm
MERGIN_VERTICAL_SIZE = 2*mm

DEFAULT_FONTSIZE = 11

MEMBER_MAX = 6

def generate_list_by_idol(idol, idol_dict, unit_dict) -> list:
    list_by_idol = []
    for unit_bin in unit_dict:
        if idol in unit_dict[unit_bin][0]['member']:
            unit_in_idol_list = []
            song_list = []
            cover_list = []
            for song in unit_dict[unit_bin]:
                if 'unit' in song:
                    unit_in_idol_list.append(song)
                elif 'cover' in song:
                    cover_list.append(song)
                else:
                    song_list.append(song)
            if len(unit_in_idol_list) > 0:
                song = unit_in_idol_list[0]
                row = [f"[{song['unit']}] {song['song']}"]
            elif len(song_list) > 0:
                song = song_list[0]
                row = [f"{song['song']}"]
            else:
                song = cover_list[0]
                row = [f"{song['song']}"]
            list_by_idol.append(row)
            unit_member = []
            for mem in idol_dict:
                if mem == idol:
                    continue
                if mem in unit_dict[unit_bin][0]['member']:
                    unit_member.append(mem)
            list_by_idol[-1] = (list_by_idol[-1] + unit_member + [''] * 5)[:6]
            note = ''
            if 'mltd' in song:
                if 'event' in song['mltd']:
                    note = f"{song['mltd']['event']}"
                    note = re.sub(r'(プラチナスター[^\s～]+).+', r'\1', note)
                if 'date' in song['mltd']:
                    note += f"({song['mltd']['date']})"
            elif 'release' in song:
                note = f"(CD){song['release'].get('disc', '')}"
                note = re.sub('THE IDOLM@STER (MILLION LIVE!)?', '', note)
            list_by_idol[-1].append(note)
            default_date = '2099.12.31'
            date = min(
                default_date, 
                song.get('mltd', {}).get('date', default_date), 
                song.get('release', {}).get('date', default_date))
            list_by_idol[-1].append(date)
    sorted_list = sorted(list_by_idol, key=lambda x: x[-1])
    result = list(map(lambda x: x[:-1], sorted_list))
    return result

def new_page(page, idol_list, idol_in_page):
    for idx in range(len(idol_list)):
        rect_width = 18*mm
        rect_icon = 3*mm
        rect_left = A4_WIDTH - rect_width - rect_icon
        rect_height = A4_HEIGHT / len(idol_list)
        rect_bottom = A4_HEIGHT - rect_height * (idx + 1)
        page.rect(rect_left, rect_bottom, rect_width, rect_height)
        page.rect(rect_left + rect_width, rect_bottom, rect_icon, rect_height, fill=1 if idol_list[idx] in idol_in_page else 0)
        page.drawCentredString(rect_left + rect_width / 2, rect_bottom + 1*mm, idol_list[idx])
        page.linkAbsolute(idol_list[idx], idol_list[idx], (rect_left, rect_bottom, A4_WIDTH, rect_bottom + rect_height))
    page.showPage()
    idol_in_page = []
    return idol_in_page

def generate(idol_dict, unit_dict, team_list, option={}):
    filename = f"output/{option.get('filename', 'unit')}.pdf"
    page = canvas.Canvas(filename, pagesize=portrait(A4))

    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    page.setFont('HeiseiKakuGo-W5', DEFAULT_FONTSIZE)
    height_top = MERGIN_VERTICAL_SIZE
    idol_in_page = []
    idol_list = list(idol_dict.keys()) + ['13人']
        
    for idol in idol_list:
        if idol == '13人':
            table_contents = [['[チーム名]代表曲'] + ['メンバー'] * 7]
            for team in team_list:
                if len(team['member']) != 13:
                    continue
                table_contents.append([
                    f"[{team['team']}]{team.get('song', '')}",
                    team['member'][0],
                    team['member'][1],
                    team['member'][2],
                    team['member'][3],
                    team['member'][4],
                    team['member'][5],
                    team['member'][6],])
                table_contents.append([
                    '',
                    team['member'][7],
                    team['member'][8],
                    team['member'][9],
                    team['member'][10],
                    team['member'][11],
                    team['member'][12],
                    '',])
            table = Table(
                table_contents, 
                rowHeights=6*mm)
            style = TableStyle([
                ('FONT', (0, 0), (-1, -1), 'HeiseiKakuGo-W5', 8),
                ('SPAN', (1, 0), (7, 0)),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('LINEAFTER', (0, 0), (0, -1), 1, colors.black),
                ])
            i = 1
            while i < len(table_contents):
                style.add('VALIGN', (0, i), (0, i + 1), 'MIDDLE')
                style.add('SPAN', (0, i), (0, i + 1))
                style.add('INNERGRID', (1, i), (-1, i + 1), 0.1, colors.black)
                style.add('LINEBELOW', (0, i + 1), (-1, i + 1), 1, colors.black)
                i = i + 2
            style.add('LINEBELOW', (0, 0), (-1, 0), 2, colors.black)
            style.add('LINEBELOW', (0, 0), (-1, 0), 1, colors.white)
        else:
            list_by_idol = generate_list_by_idol(idol, idol_dict, unit_dict)
            table_contents = [['[ユニット名]代表曲'] + ['メンバー'] * (MEMBER_MAX - 1) + ['ミリシタ実装/収録CD']] + list_by_idol
            table = Table(
                table_contents, 
                rowHeights=6*mm)
            style = TableStyle([
                ('FONT', (0, 0), (-1, -1), 'HeiseiKakuGo-W5', 8),
                ('SPAN', (1, 0), (MEMBER_MAX - 1, 0)),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('LINEAFTER', (0, 0), (0, -1), 1, colors.black),
                ('LINEAFTER', (-2, 0), (-2, -1), 1, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.white),
                ])
            for row in table_contents:
                i = table_contents.index(row)
                style.add('INNERGRID', (1, i), (MEMBER_MAX - 1, i), 0.1, colors.black)
                style.add('LINEBELOW', (0, i), (-1, i), 1, colors.black)
                song_size: int = 8
                if len(row[0]) >= 15:
                    song_size = 7
                if len(row[0]) >= 25:
                    song_size = 6
                if len(row[0]) >= 35:
                    song_size = 5
                style.add('FONT', (0, i), (0, i), 'HeiseiKakuGo-W5', song_size)
                release_size: int = 6
                if len(row[MEMBER_MAX]) >= 25:
                    release_size = 5
                if len(row[MEMBER_MAX]) >= 45:
                    release_size = 4
                style.add('FONT', (MEMBER_MAX, i), (MEMBER_MAX, i), 'HeiseiKakuGo-W5', release_size)
            style.add('LINEBELOW', (0, 0), (-1, 0), 2, colors.black)
            style.add('LINEBELOW', (0, 0), (-1, 0), 1, colors.white)
        table.setStyle(style)
        height_bottom = height_top + IDOL_NAME_SIZE + len(table_contents) * ROW_SIZE
        if height_bottom + MERGIN_VERTICAL_SIZE > A4_HEIGHT:
            idol_in_page = new_page(page, idol_list, idol_in_page)
            page.setFont('HeiseiKakuGo-W5', DEFAULT_FONTSIZE)
            height_top = MERGIN_VERTICAL_SIZE
            height_bottom = height_top + IDOL_NAME_SIZE + len(table_contents) * ROW_SIZE
        if idol == '13人':
            page.drawString(MERGIN_LEFT_SIZE, A4_HEIGHT - height_top - IDOL_NAME_SIZE + 2*mm, '13人ライブ')
        else:
            page.drawString(MERGIN_LEFT_SIZE, A4_HEIGHT - height_top - IDOL_NAME_SIZE + 2*mm, idol)
        page.bookmarkPage(idol, fit='FitH', top=A4_HEIGHT - height_top)
        table.wrapOn(page, MERGIN_LEFT_SIZE, A4_HEIGHT - height_bottom)
        table.drawOn(page, MERGIN_LEFT_SIZE, A4_HEIGHT - height_bottom)
        idol_in_page.append(idol)
        
        height_top = height_bottom + INTERVAL_SIZE
    idol_in_page = new_page(page, idol_list, idol_in_page)
    page.save()
