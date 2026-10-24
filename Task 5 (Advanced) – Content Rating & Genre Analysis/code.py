# Task 5: Content Rating and Genre Analysis
# Data Analysis Using Python Internship
# Organization: Auspify Technologies

from common import load_netflix_data, OUTPUT_DIR, save_bar

df = load_netflix_data()

if "rating" in df.columns:
    rating_counts = df["rating"].fillna("Unknown").value_counts()
    rating_counts.rename_axis("rating").reset_index(name="title_count").to_csv(
        OUTPUT_DIR / "task5_rating_distribution.csv", index=False
    )
    print("\nCONTENT RATING DISTRIBUTION")
    print(rating_counts.head(15).rename_axis("rating").reset_index(name="title_count").to_string(index=False))
    save_bar(rating_counts.head(15), "Netflix Content Ratings (Top 15)",
             "Rating", "Number of Titles", "task5_rating_distribution.png")
else:
    print("No 'rating' column found; rating analysis skipped.")

if "listed_in" in df.columns:
    genres = df[["listed_in"]].dropna().copy()
    genres["listed_in"] = genres["listed_in"].astype(str).str.split(",")
    genres = genres.explode("listed_in")
    genres["listed_in"] = genres["listed_in"].str.strip()
    genres = genres[genres["listed_in"] != ""]
    genre_counts = genres["listed_in"].value_counts()
    genre_counts.head(20).rename_axis("genre").reset_index(name="title_count").to_csv(
        OUTPUT_DIR / "task5_top_genres.csv", index=False
    )
    print("\nTOP 20 GENRES")
    print(genre_counts.head(20).rename_axis("genre").reset_index(name="title_count").to_string(index=False))
    save_bar(genre_counts.head(15), "Top 15 Netflix Genres", "Genre",
             "Number of Titles", "task5_top_genres.png", horizontal=True, figsize=(10, 7))
else:
    print("No 'listed_in' column found; genre analysis skipped.")

print(f"\nOutputs saved in: {OUTPUT_DIR}")
