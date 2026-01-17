import pandas as pd
import os

# --- CONFIGURATION ---
ORIGINAL_FILE = "code-comment-classification-original.csv"  # The existing dataset
NEW_DATA_FILE = "classified_comments_dataset.csv"       # The new data you just generated
OUTPUT_FILE   = "code-comment-classification_extended.csv" # The final merged file

def main():
    # Check if files exist
    if not os.path.exists(ORIGINAL_FILE):
        print(f"Error: Could not find '{ORIGINAL_FILE}'")
        return
    if not os.path.exists(NEW_DATA_FILE):
        print(f"Error: Could not find '{NEW_DATA_FILE}'")
        return

    print("Reading files...")
    try:
        df_orig = pd.read_csv(ORIGINAL_FILE)
        df_new = pd.read_csv(NEW_DATA_FILE)
    except Exception as e:
        print(f"Error reading CSVs: {e}")
        return

    print(f"Original dataset: {len(df_orig)} rows")
    print(f"New dataset:      {len(df_new)} rows")

    # Re-index IDs to prevent duplicates
    # We find the highest ID in the original file and add it to the new IDs
    if 'comment_sentence_id' in df_orig.columns and 'comment_sentence_id' in df_new.columns:
        max_id = df_orig['comment_sentence_id'].max()
        print(f"   -> Re-indexing new rows starting from ID {max_id + 1}...")
        
        # Assuming the new IDs started at 1, we just add the max_id to them.
        # If they aren't sequential, we can also strictly reset them:
        # df_new['comment_sentence_id'] = range(max_id + 1, max_id + 1 + len(df_new))
        df_new['comment_sentence_id'] = df_new['comment_sentence_id'] + max_id
    else:
        print("Warning: 'comment_sentence_id' column missing. Appending without re-indexing.")

    # Concatenate (Append)
    # ignore_index=True resets the Pandas index, but we rely on our 'comment_sentence_id' column
    df_combined = pd.concat([df_orig, df_new], ignore_index=True)

    # Save to new file
    df_combined.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSuccess! Merged file saved as: {OUTPUT_FILE}")
    print(f"Total rows: {len(df_combined)}")
    print("Preview of the join point:")
    
    # Show the last 2 rows of original and first 2 rows of new to verify ID continuity
    print(df_combined.iloc[len(df_orig)-2 : len(df_orig)+2].to_string())

if __name__ == "__main__":
    main()