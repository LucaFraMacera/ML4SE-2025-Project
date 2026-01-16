import csv
import os
import shutil
import subprocess
import re

# --- CONFIGURATION ---
OUTPUT_FILE = "source_code_comments.csv"

# Extensions to scan and their comment patterns
# (We focus on single-line comments for accurate line numbering)
FILE_TYPES = {
    '.py':   {'single': r'#\s*(.*)'},
    '.js':   {'single': r'//\s*(.*)'},
    '.ts':   {'single': r'//\s*(.*)'},
    '.jsx':  {'single': r'//\s*(.*)'},
    '.tsx':  {'single': r'//\s*(.*)'},
    '.java': {'single': r'//\s*(.*)'},
    '.c':    {'single': r'//\s*(.*)'},
    '.cpp':  {'single': r'//\s*(.*)'},
    '.h':    {'single': r'//\s*(.*)'},
}

TARGET_REPOS = [
    "facebook/react",
    "tensorflow/tensorflow",
    "twbs/bootstrap",
    "microsoft/vscode",
    "torvalds/linux",
    "vuejs/vue",
    "flutter/flutter",
    "ohmyzsh/ohmyzsh",
    "airbnb/javascript"
]

def get_processed_repos(filename):
    """Checks which repos are already fully scanned."""
    processed = set()
    if not os.path.exists(filename):
        return processed
    
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            next(reader, None) # Skip header
            for row in reader:
                if row:
                    processed.add(row[0]) # Column 0 is Repository Name
    except:
        pass
    return processed

def clone_repo(repo_name):
    """Clones a repo to a temp folder using git (shallow clone)."""
    repo_url = f"https://github.com/{repo_name}.git"
    temp_dir = f"temp_{repo_name.replace('/', '_')}"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
    print(f"   -> Cloning {repo_name}...")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, temp_dir],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return temp_dir
    except subprocess.CalledProcessError:
        print(f"   !!! Error cloning {repo_name}. Skipping.")
        return None

def extract_comments_from_file(file_path, extension):
    """Reads a file and finds comments based on its extension."""
    comments = []
    pattern = FILE_TYPES[extension]['single']
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            # Regex search for the comment pattern
            match = re.search(pattern, line)
            if match:
                # Group 1 is the content after the comment symbol (# or //)
                comment_content = match.group(1).strip()
                if comment_content: # Ignore empty comments
                    comments.append((i + 1, comment_content))
                    
    except Exception as e:
        # Skip files that can't be read (binary, etc.)
        pass
        
    return comments

def process_repo(repo_name, temp_dir, writer):
    """Walks through the cloned repo and scrapes comments."""
    print(f"   -> Scanning files in {repo_name}...")
    file_count = 0
    comment_count = 0
    
    for root, dirs, files in os.walk(temp_dir):
        # Skip hidden folders like .git
        if '.git' in dirs:
            dirs.remove('.git')
            
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            
            if ext in FILE_TYPES:
                full_path = os.path.join(root, file)
                # content_path is the relative path (e.g., src/index.js)
                rel_path = os.path.relpath(full_path, temp_dir)
                
                found_comments = extract_comments_from_file(full_path, ext)
                
                for line_num, content in found_comments:
                    writer.writerow([
                        repo_name,
                        rel_path,
                        ext,
                        line_num,
                        content
                    ])
                    comment_count += 1
                
                file_count += 1
                
    print(f"   -> Done. Found {comment_count} comments in {file_count} files.")

def main():
    # Setup CSV
    file_exists = os.path.exists(OUTPUT_FILE)
    processed_repos = get_processed_repos(OUTPUT_FILE)
    
    mode = 'a' if file_exists else 'w'
    
    with open(OUTPUT_FILE, mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        if not file_exists:
            writer.writerow(["Repository", "File Path", "Extension", "Line Number", "Comment Content"])

        for repo in TARGET_REPOS:
            print(f"--- Processing: {repo} ---")
            
            if repo in processed_repos:
                print(f"   -> Already processed. Skipping.")
                continue
            
            # Clone
            temp_dir = clone_repo(repo)
            if not temp_dir:
                continue
            
            # Process
            process_repo(repo, temp_dir, writer)
            
            # Cleanup
            print(f"   -> Cleaning up...")
            shutil.rmtree(temp_dir)
            print(f"--- Finished {repo} ---\n")

if __name__ == "__main__":
    main()