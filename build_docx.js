const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, ShadingType,
  BorderStyle, AlignmentType, HeadingLevel, PageBreak, LevelFormat, Footer, PageNumber, TabStopType
} = require('docx');

const [nbPath, logoPath, outPath] = process.argv.slice(2);
const nb = JSON.parse(fs.readFileSync(nbPath, 'utf8'));

const PAGE_W = 11906, MARGIN = 1020, TW = PAGE_W - 2 * MARGIN;
const NAVY = '1F3A68';
const TEXT_PX = Math.round(TW / 1440 * 96);

const BOX = {};
for (const ch of '┏┓┗┛┡┩└┘┌┐┳┻╇┼┬┴├┤╋┣┫╈╀╁┠┨┢┪') BOX[ch] = '+';
for (const ch of '━─═╍┅') BOX[ch] = '-';
for (const ch of '┃│║') BOX[ch] = '|';
const asciiSafe = s => [...s].map(c => BOX[c] || (c.codePointAt(0) < 256 ? c : '?')).join('');

function cleanStream(t) {
  t = t.replace(/\x1b\[[0-9;]*[A-Za-z]/g, '');
  while (t.includes('\x08')) {
    t = t.replace(/[^\x08\n]\x08/g, '');
    t = t.replace(/\n\x08/g, '\n').replace(/^\x08+/, '');
  }
  return t.split('\n').map(line => {
    if (!line.includes('\r')) return line;
    const segs = line.split('\r').filter(s => s.trim());
    return segs.length ? segs[segs.length - 1] : '';
  }).join('\n');
}

function wrapLines(text, width) {
  const out = [];
  for (const line of text.split('\n')) {
    if (line.length <= width) { out.push(line); continue; }
    const ind = line.length - line.trimStart().length;
    let rest = line;
    let first = true;
    while (rest.length > 0) {
      const w = first ? width : width - ind - 4;
      out.push((first ? '' : ' '.repeat(ind + 4)) + rest.slice(0, w));
      rest = rest.slice(w);
      first = false;
    }
  }
  return out;
}

function inlineRuns(s, base = {}) {
  s = asciiSafe(s);
  const runs = [];
  const re = /\*\*(.+?)\*\*|`(.+?)`/g;
  let last = 0, m;
  while ((m = re.exec(s))) {
    if (m.index > last) runs.push(new TextRun({ text: s.slice(last, m.index), ...base }));
    if (m[1] !== undefined) runs.push(new TextRun({ text: m[1], bold: true, ...base }));
    else runs.push(new TextRun({ text: m[2], font: 'Courier New', ...base }));
    last = re.lastIndex;
  }
  if (last < s.length) runs.push(new TextRun({ text: s.slice(last), ...base }));
  return runs;
}

const border = c => ({ style: BorderStyle.SINGLE, size: 4, color: c });

function box(lines, size, fill, borderColor) {
  const paras = lines.map(l => new Paragraph({
    spacing: { before: 0, after: 0, line: Math.round(size * 10 * 1.2) },
    children: [new TextRun({ text: asciiSafe(l) || ' ', font: 'Courier New', size })]
  }));
  const b = border(borderColor);
  return new Table({
    width: { size: TW, type: WidthType.DXA },
    columnWidths: [TW],
    rows: [new TableRow({
      cantSplit: false,
      children: [new TableCell({
        width: { size: TW, type: WidthType.DXA },
        shading: { fill, type: ShadingType.CLEAR, color: 'auto' },
        borders: { top: b, bottom: b, left: b, right: b },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: paras
      })]
    })]
  });
}

const label = t => new Paragraph({
  keepNext: true, spacing: { before: 100, after: 20 },
  children: [new TextRun({ text: t, bold: true, size: 15, color: '666666', font: 'Arial' })]
});

function pngSize(buf) {
  return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
}

function imagePara(buf) {
  const { w: iw, h: ih } = pngSize(buf);
  let w = Math.min(TEXT_PX * 0.9, iw * 0.75);
  let h = w * ih / iw;
  const maxH = 1123 * 0.55;
  if (h > maxH) { h = maxH; w = h * iw / ih; }
  return new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 60, after: 60 },
    children: [new ImageRun({ type: 'png', data: buf, transformation: { width: Math.round(w), height: Math.round(h) } })]
  });
}

const body = [];
const coverLine = t => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 160 },
  children: [new TextRun({ text: t, font: 'Times New Roman', size: 44 })]
});

body.push(new Paragraph({ spacing: { before: 1200 }, children: [] }));
const logo = fs.readFileSync(logoPath);
const ls = pngSize(logo);
body.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new ImageRun({ type: 'png', data: logo, transformation: { width: 189, height: Math.round(189 * ls.h / ls.w) } })]
}));
body.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 240, after: 2200 },
  children: [new TextRun({ text: 'COMSATS University Islamabad', font: 'Arial', bold: true, italics: true, size: 30 })]
}));
for (const t of ['Waleed Ahmad', 'FA23-BBD-151', 'Lab Assignment 9, 10', 'Section: 7B']) body.push(coverLine(t));
body.push(new Paragraph({ children: [new PageBreak()] }));

const bodyRun = { font: 'Times New Roman', size: 22 };
const para = t => new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 120, line: 300 }, children: inlineRuns(t, bodyRun) });
const bulletPara = t => new Paragraph({ numbering: { reference: 'bullets', level: 0 }, alignment: AlignmentType.JUSTIFIED, spacing: { after: 60, line: 300 }, children: inlineRuns(t, bodyRun) });
const h = (t, level) => new Paragraph({ heading: level, children: inlineRuns(t) });

body.push(h('Instructions', HeadingLevel.HEADING_1));
const intro = [
  ['p', 'This submission contains the complete work for Lab 9 (Sequence-to-Sequence Models in Python) and Lab 10 (Seq2Seq with Attention vs without Attention) of the deep learning lab manual on attention mechanisms for sequence modelling in Business Data Analytics. Each lab includes the step-by-step walkthrough, all lab tasks and the lab assignment, with every code cell followed by its output.'],
  ['h', 'Contents'],
  ['b', '**Lab 9:** walkthrough Steps 1 to 7 (dataset, input preparation, encoder-decoder LSTM, training, greedy decoding and evaluation, context-vector bottleneck), Lab Tasks 1 to 4, and Lab Assignment 3 (Tasks 1 to 6).'],
  ['b', '**Lab 10:** walkthrough Steps 1 to 7 (attention by hand, data, models with and without attention, training, comparison, attention heatmaps, own dates), Lab Tasks 1 to 4, and Lab Assignment 4 (Tasks 1 to 6).'],
  ['h', 'Tools and dataset'],
  ['b', '**Software:** Python 3 with TensorFlow/Keras, NumPy, pandas and Matplotlib, run in Google Colab.'],
  ['b', '**Labs 9 and 10 dataset:** 20,000 synthetic invoice dates (1990 to 2029, written in 8 supplier formats) paired with the standard ISO date; 16,000 pairs for training and 4,000 for testing, generated in the notebook with a fixed random seed.'],
  ['b', '**Assignment 3 dataset:** 12,000 amounts written in words paired with their digits (for example "two thousand five hundred" to 2500); 10,000 for training and 2,000 for testing.'],
  ['b', '**Assignment 4 dataset:** the invoice dates with a supplier name and invoice number placed before the date, so the model must find the date inside a longer string.'],
  ['h', 'How to read this document'],
  ['b', 'Grey boxes contain the code exactly as it was run. The boxes below them, with a blue border, contain the output of that code: printed results, tables, model summaries, training logs and charts.'],
  ['b', 'Written answers for tasks that ask for an explanation, recommendation or conclusion appear after the related code and output.'],
  ['b', 'Accuracy values and training times depend on the run, so the figures shown are the ones produced in this run of the notebook.'],
];
for (const [k, t] of intro) body.push(k === 'p' ? para(t) : k === 'h' ? h(t, HeadingLevel.HEADING_3) : bulletPara(t));

body.push(new Paragraph({ children: [new PageBreak()] }));
const CODE_BG = 'F4F5F7', CODE_BD = 'C9CDD3', OUT_BG = 'FFFFFF', OUT_BD = '8FB3E0';
const CODE_SZ = 14, OUT_SZ = 13, CODE_W = 108, OUT_W = 114;

function mergedOutputs(outs) {
  const merged = [];
  for (const o of outs) {
    const prev = merged[merged.length - 1];
    if (o.output_type === 'stream' && prev && prev.output_type === 'stream' && prev.name === o.name) {
      prev.text += [].concat(o.text).join('');
    } else if (o.output_type === 'stream') {
      merged.push({ output_type: 'stream', name: o.name, text: [].concat(o.text).join('') });
    } else merged.push(o);
  }
  return merged;
}

let firstLab = true;
for (const cell of nb.cells) {
  const src = [].concat(cell.source).join('');
  if (cell.cell_type === 'markdown') {
    for (let block of src.split('\n\n')) {
      block = block.trim();
      if (!block) continue;
      if (block.startsWith('# ')) {
        if (!firstLab) body.push(new Paragraph({ children: [new PageBreak()] }));
        firstLab = false;
        body.push(h(block.slice(2), HeadingLevel.HEADING_1));
      } else if (block.startsWith('### ')) body.push(h(block.slice(4), HeadingLevel.HEADING_3));
      else if (block.startsWith('## ')) body.push(h(block.slice(3), HeadingLevel.HEADING_2));
      else if (block.startsWith('- ')) for (const item of block.split('\n')) body.push(bulletPara(item.slice(2).trim()));
      else body.push(para(block.replace(/\n/g, ' ')));
    }
    continue;
  }
  body.push(label('CODE'));
  body.push(box(wrapLines(src.replace(/\n+$/, ''), CODE_W), CODE_SZ, CODE_BG, CODE_BD));
  const outs = mergedOutputs(cell.outputs || []);
  if (outs.length) body.push(label('OUTPUT'));
  for (const o of outs) {
    if (o.output_type === 'stream') {
      body.push(box(wrapLines(cleanStream(o.text).replace(/\n+$/, ''), OUT_W), OUT_SZ, OUT_BG, OUT_BD));
    } else if (o.output_type === 'execute_result' || o.output_type === 'display_data') {
      const d = o.data || {};
      if (d['image/png']) body.push(imagePara(Buffer.from([].concat(d['image/png']).join(''), 'base64')));
      else if (d['text/plain']) body.push(box(wrapLines(cleanStream([].concat(d['text/plain']).join('')).replace(/\n+$/, ''), OUT_W), OUT_SZ, OUT_BG, OUT_BD));
    } else if (o.output_type === 'error') {
      body.push(box(wrapLines(cleanStream((o.traceback || []).join('\n')), OUT_W), OUT_SZ, 'FFF4F4', 'E0A0A0'));
    }
  }
  body.push(new Paragraph({ spacing: { after: 80 }, children: [] }));
}

const footer = new Footer({
  children: [new Paragraph({
    tabStops: [{ type: TabStopType.RIGHT, position: TW }],
    children: [
      new TextRun({ text: 'Waleed Ahmad  |  FA23-BBD-151  |  Lab Assignment 9, 10', size: 16, color: '777777', font: 'Arial' }),
      new TextRun({ text: '\tPage ', size: 16, color: '777777', font: 'Arial' }),
      new TextRun({ children: [PageNumber.CURRENT], size: 16, color: '777777', font: 'Arial' })
    ]
  })]
});

const doc = new Document({
  creator: 'Waleed Ahmad',
  title: 'Lab Assignment 9, 10 - Waleed Ahmad',
  styles: {
    default: { document: { run: { font: 'Times New Roman', size: 22 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: 'Arial', size: 34, bold: true, color: NAVY }, paragraph: { spacing: { before: 120, after: 200 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: 'Arial', size: 26, bold: true, color: NAVY }, paragraph: { spacing: { before: 240, after: 120 }, keepNext: true, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: 'Arial', size: 22, bold: true, color: NAVY }, paragraph: { spacing: { before: 160, after: 80 }, keepNext: true, outlineLevel: 2 } }
    ]
  },
  numbering: { config: [{ reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 360, hanging: 220 } } } }] }] },
  sections: [{
    properties: { titlePage: true, page: { size: { width: PAGE_W, height: 16838 }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } },
    footers: { default: footer, first: new Footer({ children: [new Paragraph({ children: [] })] }) },
    children: body
  }]
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(outPath, buf); console.log('built', outPath); });
