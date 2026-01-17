def extract_metadata_features(df):
    """Extract metadata features from comment text"""
    # 1. Comment length (number of words)
    df['comment_length'] = df['comment_sentence'].str.split().str.len()
    # 2. Has parameter-related keywords
    param_keywords = ['param', 'parameter', 'arg', 'argument', 'int', 'str', 'bool', 'float', 'list', 'dict', 'type']
    param_pattern = '|'.join(param_keywords)
    df['has_params'] = df['comment_sentence'].str.contains(param_pattern, case=False, regex=True, na=False).astype(int)
    # 3. Has code symbols
    code_symbols = [r'\(', r'\)', r'\[', r'\]', r'\{', r'\}', r'_', r'\.']
    code_pattern = '|'.join(code_symbols)
    df['has_code_symbols'] = df['comment_sentence'].str.contains(code_pattern, regex=True, na=False).astype(int)
    # 4. Starts with common action verbs
    action_verbs = ['returns', 'return', 'creates', 'create', 'provides', 'provide', 'handles', 'handle',
                    'implements', 'implement', 'executes', 'execute', 'generates', 'generate',
                    'validates', 'validate', 'processes', 'process', 'manages', 'manage']
    verb_pattern = '^(' + '|'.join(action_verbs) + ')'
    df['starts_with_verb'] = df['comment_sentence'].str.contains(verb_pattern, case=False, regex=True, na=False).astype(
        int)
    # 5. Mentions default values
    df['has_default'] = df['comment_sentence'].str.contains('default', case=False, na=False).astype(int)

    return df