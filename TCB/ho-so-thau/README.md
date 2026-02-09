# Document Processing Workflow / Luồng xử lý tài liệu

## Overview

This project provides an AI-powered document processing workflow that transforms input files (PDFs, Word, Excel, PowerPoint) into professionally formatted output documents in three formats: **Word (.docx)**, **Excel (.xlsx)**, and **PowerPoint (.pptx)**.

### 4-Phase Pipeline

The workflow operates through a **4-phase multi-model pipeline**:

1. **Phase 1: CREATE** (Opus 4.6) - Analyzes input files, extracts content, generates code-based diagrams, assembles documents, applies formatting standards
2. **Phase 1b: IMAGES** (Gemini 3 Pro) - Generates conceptual images/infographics and inserts them into documents (optional, skip if only code diagrams needed)
3. **Phase 2: REVIEW** (GPT-5.2 High) - Reviews documents for content quality, formatting, language, and review tracking completeness
4. **Phase 3: FIX** (Opus 4.6) - Applies fixes based on review findings, regenerates clean versions

### 3 Output Formats

- **Word (.docx)**: Proposals, technical reports, tender documents
- **Excel (.xlsx)**: Pricing sheets, data reports, financial summaries
- **PowerPoint (.pptx)**: Presentations, executive briefs, pitch decks

### Dual-Version Output

Every output file is generated in **two versions**:
- `filename_REVIEW.ext` - Full change tracking (comments, highlights, audit columns) for internal review
- `filename.ext` - Clean version (no tracking) for client delivery

## Quick Start

### Solo Work

1. **Place your input files** in the `input/` folder (or reference them with `@file` paths)
2. **Open Cursor**, select **Opus 4.6**, and type your request:
   ```
   Process @input/ files, create proposal using @templates/word/proposal_template.docx
   ```
3. **Follow the handoff prompts** - After each phase, open a NEW chat, select the specified model, and type:
   ```
   Execute @tmp/handoff/phaseXX.md
   ```

### Team Collaboration

When multiple team members work on the same project:

1. **Before starting work**:
   ```bash
   git pull  # Get latest changes
   ./scripts/check_locks.sh  # Check if document is locked
   ```

2. **Lock the document** (Agent does this automatically when you start a phase):
   ```bash
   ./scripts/lock_document.sh output/proposal_REVIEW.docx "Your Name" "Phase 3"
   git add .locks/ && git commit -m "chat: Lock proposal for editing" && git push
   ```

3. **Work on your phase** - The lock tells other team members to wait

4. **Unlock when done** (Agent does this automatically at phase end):
   ```bash
   git add output/ .locks/ && git commit -m "chat: Complete Phase 3 + unlock" && git push
   ```

**Result**: No merge conflicts with binary files (Word/Excel/PPT), clear ownership, smooth handoffs between team members.

That's it! The Agent handles all scripts, formatting, tracking, lock management, and file management automatically.

## Setup

For detailed setup instructions, prerequisites, and team onboarding, see **[SETUP.md](SETUP.md)**.

**Quick setup:**
```bash
# Install dependencies
uv sync

# Start Docker services (for document rendering)
docker compose up -d

# Configure your author info
cp config.yaml.example config.yaml
# Edit config.yaml with your name and role
```

---

## Document Reference Syntax Guide

**THE MOST IMPORTANT SECTION** - Learn how to precisely reference specific parts of documents so the Agent can make targeted updates.

When asking the Agent to update a **specific part** of a document, use these reference patterns. The more specific you are, the more accurate the updates will be.

### Word (.docx) -- Reference by Structure

#### By Heading / Table of Contents

The **most reliable** way to reference Word content. Use the **EXACT heading text** as it appears in the document.

**Examples:**
```
"Update section '3.2 Kiến trúc hệ thống' in @output/proposal_REVIEW.docx"
"Rewrite the content under heading '4.1 Security Architecture'"
"Add a new subsection '3.2.1 Database Layer' after section 3.2"
"Delete section 5.3 and renumber subsequent sections"
"In @output/proposal_REVIEW.docx, update section 'Executive Summary' with new metrics"
```

**Why this works:** Headings are stable identifiers that don't change when content shifts. The Agent searches for exact heading text.

#### By Heading Level

Reference all headings at a specific level:

```
"Update all H2 headings to use consistent numbering format (1.1, 1.2, etc.)"
"Add executive summary after the first H1 heading"
"Format all H3 headings with italic style"
```

#### By Page Number

**Less reliable** - Page numbers can shift after edits, but useful for initial reference:

```
"Fix the table on page 15 of @output/proposal_REVIEW.docx"
"Replace the diagram between pages 22-23"
"Update the footer on page 1"
```

**Note:** After edits, page numbers may change. Prefer heading references for accuracy.

#### By Table

Reference tables by their position and/or title:

```
"Update table 3 (the one titled 'Pricing Summary') in @output/proposal_REVIEW.docx"
"Add a row to the team members table in section 6"
"Fix the column headers in the first table under '4.2 Requirements'"
"Update the second table in section 3.2 (titled 'System Components')"
"In @output/proposal_REVIEW.docx, update table 'Project Timeline' in section 7"
```

**Best practice:** Combine table reference with section context: "table 2 in section 3.1" is more precise than just "table 2".

#### By Paragraph Content

Reference paragraphs by their starting text:

```
"Replace the paragraph that starts with 'The proposed solution leverages...' in section 3"
"Remove the bullet point about 'legacy integration' in section 4.1"
"Update the paragraph beginning with 'Our team consists of...' in section 6"
"Add a new paragraph after the one starting with 'Key benefits include:'"
```

**Tip:** Quote the first 5-10 words exactly as they appear in the document.

#### By Image/Diagram

Reference images by their location and context:

```
"Replace the architecture diagram in section 3.2"
"Add a new process flow diagram after the paragraph about data ingestion"
"Update the caption under the diagram on page 12"
"Remove the image titled 'Hình 2.1: System Architecture'"
"In @output/proposal_REVIEW.docx, replace the diagram in section 3.2 with @tmp/diagrams/new_arch.png"
```

#### Multiple Targets (Multi-line Example)

When updating multiple parts, use a numbered list:

```
"In @output/proposal_REVIEW.docx:
 1. Update section 3.2 'Kiến trúc hệ thống' with new architecture description
 2. Fix table 3 'Pricing Summary' to match @output/pricing_REVIEW.xlsx totals
 3. Add diagram after section 4.1 'Security Architecture'
 4. Update the paragraph starting with 'The implementation timeline...' in section 5"
```

---

### Excel (.xlsx) -- Reference by Coordinates

#### By Sheet + Cell

The most precise Excel reference. Always specify both sheet name and cell:

```
"Update cell D15 in sheet 'Summary' of @output/pricing_REVIEW.xlsx"
"Fix the formula in cell F20 of sheet 'Item Breakdown'"
"Clear cells B5:B10 in sheet 'Dashboard'"
"In @output/pricing_REVIEW.xlsx, update sheet 'Summary' cell B3 to 'Phase 2 Expansion'"
```

**Format:** `sheet 'SheetName' cell X##` or `sheet 'SheetName' cell X##:Y##` for ranges.

#### By Sheet + Row

Reference entire rows by their number:

```
"Add 3 new rows after row 10 in sheet 'Item Breakdown'"
"Delete rows 15-18 in sheet 'Raw Data'"
"Update row 5 (the 'Cloud Infrastructure' item) with new unit price"
"In @output/pricing_REVIEW.xlsx sheet 'Item Breakdown', insert a new row at row 8"
```

**Tip:** Include context about what the row contains: "row 8 (the 'AWS Lambda' row)" helps disambiguation.

#### By Sheet + Column

Reference entire columns by letter or position:

```
"Update all values in column C (Unit Price) of sheet 'Item Breakdown'"
"Add a new column 'Discount %' after column D in sheet 'Item Breakdown'"
"Format column E as currency VND in all data sheets"
"In @output/pricing_REVIEW.xlsx, update column D 'Total Price' in sheet 'Item Breakdown'"
```

**Best practice:** Use column letters (A, B, C) or describe by header name.

#### By Column Header Name

When you don't know the column letter, use the header text:

```
"Update the 'Quantity' column for the 'Database License' row in sheet 'Item Breakdown'"
"Add values to the 'Notes' column for all rows where Status is 'NEW'"
"In @output/pricing_REVIEW.xlsx, update the 'Unit Price' column for all items"
"Format the 'Total' column as currency VND"
```

**Why this works:** The Agent searches for header text and maps it to the correct column.

#### By Sheet Name

Reference entire sheets:

```
"Recalculate all formulas in sheet 'Summary'"
"Add a new sheet 'Comparison' with data from @input/competitor_pricing.xlsx"
"Rename sheet 'Sheet1' to 'Executive Summary'"
"Delete sheet 'Old Data'"
"In @output/pricing_REVIEW.xlsx, format all cells in sheet 'Dashboard'"
```

#### By Named Range or Formula

Reference formulas and named ranges:

```
"Fix the VLOOKUP formula that references 'Item Breakdown'!A:F"
"Update the SUM formula for total cost (currently showing #REF! error)"
"In @output/pricing_REVIEW.xlsx sheet 'Summary', fix the formula in cell D15 that sums 'Item Breakdown'!E:E"
"Update the named range 'PricingData' to include new rows"
```

#### By Data Content

Reference cells/rows by their content:

```
"Update the row where 'Item Name' is 'AWS Lambda' in sheet 'Item Breakdown'"
"Find all cells containing 'TBD' and replace with actual values from @input/specs.pdf"
"In @output/pricing_REVIEW.xlsx, update the row where 'Service' column equals 'S3 Storage'"
"Change all cells with value '0' to 'N/A' in sheet 'Dashboard'"
```

**Best practice:** Combine with sheet name: "row where 'Item Name' is 'Lambda' in sheet 'Items'".

#### Multiple Targets (Multi-line Example)

When updating multiple parts:

```
"In @output/pricing_REVIEW.xlsx:
 1. Sheet 'Item Breakdown': update row 8 unit price to 15,000,000 VND
 2. Sheet 'Item Breakdown': add new row after row 12 with 'CloudFront CDN', Qty: 1, Price: 5,000,000
 3. Sheet 'Summary': verify total formula in cell D15 includes new rows
 4. Sheet 'Dashboard': refresh the chart data range to include rows 3-15"
```

**Or more detailed:**

```
"In @output/pricing_REVIEW.xlsx:
 1. Sheet 'Item Breakdown':
    - Row 8 (where 'Item Name' is 'AWS Lambda'): change Quantity to 2,000,000
    - Row 10 (where 'Item Name' is 'S3 Storage'): change Unit Price to 0.05 VND/GB
    - Add new row after row 12: 'CloudFront CDN', Quantity: 1, Unit Price: 5,000,000 VND
 2. Sheet 'Summary':
    - Cell D15: verify SUM formula includes all rows from 'Item Breakdown'
    - Cell B3: update project name to 'Phase 2 Expansion'
 3. Sheet 'Terms':
    - Cell B5: update validity period to '90 days'"
```

---

### PowerPoint (.pptx) -- Reference by Slide

#### By Slide Number

The simplest reference method:

```
"Update slide 3 in @output/presentation_REVIEW.pptx"
"Replace content on slides 5-7 with updated technical specs"
"Add a new slide after slide 4"
"In @output/presentation_REVIEW.pptx, delete slide 8"
```

**Note:** Slide numbers are 1-indexed (first slide is slide 1, not slide 0).

#### By Slide Title

Reference slides by their title text:

```
"Update the 'Technical Architecture' slide in @output/presentation_REVIEW.pptx"
"Rewrite the bullet points on the 'Key Benefits' slide"
"Add speaker notes to the 'Timeline' slide"
"In @output/presentation_REVIEW.pptx, update slide titled 'Executive Summary'"
```

**Best practice:** Use exact title text as it appears on the slide.

#### By Slide Element

Reference specific elements on a slide:

```
"Replace the diagram on slide 4 with @tmp/diagrams/new_architecture.png"
"Update the table on the 'Pricing Overview' slide"
"Fix the bullet points on slide 3 (currently 8 bullets, reduce to 5)"
"Update the chart data on slide 6"
"In @output/presentation_REVIEW.pptx slide 4, replace the image with @tmp/diagrams/v2_flow.png"
```

**Elements you can reference:**
- Images/diagrams
- Tables
- Charts/graphs
- Text boxes
- Bullet lists
- Shapes

#### By Speaker Notes

Reference or update speaker notes:

```
"Add speaker notes to all slides that don't have them"
"Update the speaker notes on slide 3 with the talking points from section 3 of @output/proposal_REVIEW.docx"
"In @output/presentation_REVIEW.pptx, add speaker notes to slide 5 describing the architecture diagram"
"Remove the change tracking block from speaker notes on slide 2"
```

#### By Slide Layout/Type

Reference slides by their layout or type:

```
"Update all title slides with the new company logo"
"Add slide numbers to all content slides"
"Ensure all slides follow the 16:9 widescreen layout"
"In @output/presentation_REVIEW.pptx, update all slides with 'Title and Content' layout"
```

#### Multiple Targets (Multi-line Example)

When updating multiple slides:

```
"In @output/presentation_REVIEW.pptx:
 1. Slide 3 'Architecture': replace diagram with @tmp/diagrams/v2_architecture.png
 2. Slide 5 'Pricing': update table to match @output/pricing_REVIEW.xlsx totals
 3. Slide 6 'Timeline': add speaker notes from section 5 of proposal
 4. Add new slide after slide 6 titled 'Risk Analysis' with content from section 7 of proposal"
```

**Or more detailed:**

```
"In @output/presentation_REVIEW.pptx:
 1. Slide 3 (titled 'Technical Architecture'):
    - Replace the architecture diagram with @tmp/diagrams/new_arch.png
    - Update bullet points to match section 3.2 of @output/proposal_REVIEW.docx
    - Add speaker notes explaining each component
 2. Slide 5 (titled 'Pricing Overview'):
    - Update the pricing table to match @output/pricing_REVIEW.xlsx sheet 'Summary' cell D15
    - Ensure totals are formatted as currency VND
 3. Slide 7: Add new slide after slide 6
    - Title: 'Risk Analysis'
    - Content: Extract from @output/proposal_REVIEW.docx section 7
    - Layout: Title and Content
    - Add speaker notes"
```

---

### Confluence Pages -- Reference by URL or Page ID

When working with Confluence as an input source:

#### By URL (with all child pages)

```
"Read Confluence page https://yourcompany.atlassian.net/wiki/spaces/TEAM/pages/12345/Requirements 
 and all child pages. Create a proposal using @templates/word/proposal_template.docx"
```

#### By Page ID

```
"Read Confluence page 12345 and all descendants. Extract technical requirements 
 and create a technical report."
```

#### By Page ID (parent only, no children)

```
"Read only Confluence page 12345 (no children). Use content to update 
 section 3 of @output/proposal_REVIEW.docx"
```

#### By Space Key

```
"Search Confluence space 'TEAM' for pages containing 'architecture' and 'deployment'. 
 Summarize findings in a technical report."
```

#### By CQL (Confluence Query Language)

```
"Search Confluence using CQL: type=page AND space=TEAM AND title~'requirements' AND lastModified > now('-7d')
 Create a summary document with recently updated requirements pages."
```

#### Update from Confluence Page

```
"Page 'Technical Requirements' (ID: 12400) in Confluence was updated. 
 Re-fetch and update section 3.2 of @output/proposal_REVIEW.docx to match 
 https://yourcompany.atlassian.net/wiki/pages/12400"
```

#### Pre-Fetched Confluence Pages

If you used `scripts/confluence_fetcher.py` to pre-fetch:

```
"Read all pages from @input/confluence/ (see manifest.json for hierarchy). 
 Create a proposal using page hierarchy as document structure."
```

---

### Cross-Document References

When updating multiple documents that must stay consistent:

#### Sync Pricing Between Word and Excel

```
"Pricing changed -- sync these documents:
 1. @output/pricing_REVIEW.xlsx sheet 'Item Breakdown': source of truth
 2. @output/proposal_REVIEW.docx section 5.1 'Bảng giá': must match Excel totals
 3. @output/presentation_REVIEW.pptx slide 5 'Pricing Overview': must match Excel summary
 Make sure all 3 documents show the same total: 2,500,000,000 VND."
```

#### Sync Key Points Between Word and PowerPoint

```
"Sync key points:
 - @output/proposal_REVIEW.docx section 1 'Executive Summary': source
 - @output/presentation_REVIEW.pptx slide 2 'Key Highlights': must summarize executive summary
 The slide should summarize the executive summary in 5 bullets, matching the tone and key metrics."
```

#### Update Multiple Formats from Single Source

```
"Update all documents with new project name 'Phase 2 Expansion':
 1. @output/proposal_REVIEW.docx: Update cover page and section 1.1
 2. @output/pricing_REVIEW.xlsx sheet 'Cover' cell B3: Update project name
 3. @output/presentation_REVIEW.pptx slide 1: Update title slide
 Ensure consistency across all three documents."
```

---

### Tips for Better References

1. **Be specific**: 
   - ✅ Good: "section 3.2 'Kiến trúc hệ thống'"
   - ❌ Bad: "the architecture section"

2. **Use exact text**: Quote heading text, table titles, and slide titles exactly as they appear

3. **Combine methods**: 
   - ✅ Good: "table 2 in section 3.1"
   - ❌ Bad: "table 2" (which table?)

4. **Include context**: 
   - ✅ Good: "the pricing table (the one with 15 line items) in section 5"
   - ❌ Bad: "the table"

5. **Reference files with @ paths**: Always use `@output/` or `@input/` paths:
   - ✅ Good: "Update @output/proposal_REVIEW.docx section 3.2"
   - ❌ Bad: "Update proposal section 3.2"

6. **Describe WHAT to change and WHERE**: 
   - ✅ Good: "Update the unit price for 'Lambda' to 500 VND/request in sheet 'Items' row 8"
   - ❌ Bad: "Update row 8" (what to update? what value?)

7. **For Excel, always specify sheet name**: 
   - ✅ Good: "sheet 'Item Breakdown' row 8"
   - ❌ Bad: "row 8" (which sheet?)

8. **For PowerPoint, prefer slide titles over numbers when possible**: Slide numbers can shift, titles are stable

9. **Use multi-line format for complex updates**: Numbered lists help the Agent process multiple changes systematically

10. **Include source context**: When syncing between documents, specify which is the "source of truth"

---

## Project Structure

```
ho-so-thau/
├── .cursor/
│   └── rules/                    # Cursor Rules (auto-applied)
│       ├── document-workflow.mdc      # Master orchestration (4 phases + handoff)
│       ├── review-checklist.mdc       # Review workflow (Phase 2)
│       ├── formatting-standards.mdc   # Formatting standards (Word/Excel/PPT)
│       └── document-types.mdc         # Document type handling
│
├── scripts/                      # Helper scripts (8 total)
│   ├── word_formatter.py         # Format .docx + review tracking
│   ├── xlsx_formatter.py         # Format .xlsx + audit columns
│   ├── pptx_builder.py           # Create/edit .pptx + notes tracking
│   ├── template_engine.py        # Fill templates (all 3 formats)
│   ├── insert_images.py          # Insert images (all 3 formats)
│   ├── render_docs.py            # Render to PNG for visual QA
│   ├── extract_images.py         # Extract images from input files
│   └── strip_tracking.py         # Create CLEAN version from REVIEW
│
├── templates/                    # Document templates
│   ├── word/
│   │   ├── proposal_template.docx
│   │   └── technical_report_template.docx
│   ├── excel/
│   │   ├── pricing_template.xlsx
│   │   └── data_report_template.xlsx
│   ├── pptx/
│   │   ├── presentation_template.pptx
│   │   └── executive_brief_template.pptx
│   └── template_config.yaml     # Field mappings
│
├── input/                        # YOU put source files here
├── output/                       # Agent puts generated docs here
│   │                            # *_REVIEW.* = with tracking
│   │                            # *.* = clean for client
├── review/                       # GPT puts review reports here
│   └── review_report.md         # Structured findings
│
├── tmp/                          # Temporary files (auto-cleaned)
│   ├── handoff/                  # Phase handoff files
│   │   ├── phase1b.md
│   │   ├── phase2.md
│   │   ├── phase3.md
│   │   └── history/             # Archived handoffs
│   ├── renders/                  # PNG pages for visual QA
│   ├── images/                   # Extracted images
│   └── diagrams/                 # Generated diagrams
│
├── chat/                         # Chat history logs
├── config.yaml.example           # Author config template
├── config.yaml                   # Your author config (git-ignored)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── SETUP.md                      # Setup and onboarding guide
└── README.md                     # This file
```

---

## Available Templates

### Word Templates

- **`templates/word/proposal_template.docx`** - Bid/tender proposal template
  - Cover page, TOC, company profile, technical solution, timeline, pricing, team, appendix
  - Placeholders: `{{project_name}}`, `{{company_name}}`, `{{IMAGE:architecture_diagram}}`

- **`templates/word/technical_report_template.docx`** - Technical report template
  - Cover page, TOC, executive summary, methodology, findings, recommendations, appendix
  - Placeholders: `{{report_title}}`, `{{IMAGE:system_diagram}}`

### Excel Templates

- **`templates/excel/pricing_template.xlsx`** - Pricing/quotation sheet
  - Sheets: Cover, Item Breakdown (with row replication), Summary (formulas), Terms
  - Placeholders: `{{items}}` (row replication), `{{project_name}}`

- **`templates/excel/data_report_template.xlsx`** - Data analysis report
  - Sheets: Dashboard (KPIs + charts), Raw Data, Analysis, Summary
  - Placeholders: `{{data_range}}`, `{{metrics}}`

### PowerPoint Templates

- **`templates/pptx/presentation_template.pptx`** - Standard presentation
  - Slides: Title, Agenda, Executive Summary, Solution, Timeline, Team, Q&A
  - Placeholders: `{{title}}`, `{{IMAGE:architecture_diagram}}`

- **`templates/pptx/executive_brief_template.pptx`** - Executive summary slides
  - Slides: Title, Key Points (3 slides), Recommendation, Next Steps
  - Placeholders: `{{key_metrics}}`, `{{recommendation}}`

---

## Scripts Reference

### 1. `word_formatter.py`

**Purpose:** Format Word documents and apply review tracking

**Features:**
- Applies formatting standards (fonts, margins, spacing, headings, TOC)
- Adds inline comments for changed content
- Highlights new text (green) and modified text (yellow)
- Adds section-level update markers
- Generates Change Log page
- Sets author metadata from `config.yaml`

**Usage:** Called automatically by Agent during Phase 1 and Phase 3

### 2. `xlsx_formatter.py`

**Purpose:** Format Excel files and apply audit tracking

**Features:**
- Formats header rows (bold, dark background, frozen panes)
- Applies number formats (currency VND, dates dd/mm/yyyy)
- Auto-fits column widths
- Validates formulas (checks for #REF!, #DIV/0! errors)
- Adds audit columns: `_Status`, `_Change_Desc`, `_Updated_By`
- Applies row color coding (green=new, yellow=modified)
- Creates `_Change_Log` sheet
- Adds cell comments for modified cells

**Usage:** Called automatically by Agent during Phase 1 and Phase 3

### 3. `pptx_builder.py`

**Purpose:** Create and edit PowerPoint presentations with review tracking

**Features:**
- Creates presentations from templates or scratch
- Adds/edits/reorders slides with proper layouts
- Sets text content with formatting
- Inserts images and diagrams
- Adds speaker notes with change tracking
- Creates Change Summary slide
- Sets author metadata

**Usage:** Called automatically by Agent during Phase 1 and Phase 3

### 4. `template_engine.py`

**Purpose:** Universal template filling for all 3 formats

**Features:**
- Reads `template_config.yaml` for placeholder mappings
- Detects format by extension (.docx, .xlsx, .pptx)
- Replaces `{{placeholder}}` markers in content
- Handles `{{IMAGE:name}}` placeholders (delegates to `insert_images.py`)
- Replicates table rows from list data (Excel row replication)
- Handles conditional sections

**Usage:** Called automatically by Agent during Phase 1

### 5. `insert_images.py`

**Purpose:** Insert images/diagrams into all output formats

**Features:**
- Inserts images into Word documents (after headings, at bookmarks, replace placeholders)
- Inserts images into Excel sheets (at specific cell references)
- Inserts images into PowerPoint slides (centered, custom positioning)
- Supports sizing and positioning options
- Works with extracted images (`tmp/images/`) and generated diagrams (`tmp/diagrams/`)

**Usage:** Called automatically by Agent during Phase 1 and Phase 1b

### 6. `render_docs.py`

**Purpose:** Render documents to PNG for visual QA

**Features:**
- Converts Word/Excel/PowerPoint to PDF via LibreOffice
- Converts PDF pages to PNG images
- Saves PNGs to `tmp/renders/` for Agent inspection
- Returns manifest with page/sheet/slide mappings
- Enables visual QA loop (Agent inspects PNGs via `read_image()`)

**Usage:** Called automatically by Agent during Phase 1, 1b, and 3

### 7. `extract_images.py`

**Purpose:** Extract images from input files

**Features:**
- Extracts images from Word documents (`.docx`)
- Extracts images from PDF files (`.pdf`)
- Saves images to `tmp/images/` with descriptive names
- Returns JSON manifest with image metadata (location, alt text, dimensions)
- Preserves image quality

**Usage:** Called automatically by Agent during Phase 1

### 8. `strip_tracking.py`

**Purpose:** Create CLEAN version from REVIEW version

**Features:**
- Removes all tracking artifacts from REVIEW versions
- **Word:** Removes comments, highlights, section markers, Change Log page
- **Excel:** Deletes audit columns, removes row colors, deletes `_Change_Log` sheet, removes cell comments
- **PowerPoint:** Removes change tracking from notes, removes footer annotations, removes Change Summary slide
- Saves clean version as `filename.ext` (without `_REVIEW` suffix)

**Usage:** Called automatically by Agent after creating REVIEW versions

---

## Cursor Rules

### 1. `document-workflow.mdc`

**Purpose:** Master orchestration rule for all 4 phases

**Key Features:**
- Defines Phase 1 (CREATE), Phase 1b (IMAGES), Phase 2 (REVIEW), Phase 3 (FIX) workflows
- Handles phase handoff protocol using `@file` references
- Generates handoff files (`tmp/handoff/phaseXX.md`) with complete context
- Archives previous handoffs to `tmp/handoff/history/`
- Instructs Agent on when to use which model
- Defines dual-version output strategy (REVIEW + CLEAN)

**When Applied:** Always (alwaysApply: true)

### 2. `review-checklist.mdc`

**Purpose:** Review workflow for Phase 2

**Key Features:**
- Defines review categories: Content Quality, Formatting, Language, Review Tracking Quality
- Provides checklists for Word, Excel, PowerPoint formats
- Defines severity levels: CRITICAL, HIGH, MEDIUM, LOW
- Specifies review report format (`review/review_report.md`)
- Generates Phase 3 handoff file with findings

**When Applied:** Always (alwaysApply: true), but primarily guides GPT models in Phase 2

### 3. `formatting-standards.mdc`

**Purpose:** Formatting standards for all 3 output formats

**Key Features:**
- **Word:** Typography (Times New Roman 13pt), margins (3cm left, 2cm others), line spacing (1.5), heading numbering, table formatting, TOC format
- **Excel:** Header row styling, number formats (currency VND, dates dd/mm/yyyy), column widths, formulas, conditional formatting
- **PowerPoint:** Slide layout (16:9), typography (Calibri 28pt title, 18pt body), max 6 bullets per slide, speaker notes requirements
- Defines review tracking standards for each format (comments, highlights, audit columns, notes tracking)

**When Applied:** Always (alwaysApply: true)

### 4. `document-types.mdc`

**Purpose:** Document type handling and templates

**Key Features:**
- Defines required sections for each document type:
  - Proposal: Cover, TOC, Executive Summary, Company Profile, Technical Solution, Timeline, Pricing, Team, Appendix
  - Technical Report: Cover, TOC, Executive Summary, Methodology, Findings, Recommendations, Appendix
  - Pricing Sheet: Cover, Item Breakdown, Summary, Terms
  - Presentation: Title, Agenda, Executive Summary, Solution, Timeline, Team, Q&A
- Specifies cross-format consistency requirements (pricing matches between Word and Excel)
- Maps document types to templates

**When Applied:** Always (alwaysApply: true)

---

## Next Steps

1. **Read [SETUP.md](SETUP.md)** for detailed setup instructions
2. **Place files in `input/`** folder
3. **Open Cursor**, select **Opus 4.6**, and start Phase 1
4. **Follow handoff prompts** for subsequent phases

For workflow examples and detailed prompts, see the project documentation.

---

**Project:** Document Processing Workflow  
**Version:** 1.0  
**Last Updated:** February 2026
