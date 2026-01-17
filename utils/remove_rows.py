import pandas as pd


def balance_dataset(file_path, output_path, target_column, target_count=5000):
    """
    Reduces every category in the dataset to a maximum of target_count rows.
    """
    try:
        # 1. Load the dataset
        print(f"Loading {file_path}...")
        df = pd.read_csv(file_path)

        # 2. Apply downsampling per category
        # If a category has > 5000 rows, it samples 5000.
        # If a category has < 5000 rows, it keeps all of them (min logic).
        df_balanced = df.groupby(target_column, group_keys=False).apply(
            lambda x: x.sample(n=min(len(x), target_count), random_state=42)
        )

        # 3. Shuffle the final result so categories are mixed
        df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

        # 4. Print Summary
        print("-" * 30)
        print(f"Original total rows: {len(df)}")
        print(f"New total rows:      {len(df_balanced)}")
        print("\nNew distribution (top 10 categories):")
        print(df_balanced[target_column].value_counts().head(10))
        print("-" * 30)

        # 5. Save the file
        df_balanced.to_csv(output_path, index=False)
        print(f"Success! Balanced dataset saved to: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


# --- Configuration ---
INPUT_FILE = 'code-comment-classification.csv'
OUTPUT_FILE = 'code-comment-classification-downsample.csv'
CATEGORY_COL = 'category'  # Replace with your actual column name

if __name__ == "__main__":
    balance_dataset(INPUT_FILE, OUTPUT_FILE, CATEGORY_COL, target_count=6000)