# Task: Run the Lab 9 + Lab 10 notebook and build the submission PDF

You are working in a folder that contains:

- `Lab9_Lab10_Seq2Seq_Attention.ipynb`: the full notebook (Lab 9 walkthrough, tasks, Assignment 3; Lab 10 walkthrough, tasks, Assignment 4). It has not been run yet.
- `build_pdf.py`: builds the final PDF (cover page, instructions page, then every code cell with its output) from an executed notebook.
- `logo.png`: the COMSATS logo used on the cover page.

Goal: produce `Waleed_Ahmad_FA23-BBD-151_Lab_9_10.pdf` with real outputs from a real run.

## Rules

- Do not add comments to the code. The notebook must stay comment-free.
- Never type or invent outputs. Every number, table and chart must come from actually running the notebook.
- Do not change the logic of the walkthrough steps. Only fix code if a cell raises an error, and keep the fix minimal.

## Step 1: Set up Python

1. Use Python 3.10, 3.11 or 3.12 (TensorFlow may not support newer versions). Create a virtual environment in this folder:
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows: `py -3.11 -m venv .venv` then `.venv\Scripts\activate`
2. Install the packages:
   `pip install tensorflow pandas matplotlib nbformat nbconvert ipykernel reportlab pypdf pillow`
3. Check it works: `python -c "import tensorflow as tf; print(tf.__version__)"`

## Step 2: Run the whole notebook

Run:

```
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=-1 --ExecutePreprocessor.kernel_name=python3 --output Lab9_Lab10_executed.ipynb Lab9_Lab10_Seq2Seq_Attention.ipynb
```

- This trains about 20 models. On a CPU it can take 1 to 3 hours, so run it in the background and check on it rather than waiting with a short timeout.
- If a cell fails, read the traceback, apply the smallest fix to `Lab9_Lab10_Seq2Seq_Attention.ipynb` (no comments), and run again.
- When it finishes, confirm that every code cell in `Lab9_Lab10_executed.ipynb` has outputs and that no output is an error.

## Step 3: Make the written answers match the real results

The notebook has short written answers (markdown cells) after tasks that ask for an explanation, a recommendation or a conclusion. They were written before the run, based on the results the lab manual expects. Read the actual outputs and edit any markdown sentence that contradicts them. Check in particular:

- Lab 9 Task 1: which of the 5 own dates were wrong.
- Lab 9 Task 2: where accuracy levels off as units increase.
- Lab 9 Task 3: which formats and error types are most common.
- Lab 9 Task 4: the number of wrong dates per month.
- Assignment 3 Tasks 5 and 6: the effect of the number of units on amount conversion.
- Lab 10 Task 1: whether the weekday really gets almost no attention (see the printed share).
- Lab 10 Task 2: which attention type is sharper (higher "Mean max attention weight") and which is more accurate.
- Lab 10 Task 3: whether the gap between models is largest at 16 units.
- Lab 10 Task 4 and Assignment 4 Task 6: the recommended model must be the one the results support.
- Assignment 4 Tasks 4 and 5: describe what the heatmaps and wrong predictions actually show.

Make the edits in the markdown cells of `Lab9_Lab10_executed.ipynb` only (do not re-run). Keep the answers short and in plain English.

## Step 4: Build the PDF

```
python build_pdf.py Lab9_Lab10_executed.ipynb logo.png Waleed_Ahmad_FA23-BBD-151_Lab_9_10.pdf
```

The PDF has, in order:
1. A cover page: COMSATS logo, "COMSATS University Islamabad", Waleed Ahmad, FA23-BBD-151, Lab Assignment 9, 10, Section: 7B.
2. An instructions page.
3. Lab 9 and then Lab 10: each code cell in a grey box, its output (text, tables, model summaries, training logs, charts) right below it, and the written answers.

## Step 5: Check the PDF

1. Open the PDF, or render a few pages to images (for example with `pdftoppm -r 60 -png`), and look at the cover, the instructions page, a training log, a model summary and a heatmap.
2. Confirm that every code block has an output under it and that all charts appear.
3. If very long training logs make the PDF too long, you may re-run the notebook with `verbose=2` in the `fit` calls. Do not delete outputs by hand.
4. Report the page count and the main accuracy results (Lab 9 exact-match accuracy, and the Lab 10 results table) when done.
