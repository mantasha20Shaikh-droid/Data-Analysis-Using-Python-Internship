# TASK 4: TREND ANALYSIS BY RELEASE YEAR
# Data Analysis Using Python Internship
# Organization: Auspify Technologies

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from IPython.display import display, Markdown

# 1. DASHBOARD CONFIGURATION
sns.set_theme(style="whitegrid", context="notebook")

BASE_DIR = Path("/content")
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 75)
print("             NETFLIX TREND ANALYSIS BY RELEASE YEAR")
print("                    TIME SERIES ANALYSIS")
print("=" * 75)

# 2. LOAD THE DATASET

print("\n[STEP 1] LOADING NETFLIX DATASET")

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
        "Netflix dataset not found!\n"
        "Please upload Dataset.csv or generate "
        "netflix_cleaned.csv using Task 1."
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

if df.empty:
    raise ValueError("The dataset contains no records.")

if "release_year" not in df.columns:
    raise ValueError(
        "The dataset does not contain a release_year column."
    )

# 3. CLEAN AND VALIDATE RELEASE YEARS

print("\n[STEP 2] CLEANING RELEASE YEAR DATA")

# Convert release year to numeric
df["release_year"] = pd.to_numeric(
    df["release_year"],
    errors="coerce"
)

# Count missing or invalid years before filtering
missing_years = int(df["release_year"].isna().sum())

# Accept years from 1900 through the current calendar year.
# This prevents obviously invalid year values from distorting trends.
current_year = pd.Timestamp.now().year

valid_year_mask = (
    df["release_year"].notna()
    & df["release_year"].between(1900, current_year)
    & (df["release_year"] % 1 == 0)
)

invalid_years = int((~valid_year_mask).sum())

trend_df = df.loc[valid_year_mask].copy()

trend_df["release_year"] = (
    trend_df["release_year"].astype(int)
)

if trend_df.empty:
    raise ValueError(
        "No valid release years were found in the dataset."
    )

print(f"Records with missing release years: {missing_years:,}")
print(f"Records excluded for invalid years: {invalid_years:,}")
print(f"Records included in analysis: {len(trend_df):,}")

print("\nCleaned dataset preview:")
display(trend_df.head())

# 4. CALCULATE YEARLY CONTENT RELEASES

print("\n[STEP 3] CALCULATING YEARLY CONTENT RELEASES")

yearly_counts = (
    trend_df.groupby("release_year")
    .size()
    .sort_index()
)

# Include years with zero recorded titles between observed years.
# This makes year-over-year comparisons consistent.
all_years = range(
    int(yearly_counts.index.min()),
    int(yearly_counts.index.max()) + 1
)

yearly_counts = yearly_counts.reindex(
    all_years,
    fill_value=0
)

yearly_summary = pd.DataFrame({
    "Release_Year": yearly_counts.index,
    "Titles_Released": yearly_counts.values
})

yearly_summary["Yearly_Change"] = (
    yearly_summary["Titles_Released"].diff()
)

previous_year_count = yearly_summary["Titles_Released"].shift(1)

yearly_summary["Yearly_Growth_Percent"] = np.where(
    previous_year_count > 0,
    (
        yearly_summary["Titles_Released"] - previous_year_count
    ) / previous_year_count * 100,
    np.nan
)

# Five-year rolling average helps reveal longer-term patterns
yearly_summary["Five_Year_Rolling_Average"] = (
    yearly_summary["Titles_Released"]
    .rolling(window=5, min_periods=1)
    .mean()
    .round(2)
)

print("\nYEARLY CONTENT RELEASE SUMMARY")
display(yearly_summary.tail(20))

# 5. ANALYZE MOVIES AND TV SHOWS SEPARATELY

print("\n[STEP 4] ANALYZING CONTENT TYPES")

if "type" in trend_df.columns:

    trend_df["type"] = (
        trend_df["type"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    trend_df["type"] = trend_df["type"].map({
        "movie": "Movie",
        "tv show": "TV Show"
    })

    typed_df = trend_df[trend_df["type"].notna()].copy()

    type_yearly = pd.crosstab(
        typed_df["release_year"],
        typed_df["type"]
    )

    type_yearly = type_yearly.reindex(
        all_years,
        fill_value=0
    )

    for content_type in ["Movie", "TV Show"]:
        if content_type not in type_yearly.columns:
            type_yearly[content_type] = 0

    type_yearly = type_yearly[
        ["Movie", "TV Show"]
    ]

    type_yearly.index.name = "Release_Year"

    print("\nMOVIES VS TV SHOWS BY RELEASE YEAR")
    display(type_yearly.tail(15))

else:
    type_yearly = None
    print("The type column is unavailable. "
          "Only overall yearly trends will be analyzed.")

# 6. IDENTIFY GROWTH AND DECLINE TRENDS

print("\n[STEP 5] IDENTIFYING GROWTH AND DECLINE TRENDS")

# Exclude years with zero recorded titles when finding peak year
nonzero_years = yearly_summary[
    yearly_summary["Titles_Released"] > 0
]

peak_row = nonzero_years.loc[
    nonzero_years["Titles_Released"].idxmax()
]

lowest_row = nonzero_years.loc[
    nonzero_years["Titles_Released"].idxmin()
]

peak_year = int(peak_row["Release_Year"])
peak_count = int(peak_row["Titles_Released"])

lowest_year = int(lowest_row["Release_Year"])
lowest_count = int(lowest_row["Titles_Released"])

# Identify largest positive and negative year-over-year changes
growth_candidates = yearly_summary.dropna(
    subset=["Yearly_Change"]
)

largest_growth = growth_candidates.loc[
    growth_candidates["Yearly_Change"].idxmax()
]

largest_decline = growth_candidates.loc[
    growth_candidates["Yearly_Change"].idxmin()
]

print(f"\nYear with the highest recorded release count: {peak_year}")
print(f"Titles in that year: {peak_count:,}")

print(f"\nYear with the lowest nonzero release count: {lowest_year}")
print(f"Titles in that year: {lowest_count:,}")

print(
    f"\nLargest year-over-year increase: "
    f"{int(largest_growth['Release_Year'])}"
)

print(
    f"Increase in recorded titles: "
    f"{int(largest_growth['Yearly_Change']):+,}"
)

print(
    f"\nLargest year-over-year decrease: "
    f"{int(largest_decline['Release_Year'])}"
)

print(
    f"Decrease in recorded titles: "
    f"{int(largest_decline['Yearly_Change']):+,}"
)

# 7. CREATE PROFESSIONAL TREND VISUALIZATIONS

print("\n[STEP 6] CREATING TREND VISUALIZATIONS")

# CHART 1: YEARLY RELEASE COUNT AND ROLLING AVERAGE

fig, axes = plt.subplots(
    2, 1,
    figsize=(16, 12)
)

fig.suptitle(
    "NETFLIX RELEASE YEAR TREND ANALYSIS",
    fontsize=22,
    fontweight="bold",
    y=0.99
)

axes[0].plot(
    yearly_summary["Release_Year"],
    yearly_summary["Titles_Released"],
    marker="o",
    markersize=3,
    linewidth=1.5,
    label="Yearly Titles"
)

axes[0].plot(
    yearly_summary["Release_Year"],
    yearly_summary["Five_Year_Rolling_Average"],
    linewidth=2.5,
    label="Five-Year Rolling Average"
)

axes[0].set_title(
    "Number of Netflix Titles by Release Year",
    fontsize=16,
    fontweight="bold"
)

axes[0].set_xlabel("Release Year")
axes[0].set_ylabel("Number of Titles")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# CHART 2: YEAR-OVER-YEAR CHANGE

change_data = yearly_summary.dropna(
    subset=["Yearly_Change"]
)

bar_colors = [
    "seagreen" if value >= 0 else "indianred"
    for value in change_data["Yearly_Change"]
]

axes[1].bar(
    change_data["Release_Year"],
    change_data["Yearly_Change"],
    color=bar_colors,
    width=0.8
)

axes[1].axhline(
    0,
    linewidth=1
)

axes[1].set_title(
    "Year-over-Year Change in Title Counts",
    fontsize=16,
    fontweight="bold"
)

axes[1].set_xlabel("Release Year")
axes[1].set_ylabel("Change in Number of Titles")
axes[1].grid(axis="y", alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])

trend_chart_path = (
    OUTPUT_DIR / "netflix_release_year_trend.png"
)

plt.savefig(
    trend_chart_path,
    dpi=200,
    bbox_inches="tight"
)

plt.show()

# 8. MOVIE VS TV SHOW TREND CHART

if type_yearly is not None:

    fig, ax = plt.subplots(figsize=(15, 7))

    type_yearly.plot(
        ax=ax,
        linewidth=2
    )

    ax.set_title(
        "Movies vs TV Shows by Release Year",
        fontsize=18,
        fontweight="bold"
    )

    ax.set_xlabel("Release Year")
    ax.set_ylabel("Number of Titles")
    ax.legend(title="Content Type")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    type_chart_path = (
        OUTPUT_DIR / "netflix_movie_tv_year_trend.png"
    )

    plt.savefig(
        type_chart_path,
        dpi=200,
        bbox_inches="tight"
    )

    plt.show()

else:
    type_chart_path = None

print(f"Yearly trend chart: {trend_chart_path}")

if type_chart_path:
    print(f"Content type chart: {type_chart_path}")

# 9. GENERATE BUSINESS INSIGHTS REPORT

print("\n[STEP 7] GENERATING BUSINESS INSIGHTS")

insights = [
    "NETFLIX TREND ANALYSIS BY RELEASE YEAR",
    "=" * 65,
    "",
    f"Dataset: {INPUT_FILE.name}",
    f"Original records: {len(df):,}",
    f"Records included in yearly analysis: {len(trend_df):,}",
    f"Records with missing release years: {missing_years:,}",
    f"Records excluded for invalid years: {invalid_years:,}",
    "",
    "KEY FINDINGS",
    "-" * 45,
    f"Highest-count release year: {peak_year}",
    f"Titles associated with that year: {peak_count:,}",
    f"Lowest nonzero release year: {lowest_year}",
    f"Titles associated with that year: {lowest_count:,}",
    "",
    f"Largest recorded year-over-year increase occurred in "
    f"{int(largest_growth['Release_Year'])}: "
    f"{int(largest_growth['Yearly_Change']):+,} titles.",
    "",
    f"Largest recorded year-over-year decrease occurred in "
    f"{int(largest_decline['Release_Year'])}: "
    f"{int(largest_decline['Yearly_Change']):+,} titles.",
    "",
    "BUSINESS INTERPRETATION",
    "-" * 45,
    "The yearly counts show how the release years of titles in the",
    "supplied catalog are distributed over time.",
    "",
    "A rolling average helps reveal broader patterns by reducing",
    "the effect of individual year-to-year fluctuations.",
    "",
    "Yearly counts in a Netflix catalog do not necessarily measure",
    "the number of titles Netflix originally produced in each year.",
    "They describe the release years recorded in this dataset.",
    "",
    "RECOMMENDATIONS",
    "-" * 45,
    "1. Compare release-year trends for Movies and TV Shows.",
    "2. Examine genre and country patterns across different periods.",
    "3. Investigate unusually large yearly increases or decreases.",
    "4. Consider dataset coverage before drawing conclusions.",
    "",
    "LIMITATIONS",
    "-" * 45,
    "The dataset may not represent the entire Netflix catalog.",
    "Recent years may be incomplete, so lower recent counts do not",
    "necessarily indicate a decline in content production.",
    "This analysis does not measure viewing hours or audience demand."
]

report_text = "\n".join(insights)

print("\n" + report_text)

# 10. EXPORT RESULTS

print("\n[STEP 8] EXPORTING ANALYSIS RESULTS")

yearly_csv_path = (
    OUTPUT_DIR / "netflix_yearly_release_summary.csv"
)

report_path = (
    OUTPUT_DIR / "netflix_release_year_business_report.txt"
)

yearly_summary.to_csv(
    yearly_csv_path,
    index=False
)

report_path.write_text(
    report_text,
    encoding="utf-8"
)

if type_yearly is not None:
    type_yearly.to_csv(
        OUTPUT_DIR / "netflix_movie_tv_yearly_summary.csv"
    )

print("\nFILES GENERATED SUCCESSFULLY")
print("-" * 60)
print(f"Yearly summary: {yearly_csv_path}")
print(f"Business report: {report_path}")
print(f"Trend chart: {trend_chart_path}")

if type_chart_path:
    print(
        "Movie/TV Show chart: "
        f"{type_chart_path}"
    )

print("\n\n\n")
print("          TASK 4 COMPLETED SUCCESSFULLY!")

# 11. DOWNLOAD RESULTS IN GOOGLE COLAB

from google.colab import files

print("\nDownloading project deliverables...")

files.download(str(yearly_csv_path))
files.download(str(report_path))
files.download(str(trend_chart_path))

if type_chart_path:
    files.download(str(type_chart_path))

print("\nAll available deliverables have been prepared.")
