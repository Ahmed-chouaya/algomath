---
description: "Extract algorithm from PDF or text file"
argument-hint: "[file-path] [--auto] [--step] [--name <name>]"
tools:
  read: true
  write: true
---

<objective>
Extract algorithm from PDF or text file using LLM-powered parsing.
Supports automatic extraction or step-by-step with review points.
</objective>

<execution_context>
@/home/milgraph/Projects/algo_framework/src/extraction/pdf_processor.py
@/home/milgraph/Projects/algo_framework/src/extraction/llm_extractor.py
</execution_context>

<process>
Execute extraction workflow:

1. **Parse Arguments**
   - Check if file path provided
   - Determine mode: auto, step-by-step, or interactive

2. **Extract Text from File**
   - Auto-detect file type (PDF, .txt, .md)
   - Use pdfplumber for PDFs
   - Handle encoding issues
   - Validate extraction success

3. **Parse Algorithm Structure**
   - Use opencode LLM to parse text
   - Identify algorithm name
   - Extract inputs and outputs
   - Parse step-by-step procedure
   - Handle mathematical notation

4. **Review Point (if step-by-step)**
   - Display extracted text
   - Ask user to confirm or edit
   - Apply user corrections

5. **Generate Structured Steps**
   - Convert parsed text to Algorithm object
   - Validate step structure
   - Check for completeness

6. **Review Point (if step-by-step)**
   - Display structured steps
   - Show inputs, outputs, step list
   - Allow editing

7. **Save Algorithm**
   - Create directory: .algomath/algorithms/{name}/
   - Save source.txt (original text)
   - Save steps.json (structured)
   - Save metadata.json (info)

8. **Display Summary**
   - Show algorithm name
   - Show step count
   - Display next steps
   - Suggest: /algo-generate
</process>

<examples>

**Extract from PDF (interactive):**
/algo-extract research_paper.pdf

**Auto-extract (no prompts):**
/algo-extract --auto research_paper.pdf

**Extract from text file:**
/algo-extract algorithm.txt

**Specify algorithm name:**
/algo-extract research.pdf --name "Dijkstra Shortest Path"

</examples>

<options>

--auto
Skip review points, extract automatically

--step
Enable step-by-step mode with review at each stage

--name <name>
Specify algorithm name (optional)

</options>

<next_steps>
/algo-generate - Generate Python code from extracted steps
/algo-status - Check current algorithm state
</next_steps>
