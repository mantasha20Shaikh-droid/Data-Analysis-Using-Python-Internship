# TASK 4: TREND ANALYSIS BY RELEASE YEAR
# Data Analysis Using Python Internship
# Organization: Auspify Technologies

from common import load_netflix_data, OUTPUT_DIR, save_bar, save_line
import pandas as pd

df = load_netflix_data()
insights = []
total = len(df)
insights.append(f"Total records in dataset: {total:,}")
insights.append(f"Total columns: {len(df.columns)}")
insights.append(f"Exact duplicate rows: {int(df.duplicated().sum()):,}")

if "show_id" in df.columns:
    insights.append(f"Unique show IDs: {df['show_id'].nunique(dropna=True):,}")

if "type" in df.columns:
    type_counts = df["type"].fillna("Unknown").value_counts()
    for name, count in type_counts.items():
        pct = count / total * 100 if total else 0
        insights.append(f"{name}: {count:,} titles ({pct:.2f}%)")
    save_bar(type_counts, "Business Insight: Content Mix", "Content Type",
             "Titles", "task6_content_mix.png")

if "country" in df.columns:
    countries = df["country"].dropna().astype(str).str.split(",").explode().str.strip()
    countries = countries[countries != ""].value_counts()
    if not countries.empty:
        insights.append(f"Most frequently listed country: {countries.index[0]} ({countries.iloc[0]} title-country listings)")
        countries.head(10).rename_axis("country").reset_index(name="title_count").to_csv(
            OUTPUT_DIR / "task6_top_countries.csv", index=False
        )
        save_bar(countries.head(10), "Business Insight: Top 10 Countries",
                 "Number of Titles", "Country", "task6_top_countries.png",
                 horizontal=True, figsize=(10, 6))

if "release_year" in df.columns:
    years = pd.to_numeric(df["release_year"], errors="coerce").dropna()
    if not years.empty:
        year_counts = years.astype(int).value_counts().sort_index()
        insights.append(f"Most common release year: {int(year_counts.idxmax())} ({int(year_counts.max())} titles)")
        save_line(year_counts, "Business Insight: Release Year Trend",
                  "Release Year", "Titles", "task6_release_year_trend.png")

if "rating" in df.columns:
    ratings = df["rating"].fillna("Unknown").value_counts()
    if not ratings.empty:
        insights.append(f"Most common rating label: {ratings.index[0]} ({ratings.iloc[0]} titles)")
        ratings.rename_axis("rating").reset_index(name="title_count").to_csv(
            OUTPUT_DIR / "task6_rating_summary.csv", index=False
        )

if "duration" in df.columns:
    duration = df["duration"].dropna().astype(str)
    minutes = pd.to_numeric(duration.str.extract(r"(\d+)\s*min", expand=False), errors="coerce")
    seasons = pd.to_numeric(duration.str.extract(r"(\d+)\s*Season", expand=False), errors="coerce")
    if minutes.notna().any():
        insights.append(f"Average movie duration (where parseable): {minutes.mean():.1f} minutes")
    if seasons.notna().any():
        insights.append(f"Average seasons for TV shows (where parseable): {seasons.mean():.2f}")

if "date_added" in df.columns:
    added = df["date_added"].dropna()
    if not added.empty:
        added_years = added.dt.year.value_counts().sort_index()
        added_years.rename_axis("date_added_year").reset_index(name="titles_added").to_csv(
            OUTPUT_DIR / "task6_added_by_year.csv", index=False
        )
        insights.append(f"Year with most recorded additions: {int(added_years.idxmax())} ({int(added_years.max())} titles)")
        save_line(added_years, "Titles Added to Netflix by Year", "Year Added",
                  "Titles Added", "task6_added_by_year.png")

report = [
    "NETFLIX ADVANCED BUSINESS INSIGHTS REPORT",
    "",
    "Purpose: Summarize high-level patterns in the supplied Netflix dataset.",
    "Important: Descriptive patterns do not prove business causation.",
    "",
    "KEY FINDINGS",
]
report.extend(f"- {item}" for item in insights)
report.extend([
    "",
    "POSSIBLE BUSINESS INTERPRETATIONS",
    "- Content type mix describes the balance between movies and TV shows.",
    "- Country listings identify countries frequently represented in the catalogue.",
    "- Release-year trends describe catalogue age, not when Netflix acquired titles.",
    "- Ratings and genres summarize content classifications and categories.",
    "",
    "LIMITATIONS",
    "- Country and genre fields may contain multiple comma-separated values per title.",
    "- Missing or inconsistent source records can affect counts.",
    "- This dataset alone does not provide viewership, revenue, subscriber, or engagement data.",
    "",
    "RECOMMENDED NEXT STEPS",
    "- Review missing values and duplicate records before drawing conclusions.",
    "- Combine with viewing, subscription, and regional revenue data before investment decisions.",
    "- Include generated charts and CSV summaries in the final internship report."
])
report_text = "\n".join(report)
(OUTPUT_DIR / "task6_business_insights_report.txt").write_text(report_text, encoding="utf-8")
print(report_text)
print(f"\nReport saved to: {OUTPUT_DIR / 'task6_business_insights_report.txt'}")
