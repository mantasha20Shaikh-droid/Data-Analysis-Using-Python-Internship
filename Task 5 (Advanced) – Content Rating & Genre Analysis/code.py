# Task 5: Content Rating and Genre Analysis
# Data Analysis Using Python Internship
# Organization: Auspify Technologies

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path
from IPython.display import display, Markdown

# Configure visualizations

sns.set_theme(style="whitegrid", context="notebook")

BASE_DIR = Path("/content")
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

print("TASK 5: CONTENT RATING AND GENRE ANALYSIS")
print("Netflix Audience Insights Dashboard")

# Step 1: Load the Netflix dataset

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
        "or run Task 1 to generate netflix_cleaned.csv."
    )

df = pd.read_csv(INPUT_FILE)

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
    raise ValueError("The dataset is empty.")

required_columns = ["rating", "listed_in", "type"]
missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Required columns are missing: {missing_columns}"
    )

# Step 2: Clean rating, genre, and content type

print("\nSTEP 1: ANALYZING RATING CATEGORIES")

missing_markers = [
    "", "NA", "N/A", "NULL", "None", "nan"
]

for col in ["rating", "listed_in", "type"]:
    df[col] = (
        df[col]
        .astype("string")
        .str.strip()
        .replace(missing_markers, pd.NA)
    )

df["type"] = df["type"].str.title()

# Correct common spacing inconsistencies in rating labels
df["rating"] = (
    df["rating"]
    .str.upper()
    .str.replace(r"\s+", " ", regex=True)
)

missing_ratings = int(df["rating"].isna().sum())
missing_genres = int(df["listed_in"].isna().sum())

print(f"Missing rating values: {missing_ratings:,}")
print(f"Missing genre values: {missing_genres:,}")

# Exclude missing ratings from rating analysis
rating_df = df[df["rating"].notna()].copy()

rating_counts = (
    rating_df["rating"]
    .value_counts()
    .rename_axis("Rating")
    .reset_index(name="Total_Titles")
)

rating_counts["Percentage"] = (
    rating_counts["Total_Titles"]
    / rating_counts["Total_Titles"].sum() * 100
).round(2)

print("\nRating distribution")
display(rating_counts)

# Interactive chart: rating distribution

rating_fig = px.bar(
    rating_counts,
    x="Rating",
    y="Total_Titles",
    color="Rating",
    text="Total_Titles",
    title="Netflix Content Rating Distribution",
    labels={
        "Rating": "Content Rating",
        "Total_Titles": "Number of Titles"
    },
    template="plotly_white"
)

rating_fig.update_traces(
    textposition="outside"
)

rating_fig.update_layout(
    showlegend=False,
    title_x=0.5,
    xaxis_title="Content Rating",
    yaxis_title="Number of Titles"
)

rating_fig.show()

rating_chart_path = OUTPUT_DIR / "content_rating_distribution.html"

rating_fig.write_html(str(rating_chart_path))

# Step 3: Identify the most common genres

print("\nSTEP 2: IDENTIFYING THE MOST COMMON GENRES")

genre_df = df[df["listed_in"].notna()].copy()

# Each title can have multiple genres.
# Split genres so each genre can be counted separately.

genre_df["Genre"] = genre_df["listed_in"].str.split(",")

genre_df = genre_df.explode("Genre")

genre_df["Genre"] = (
    genre_df["Genre"]
    .astype("string")
    .str.strip()
)

genre_df = genre_df[
    genre_df["Genre"].notna()
    & genre_df["Genre"].ne("")
].copy()

# Count each title once per genre
if "show_id" in genre_df.columns:
    genre_df = genre_df.drop_duplicates(
        subset=["show_id", "Genre"]
    )
else:
    genre_df = genre_df.drop_duplicates(
        subset=["title", "type", "release_year", "Genre"]
        if {"title", "type", "release_year"}.issubset(genre_df.columns)
        else ["title", "Genre"]
    )

genre_counts = (
    genre_df["Genre"]
    .value_counts()
    .rename_axis("Genre")
    .reset_index(name="Total_Titles")
)

genre_counts["Percentage"] = (
    genre_counts["Total_Titles"]
    / genre_counts["Total_Titles"].sum() * 100
).round(2)

top_genres = genre_counts.head(15).sort_values(
    "Total_Titles",
    ascending=True
)

print("\nTOP 15 MOST COMMON GENRES")

display(
    genre_counts.head(15).style.format({
        "Total_Titles": "{:,.0f}",
        "Percentage": "{:.2f}%"
    })
)

# Interactive chart: popular genres

genre_fig = px.bar(
    top_genres,
    x="Total_Titles",
    y="Genre",
    orientation="h",
    text="Total_Titles",
    color="Total_Titles",
    color_continuous_scale="Blues",
    title="Top 15 Netflix Genres",
    labels={
        "Total_Titles": "Number of Titles",
        "Genre": "Genre"
    },
    template="plotly_white"
)

genre_fig.update_traces(
    textposition="outside"
)

genre_fig.update_layout(
    title_x=0.5,
    yaxis_title="Genre",
    xaxis_title="Number of Titles"
)

genre_fig.show()

genre_chart_path = OUTPUT_DIR / "top_netflix_genres.html"

genre_fig.write_html(str(genre_chart_path))

# Step 4: Compare ratings across Movies and TV Shows

print("\nSTEP 3: COMPARING RATINGS ACROSS CONTENT TYPES")

comparison_df = df[
    df["rating"].notna()
    & df["type"].isin(["Movie", "TV Show"])
].copy()

rating_comparison = pd.crosstab(
    comparison_df["rating"],
    comparison_df["type"]
)

# Ensure both content types appear as columns
for content_type in ["Movie", "TV Show"]:
    if content_type not in rating_comparison.columns:
        rating_comparison[content_type] = 0

rating_comparison = rating_comparison[
    ["Movie", "TV Show"]
]

print("\nRating comparison table")
display(rating_comparison)

# Interactive stacked bar chart

comparison_long = (
    rating_comparison
    .reset_index()
    .melt(
        id_vars="rating",
        var_name="Content_Type",
        value_name="Total_Titles"
    )
)

comparison_fig = px.bar(
    comparison_long,
    x="rating",
    y="Total_Titles",
    color="Content_Type",
    barmode="group",
    text="Total_Titles",
    title="Content Ratings: Movies vs TV Shows",
    labels={
        "rating": "Content Rating",
        "Total_Titles": "Number of Titles",
        "Content_Type": "Content Type"
    },
    template="plotly_white"
)

comparison_fig.update_layout(
    title_x=0.5,
    xaxis_title="Content Rating",
    yaxis_title="Number of Titles"
)

comparison_fig.show()

comparison_chart_path = (
    OUTPUT_DIR / "rating_movie_tv_comparison.html"
)

comparison_fig.write_html(str(comparison_chart_path))

# Step 5: Compare genres across content types

print("\nSTEP 4: ANALYZING GENRES BY CONTENT TYPE")

genre_type_counts = (
    genre_df[
        genre_df["type"].isin(["Movie", "TV Show"])
    ]
    .groupby(["Genre", "type"])
    .size()
    .reset_index(name="Total_Titles")
)

top_10_genres = genre_counts.head(10)["Genre"]

genre_type_top10 = genre_type_counts[
    genre_type_counts["Genre"].isin(top_10_genres)
].copy()

genre_type_fig = px.bar(
    genre_type_top10,
    x="Genre",
    y="Total_Titles",
    color="type",
    barmode="group",
    title="Top Genres: Movies vs TV Shows",
    labels={
        "Genre": "Genre",
        "Total_Titles": "Number of Titles",
        "type": "Content Type"
    },
    template="plotly_white"
)

genre_type_fig.update_layout(
    title_x=0.5,
    xaxis_title="Genre",
    yaxis_title="Number of Titles",
    xaxis_tickangle=-35
)

genre_type_fig.show()

genre_type_chart_path = (
    OUTPUT_DIR / "genre_movie_tv_comparison.html"
)

genre_type_fig.write_html(str(genre_type_chart_path))

# Step 6: Create an audience insights summary

print("\nSTEP 5: GENERATING AUDIENCE INSIGHTS")

top_rating = rating_counts.iloc[0]["Rating"]
top_rating_count = int(rating_counts.iloc[0]["Total_Titles"])
top_rating_percentage = float(
    rating_counts.iloc[0]["Percentage"]
)

top_genre = genre_counts.iloc[0]["Genre"]
top_genre_count = int(genre_counts.iloc[0]["Total_Titles"])

movie_count = int(
    (df["type"] == "Movie").sum()
)

tv_count = int(
    (df["type"] == "TV Show").sum()
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

insights = [
    "NETFLIX CONTENT RATING AND GENRE ANALYSIS",
    "",
    "DATASET OVERVIEW",
    f"Dataset file: {INPUT_FILE.name}",
    f"Total dataset records: {len(df):,}",
    f"Movies: {movie_count:,} ({movie_percentage:.2f}% of known content types)",
    f"TV Shows: {tv_count:,} ({tv_percentage:.2f}% of known content types)",
    f"Records with missing ratings: {missing_ratings:,}",
    f"Records with missing genres: {missing_genres:,}",
    "",
    "RATING INSIGHTS",
    f"Most common rating: {top_rating}",
    f"Titles with this rating: {top_rating_count:,}",
    f"Share of titles with known ratings: {top_rating_percentage:.2f}%",
    "",
    "GENRE INSIGHTS",
    f"Most common genre: {top_genre}",
    f"Titles associated with this genre: {top_genre_count:,}",
    "",
    "BUSINESS INTERPRETATION",
    "The rating distribution describes the content classifications",
    "recorded in the supplied Netflix dataset.",
    "",
    "Genre counts show how frequently genres are associated with titles.",
    "A title can belong to multiple genres, so genre totals overlap.",
    "",
    "Ratings can help describe the intended age suitability of content.",
    "However, ratings and genres alone do not establish actual viewer",
    "age, personal preferences, popularity, or viewing behavior.",
    "",
    "RECOMMENDATIONS",
    "1. Compare content ratings across Movies and TV Shows.",
    "2. Explore genre preferences by country and release year.",
    "3. Investigate missing rating and genre information.",
    "4. Combine these findings with audience and viewing data",
    "   before making decisions about audience demand."
]

report_text = "\n".join(insights)

print("\n" + report_text)

# Step 7: Export analysis results

print("\nEXPORTING ANALYSIS RESULTS")

rating_csv_path = OUTPUT_DIR / "netflix_rating_summary.csv"
genre_csv_path = OUTPUT_DIR / "netflix_genre_summary.csv"
comparison_csv_path = OUTPUT_DIR / "netflix_rating_type_comparison.csv"
genre_type_csv_path = OUTPUT_DIR / "netflix_genre_type_comparison.csv"
report_path = OUTPUT_DIR / "netflix_rating_genre_business_report.txt"

rating_counts.to_csv(rating_csv_path, index=False)
genre_counts.to_csv(genre_csv_path, index=False)
rating_comparison.to_csv(comparison_csv_path)
genre_type_counts.to_csv(genre_type_csv_path, index=False)

report_path.write_text(
    report_text,
    encoding="utf-8"
)

print("\nTASK 5 COMPLETED SUCCESSFULLY")

print("\nGENERATED FILES")

for file_path in [
    rating_csv_path,
    genre_csv_path,
    comparison_csv_path,
    genre_type_csv_path,
    rating_chart_path,
    genre_chart_path,
    comparison_chart_path,
    genre_type_chart_path,
    report_path
]:
    print(file_path)

# Step 8: Download deliverables in Google Colab

from google.colab import files

download_files = [
    rating_csv_path,
    genre_csv_path,
    comparison_csv_path,
    genre_type_csv_path,
    rating_chart_path,
    genre_chart_path,
    comparison_chart_path,
    genre_type_chart_path,
    report_path
]

print("\nPreparing downloads...")

for file_path in download_files:
    files.download(str(file_path))

print("\nAll Task 5 deliverables have been generated.")
