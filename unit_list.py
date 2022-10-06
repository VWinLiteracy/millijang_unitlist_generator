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
IDOL_NAME_SIZE = 4*mm
ROW_SIZE = 6*mm
INTERVAL_SIZE = 6*mm
MERGIN_LEFT_SIZE = 10*mm
MERGIN_VERTICAL_SIZE = 10*mm
MEMBER_MAX = 6

def generate_list_by_idol(idol, idol_dict, unit_dict):
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
                    note += f"{song['mltd']['event']} "
                    note = re.sub('～.+～', '', note)
                if 'date' in song['mltd']:
                    note += f"({song['mltd']['date']})"
            elif 'release' in song:
                note += f"(CD){song['release'].get('disc', '')}"
                note = re.sub('THE IDOLM@STER (MILLION LIVE!)?', '', note)
            list_by_idol[-1].append(note)
    return list_by_idol

def generate(idol_dict, unit_dict, filename):
    filename = f"output/{filename}.pdf"
    page = canvas.Canvas(filename, pagesize=portrait(A4))

    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
    page.setFont('HeiseiKakuGo-W5', 12)
    height_top = MERGIN_VERTICAL_SIZE

    for idol in idol_dict:
        list_by_idol = generate_list_by_idol(idol, idol_dict, unit_dict)
        list_by_idol = [['[ユニット名]代表曲'] + ['メンバー'] * (MEMBER_MAX - 1) + ['ミリシタ実装/収録CD']] + list_by_idol
        table = Table(
            list_by_idol, 
            rowHeights=6*mm)
        style = TableStyle([
            ('FONT', (0, 0), (-1, -1), 'HeiseiKakuGo-W5', 8),
            ('SPAN', (1, 0), (MEMBER_MAX - 1, 0)),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.white),
            ])
        for row in list_by_idol:
            if len(row[0]) > 27:
                i = list_by_idol.index(row)
                style.add('FONT', (0, i), (0, i), 'HeiseiKakuGo-W5', 6)
        style.add('FONT', (MEMBER_MAX, 1), (MEMBER_MAX, -1), 'HeiseiKakuGo-W5', 6)
        table.setStyle(style)
        height_bottom = height_top + IDOL_NAME_SIZE + len(list_by_idol) * ROW_SIZE
        if height_bottom + MERGIN_VERTICAL_SIZE > A4_HEIGHT:
            page.showPage()
            page.setFont('HeiseiKakuGo-W5', 12)
            height_top = MERGIN_VERTICAL_SIZE
            height_bottom = height_top + IDOL_NAME_SIZE + len(list_by_idol) * ROW_SIZE
        page.drawString(MERGIN_LEFT_SIZE, A4_HEIGHT - height_top - IDOL_NAME_SIZE * 0.5, idol)
        table.wrapOn(page, MERGIN_LEFT_SIZE, A4_HEIGHT - height_bottom)
        table.drawOn(page, MERGIN_LEFT_SIZE, A4_HEIGHT - height_bottom)
        
        height_top = height_bottom + INTERVAL_SIZE
    page.save()
