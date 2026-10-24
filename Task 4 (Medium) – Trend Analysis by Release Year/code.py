# TASK 4: TREND ANALYSIS BY RELEASE YEAR
# Data Analysis Using Python Internship
# Organization: Auspify Technologies

from common import load_netflix_data, OUTPUT_DIR, save_line

df = load_netflix_data()
if "release_year" not in df.columns:
    raise ValueError("Dataset must contain a 'release_year' column.")

years = df["release_year"].dropna().astype(int)
counts = years.value_counts().sort_index()
trend = counts.rename_axis("release_year").reset_index(name="title_count")
trend.to_csv(OUTPUT_DIR / "task4_release_year_trend.csv", index=False)

print("\nNETFLIX RELEASE YEAR TREND ANALYSIS")
print(f"Titles with a valid release year: {len(years)}")
if not counts.empty:
    print(f"Most represented release year: {counts.idxmax()} ({counts.max()} titles)")
    print("\nMost represented 10 release years:")
    print(trend.sort_values("title_count", ascending=False).head(10).to_string(index=False))
save_line(counts, "Netflix Titles by Release Year", "Release Year",
          "Number of Titles", "task4_release_year_trend.png")
trend.tail(20).to_csv(OUTPUT_DIR / "task4_recent_20_release_years.csv", index=False)
print(f"\nResults saved to: {OUTPUT_DIR / 'task4_release_year_trend.csv'}")
