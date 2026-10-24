# TASK 2: CONTENT TYPE ANALYSIS DASHBOARD
# Data Analysis Using Python Internship
# Organization: Auspify Technologies

from common import load_netflix_data, OUTPUT_DIR, save_bar

df = load_netflix_data()
if "type" not in df.columns:
    raise ValueError("Dataset must contain a 'type' column.")

counts = df["type"].fillna("Unknown").value_counts()
total = int(counts.sum())
summary = counts.rename_axis("content_type").reset_index(name="title_count")
summary["percentage"] = (summary["title_count"] / total * 100).round(2) if total else 0
summary.to_csv(OUTPUT_DIR / "task2_content_type_summary.csv", index=False)

print("\nNETFLIX CONTENT TYPE ANALYSIS")
print(summary.to_string(index=False))
print(f"\nTotal titles analysed: {total}")
if not counts.empty:
    print(f"Most common content type: {counts.index[0]} ({counts.iloc[0]} titles)")
save_bar(counts, "Netflix Titles by Content Type", "Content Type",
         "Number of Titles", "task2_content_type_distribution.png")
print(f"\nSummary saved to: {OUTPUT_DIR / 'task2_content_type_summary.csv'}")
