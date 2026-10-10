import json, sys, re, base64, io, textwrap
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table,
                                TableStyle, XPreformatted, KeepTogether)
from reportlab.lib.utils import ImageReader

nb_path, logo_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
nb = json.load(open(nb_path))

W, H = A4
M = 1.8 * cm
TW = W - 2 * M
NAVY = colors.HexColor('#1F3A68')

cover_uni = ParagraphStyle('uni', fontName='Helvetica-BoldOblique', fontSize=15, alignment=TA_CENTER, leading=20)
cover_txt = ParagraphStyle('ct', fontName='Times-Roman', fontSize=22, alignment=TA_CENTER, leading=30)
h1 = ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=17, leading=22, textColor=NAVY, spaceBefore=6, spaceAfter=10)
h2 = ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=NAVY, spaceBefore=12, spaceAfter=6, keepWithNext=1)
h3 = ParagraphStyle('h3', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=NAVY, spaceBefore=8, spaceAfter=4, keepWithNext=1)
body = ParagraphStyle('b', fontName='Times-Roman', fontSize=11, leading=15, alignment=TA_JUSTIFY, spaceAfter=6)
bullet = ParagraphStyle('bl', parent=body, leftIndent=14, bulletIndent=4, spaceAfter=3)
label = ParagraphStyle('lb', fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.HexColor('#666666'), spaceBefore=4, spaceAfter=1)
code_st = ParagraphStyle('code', fontName='Courier', fontSize=7.6, leading=9.4)
out_st = ParagraphStyle('out', fontName='Courier', fontSize=7.2, leading=8.8)

BOX = {}
for ch in '┏┓┗┛┡┩└┘┌┐┳┻╇┼┬┴├┤╋┣┫╈╀╁┠┨┢┪': BOX[ord(ch)] = '+'
for ch in '━─═╍┅': BOX[ord(ch)] = '-'
for ch in '┃│║': BOX[ord(ch)] = '|'

def ascii_safe(s):
    s = s.translate(BOX)
    return ''.join(c if ord(c) < 256 else '?' for c in s)

def esc(s):
    s = ascii_safe(s)
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def inline_md(s):
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'`(.+?)`', r'<font face="Courier">\1</font>', s)
    return s

def wrap_lines(text, width):
    out = []
    for line in text.split('\n'):
        if len(line) <= width:
            out.append(line)
            continue
        ind = len(line) - len(line.lstrip())
        parts = textwrap.wrap(line, width=width, subsequent_indent=' ' * (ind + 4), break_long_words=True, break_on_hyphens=False, drop_whitespace=False)
        out.extend(parts or [line])
    return '\n'.join(out)

def clean_stream(t):
    t = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', t)
    while '\x08' in t:
        t = re.sub(r'[^\x08\n]\x08', '', t)
        t = t.replace('\n\x08', '\n').lstrip('\x08')
    lines = []
    for line in t.split('\n'):
        if '\r' in line:
            segs = [s for s in line.split('\r') if s.strip()]
            line = segs[-1] if segs else ''
        lines.append(line)
    return '\n'.join(lines)

def boxed(flow, bg, border):
    t = Table([[flow]], colWidths=[TW])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg), ('BOX', (0, 0), (-1, -1), 0.5, border),
                           ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                           ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    return t

def text_blocks(text, style, bg, border, width=108, chunk=70):
    text = wrap_lines(text.rstrip('\n'), width)
    lines = text.split('\n')
    flows = []
    for i in range(0, len(lines), chunk):
        flows.append(boxed(XPreformatted(esc('\n'.join(lines[i:i + chunk])), style), bg, border))
    return flows

story = []
story.append(Spacer(1, 2.2 * cm))
logo = Image(logo_path, width=5 * cm, height=5 * cm * 150 / 148)
story.append(logo)
story.append(Spacer(1, 0.6 * cm))
story.append(Paragraph('COMSATS University Islamabad', cover_uni))
story.append(Spacer(1, 4 * cm))
for line in ['Waleed Ahmad', 'FA23-BBD-151', 'Lab Assignment 9, 10', 'Section: 7B']:
    story.append(Paragraph(line, cover_txt))
story.append(PageBreak())

story.append(Paragraph('Instructions', h1))
intro = [
    ('p', 'This submission contains the complete work for Lab 9 (Sequence-to-Sequence Models in Python) and Lab 10 (Seq2Seq with Attention vs without Attention) of the deep learning lab manual on attention mechanisms for sequence modelling in Business Data Analytics. Each lab includes the step-by-step walkthrough, all lab tasks and the lab assignment, with every code cell followed by its output.'),
    ('h', 'Contents'),
    ('b', '<b>Lab 9:</b> walkthrough Steps 1 to 7 (dataset, input preparation, encoder-decoder LSTM, training, greedy decoding and evaluation, context-vector bottleneck), Lab Tasks 1 to 4, and Lab Assignment 3 (Tasks 1 to 6).'),
    ('b', '<b>Lab 10:</b> walkthrough Steps 1 to 7 (attention by hand, data, models with and without attention, training, comparison, attention heatmaps, own dates), Lab Tasks 1 to 4, and Lab Assignment 4 (Tasks 1 to 6).'),
    ('h', 'Tools and dataset'),
    ('b', '<b>Software:</b> Python 3 with TensorFlow/Keras, NumPy, pandas and Matplotlib, run in Google Colab.'),
    ('b', '<b>Labs 9 and 10 dataset:</b> 20,000 synthetic invoice dates (1990 to 2029, written in 8 supplier formats) paired with the standard ISO date; 16,000 pairs for training and 4,000 for testing, generated in the notebook with a fixed random seed.'),
    ('b', '<b>Assignment 3 dataset:</b> 12,000 amounts written in words paired with their digits (for example "two thousand five hundred" to 2500); 10,000 for training and 2,000 for testing.'),
    ('b', '<b>Assignment 4 dataset:</b> the invoice dates with a supplier name and invoice number placed before the date, so the model must find the date inside a longer string.'),
    ('h', 'How to read this document'),
    ('b', 'Grey boxes contain the code exactly as it was run. The boxes below them, with a blue border, contain the output of that code: printed results, tables, model summaries, training logs and charts.'),
    ('b', 'Written answers for tasks that ask for an explanation, recommendation or conclusion appear after the related code and output.'),
    ('b', 'Accuracy values and training times depend on the run, so the figures shown are the ones produced in this run of the notebook.'),
]
for kind, t in intro:
    if kind == 'p':
        story.append(Paragraph(t, body))
    elif kind == 'h':
        story.append(Paragraph(t, h3))
    else:
        story.append(Paragraph(t, bullet, bulletText='•'))
story.append(PageBreak())

CODE_BG, CODE_BD = colors.HexColor('#F4F5F7'), colors.HexColor('#C9CDD3')
OUT_BG, OUT_BD = colors.white, colors.HexColor('#8FB3E0')
first_lab = True

for cell in nb['cells']:
    src = ''.join(cell['source'])
    if cell['cell_type'] == 'markdown':
        for block in src.split('\n\n'):
            block = block.strip()
            if not block:
                continue
            if block.startswith('# '):
                if not first_lab:
                    story.append(PageBreak())
                first_lab = False
                story.append(Paragraph(inline_md(block[2:]), h1))
            elif block.startswith('### '):
                story.append(Paragraph(inline_md(block[4:]), h3))
            elif block.startswith('## '):
                story.append(Paragraph(inline_md(block[3:]), h2))
            elif block.startswith('- '):
                for item in block.split('\n'):
                    story.append(Paragraph(inline_md(item[2:].strip()), bullet, bulletText='•'))
            else:
                story.append(Paragraph(inline_md(block.replace('\n', ' ')), body))
        continue

    flows = [Paragraph('CODE', label)] + text_blocks(src, code_st, CODE_BG, CODE_BD, width=108)
    out_flows = []
    for o in cell.get('outputs', []):
        if o['output_type'] == 'stream':
            out_flows += text_blocks(clean_stream(''.join(o['text'])), out_st, OUT_BG, OUT_BD, width=114)
        elif o['output_type'] in ('execute_result', 'display_data'):
            d = o.get('data', {})
            if 'image/png' in d:
                raw = base64.b64decode(d['image/png'] if isinstance(d['image/png'], str) else ''.join(d['image/png']))
                iw, ih = ImageReader(io.BytesIO(raw)).getSize()
                w = min(TW * 0.9, iw * 0.75)
                h = w * ih / iw
                if h > H * 0.55:
                    h = H * 0.55
                    w = h * iw / ih
                out_flows.append(Image(io.BytesIO(raw), width=w, height=h))
            elif 'text/plain' in d:
                out_flows += text_blocks(clean_stream(''.join(d['text/plain'])), out_st, OUT_BG, OUT_BD, width=114)
        elif o['output_type'] == 'error':
            out_flows += text_blocks(clean_stream('\n'.join(o.get('traceback', []))), out_st, colors.HexColor('#FFF4F4'), colors.HexColor('#E0A0A0'), width=114)
    if out_flows:
        flows += [Paragraph('OUTPUT', label)] + out_flows
    flows.append(Spacer(1, 6))
    story.append(KeepTogether(flows[:3]))
    story.extend(flows[3:])

def footer(c, doc):
    if doc.page == 1:
        return
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#777777'))
    c.drawString(M, 1.0 * cm, 'Waleed Ahmad  |  FA23-BBD-151  |  Lab Assignment 9, 10')
    c.drawRightString(W - M, 1.0 * cm, f'Page {doc.page}')

doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=1.8 * cm,
                        title='Lab Assignment 9, 10 - Waleed Ahmad', author='Waleed Ahmad')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print('built', out_path)
