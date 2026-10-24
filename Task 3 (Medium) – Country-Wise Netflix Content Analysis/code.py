# TASK 3: COUNTRY-WISE NETFLIX CONTENT ANALYSIS
# Data Analysis Using Python Internship
# Organization: Auspify Technologies

from common import load_netflix_data, OUTPUT_DIR, save_bar

df = load_netflix_data()
if "country" not in df.columns:
    raise ValueError("Dataset must contain a 'country' column.")

countries = df[["country"]].dropna().copy()
countries["country"] = countries["country"].astype(str).str.split(",")
countries = countries.explode("country")
countries["country"] = countries["country"].str.strip()
countries = countries[countries["country"] != ""]
counts = countries["country"].value_counts()
top = counts.head(15)
top.rename_axis("country").reset_index(name="title_count").to_csv(
    OUTPUT_DIR / "task3_top_countries.csv", index=False
)

print("\nCOUNTRY-WISE NETFLIX CONTENT ANALYSIS")
print("\nTop 15 countries by number of listed titles:")
print(top.rename_axis("country").reset_index(name="title_count").to_string(index=False))
print(f"\nUnique country names counted: {counts.size}")
save_bar(top, "Top 15 Countries by Netflix Titles", "Number of Titles",
         "Country", "task3_top_15_countries.png", horizontal=True, figsize=(10, 7))
print(f"\nResults saved to: {OUTPUT_DIR / 'task3_top_countries.csv'}")

