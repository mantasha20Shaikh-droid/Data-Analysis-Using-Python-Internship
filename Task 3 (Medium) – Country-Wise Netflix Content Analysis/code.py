# TASK 3: COUNTRY-WISE NETFLIX CONTENT ANALYSIS
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
print("          COUNTRY-WISE NETFLIX CONTENT ANALYSIS")
print("               GEOGRAPHIC INSIGHTS DASHBOARD")
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
        "Dataset not found. Upload Dataset.csv to /content "
        "or generate netflix_cleaned.csv using Task 1."
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

if "country" not in df.columns:
    raise ValueError(
        "The dataset does not contain a 'country' column. "
        "Please check your dataset."
    )

if df.empty:
    raise ValueError("The dataset contains no records.")

# 3. CLEAN COUNTRY INFORMATION

print("\n[STEP 2] CLEANING COUNTRY INFORMATION")

# Normalize whitespace and missing-value markers
df["country"] = (
    df["country"]
    .astype("string")
    .str.strip()
    .replace(
        ["", "NA", "N/A", "NULL", "null", "None", "nan"],
        pd.NA
    )
)

missing_country_records = int(df["country"].isna().sum())

print(f"Records with missing country information: "
      f"{missing_country_records:,}")

# Keep records with country information for this analysis
country_df = df[df["country"].notna()].copy()

if country_df.empty:
    raise ValueError(
        "No country information is available in the dataset."
    )

# Each Netflix record can list multiple countries.
# Split those countries and create one row per title-country pair.
country_df["country_list"] = country_df["country"].str.split(",")

country_df = country_df.explode("country_list")

country_df["country_list"] = (
    country_df["country_list"]
    .astype("string")
    .str.strip()
)

# Remove empty country names
country_df = country_df[
    country_df["country_list"].notna()
    & country_df["country_list"].ne("")
].copy()

# Count each title only once per country.
# This avoids double-counting a title-country pair.
if "show_id" in country_df.columns:
    country_df = country_df.drop_duplicates(
        subset=["show_id", "country_list"]
    )
else:
    # Fallback for datasets without a show_id column
    country_df = country_df.drop_duplicates(
        subset=["title", "release_year", "type", "country_list"]
        if {"title", "release_year", "type"}.issubset(country_df.columns)
        else ["title", "country_list"]
    )

country_df.rename(
    columns={"country_list": "country_name"},
    inplace=True
)

print("\nCountry information cleaned successfully!")
print(f"Title-country pairs analyzed: {len(country_df):,}")
print(f"Unique countries found: "
      f"{country_df['country_name'].nunique():,}")

# 4. CALCULATE COUNTRY-WISE CONTENT COUNTS

print("\n[STEP 3] CALCULATING CONTENT COUNT BY COUNTRY")

country_counts = (
    country_df.groupby("country_name")
    .size()
    .sort_values(ascending=False)
)

country_summary = country_counts.reset_index()
country_summary.columns = ["Country", "Total_Titles"]

total_title_country_pairs = int(country_counts.sum())

country_summary["Percentage (%)"] = (
    country_summary["Total_Titles"]
    / total_title_country_pairs * 100
).round(2)

country_summary["Rank"] = (
    country_summary["Total_Titles"]
    .rank(method="min", ascending=False)
    .astype(int)
)

country_summary = country_summary[
    ["Rank", "Country", "Total_Titles", "Percentage (%)"]
].sort_values(
    ["Total_Titles", "Country"],
    ascending=[False, True]
).reset_index(drop=True)

print("\nCOUNTRY-WISE CONTENT SUMMARY")

display(country_summary.head(15))

# 5. IDENTIFY TOP 10 CONTENT-PRODUCING COUNTRIES

print("\n[STEP 4] IDENTIFYING TOP 10 COUNTRIES")

top_10 = country_counts.head(10).sort_values(ascending=True)

display(
    Markdown("## Top 10 Countries by Netflix Title Count")
)

display(
    country_summary.head(10).style.format({
        "Total_Titles": "{:,.0f}",
        "Percentage (%)": "{:.2f}%"
    })
)

# 6. CREATE PROFESSIONAL VISUAL DASHBOARD

print("\n[STEP 5] CREATING COUNTRY ANALYSIS DASHBOARD")

fig, axes = plt.subplots(
    2, 1,
    figsize=(15, 14),
    gridspec_kw={"height_ratios": [1.25, 1]}
)

fig.suptitle(
    "NETFLIX COUNTRY-WISE CONTENT ANALYSIS",
    fontsize=22,
    fontweight="bold",
    y=0.98
)

fig.text(
    0.5, 0.95,
    "Geographic Distribution | Top Countries | Content Rankings",
    ha="center",
    fontsize=12
)

# ---------------- CHART 1: TOP 10 COUNTRIES ----------------

ax1 = axes[0]

bars = ax1.barh(
    top_10.index,
    top_10.values
)

ax1.set_title(
    "Top 10 Countries by Number of Netflix Titles",
    fontsize=16,
    fontweight="bold",
    pad=15
)

ax1.set_xlabel("Number of Title-Country Associations", fontsize=12)
ax1.set_ylabel("Country", fontsize=12)

ax1.bar_label(
    bars,
    labels=[f"{value:,}" for value in top_10.values],
    padding=5,
    fontsize=10
)

ax1.grid(axis="y", visible=False)
ax1.set_axisbelow(True)

# ---------------- CHART 2: COUNTRY SHARE ----------------

ax2 = axes[1]

top_10_desc = country_counts.head(10)

top_percentages = (
    top_10_desc / total_title_country_pairs * 100
).sort_values(ascending=True)

bars2 = ax2.barh(
    top_percentages.index,
    top_percentages.values
)

ax2.set_title(
    "Top 10 Countries: Share of All Title-Country Associations",
    fontsize=15,
    fontweight="bold",
    pad=15
)

ax2.set_xlabel("Percentage (%)", fontsize=12)
ax2.set_ylabel("Country", fontsize=12)

ax2.bar_label(
    bars2,
    labels=[f"{value:.2f}%" for value in top_percentages.values],
    padding=5,
    fontsize=10
)

ax2.grid(axis="y", visible=False)
ax2.set_axisbelow(True)

plt.tight_layout(rect=[0, 0, 1, 0.93])

dashboard_path = OUTPUT_DIR / "country_wise_netflix_dashboard.png"

plt.savefig(
    dashboard_path,
    dpi=200,
    bbox_inches="tight"
)

plt.show()

print(f"\nDashboard saved: {dashboard_path}")

# 7. GENERATE BUSINESS INSIGHTS

print("\n[STEP 6] GENERATING BUSINESS INSIGHTS")

top_country = country_counts.index[0]
top_country_count = int(country_counts.iloc[0])

top_country_percentage = (
    top_country_count / total_title_country_pairs * 100
)

top_3_count = int(country_counts.head(3).sum())

top_3_percentage = (
    top_3_count / total_title_country_pairs * 100
)

insights = [
    "NETFLIX COUNTRY-WISE CONTENT ANALYSIS REPORT",
    "=" * 60,
    "",
    f"Source dataset: {INPUT_FILE.name}",
    f"Original dataset records: {len(df):,}",
    f"Records without country information: "
    f"{missing_country_records:,}",
    f"Unique countries identified: "
    f"{country_df['country_name'].nunique():,}",
    f"Title-country associations analyzed: "
    f"{total_title_country_pairs:,}",
    "",
    "TOP CONTENT-PRODUCING COUNTRIES",
    "-" * 40
]

for rank, (country, count) in enumerate(
    country_counts.head(10).items(),
    start=1
):
    percentage = count / total_title_country_pairs * 100

    insights.append(
        f"{rank}. {country}: {count:,} title-country associations "
        f"({percentage:.2f}%)"
    )

insights.extend([
    "",
    "KEY FINDINGS",
    "-" * 40,
    f"Highest-ranked country: {top_country}",
    f"Associated title count: {top_country_count:,}",
    f"Share of all title-country associations: "
    f"{top_country_percentage:.2f}%",
    f"Combined share of the top three countries: "
    f"{top_3_percentage:.2f}%",
    "",
    "BUSINESS INTERPRETATION",
    "-" * 40,
    "The rankings show how country associations are distributed",
    "within the supplied Netflix dataset.",
    "",
    "A title associated with multiple countries contributes once",
    "to each listed country's count. Therefore, country counts can",
    "overlap and percentages across countries need not sum to 100%.",
    "",
    "RECOMMENDATIONS",
    "-" * 40,
    "1. Compare country rankings with content type and release year.",
    "2. Investigate countries with increasing title counts over time.",
    "3. Examine genre and rating patterns across leading countries.",
    "4. Consider missing country information when interpreting results.",
    "",
    "LIMITATION",
    "-" * 40,
    "These counts describe dataset associations, not audience size,",
    "viewing hours, revenue, or actual market demand."
])

report_text = "\n".join(insights)

print("\n" + report_text)

# 8. EXPORT ANALYSIS RESULTS

print("\n[STEP 7] EXPORTING RESULTS")

country_summary_path = OUTPUT_DIR / "country_wise_content_summary.csv"
top_10_path = OUTPUT_DIR / "top_10_countries.csv"
report_path = OUTPUT_DIR / "country_analysis_business_report.txt"

country_summary.to_csv(
    country_summary_path,
    index=False
)

country_summary.head(10).to_csv(
    top_10_path,
    index=False
)

report_path.write_text(
    report_text,
    encoding="utf-8"
)

print("\nFILES GENERATED SUCCESSFULLY")
print("-" * 60)
print(f"Full country ranking : {country_summary_path}")
print(f"Top 10 countries     : {top_10_path}")
print(f"Dashboard image      : {dashboard_path}")
print(f"Business report      : {report_path}")

# 9. FINAL PROJECT SUMMARY

print("\n" + "=" * 75)
print("             TASK 3 COMPLETED SUCCESSFULLY!")
print("=" * 75)

print(f"Countries analyzed: {country_summary['Country'].nunique():,}")
print(f"Title-country pairs: {total_title_country_pairs:,}")
print(f"Top-ranked country: {top_country}")
print(f"Top country count: {top_country_count:,}")

# 10. DOWNLOAD OUTPUTS IN GOOGLE COLAB

from google.colab import files

print("\nDownloading your project deliverables...")

files.download(str(country_summary_path))
files.download(str(top_10_path))
files.download(str(dashboard_path))
files.download(str(report_path))
