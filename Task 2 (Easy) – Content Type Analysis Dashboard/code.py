# TASK 2: CONTENT TYPE ANALYSIS DASHBOARD
# Data Analysis Using Python Internship
# Organization: Auspify Technologies

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from IPython.display import display, Markdown
from IPython.display import Image as NotebookImage

# 1. PROFESSIONAL DASHBOARD CONFIGURATION

sns.set_theme(style="whitegrid", context="notebook")

BASE_DIR = Path("/content")
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 75)
print("              NETFLIX CONTENT TYPE ANALYSIS")
print("                 DATA ANALYTICS DASHBOARD")
print("=" * 75)

# 2. LOAD THE CLEANED DATASET

print("\n[STEP 1] LOADING THE CLEANED DATASET")

possible_files = [
    OUTPUT_DIR / "netflix_cleaned.csv",
    BASE_DIR / "netflix_cleaned.csv",
    BASE_DIR / "Dataset.csv"
]

INPUT_FILE = next(
    (file for file in possible_files if file.exists()),
    None
)

if INPUT_FILE is None:
    raise FileNotFoundError(
        "Dataset not found!\n"
        "Please upload Dataset.csv or provide "
        "outputs/netflix_cleaned.csv."
    )

df = pd.read_csv(INPUT_FILE)

# Standardize column names
df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)

print(f"\nDataset loaded: {INPUT_FILE}")
print(f"Total records: {len(df):,}")
print(f"Total columns: {len(df.columns)}")

if "type" not in df.columns:
    raise ValueError(
        "The dataset does not contain a 'type' column. "
        "Please check that you uploaded the correct Netflix dataset."
    )

if df.empty:
    raise ValueError("The dataset contains no records.")

# 3. PREPARE CONTENT TYPE DATA

print("\n[STEP 2] ANALYZING MOVIES AND TV SHOWS")

df["type"] = (
    df["type"]
    .astype("string")
    .str.strip()
    .str.casefold()
)

# Keep only recognized categories for this analysis
valid_df = df[df["type"].isin(["movie", "tv show"])].copy()

valid_df["type"] = valid_df["type"].map({
    "movie": "Movie",
    "tv show": "TV Show"
})

if valid_df.empty:
    raise ValueError(
        "No recognized Movie or TV Show records were found."
    )

# Calculate content counts
content_counts = (
    valid_df["type"]
    .value_counts()
    .reindex(["Movie", "TV Show"], fill_value=0)
)

total_titles = int(content_counts.sum())

# Calculate percentages
content_percentages = (
    content_counts / total_titles * 100
)

# Create summary table
summary = pd.DataFrame({
    "Content Type": content_counts.index,
    "Total Titles": content_counts.values,
    "Percentage (%)": content_percentages.values.round(2)
})

summary["Percentage (%)"] = summary["Percentage (%)"].astype(float)

print("\nCONTENT DISTRIBUTION SUMMARY")
display(summary)

# 4. EXECUTIVE DASHBOARD

print("\n[STEP 3] CREATING THE DASHBOARD")

movie_count = int(content_counts.get("Movie", 0))
tv_count = int(content_counts.get("TV Show", 0))

movie_percentage = movie_count / total_titles * 100
tv_percentage = tv_count / total_titles * 100

fig = plt.figure(figsize=(16, 10))

fig.suptitle(
    "NETFLIX CONTENT TYPE ANALYSIS",
    fontsize=23,
    fontweight="bold",
    y=0.98
)

fig.text(
    0.5, 0.94,
    "Movies vs TV Shows | Content Distribution & Business Insights",
    ha="center",
    fontsize=12,
    color="dimgray"
)

# ---------------- KPI CARDS ----------------

ax1 = fig.add_axes([0.07, 0.76, 0.25, 0.12])
ax2 = fig.add_axes([0.375, 0.76, 0.25, 0.12])
ax3 = fig.add_axes([0.68, 0.76, 0.25, 0.12])

kpi_data = [
    (ax1, "TOTAL TITLES", f"{total_titles:,}"),
    (ax2, "MOVIES", f"{movie_count:,}"),
    (ax3, "TV SHOWS", f"{tv_count:,}")
]

for ax, title, value in kpi_data:
    ax.set_facecolor("#F0F5FA")

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_xticks([])
    ax.set_yticks([])

    ax.text(
        0.5, 0.68, title,
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        transform=ax.transAxes
    )

    ax.text(
        0.5, 0.30, value,
        ha="center",
        va="center",
        fontsize=24,
        fontweight="bold",
        transform=ax.transAxes
    )

# ---------------- BAR CHART ----------------

ax4 = fig.add_axes([0.08, 0.12, 0.40, 0.53])

bars = ax4.bar(
    content_counts.index,
    content_counts.values,
    width=0.55
)

ax4.set_title(
    "Content Type Comparison",
    fontsize=16,
    fontweight="bold",
    pad=15
)

ax4.set_xlabel("Content Type", fontsize=12)
ax4.set_ylabel("Number of Titles", fontsize=12)

ax4.bar_label(
    bars,
    labels=[f"{value:,}" for value in content_counts.values],
    padding=5,
    fontsize=12,
    fontweight="bold"
)

ax4.grid(axis="x", visible=False)
ax4.set_axisbelow(True)

# ---------------- DONUT CHART ----------------

ax5 = fig.add_axes([0.55, 0.15, 0.38, 0.48])

nonzero_counts = content_counts[content_counts > 0]

wedges, texts, autotexts = ax5.pie(
    nonzero_counts.values,
    labels=nonzero_counts.index,
    autopct="%1.1f%%",
    startangle=90,
    pctdistance=0.75,
    wedgeprops={
        "width": 0.40,
        "edgecolor": "white",
        "linewidth": 3
    },
    textprops={"fontsize": 12}
)

for autotext in autotexts:
    autotext.set_fontweight("bold")
    autotext.set_fontsize(12)

ax5.text(
    0, 0,
    f"{total_titles:,}\nTitles",
    ha="center",
    va="center",
    fontsize=17,
    fontweight="bold"
)

ax5.set_title(
    "Content Proportion",
    fontsize=16,
    fontweight="bold",
    pad=15
)

# Save the dashboard image
dashboard_path = OUTPUT_DIR / "content_type_dashboard.png"

fig.savefig(
    dashboard_path,
    dpi=200,
    bbox_inches="tight"
)

plt.show()

print(f"\nDashboard saved to: {dashboard_path}")

# 5. CONTENT PROPORTION COMPARISON

print("\n[STEP 4] COMPARING CONTENT PROPORTIONS")

comparison = summary.copy()

display(
    Markdown("### Content Type Percentage Comparison")
)

display(
    comparison.style
    .format({
        "Total Titles": "{:,.0f}",
        "Percentage (%)": "{:.2f}%"
    })
    .background_gradient(
        subset=["Total Titles"],
        cmap="Blues"
    )
)

if movie_count > tv_count:
    difference = movie_count - tv_count

    print(
        f"Movies exceed TV Shows by {difference:,} titles."
    )

elif tv_count > movie_count:
    difference = tv_count - movie_count

    print(
        f"TV Shows exceed Movies by {difference:,} titles."
    )

else:
    print("Movies and TV Shows have equal counts.")

# 6. GENERATE BUSINESS INSIGHTS

print("\n[STEP 5] GENERATING BUSINESS INSIGHTS")

if movie_percentage > tv_percentage:
    dominant_type = "Movies"
    dominant_percentage = movie_percentage

elif tv_percentage > movie_percentage:
    dominant_type = "TV Shows"
    dominant_percentage = tv_percentage

else:
    dominant_type = "Movies and TV Shows equally"
    dominant_percentage = movie_percentage

insights = [
    "NETFLIX CONTENT ANALYSIS REPORT",
    "=" * 55,
    "",
    f"Total analyzed titles: {total_titles:,}",
    "",
    "CONTENT DISTRIBUTION",
    f"Movies: {movie_count:,} ({movie_percentage:.2f}%)",
    f"TV Shows: {tv_count:,} ({tv_percentage:.2f}%)",
    "",
    "KEY FINDINGS",
    f"The larger content category is: {dominant_type}.",
    f"Its share of analyzed titles is: {dominant_percentage:.2f}%.",
    "",
    "BUSINESS INTERPRETATION",
    "The distribution describes the composition of the supplied dataset.",
    "It can help analysts understand the relative representation of",
    "Movies and TV Shows in the catalog.",
    "",
    "RECOMMENDATION",
    "Combine this result with country, genre, rating and release-year",
    "analysis before making broader content strategy recommendations.",
    "",
    "Note: These results describe the supplied dataset and do not",
    "measure audience demand, viewing hours or profitability."
]

report_text = "\n".join(insights)

print("\n" + report_text)

# 7. EXPORT RESULTS

print("\n[STEP 6] EXPORTING ANALYSIS RESULTS")

summary_path = OUTPUT_DIR / "content_type_summary.csv"
report_path = OUTPUT_DIR / "content_type_business_report.txt"

summary.to_csv(summary_path, index=False)

report_path.write_text(
    report_text,
    encoding="utf-8"
)

print("\nFILES GENERATED SUCCESSFULLY")
print("-" * 55)
print(f"Dashboard image : {dashboard_path}")
print(f"Summary CSV     : {summary_path}")
print(f"Business report : {report_path}")

print("\nTASK 2 COMPLETED SUCCESSFULLY!")
print("=" * 75)

# 8. DOWNLOAD RESULTS IN GOOGLE COLAB

from google.colab import files

print("\nDownload your project deliverables:")

files.download(str(summary_path))
files.download(str(report_path))
files.download(str(dashboard_path))
