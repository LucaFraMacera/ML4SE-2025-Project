"""
Script: Convert Raw Source Comments to Classified Dataset
=========================================================

Purpose:
    This script transforms a raw CSV of source code comments (scraped from repositories)
    into a structured, classified dataset suitable for training or evaluating 
    machine learning models (specifically formatted for code comment classification tasks).

Input:
    - A CSV file (e.g., 'source_code_comments.csv') with columns:
      [Repository, File Path, Extension, Line Number, Comment Content]

Output:
    - A new CSV file (e.g., 'classified_comments_dataset.csv') with columns:
      [comment_sentence_id, class, comment_sentence, partition, instance_type, category]

How it Works:
    1. **Data Cleaning**: 
       - It converts file paths (e.g., 'src/utils/Dangerfile.js') into simpler 
         class identifiers (e.g., 'Dangerfile') to populate the 'class' column.
    
    2. **Heuristic Classification**:
       - Instead of using a complex AI model, it uses a Rule-Based Classifier 
         (Regular Expressions) to automatically tag comments into 5 categories:
         
         * 'Parameters': Comments defining types, arguments, or return values 
           (e.g., matches words like '@param', 'string', 'int').
         * 'DevelopmentNotes': Internal dev notes, Todos, warnings, or rationale 
           (e.g., matches 'TODO', 'fixme', 'why', 'deprecated').
         * 'Usage': Instructions on how to use code 
           (e.g., matches 'use', 'run', 'example', 'import').
         * 'Expand': Elaborations or detailed lists 
           (e.g., matches 'i.e.', 'specifically', 'include').
         * 'Summary': The default category for general descriptions if no other keywords match.

    3. **Dataset Partitioning**:
       - It assigns a 'partition' value of 0 (Train) or 1 (Test) randomly, 
         aiming for an 80/20 split.

    4. **ID Generation**:
       - Generates a unique sequential 'comment_sentence_id' for every row.
"""

import pandas as pd
import random
import re
import os
import sys

# --- CONFIGURATION ---
INPUT_FILE = "source_code_comments.csv"
OUTPUT_FILE = "../datasets/classified_comments_dataset.csv"

# Classification Keywords (Heuristic Rules)
# We check these in order. If a match is found, we assign that class.
KEYWORDS = {
    'Parameters': [
        r'\bparam\b', r'\b@param\b', r'\bargs\b', r'\barguments\b', 
        r'\breturn\b', r'\b@return\b', r'\btype\b', r'\bstring\b', 
        r'\bint\b', r'\bboolean\b', r'\bobject\b', r'\bnull\b'
    ],
    'Usage': [
        r'\buse\b', r'\bcall\b', r'\brun\b', r'\bexample\b', r'\bsee\b', 
        r'\bcommand\b', r'\binstall\b', r'\btry\b', r'\bcode\b', 
        r'\bconst\b', r'\bvar\b', r'\bimport\b', r'\bhttp\b'
    ],
    'DevelopmentNotes': [
        r'\btodo\b', r'\bfixme\b', r'\bugly\b', r'\bhack\b', r'\bworkaround\b',
        r'\bnote\b', r'\bwarning\b', r'\bdeprecated\b', r'\blimit\b', 
        r'\bcopyright\b', r'\blicense\b', r'\bauthor\b', r'\bwhy\b', 
        r'\bbecause\b', r'\bfix\b', r'\bissue\b', r'\bbug\b', r'\bremove\b'
    ],
    'Expand': [
        r'\bi\.e\.\b', r'\be\.g\.\b', r'\bspecifically\b', r'\bdetail\b', 
        r'\binclude\b', r'\bcontain\b', r'\balso\b', r'\bfurther\b', 
        r'\bmeaning\b', r'\bor\b', r'\band\b'
    ],
    # 'Summary' is the default/fallback
}

def classify_comment(text):
    """
    Classifies a comment string into Usage, Parameters, Expand, 
    DevelopmentNotes, or Summary.
    """
    text_lower = str(text).lower()
    
    # Parameters (Specific variable descriptions)
    for pattern in KEYWORDS['Parameters']:
        if re.search(pattern, text_lower):
            return 'Parameters'
            
    # DevelopmentNotes (Internal dev chatter, todos, warnings, rationale)
    for pattern in KEYWORDS['DevelopmentNotes']:
        if re.search(pattern, text_lower):
            return 'DevelopmentNotes'

    # Usage (How to run/call/import)
    for pattern in KEYWORDS['Usage']:
        if re.search(pattern, text_lower):
            return 'Usage'
            
    # Expand (Elaboration, details, lists)
    for pattern in KEYWORDS['Expand']:
        if re.search(pattern, text_lower):
            return 'Expand'
            
    # Summary (General description, default)
    return 'Summary'

def clean_class_name(file_path):
    """Converts 'src/utils/AccessMixin.js' -> 'AccessMixin'"""
    filename = os.path.basename(file_path)
    name, _ = os.path.splitext(filename)
    return name

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Could not find {INPUT_FILE}")
        return

    print("Reading input CSV...")
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    total_rows = len(df)
    print(f"Loaded {total_rows} comments. Processing...")
    
    output_rows = []
    
    for index, row in df.iterrows():
        # Update progress every 100 rows (or 10% if file is small)
        if (index + 1) % 100 == 0:
            percent = ((index + 1) / total_rows) * 100
            sys.stdout.write(f"\r   -> Processed {index + 1}/{total_rows} comments ({percent:.1f}%)")
            sys.stdout.flush()

        comment_content = row.get('Comment Content', '')
        file_path = row.get('File Path', 'Unknown')
        
        # ID
        cid = index + 1
        
        # Class Name
        class_name = clean_class_name(file_path)
        
        # Partition (80/20 Split)
        partition = 0 if random.random() > 0.2 else 1
        
        # Instance Type
        instance_type = 1
        
        # Category (New Classification Logic)
        category = classify_comment(comment_content)
        
        output_rows.append({
            'comment_sentence_id': cid,
            'class': class_name,
            'comment_sentence': comment_content,
            'partition': partition,
            'instance_type': instance_type,
            'category': category
        })
    
    # Clear the progress line
    print("\nProcessing complete. Saving file...")

    new_df = pd.DataFrame(output_rows)
    new_df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"Success! Saved {len(new_df)} rows to {OUTPUT_FILE}")
    print("\nPreview of the first 5 rows:")
    print(new_df[['class', 'category', 'comment_sentence']].head(5).to_string())

if __name__ == "__main__":
    main()