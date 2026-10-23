# Netflix Data Analysis Using Python
### Data Cleaning • Exploratory Analysis • Visualization • Business Insights

<p align="center">
  <strong>Portfolio Project | Data Analysis Using Python Internship</strong><br>
  <em>Built with Python, Pandas, NumPy, Matplotlib, Seaborn, and Google Colab</em>
</p>

---

## Overview

This project explores Netflix titles data through a practical data-analysis workflow: importing a dataset, assessing data quality, cleaning and standardizing records, and preparing the result for downstream analysis and reporting.

The project is designed around the **Netflix Data Cleaning & Preparation** internship task. It can also serve as the starting point for related analyses such as content-type distribution, country-wise content, and release-year trends.

> **Data transparency:** Results depend on the actual CSV file used. This repository does not claim specific findings until the dataset has been processed and the outputs have been inspected.

## Objectives

- Import a Netflix titles CSV into Python using Pandas.
- Inspect the dataset's dimensions, columns, missing values, and duplicate records.
- Normalize column names and common text formatting.
- Standardize selected fields such as `type`, `country`, and `rating` when present.
- Convert release-year and date fields to suitable data types when present.
- Export a cleaned CSV and a column-level data-quality report.
- Keep the workflow reproducible and easy to explain during an internship review or project demonstration.

## Technology Stack

| Tool | Purpose |
|---|---|
| Python | Main programming language |
| Pandas | Data import, cleaning, transformation, and export |
| NumPy | Numerical/data-analysis support |
| Google Colab / Jupyter Notebook | Interactive execution and demonstration |
| CSV | Dataset input and output format |

Matplotlib and Seaborn can be used for visualization in follow-up analysis tasks.

## Project Workflow

1. **Import data** — load the CSV and inspect sample records, row count, and column count.
2. **Assess data quality** — measure missing values and identify duplicate rows.
3. **Clean records** — remove exact duplicate rows and, when appropriate, resolve repeated `show_id` values.
4. **Standardize fields** — trim text whitespace, normalize selected labels, and parse year/date fields where available.
5. **Generate quality report** — record each column's data type, missing-value count, missing percentage, and unique-value count.
6. **Export results** — save the cleaned dataset and quality report for review or later analysis.

## Repository Structure

```text
Netflix-Data-Analysis/
├── task1_netflix_cleaning.py      # Python cleaning workflow (if included)
├── Data Analysis Using Python Internship.ipynb  # Notebook (if included)
├── data/
│   └── netflix_titles.csv         # Input dataset (not included by default)
├── outputs/
│   ├── netflix_cleaned.csv        # Generated cleaned dataset
│   └── data_quality_report.csv    # Generated data-quality report
├── README.md
└── requirements.txt               # Optional dependency list
```

The exact files in your repository may differ. Update this tree to match the files you actually upload to GitHub. Avoid committing large datasets or generated files if the dataset's license or repository policy does not allow it.

## Dataset Setup

The cleaning code expects a CSV file named:

```text
data/netflix_titles.csv
```

If you are using Google Colab and uploaded the file as `/content/Dataset.csv`, change the input path in the notebook accordingly, or upload/rename the file to match the path expected by your code.

A typical Netflix titles dataset may contain columns such as:

- `show_id`
- `type`
- `title`
- `director`
- `cast`
- `country`
- `date_added`
- `release_year`
- `rating`
- `duration`
- `listed_in`
- `description`

The script should only transform columns that actually exist in your selected dataset. Check the CSV's column names before running the workflow.

## Installation and Usage

### Option A — Google Colab

1. Open your notebook in Google Colab.
2. Upload your dataset using the Files panel.
3. Confirm the dataset path. For example, `/content/Dataset.csv`.
4. Install dependencies if needed:

   ```python
   !pip install pandas numpy
   ```

5. Update the input path in the notebook to match the uploaded file.
6. Run the notebook cells from top to bottom.
7. Check the printed cleaning summary and inspect the generated CSV files.

### Option B — Run locally

1. Install Python 3.10 or later.
2. Place your input file at `data/netflix_titles.csv`.
3. Install dependencies:

   ```bash
   python -m pip install pandas numpy
   ```

4. Run the script:

   ```bash
   python task1_netflix_cleaning.py
   ```

If you use a notebook instead of a `.py` file, open it in Jupyter Notebook or VS Code and run the cells in order.

## Generated Outputs

### `netflix_cleaned.csv`
The prepared dataset after the implemented cleaning and standardization steps. Use this file as the input for subsequent analysis, after checking that the transformations are suitable for your data.

### `data_quality_report.csv`
A column-level report containing data types, missing-value counts, missing percentages, and unique-value counts. It helps identify fields that may need further attention.

## Data Quality Decisions

- **Missing values are not automatically filled with guesses.** A missing director, cast member, or country should not be replaced with invented information.
- **Missing-value reporting is not the same as missing-value removal.** Review each column and decide whether to preserve, fill, or remove missing values based on the analytical goal.
- **Exact duplicate rows** can be removed to avoid counting identical records multiple times.
- **Duplicate identifiers** should be investigated. If two records share a `show_id` but contain different information, inspect the conflict before dropping one.
- **Standardization should preserve meaning.** Trimming whitespace and normalizing case can improve consistency, but country names and rating labels should not be changed blindly.
- **Date parsing can produce missing values** when a source date is invalid or formatted unexpectedly. Inspect these records before final reporting.

## Validation Checklist

Before presenting or submitting the project, verify:

- [ ] The correct CSV was loaded.
- [ ] Row and column counts match the source file before cleaning.
- [ ] Missing values were reviewed rather than blindly deleted.
- [ ] Duplicate rows and identifiers were handled with documented rules.
- [ ] Important columns have the expected data types.
- [ ] The exported cleaned CSV opens successfully.
- [ ] The data-quality report matches the cleaned dataset.
- [ ] Screenshots show actual notebook output.
- [ ] Any findings in the report are supported by the data.

## Internship Task Alignment

This project directly addresses the Task 1 workflow:

- Import a dataset using Python and Pandas.
- Identify and handle missing values.
- Remove duplicate records and formatting inconsistencies.
- Standardize fields such as Country, Rating, and Type.
- Export the cleaned dataset for analysis.

Related tasks can build on the cleaned data:

- **Task 2:** Content Type Analysis Dashboard
- **Task 3:** Country-Wise Netflix Content Analysis
- **Task 4:** Trend Analysis by Release Year

Complete and document each additional task before describing it as finished.

## Limitations

- Output quality depends on the source dataset's completeness and consistency.
- Cleaning rules may need adjustment for datasets with different schemas.
- The project does not establish business causation; it describes patterns in the provided data.
- A generated output is not proof of internship completion or certification.

## Future Improvements

- Add an interactive dashboard using Streamlit.
- Visualize missing values and content distributions with Matplotlib or Seaborn.
- Add automated data-validation checks and a run summary.
- Compare Movies and TV Shows by release year.
- Analyze multi-country entries with documented counting rules.
- Create an executive report with charts and evidence-based recommendations.

## Author

**Mantasha Shaikh**  
BCA — Artificial Intelligence and Data Analytics

## Acknowledgement

Prepared as a learning and portfolio project aligned with the *Data Analysis Using Python Internship* task description from Auspify Technologies. Confirm internship submission requirements and attribution guidance with the program provider.

---

### Suggested GitHub Topics

`python` `data-analysis` `pandas` `numpy` `data-cleaning` `netflix-dataset` `exploratory-data-analysis` `google-colab`
