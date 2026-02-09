# Document Processing Workflow Guide

**Master guide for using the document processing system**

---

## Quick Start (3 Steps)

1. **Place your source files** in the `input/` folder
2. **Open a new chat** and select **Opus 4.6** model
3. **Type your Phase 1 prompt** (see examples below)

That's it! The system will:
- Generate your document(s) with review tracking
- Create handoff files for subsequent phases
- Tell you exactly what to type in the next chat

---

## The 4-Phase Workflow

### Phase 1: CREATE (Opus 4.6)
**What happens:** Document(s) are created from input files  
**User action:** Write a prompt describing what you want  
**Output:** `output/filename_REVIEW.ext` and `output/filename.ext`  
**Next step:** System generates `tmp/handoff/phase1b.md` or `tmp/handoff/phase2.md`

### Phase 1b: IMAGES (Gemini 3 Pro) - Optional
**What happens:** AI-generated images replace `{{IMAGE:name}}` placeholders  
**User action:** Type `Execute @tmp/handoff/phase1b.md` (5 words)  
**Output:** Updated documents with images inserted  
**Next step:** System generates `tmp/handoff/phase2.md`

### Phase 2: REVIEW (GPT-5.2 High)
**What happens:** Expert review of document quality and tracking  
**User action:** Type `Execute @tmp/handoff/phase2.md` (5 words)  
**Output:** `review/review_report.md` with findings  
**Next step:** System generates `tmp/handoff/phase3.md` (if fixes needed)

### Phase 3: FIX (Opus 4.6)
**What happens:** Fixes are applied based on review findings  
**User action:** Type `Execute @tmp/handoff/phase3.md` (5 words)  
**Output:** Updated documents with fixes and updated tracking  
**Next step:** Document is ready for client delivery

---

## Phase 1: CREATE Prompts (Opus 4.6)

**Model:** Opus 4.6  
**This is the ONLY phase where you write a real prompt**

### Word Document Prompts

#### Create Proposal from Requirements
```
Create a proposal document (hồ sơ thầu) from input/requirements.pdf. 
Include all standard sections: cover page, executive summary, company profile, 
technical solution with architecture diagram, implementation timeline, pricing 
summary (reference Excel pricing sheet), team introduction, and appendix. 
Use Vietnamese language with technical terms in English where appropriate.
```

#### Create Technical Report
```
Create a technical report from input/analysis_data.xlsx and input/system_overview.docx. 
Include: executive summary, background, methodology, findings with system diagrams, 
recommendations, and appendix. Follow the technical report template structure.
```

#### Reformat Existing Document
```
Reformat input/old_proposal.docx to match our standard formatting:
- Times New Roman 13pt body text
- Proper heading hierarchy (1. / 1.1. / 1.1.1.)
- 3cm left margin, 2cm other margins
- Add table of contents
- Fix table formatting with proper borders and header styling
- Add page numbers and headers
Save as output/proposal_REVIEW.docx and output/proposal.docx
```

#### Update Specific Section
```
Update section "3. Technical Solution" in output/proposal_REVIEW.docx. 
Replace the current content with the new architecture description from 
input/new_architecture.docx. Keep all other sections unchanged. 
Maintain review tracking for the updated section.
```

#### Update Table
```
Update the "Team Introduction" table in output/proposal_REVIEW.docx. 
Add 3 new team members from input/team_updates.xlsx. 
Keep existing team members and update the table formatting to match standards.
```

### Excel Document Prompts

#### Create Pricing Sheet
```
Create a pricing sheet from input/requirements.pdf and input/item_list.xlsx. 
Include sheets: Cover (project info), Item Breakdown (with Qty, Unit Price, Total), 
Summary (totals with formulas), and Terms (payment terms, validity). 
Use VND currency format (#,##0 VND). Ensure all formulas work correctly.
```

#### Create Data Report
```
Create a data report from input/raw_data.csv. Include sheets: Dashboard (KPIs and 
summary charts), Raw Data (source data with timestamps), Analysis (pivot tables 
and calculated metrics), and Summary (key findings and trends). Format all 
numbers and dates according to standards.
```

#### Update Rows/Cells
```
Update the pricing sheet output/pricing_REVIEW.xlsx:
- Add 5 new line items from input/additional_items.xlsx to the Item Breakdown sheet
- Update unit prices for items in rows 10-15 based on input/price_updates.xlsx
- Recalculate all totals and update the Summary sheet
Maintain audit tracking for all changes.
```

#### Reformat Spreadsheet
```
Reformat input/old_pricing.xlsx to match our standards:
- Apply header row formatting (dark blue background, white text, bold)
- Fix currency formatting (VND with thousands separator)
- Set proper column widths and freeze top row
- Add auto-filter to all data sheets
- Fix any formula errors
Save as output/pricing_REVIEW.xlsx and output/pricing.xlsx
```

### PowerPoint Document Prompts

#### Create Presentation
```
Create a presentation from output/proposal_REVIEW.docx. Include slides:
1. Title (project name, company, date, presenter)
2. Agenda
3. Executive Summary (3-5 key points)
4. Solution Overview with architecture diagram
5. Implementation Timeline
6. Key Metrics/Benefits
7. Team Introduction
8. Q&A/Thank You
Add speaker notes for every content slide. Use 16:9 widescreen format.
```

#### Create Executive Brief
```
Create an executive brief presentation (maximum 5 slides) from 
output/proposal_REVIEW.docx. Include: Title, Key Highlights (3-4 bullets), 
Solution (visual-heavy), Investment Summary (from Excel pricing), and 
Recommendation/Next Steps. Keep text minimal, use diagrams and visuals.
```

#### Update Specific Slides
```
Update slides 4-6 in output/presentation_REVIEW.pptx. Replace content with 
updated information from input/updated_content.docx. Keep all other slides 
unchanged. Update speaker notes for modified slides.
```

#### Add New Slides
```
Add 3 new slides to output/presentation_REVIEW.pptx after slide 5:
- Slide 6: "Risk Management" (from input/risks.docx)
- Slide 7: "Quality Assurance" (from input/qa.docx)
- Slide 8: "Support Plan" (from input/support.docx)
Update the agenda slide to include these new sections. Add speaker notes.
```

### Multi-Format Prompts

#### Full Tender Package
```
Create a complete tender package (hồ sơ thầu đầy đủ) from input/requirements.pdf:
1. Word: Detailed proposal document with all standard sections
2. Excel: Pricing sheet with item breakdown, summary, and terms
3. PowerPoint: Executive presentation (8-10 slides)
Ensure cross-format consistency:
- Pricing totals match between Word and Excel
- Key points align between Word and PowerPoint
- Dates and project names are consistent across all three
```

#### Project Report Package
```
Create a project report package from input/project_data.xlsx:
1. Word: Detailed project report with findings and recommendations
2. Excel: Data analysis with metrics and pivot tables
3. PowerPoint: Executive summary presentation (5-7 slides)
Ensure all three formats reference the same data sources and maintain consistency.
```

### Partial Update Prompts

#### Update by Heading
```
Update the section "2.1. Architecture Overview" in output/proposal_REVIEW.docx. 
Replace with content from input/new_architecture.docx. Keep all other sections 
unchanged. Maintain review tracking.
```

#### Update by Cell Range
```
Update cells B10:F15 in the "Item Breakdown" sheet of output/pricing_REVIEW.xlsx. 
Replace with new pricing data from input/updated_prices.xlsx. Recalculate 
affected totals. Maintain audit tracking for changed cells.
```

#### Update by Slide Number
```
Update slide 5 in output/presentation_REVIEW.pptx. Replace the timeline content 
with updated timeline from input/new_timeline.docx. Update speaker notes. 
Keep all other slides unchanged.
```

#### Cross-Document Sync
```
Sync pricing information across all three documents:
1. Update Excel pricing sheet output/pricing_REVIEW.xlsx with new prices from input/new_prices.xlsx
2. Update the "Pricing Summary" section in output/proposal_REVIEW.docx to match Excel totals
3. Update slide 6 "Investment Summary" in output/presentation_REVIEW.pptx to match Excel totals
Ensure all three documents show the same pricing numbers.
```

---

## Phase 1b: IMAGE Prompts (Gemini 3 Pro)

**Model:** Gemini 3 Pro  
**Note:** This phase is normally auto-generated. You only type:

```
Execute @tmp/handoff/phase1b.md
```

**What it does:** Replaces `{{IMAGE:name}}` placeholders with AI-generated images

**When it's needed:** When Phase 1 output contains `{{IMAGE:...}}` placeholders that couldn't be generated with code-based diagrams.

**Example handoff file content** (auto-generated):
```
# Handoff: Phase 1b (IMAGE GENERATION)
## Select Model: Gemini 3 Pro
## Previous Phase Summary
Created proposal document with 3 {{IMAGE:...}} placeholders for conceptual visuals.
## Tasks for This Phase
1. Generate image for {{IMAGE:business_process_flow}}
2. Generate image for {{IMAGE:user_journey}}
3. Generate image for {{IMAGE:value_proposition}}
4. Insert all images into output/proposal_REVIEW.docx
5. Regenerate clean version output/proposal.docx
```

---

## Phase 2: REVIEW Prompts (GPT-5.2 High)

**Model:** GPT-5.2 High  
**Note:** This phase is normally auto-generated. You only type:

```
Execute @tmp/handoff/phase2.md
```

**What it does:** Expert review of document quality, formatting, language, and review tracking

**Example handoff file content** (auto-generated):
```
# Handoff: Phase 2 (REVIEW)
## Select Model: GPT-5.2 High
## Previous Phase Summary
Created proposal document with all sections, images inserted, review tracking applied.
## Tasks for This Phase
1. Read output/proposal_REVIEW.docx and review against standards
2. Check content quality, formatting, language, and tracking
3. Render to PNG and visually inspect all pages
4. Write structured review report to review/review_report.md
5. Generate Phase 3 handoff if fixes needed
```

**Review categories:**
- Content Quality (accuracy, completeness, placeholders)
- Formatting (fonts, margins, tables, images)
- Language (grammar, spelling, tone)
- Review Tracking Quality (comments, highlights, audit columns)

---

## Phase 3: FIX Prompts (Opus 4.6)

**Model:** Opus 4.6  
**Note:** This phase is normally auto-generated. You only type:

```
Execute @tmp/handoff/phase3.md
```

**What it does:** Applies fixes based on review findings

**Example handoff file content** (auto-generated):
```
# Handoff: Phase 3 (FIX)
## Select Model: Opus 4.6
## Previous Phase Summary
Review found 12 issues: 2 CRITICAL, 5 HIGH, 3 MEDIUM, 2 LOW
## Tasks for This Phase
1. Read review/review_report.md
2. Fix all CRITICAL and HIGH items (REV-001 through REV-007)
3. Update review tracking with fix comments
4. Regenerate both REVIEW and CLEAN versions
5. Re-render and QA all pages
```

**Fix process:**
- Reads review report
- Fixes selected items (default: all CRITICAL + HIGH)
- Updates review tracking with fix annotations
- Regenerates both versions
- Visual QA to verify fixes

---

## Model Selection Guide

### Primary Workflow Models

| Phase | Model | When to Use |
|-------|-------|-------------|
| Phase 1 CREATE | **Opus 4.6** | Creating new documents, major updates, complex formatting |
| Phase 1b IMAGES | **Gemini 3 Pro** | Only model with native image generation |
| Phase 2 REVIEW | **GPT-5.2 High** | Expert review and quality analysis |
| Phase 3 FIX | **Opus 4.6** | Applying fixes based on review |

### Quick Edit Models

| Task | Model | When to Use |
|------|-------|-------------|
| Minor edits | **Opus 4.6 Fast** | Small text changes, quick formatting fixes |
| Simple updates | **Sonnet 4.5** | Single cell updates, simple text replacements |

### Model Selection Rules

1. **Always use Opus 4.6 for Phase 1** - Best for complex document creation
2. **Always use Gemini 3 Pro for Phase 1b** - Only model that can generate images
3. **Always use GPT-5.2 High for Phase 2** - Best for thorough review
4. **Always use Opus 4.6 for Phase 3** - Best for applying fixes
5. **Use Fast models only for quick edits** - Not for full workflow phases

---

## When to Skip Phase 1b

**Skip Phase 1b if:**
- ✅ All images were generated with code-based diagrams (architecture, flowcharts)
- ✅ No `{{IMAGE:...}}` placeholders remain in the document
- ✅ All visuals are already inserted and positioned correctly

**Don't skip Phase 1b if:**
- ❌ Document contains `{{IMAGE:...}}` placeholders
- ❌ You need conceptual/creative visuals (business process, user journey, value proposition)
- ❌ Phase 1 handoff explicitly mentions image generation needed

**How to check:** Look at the Phase 1 output. If you see `{{IMAGE:name}}` anywhere, Phase 1b is needed.

---

## Output File Versions

Every document has **TWO versions**:

### REVIEW Version (`filename_REVIEW.ext`)
- **Purpose:** Internal review and change tracking
- **Contains:**
  - Inline comments
  - Highlighted changes (green=new, yellow=modified)
  - Audit columns (Excel)
  - Speaker notes tracking (PowerPoint)
  - Change log pages/sheets/slides
- **Use:** For internal review and quality control

### CLEAN Version (`filename.ext`)
- **Purpose:** Client delivery
- **Contains:**
  - Same content as REVIEW version
  - **No** tracking marks, comments, or audit columns
  - Professional appearance
- **Use:** Send to client

**Both versions are always generated together.**

---

## Handoff File Format

Handoff files are saved in `tmp/handoff/` and follow this structure:

```markdown
# Handoff: Phase [N] ([PHASE NAME])
## Select Model: [MODEL NAME]
## Previous Phase Summary
[what was done, files created, stats]
## Tasks for This Phase
[numbered list of specific tasks with @file references]
## Files to Reference
[list of @output/ and @review/ files]
## After This Phase
[what handoff to generate next]
```

**To execute:** Simply type `Execute @tmp/handoff/phaseXX.md` in a new chat with the specified model.

---

## Common Workflows

### New Document Creation
1. Place source files in `input/`
2. Open chat with **Opus 4.6**
3. Type Phase 1 CREATE prompt
4. Wait for completion → system tells you next step
5. If images needed: Open chat with **Gemini 3 Pro** → `Execute @tmp/handoff/phase1b.md`
6. Open chat with **GPT-5.2 High** → `Execute @tmp/handoff/phase2.md`
7. If fixes needed: Open chat with **Opus 4.6** → `Execute @tmp/handoff/phase3.md`
8. Send CLEAN version to client, keep REVIEW version for records

### Quick Update
1. Open chat with **Opus 4.6 Fast** or **Sonnet 4.5**
2. Type: "Update [specific section/cell/slide] in output/filename_REVIEW.ext with [new content]"
3. Done (no review needed for minor edits)

### Cross-Document Sync
1. Open chat with **Opus 4.6**
2. Type: "Sync [data] across [list of documents]"
3. System updates all referenced documents
4. Proceed to Phase 2 review if needed

---

## Tips & Best Practices

1. **Always start with Phase 1** - Don't skip to later phases
2. **Use exact file paths** - Reference `output/filename_REVIEW.ext` explicitly
3. **Be specific in prompts** - Include file names, section names, cell ranges
4. **Check handoff files** - They contain complete context for the next phase
5. **Review the REVIEW version** - Always check tracking before sending CLEAN version
6. **Keep both versions** - REVIEW for records, CLEAN for client
7. **Use @file references** - In prompts, reference files with `@output/` or `@input/`
8. **One prompt per phase** - Don't combine multiple phases in one prompt

---

## Troubleshooting

### "No handoff file found"
- Check `tmp/handoff/` folder exists
- Verify the handoff file was created in previous phase
- Look for files named `phase1b.md`, `phase2.md`, or `phase3.md`

### "Model not available"
- Use the exact model specified in the handoff file
- For Phase 1b, you MUST use Gemini 3 Pro (only model with image generation)

### "Output files missing"
- Check `output/` folder
- Verify Phase 1 completed successfully
- Look for both `_REVIEW` and clean versions

### "Review tracking not working"
- Ensure you're editing the `_REVIEW` version, not the clean version
- Check that formatter scripts ran successfully
- Verify config.yaml has author information

---

## Quick Reference

| Action | Command |
|--------|---------|
| Create document | Phase 1 prompt (Opus 4.6) |
| Generate images | `Execute @tmp/handoff/phase1b.md` (Gemini 3 Pro) |
| Review document | `Execute @tmp/handoff/phase2.md` (GPT-5.2 High) |
| Fix issues | `Execute @tmp/handoff/phase3.md` (Opus 4.6) |
| Quick edit | Direct prompt (Opus 4.6 Fast or Sonnet 4.5) |

---

**Last Updated:** 2026-02-09  
**Version:** 1.0
