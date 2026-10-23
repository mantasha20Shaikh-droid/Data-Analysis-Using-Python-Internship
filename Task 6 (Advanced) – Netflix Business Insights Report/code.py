# Task 6: Netflix Business Insights Report
# Data Analysis Using Python Internship
# Organization: Auspify Technologies

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path
from datetime import datetime
from IPython.display import display, HTML
import warnings
import zipfile
import json

warnings.filterwarnings("ignore")

# Configure project directories

BASE_DIR = Path("/content")
OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_DIR = OUTPUT_DIR / "business_insights_report"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")

print("TASK 6: NETFLIX BUSINESS INSIGHTS REPORT")
print("Business Intelligence and Executive Reporting")
print("Organization: Auspify Technologies")

# Step 1: Load and validate the dataset

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
        "Netflix dataset not found.\n"
        "Upload Dataset.csv to /content or run Task 1 first."
    )

df = pd.read_csv(INPUT_FILE)

df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)

if df.empty:
    raise ValueError("The dataset is empty.")

required_columns = ["type", "title", "release_year"]

missing_required = [
    column for column in required_columns
    if column not in df.columns
]

if missing_required:
    raise ValueError(
        f"Required columns missing: {missing_required}"
    )

print(f"\nDataset: {INPUT_FILE}")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")

# Clean common missing-value markers

missing_markers = [
    "", "NA", "N/A", "NULL", "None", "nan"
]

for column in df.select_dtypes(
    include=["object", "string"]
).columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
        .replace(missing_markers, pd.NA)
    )

# Normalize categorical columns

df["type"] = df["type"].str.title()

if "rating" in df.columns:
    df["rating"] = df["rating"].str.upper()

df["release_year"] = pd.to_numeric(
    df["release_year"],
    errors="coerce"
)

# Preserve original data for quality analysis

original_rows = len(df)
original_duplicates = int(df.duplicated().sum())
missing_by_column = df.isna().sum()

quality_report = pd.DataFrame({
    "Column": df.columns,
    "Data_Type": [
        str(df[column].dtype) for column in df.columns
    ],
    "Missing_Values": [
        int(df[column].isna().sum()) for column in df.columns
    ],
    "Missing_Percentage": [
        round(df[column].isna().mean() * 100, 2)
        for column in df.columns
    ],
    "Unique_Values": [
        int(df[column].nunique()) for column in df.columns
    ]
})

# Remove exact duplicate records for analysis

analysis_df = df.drop_duplicates().copy()

# Validate release years

current_year = pd.Timestamp.now().year

valid_year = (
    analysis_df["release_year"].notna()
    & analysis_df["release_year"].between(1900, current_year)
    & (analysis_df["release_year"] % 1 == 0)
)

invalid_year_count = int((~valid_year).sum())

analysis_df["release_year"] = (
    analysis_df["release_year"].where(valid_year)
)

analysis_df["release_year"] = (
    analysis_df["release_year"].astype("Int64")
)

analysis_df["type"] = analysis_df["type"].where(
    analysis_df["type"].isin(["Movie", "TV Show"])
)

print("\nSTEP 1: EXPLORATORY DATA ANALYSIS")

print("\nDataset preview")
display(analysis_df.head())

print("\nDataset information")
print(f"Original rows: {original_rows:,}")
print(f"Exact duplicate rows: {original_duplicates:,}")
print(f"Rows after duplicate removal: {len(analysis_df):,}")
print(f"Invalid or missing release years: {invalid_year_count:,}")

print("\nData quality report")
display(quality_report)

# Step 2: Calculate business KPIs

print("\nSTEP 2: CALCULATING BUSINESS KPIs")

total_titles = len(analysis_df)

movie_count = int(
    (analysis_df["type"] == "Movie").sum()
)

tv_count = int(
    (analysis_df["type"] == "TV Show").sum()
)

known_type_count = movie_count + tv_count

movie_percentage = (
    movie_count / known_type_count * 100
    if known_type_count else 0
)

tv_percentage = (
    tv_count / known_type_count * 100
    if known_type_count else 0
)

if "country" in analysis_df.columns:
    country_count = int(
        analysis_df["country"].dropna().str.split(",").explode()
        .str.strip().nunique()
    )
else:
    country_count = 0

if "listed_in" in analysis_df.columns:
    genre_count = int(
        analysis_df["listed_in"].dropna().str.split(",").explode()
        .str.strip().nunique()
    )
else:
    genre_count = 0

valid_release_years = analysis_df["release_year"].dropna()

year_min = (
    int(valid_release_years.min())
    if not valid_release_years.empty else None
)

year_max = (
    int(valid_release_years.max())
    if not valid_release_years.empty else None
)

kpi_data = pd.DataFrame({
    "Business_Metric": [
        "Total Titles",
        "Movies",
        "TV Shows",
        "Movie Share (%)",
        "TV Show Share (%)",
        "Distinct Countries",
        "Distinct Genres",
        "Exact Duplicate Rows",
        "Missing Release Years"
    ],
    "Value": [
        total_titles,
        movie_count,
        tv_count,
        round(movie_percentage, 2),
        round(tv_percentage, 2),
        country_count,
        genre_count,
        original_duplicates,
        invalid_year_count
    ]
})

display(kpi_data)

# Step 3: Content type analysis

type_counts = (
    analysis_df["type"]
    .dropna()
    .value_counts()
    .rename_axis("Content_Type")
    .reset_index(name="Total_Titles")
)

type_counts["Percentage"] = (
    type_counts["Total_Titles"]
    / type_counts["Total_Titles"].sum() * 100
).round(2)

type_fig = px.pie(
    type_counts,
    names="Content_Type",
    values="Total_Titles",
    hole=0.55,
    title="Netflix Content Distribution",
    template="plotly_white"
)

type_fig.update_traces(
    textposition="inside",
    textinfo="label+percent+value"
)

type_fig.update_layout(title_x=0.5)

print("\nCONTENT TYPE DISTRIBUTION")
display(type_counts)
type_fig.show()

# Step 4: Rating analysis

if "rating" in analysis_df.columns:

    rating_data = analysis_df[
        analysis_df["rating"].notna()
    ]

    rating_counts = (
        rating_data["rating"]
        .value_counts()
        .rename_axis("Rating")
        .reset_index(name="Total_Titles")
    )

    rating_fig = px.bar(
        rating_counts,
        x="Rating",
        y="Total_Titles",
        color="Total_Titles",
        text="Total_Titles",
        title="Netflix Content Ratings",
        template="plotly_white",
        color_continuous_scale="Blues"
    )

    rating_fig.update_layout(
        title_x=0.5,
        coloraxis_showscale=False
    )

    print("\nCONTENT RATING ANALYSIS")
    display(rating_counts.head(15))
    rating_fig.show()

else:
    rating_counts = pd.DataFrame(
        columns=["Rating", "Total_Titles"]
    )
    rating_fig = None

# Step 5: Genre analysis

if "listed_in" in analysis_df.columns:

    genre_data = analysis_df[
        analysis_df["listed_in"].notna()
    ].copy()

    genre_data["Genre"] = genre_data["listed_in"].str.split(",")

    genre_data = genre_data.explode("Genre")

    genre_data["Genre"] = (
        genre_data["Genre"]
        .astype("string")
        .str.strip()
    )

    genre_data = genre_data[
        genre_data["Genre"].notna()
        & genre_data["Genre"].ne("")
    ].copy()

    if "show_id" in genre_data.columns:
        genre_data = genre_data.drop_duplicates(
            subset=["show_id", "Genre"]
        )

    genre_counts = (
        genre_data["Genre"]
        .value_counts()
        .rename_axis("Genre")
        .reset_index(name="Total_Titles")
    )

    top_genres = genre_counts.head(15).sort_values(
        "Total_Titles",
        ascending=True
    )

    genre_fig = px.bar(
        top_genres,
        x="Total_Titles",
        y="Genre",
        orientation="h",
        color="Total_Titles",
        title="Top 15 Netflix Genres",
        template="plotly_white",
        color_continuous_scale="Blues"
    )

    genre_fig.update_layout(
        title_x=0.5,
        coloraxis_showscale=False
    )

    print("\nTOP GENRES")
    display(genre_counts.head(15))
    genre_fig.show()

else:
    genre_counts = pd.DataFrame(
        columns=["Genre", "Total_Titles"]
    )
    genre_fig = None
    genre_data = pd.DataFrame()

# Step 6: Country-wise content analysis

if "country" in analysis_df.columns:

    country_data = analysis_df[
        analysis_df["country"].notna()
    ].copy()

    country_data["Country"] = (
        country_data["country"].str.split(",")
    )

    country_data = country_data.explode("Country")

    country_data["Country"] = (
        country_data["Country"]
        .astype("string")
        .str.strip()
    )

    country_data = country_data[
        country_data["Country"].notna()
        & country_data["Country"].ne("")
    ].copy()

    if "show_id" in country_data.columns:
        country_data = country_data.drop_duplicates(
            subset=["show_id", "Country"]
        )

    country_counts = (
        country_data["Country"]
        .value_counts()
        .rename_axis("Country")
        .reset_index(name="Total_Titles")
    )

    top_countries = country_counts.head(15).sort_values(
        "Total_Titles",
        ascending=True
    )

    country_fig = px.bar(
        top_countries,
        x="Total_Titles",
        y="Country",
        orientation="h",
        color="Total_Titles",
        title="Top 15 Countries by Catalog Titles",
        template="plotly_white",
        color_continuous_scale="Teal"
    )

    country_fig.update_layout(
        title_x=0.5,
        coloraxis_showscale=False
    )

    print("\nTOP COUNTRIES")
    display(country_counts.head(15))
    country_fig.show()

else:
    country_counts = pd.DataFrame(
        columns=["Country", "Total_Titles"]
    )
    country_fig = None
    country_data = pd.DataFrame()

# Step 7: Release-year trends

year_data = analysis_df[
    analysis_df["release_year"].notna()
].copy()

if not year_data.empty:

    yearly_counts = (
        year_data.groupby("release_year")
        .size()
        .sort_index()
    )

    yearly_summary = pd.DataFrame({
        "Release_Year": yearly_counts.index.astype(int),
        "Total_Titles": yearly_counts.values
    })

    yearly_summary["Yearly_Change"] = (
        yearly_summary["Total_Titles"].diff()
    )

    yearly_summary["Growth_Percentage"] = (
        yearly_summary["Total_Titles"]
        .pct_change(fill_method=None)
        .replace([np.inf, -np.inf], np.nan)
        .mul(100)
        .round(2)
    )

    yearly_summary["Rolling_Average"] = (
        yearly_summary["Total_Titles"]
        .rolling(window=5, min_periods=1)
        .mean()
        .round(2)
    )

    year_fig = px.line(
        yearly_summary,
        x="Release_Year",
        y=["Total_Titles", "Rolling_Average"],
        markers=True,
        title="Netflix Catalog Distribution by Release Year",
        template="plotly_white",
        labels={
            "Release_Year": "Release Year",
            "value": "Number of Titles",
            "variable": "Metric"
        }
    )

    year_fig.update_layout(title_x=0.5)

    print("\nRELEASE YEAR ANALYSIS")
    display(yearly_summary.tail(15))
    year_fig.show()

else:
    yearly_summary = pd.DataFrame(
        columns=[
            "Release_Year",
            "Total_Titles",
            "Yearly_Change",
            "Growth_Percentage",
            "Rolling_Average"
        ]
    )
    year_fig = None

# Step 8: Compare content ratings by type

if (
    "rating" in analysis_df.columns
    and analysis_df["type"].notna().any()
):

    rating_type_data = analysis_df[
        analysis_df["rating"].notna()
        & analysis_df["type"].notna()
    ]

    rating_type_counts = pd.crosstab(
        rating_type_data["rating"],
        rating_type_data["type"]
    )

    rating_type_long = (
        rating_type_counts
        .reset_index()
        .melt(
            id_vars="rating",
            var_name="Content_Type",
            value_name="Total_Titles"
        )
    )

    rating_type_fig = px.bar(
        rating_type_long,
        x="rating",
        y="Total_Titles",
        color="Content_Type",
        barmode="group",
        title="Content Ratings by Content Type",
        template="plotly_white"
    )

    rating_type_fig.update_layout(title_x=0.5)

    print("\nRATING COMPARISON BY CONTENT TYPE")
    display(rating_type_counts)
    rating_type_fig.show()

else:
    rating_type_counts = pd.DataFrame()
    rating_type_fig = None

# Step 9: Create business insights

print("\nSTEP 4: GENERATING ACTIONABLE BUSINESS INSIGHTS")

insights = []

if not type_counts.empty:
    largest_type = type_counts.iloc[0]
    insights.append(
        f"The largest content category is {largest_type['Content_Type']}, "
        f"representing {largest_type['Percentage']:.2f}% "
        f"of records with recognized content types."
    )

if not rating_counts.empty:
    most_common_rating = rating_counts.iloc[0]
    insights.append(
        f"The most frequently recorded rating is "
        f"{most_common_rating['Rating']}, with "
        f"{int(most_common_rating['Total_Titles']):,} titles."
    )

if not genre_counts.empty:
    most_common_genre = genre_counts.iloc[0]
    insights.append(
        f"The most frequently associated genre is "
        f"{most_common_genre['Genre']}, appearing in "
        f"{int(most_common_genre['Total_Titles']):,} titles."
    )

if not country_counts.empty:
    top_country = country_counts.iloc[0]
    insights.append(
        f"The country with the largest recorded title count is "
        f"{top_country['Country']}, with "
        f"{int(top_country['Total_Titles']):,} title associations."
    )

if not yearly_summary.empty:
    peak_year_row = yearly_summary.loc[
        yearly_summary["Total_Titles"].idxmax()
    ]

    insights.append(
        f"The release year with the highest number of catalog titles "
        f"is {int(peak_year_row['Release_Year'])}, with "
        f"{int(peak_year_row['Total_Titles']):,} titles."
    )

insights.extend([
    "Genre and country counts can overlap because a title may have "
    "multiple genres or multiple associated countries.",
    "Release year describes when a title was released, not necessarily "
    "when Netflix produced or acquired it.",
    "Catalog records alone cannot establish audience demand, "
    "viewing hours, or profitability."
])

recommendations = [
    "Use rating distributions to review age-appropriateness and "
    "catalog coverage across audience segments.",
    "Compare genre distributions by country before proposing "
    "regional content strategies.",
    "Investigate changes in release-year distributions alongside "
    "acquisition, licensing, and viewing data.",
    "Prioritize additional data on viewing hours, completion rates, "
    "subscriptions, and content costs before making investment decisions.",
    "Review missing values and inconsistent labels regularly "
    "to improve data quality."
]

print("\nKEY FINDINGS")

for index, insight in enumerate(insights, start=1):
    print(f"{index}. {insight}")

print("\nBUSINESS RECOMMENDATIONS")

for index, recommendation in enumerate(recommendations, start=1):
    print(f"{index}. {recommendation}")

# Step 10: Create a combined interactive dashboard

print("\nSTEP 5: CREATING THE BUSINESS INTELLIGENCE DASHBOARD")

figures = [
    ("Content Distribution", type_fig),
    ("Content Ratings", rating_fig),
    ("Popular Genres", genre_fig),
    ("Country Analysis", country_fig),
    ("Release Year Trends", year_fig),
    ("Ratings by Content Type", rating_type_fig)
]

dashboard_parts = []

for title, figure in figures:
    if figure is not None:
        dashboard_parts.append(
            f"<section><h2>{title}</h2>"
            + figure.to_html(
                full_html=False,
                include_plotlyjs="cdn"
            )
            + "</section>"
        )

kpi_cards = f"""
<div class="kpis">
    <div class="card">
        <h3>Total Titles</h3>
        <p>{total_titles:,}</p>
    </div>
    <div class="card">
        <h3>Movies</h3>
        <p>{movie_count:,}</p>
    </div>
    <div class="card">
        <h3>TV Shows</h3>
        <p>{tv_count:,}</p>
    </div>
    <div class="card">
        <h3>Genres</h3>
        <p>{genre_count:,}</p>
    </div>
    <div class="card">
        <h3>Countries</h3>
        <p>{country_count:,}</p>
    </div>
</div>
"""

dashboard_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Netflix Business Intelligence Dashboard</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 0;
    background: #f3f6fb;
    color: #182230;
}}
header {{
    background: #14213d;
    color: white;
    padding: 30px;
    text-align: center;
}}
header h1 {{
    margin-bottom: 8px;
}}
main {{
    max-width: 1400px;
    margin: auto;
    padding: 24px;
}}
.kpis {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}}
.card {{
    background: white;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 3px 12px rgba(0,0,0,0.07);
}}
.card h3 {{
    font-size: 15px;
    color: #526071;
}}
.card p {{
    font-size: 28px;
    font-weight: bold;
    margin: 10px 0;
}}
section {{
    background: white;
    padding: 20px;
    margin-bottom: 24px;
    border-radius: 12px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
}}
h2 {{
    color: #14213d;
}}
footer {{
    text-align: center;
    padding: 20px;
    color: #526071;
}}
</style>
</head>
<body>
<header>
    <h1>Netflix Business Intelligence Dashboard</h1>
    <p>Data Analysis Using Python Internship</p>
    <p>Auspify Technologies | Executive Analytics Report</p>
</header>
<main>
    {kpi_cards}
    {''.join(dashboard_parts)}
    <section>
        <h2>Key Business Insights</h2>
        <ol>
            {''.join(f"<li>{i}</li>" for i in insights)}
        </ol>
    </section>
    <section>
        <h2>Actionable Recommendations</h2>
        <ol>
            {''.join(f"<li>{r}</li>" for r in recommendations)}
        </ol>
    </section>
</main>
<footer>
    Generated using Python, Pandas, Plotly, and Netflix catalog data.
</footer>
</body>
</html>
"""

dashboard_path = REPORT_DIR / "netflix_business_dashboard.html"

dashboard_path.write_text(
    dashboard_html,
    encoding="utf-8"
)

print(f"Interactive dashboard saved: {dashboard_path}")

# Step 11: Generate an executive report

report_date = datetime.now().strftime("%d %B %Y")

report_lines = [
    "# Netflix Business Insights Report",
    "",
    "**Project:** Data Analysis Using Python Internship",
    "",
    "**Organization:** Auspify Technologies",
    "",
    f"**Report generated:** {report_date}",
    "",
    "## 1. Executive Summary",
    "",
    f"This report analyzes {total_titles:,} Netflix catalog records "
    "to understand content distribution, ratings, genres, countries, "
    "and release-year patterns.",
    "",
    "The analysis is descriptive. It identifies patterns in the "
    "supplied dataset and does not independently measure viewing "
    "demand, revenue, profitability, or Netflix production activity.",
    "",
    "## 2. Dataset Overview",
    "",
    f"- Input dataset: `{INPUT_FILE.name}`",
    f"- Original records: {original_rows:,}",
    f"- Records after exact duplicate removal: {len(analysis_df):,}",
    f"- Exact duplicate records detected: {original_duplicates:,}",
    f"- Missing or invalid release years: {invalid_year_count:,}",
    f"- Movies: {movie_count:,}",
    f"- TV Shows: {tv_count:,}",
    f"- Distinct recorded genres: {genre_count:,}",
    f"- Distinct recorded countries: {country_count:,}",
    "",
    "## 3. Data Quality Assessment",
    "",
    "Missing values, column types, and unique values were reviewed. "
    "Exact duplicate rows were removed for the main analysis. "
    "Invalid release years were excluded from year-based analysis.",
    "",
    "Other missing fields were not automatically filled with invented "
    "values. Counts and percentages should be interpreted in light of "
    "the records available for each analysis.",
    "",
    "## 4. Key Business Findings",
    ""
]

report_lines.extend(
    f"{index}. {insight}"
    for index, insight in enumerate(insights, start=1)
)

report_lines.extend([
    "",
    "## 5. Actionable Recommendations",
    ""
])

report_lines.extend(
    f"{index}. {recommendation}"
    for index, recommendation in enumerate(
        recommendations,
        start=1
    )
)

report_lines.extend([
    "",
    "## 6. Dashboard and Deliverables",
    "",
    "The interactive dashboard includes content distribution, "
    "rating analysis, genre rankings, country analysis, release-year "
    "trends, and rating comparisons by content type.",
    "",
    "The exported CSV files provide the underlying summary tables "
    "for further analysis.",
    "",
    "## 7. Limitations",
    "",
    "- Catalog data may not represent every Netflix title.",
    "- Multiple genres and countries can be associated with one title.",
    "- Release year is not the same as production or acquisition year.",
    "- Ratings indicate content classifications, not actual viewer ages.",
    "- The dataset does not establish audience engagement, revenue, "
    "or profitability.",
    "- Recent release years may be incomplete.",
    "",
    "## 8. Conclusion",
    "",
    "This project demonstrates an end-to-end business intelligence "
    "workflow using Python: data validation, exploratory analysis, "
    "content trend analysis, interactive visualization, insight "
    "generation, and executive reporting.",
    "",
    "For stronger strategic decisions, these findings should be "
    "combined with audience engagement, subscription, licensing, "
    "and financial data."
])

report_text = "\n".join(report_lines)

markdown_path = REPORT_DIR / "netflix_executive_report.md"
markdown_path.write_text(report_text, encoding="utf-8")

html_report = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Netflix Executive Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    max-width: 1000px;
    margin: 40px auto;
    padding: 20px;
    line-height: 1.7;
    color: #243047;
}}
h1, h2 {{
    color: #14213d;
}}
h1 {{
    border-bottom: 3px solid #168aad;
    padding-bottom: 12px;
}}
li {{
    margin-bottom: 10px;
}}
</style>
</head>
<body>
<pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">
{report_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}
</pre>
</body>
</html>
"""

html_report_path = REPORT_DIR / "netflix_executive_report.html"

html_report_path.write_text(
    html_report,
    encoding="utf-8"
)

print("\nEXECUTIVE REPORT")
print(report_text)

# Step 12: Export analytical tables

exports = {
    "data_quality_report.csv": quality_report,
    "business_kpi_summary.csv": kpi_data,
    "content_type_summary.csv": type_counts,
    "rating_summary.csv": rating_counts,
    "genre_summary.csv": genre_counts,
    "country_summary.csv": country_counts,
    "yearly_trend_summary.csv": yearly_summary,
    "rating_by_content_type.csv": rating_type_counts
}

for filename, table in exports.items():
    table.to_csv(
        REPORT_DIR / filename,
        index=True if filename == "rating_by_content_type.csv" else False
    )

# Save report insights in JSON for reuse

insight_json_path = REPORT_DIR / "business_insights.json"

insight_json_path.write_text(
    json.dumps(
        {
            "report_date": report_date,
            "dataset": INPUT_FILE.name,
            "total_titles": total_titles,
            "movies": movie_count,
            "tv_shows": tv_count,
            "insights": insights,
            "recommendations": recommendations
        },
        indent=4,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

# Step 13: Create a ZIP package

zip_path = OUTPUT_DIR / "Netflix_Business_Insights_Report.zip"

with zipfile.ZipFile(
    zip_path,
    "w",
    compression=zipfile.ZIP_DEFLATED
) as zip_file:

    for file_path in REPORT_DIR.rglob("*"):
        if file_path.is_file():
            zip_file.write(
                file_path,
                arcname=str(file_path.relative_to(REPORT_DIR))
            )

print("\nTASK 6 COMPLETED SUCCESSFULLY")

print("\nPROJECT DELIVERABLES")
print(f"Interactive dashboard: {dashboard_path}")
print(f"Executive report (Markdown): {markdown_path}")
print(f"Executive report (HTML): {html_report_path}")
print(f"Complete ZIP package: {zip_path}")

print("\nOUTPUT DIRECTORY CONTENTS")

for file_path in sorted(REPORT_DIR.iterdir()):
    if file_path.is_file():
        print(f"{file_path.name} ({file_path.stat().st_size:,} bytes)")

# Step 14: Download the ZIP package in Google Colab

from google.colab import files

files.download(str(zip_path))

print("\nYour complete Task 6 project package is ready.")
