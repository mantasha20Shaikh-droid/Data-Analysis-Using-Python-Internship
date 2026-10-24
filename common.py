from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Dataset.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
CHART_DIR = BASE_DIR / "charts"

def load_netflix_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset.csv not found: {DATA_FILE}\n"
            "Place Dataset.csv in the same folder as the Python scripts."
        )
    df = pd.read_csv(DATA_FILE)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].replace(r"^\s*$", pd.NA, regex=True)
    if "date_added" in df.columns:
        df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    if "release_year" in df.columns:
        df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")
    OUTPUT_DIR.mkdir(exist_ok=True)
    CHART_DIR.mkdir(exist_ok=True)
    return df

def save_bar(series, title, xlabel, ylabel, filename, horizontal=False, figsize=(10, 6)):
    series = series.dropna()
    if series.empty:
        print(f"No data available for chart: {title}")
        return
    plt.figure(figsize=figsize)
    if horizontal:
        series.sort_values().plot(kind="barh")
    else:
        series.plot(kind="bar")
        plt.xticks(rotation=35, ha="right")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    path = CHART_DIR / filename
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Chart saved: {path}")

def save_line(series, title, xlabel, ylabel, filename):
    series = series.dropna()
    if series.empty:
        print(f"No data available for chart: {title}")
        return
    plt.figure(figsize=(10, 5))
    series.plot(kind="line", marker="o")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    path = CHART_DIR / filename
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Chart saved: {path}")
