# TASK 1: NETFLIX DATA CLEANING & PREPARATION
# Data Analysis Using Python Internship
# Compatible with Visual Studio Code

import pandas as pd
from pathlib import Path

print("NETFLIX DATA CLEANING & PREPARATION")
print("Data Analysis Using Python Internship")

# STEP 1: SET FILE PATHS

BASE_DIR = Path("D:/Inten/Dataset.csv").resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = BASE_DIR / "Dataset.csv"

CLEAN_FILE = OUTPUT_DIR / "netflix_cleaned.csv"
QUALITY_FILE = OUTPUT_DIR / "data_quality_report.csv"

# STEP 2: IMPORT DATASET

print("\n[STEP 1] IMPORTING DATASET")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Dataset.csv not found at: {INPUT_FILE}\n"
        "Place Dataset.csv in the same folder as this Python file."
    )

df = pd.read_csv(INPUT_FILE)

print("\nDataset imported successfully!")
print(f"Total records: {len(df):,}")
print(f"Total columns: {len(df.columns)}")

# STANDARDIZE COLUMN NAMES

df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)

print("\nDataset Preview:")
print(df.head().to_string(index=False))

# SAVE ORIGINAL STATISTICS

original_rows = len(df)
original_columns = len(df.columns)
original_missing = int(df.isna().sum().sum())

# STEP 3: HANDLE MISSING VALUES

print("\n[STEP 2] IDENTIFYING MISSING VALUES")

missing_markers = [
    "", "NA", "N/A", "NULL", "null", "None", "nan"
]

for column in df.select_dtypes(
    include=["object", "string"]
).columns:

    df[column] = df[column].astype("string").str.strip()

    df[column] = df[column].replace(
        missing_markers,
        pd.NA
    )

missing_report = pd.DataFrame({
    "Column": df.columns,
    "Missing_Values": [
        int(df[column].isna().sum())
        for column in df.columns
    ],
    "Missing_Percentage": [
        round(df[column].isna().mean() * 100, 2)
        for column in df.columns
    ]
})

print("\nMissing Values Report:")
print(missing_report.to_string(index=False))

# STEP 4: REMOVE DUPLICATES

print("\n[STEP 3] REMOVING DUPLICATES")

duplicates_before = int(df.duplicated().sum())

df = df.drop_duplicates().copy()

duplicate_ids_removed = 0

if "show_id" in df.columns:

    valid_ids = df["show_id"].notna()

    duplicate_ids_removed = int(
        df.loc[valid_ids, "show_id"].duplicated().sum()
    )

    df = pd.concat([
        df.loc[~valid_ids],
        df.loc[valid_ids].drop_duplicates(
            subset=["show_id"],
            keep="first"
        )
    ]).sort_index().copy()

print(f"Duplicate rows removed: {duplicates_before}")
print(f"Duplicate IDs removed: {duplicate_ids_removed}")

# STEP 5: STANDARDIZE IMPORTANT COLUMNS

print("\n[STEP 4] STANDARDIZING DATA")

for column in [
    "country",
    "rating",
    "type",
    "title",
    "director"
]:
    if column in df.columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

# Standardize content type

if "type" in df.columns:
    df["type"] = df["type"].str.title()

# Standardize country formatting

if "country" in df.columns:

    df["country"] = df["country"].apply(
        lambda value: (
            ", ".join(
                part.strip()
                for part in value.split(",")
                if part.strip()
            )
            if pd.notna(value)
            else pd.NA
        )
    )

# Standardize rating labels

if "rating" in df.columns:
    df["rating"] = df["rating"].str.upper()

# Convert release year to numeric

if "release_year" in df.columns:

    df["release_year"] = pd.to_numeric(
        df["release_year"],
        errors="coerce"
    ).astype("Int64")

# Convert date_added to datetime

if "date_added" in df.columns:

    df["date_added"] = pd.to_datetime(
        df["date_added"],
        errors="coerce"
    )

print("Column names standardized.")
print("Country, rating and type formatting checked.")
print("Date and year columns processed.")

# STEP 6: CREATE DATA QUALITY REPORT

print("\nGENERATING DATA QUALITY REPORT")

quality_report = pd.DataFrame({
    "Column": df.columns,

    "Data_Type": [
        str(df[column].dtype)
        for column in df.columns
    ],

    "Missing_Values": [
        int(df[column].isna().sum())
        for column in df.columns
    ],

    "Missing_Percentage": [
        round(df[column].isna().mean() * 100, 2)
        for column in df.columns
    ],

    "Unique_Values": [
        int(df[column].nunique())
        for column in df.columns
    ]
})

quality_report.to_csv(
    QUALITY_FILE,
    index=False
)

print("\nData Quality Report:")
print(quality_report.to_string(index=False))

# STEP 7: EXPORT CLEANED DATASET

print("\n[STEP 5] EXPORTING CLEANED DATASET")

df.to_csv(
    CLEAN_FILE,
    index=False
)

print("Cleaned dataset exported successfully.")

# STEP 8: FINAL SUMMARY

print("\nCLEANING SUMMARY")

print(f"Original records       : {original_rows:,}")
print(f"Cleaned records        : {len(df):,}")
print(f"Original columns       : {original_columns}")
print(f"Duplicate rows removed : {duplicates_before:,}")
print(f"Duplicate IDs removed  : {duplicate_ids_removed:,}")
print(f"Missing cells before   : {original_missing:,}")
print(f"Missing cells after    : {int(df.isna().sum().sum()):,}")

print("\nEXPORTED FILES")

print(f"Cleaned dataset: {CLEAN_FILE}")
print(f"Quality report : {QUALITY_FILE}")

print("\nTASK 1 COMPLETED SUCCESSFULLY!")
