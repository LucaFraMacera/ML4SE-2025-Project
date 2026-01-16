import csv
import sys
import time
import os
from github import Github, RateLimitExceededException, Auth

# --- CONFIGURATION ---
# Leave empty "" for Anonymous mode (60 req/hr)
# Or paste token "ghp_..." for Authenticated mode (5000 req/hr)
GITHUB_TOKEN = "" 

# How many NEW threads to grab per repo in this run
LIMIT_ISSUES_PER_REPO = 50

# Single output file for all data
OUTPUT_FILE = "github_comments.csv"

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

def get_github_client():
    if GITHUB_TOKEN and "EXAMPLE" not in GITHUB_TOKEN:
        print("Authenticated Mode: Using provided GitHub Token.")
        auth = Auth.Token(GITHUB_TOKEN)
        return Github(auth=auth)
    else:
        print("Anonymous Mode: No token provided.")
        print("Rate Limit is very low (60 req/hr). Expect the script to stop quickly.")
        return Github()

def get_safe_rate_limit(g):
    """Robustly fetches (remaining, limit) as integers."""
    try:
        rate = g.get_rate_limit()
        if hasattr(rate, 'core'):
            return rate.core.remaining, rate.core.limit
        if hasattr(rate, 'rate'):
            return rate.rate.remaining, rate.rate.limit
    except Exception:
        pass
    
    try:
        return g.rate_limiting
    except Exception:
        pass

    return 0, 60

def get_processed_ids(filename):
    """
    Reads the existing CSV to find which (Repo, IssueID) pairs 
    have already been scraped.
    Returns a set of strings: "owner/repo#123"
    """
    processed = set()
    if not os.path.exists(filename):
        return processed

    try:
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row and len(row) > 1:
                    # Row structure: [RepoName, IssueID, ...]
                    repo_name = row[0]
                    try:
                        issue_num = row[1]
                        # Store unique key: "facebook/react#102"
                        processed.add(f"{repo_name}#{issue_num}")
                    except ValueError:
                        pass
    except Exception as e:
        print(f"Warning: Could not read existing file: {e}")
    
    return processed

def scrape_repo(g, repo_name, processed_keys):
    print(f"--- Starting: {repo_name} ---")
    
    try:
        repo = g.get_repo(repo_name)
    except Exception as e:
        print(f"Error accessing {repo_name}: {e}")
        return

    # Check if file exists to determine if we need a header
    file_exists = os.path.exists(OUTPUT_FILE)
    
    # Open in 'a' (append) mode always
    with open(OUTPUT_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write header only if file is brand new
        if not file_exists:
            writer.writerow([
                "Repository", "Issue/PR Number", "Type", "Author", 
                "Date", "Comment Body", "URL"
            ])

        issues = repo.get_issues(state='all')
        count = 0
        
        try:
            for issue in issues:
                # Check if "repo_name#issue_number" is already in our set
                unique_key = f"{repo_name}#{issue.number}"
                if unique_key in processed_keys:
                    continue

                if count >= LIMIT_ISSUES_PER_REPO:
                    break

                # Check Rate Limit
                remaining, limit = get_safe_rate_limit(g)
                if remaining < 5:
                    print(f"!!! Rate limit exhausted ({remaining}/{limit}). Stopping script. !!!")
                    sys.exit(0)

                issue_type = "Pull Request" if issue.pull_request else "Issue"
                print(f"[{repo_name}] Processing {issue_type} #{issue.number}")

                # Write the main body
                if issue.body:
                    writer.writerow([
                        repo_name,
                        issue.number, issue_type, issue.user.login, 
                        issue.created_at, issue.body[:5000], issue.html_url
                    ])

                # Write comments
                for comment in issue.get_comments():
                    writer.writerow([
                        repo_name,
                        issue.number, issue_type, comment.user.login, 
                        comment.created_at, comment.body[:5000], comment.html_url
                    ])
                
                count += 1
                
        except RateLimitExceededException:
            print(f"GitHub Rate Limit Hit during {repo_name}!")
            sys.exit(0)
        except Exception as e:
            print(f"Error processing {repo_name}: {e}")

    print(f"Finished batch for {repo_name}. Appended {count} threads.\n")

def main():
    g = get_github_client()
    
    # Check initial rate limit
    remaining, limit = get_safe_rate_limit(g)
    print(f"API Requests Remaining: {remaining}/{limit}")
    
    if remaining < 10:
        print("Your rate limit is too low to start scraping.")
        return

    # Load history once at the start to prevent re-reading file constantly
    print(f"Scanning {OUTPUT_FILE} for existing data...")
    processed_keys = get_processed_ids(OUTPUT_FILE)
    print(f"Found {len(processed_keys)} processed threads previously saved.")

    for repo_to_scrape in TARGET_REPOS:
        scrape_repo(g, repo_to_scrape, processed_keys)

if __name__ == "__main__":
    main()