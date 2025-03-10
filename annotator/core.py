import pandas as pd
from collections import Counter

SCORE_CUTOFF = 0.1
LIMIT = 5

def load_sheet(file_path, sheet_name=None):
    """
    Load the sheet from the Excel file
    
    Remove columns up to and including the first column with purely numeric data so
    that data of the form:

      | A  | B | C | D | E | F | G ...
    0 | .. | ..| ..| ..| ..| ..| .. ...
    1 | .. | ..| ..| ..| ..| ..| .. ...
    2 | .. | ..| ..| ..| ..| ..| .. ...
    ...

    is loaded even if it is not aligned exactly to the left.
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name or 'Integ summary')
    
    # Find first column with purely numeric data or NaN
    start_idx = None
    length = 0
    for col in df.columns:
        data = pd.to_numeric(df[col], errors='coerce')
        if all(isinstance(item, (int, float)) for item in data.to_list()) and not data.isna().all():
            start_idx = df.columns.get_loc(col)
            length = data.isna().idxmax() if data.isna().any() else len(data)
            break
    
    # Remove columns up to and including start_idx
    if start_idx is not None:
        df = df.iloc[:, start_idx + 1:]
    df = df.iloc[:length]

    return df

def load_reference(file_path, sheet_name=None):
    """
    Load the reference sheet from the Excel file

    The reference sheet must be of the form:

    | Cell type 1       | Cell type 1    | Cell type 2       | Cell type 2    | ...
    | Wilcoxon Ordering | Other ordering | Wilcoxon Ordering | Other ordering | ...
    ...

    The first column contains the cell type labels, and the remaining
    columns contain the number of integrations for each cell type.
    """
    reference = pd.read_excel(file_path, sheet_name=sheet_name)
    reference = reference.iloc[:, ::2]
    return reference

def _get_gene_counts(df):
    """
    Create a count for all genes in the dataframe
    """
    return Counter(df.values.flatten())

def _create_marker_potential_matrix(reference, counts): 
    """
    Create a matrix of the form:

              | Cell type 1 | Cell type 2 | ...
    Gene 1    | Marker potential
    Gene 2    | 
    ...
    """
    result_matrix = pd.DataFrame(0, index=counts.keys(), columns=reference.columns, dtype=float)
    for col in reference.columns:
        for idx, value in enumerate(reference[col]):
            if pd.notna(value):
                result_matrix.loc[str(value), col] = 1 / (1 + idx) / counts[value]
    return result_matrix

def _create_top_gene_scores(weightings, result_matrix, match_matrix, limit, level):
    """
    Create a dictionary of dataframes with top matching cell types and their top 10 gene scores.
    """
    limit = limit or weightings.shape[1]
    results = {}
    for col in weightings.columns:
        col_sorted = weightings[col].sort_values(ascending=False)
        col_filtered = col_sorted[col_sorted >= SCORE_CUTOFF].head(LIMIT)
        top_gene_scores_df = pd.DataFrame()
        max_genes = 0
        for match in col_filtered.index:
            scores = match_matrix[col] * result_matrix[match] * 100
            top_genes = scores.sort_values(ascending=False)
            top_genes = top_genes[top_genes > level].head(limit)
            formatted_genes = [f"{gene} ({score:.2f})" for gene, score in top_genes.items()]
            match_series = pd.Series(formatted_genes, name=match)
            match_series = match_series.reindex(range(limit), fill_value="")
            top_gene_scores_df = pd.concat([top_gene_scores_df, match_series], axis=1)
            max_genes = max(max_genes, len(formatted_genes))
        results[col] = top_gene_scores_df.reindex(range(max_genes), fill_value="")
    return results

def create_annotations(reference, df, limit=None, level=0):
    """
    Create an annotation weighting matrix from the reference and the dataframe

    Parameters:
        reference (pd.DataFrame): Reference data loaded using load_reference()
        df (pd.DataFrame): Sheet data loaded using load_sheet()
        limit (int): Number of top matching cell types to include
        level (float): Minimum score to include a gene
        
    Returns:
        tuple: (weightings, top_gene_scores)
            - weightings: DataFrame containing cell type match percentages
            - top_gene_scores: Dictionary of DataFrames with top matching genes
    """
    counts = _get_gene_counts(reference)
    counts.update({gene: 0 for gene in df.values.flatten() if gene not in counts})
    result_matrix = _create_marker_potential_matrix(reference, counts)
    match_matrix = _create_marker_potential_matrix(df, {gene: 1 for gene in counts})
    weightings = result_matrix.transpose() @ match_matrix
    weightings = weightings.div(weightings.sum(axis=0), axis=1).mul(100).round(2)
    return weightings, _create_top_gene_scores(weightings, result_matrix, match_matrix, limit, level)

def create_display_matrix(weightings, level=SCORE_CUTOFF):
    """
    Create a display matrix from the weightings
    
    Parameters:
        weightings (pd.DataFrame): Weightings matrix from create_annotations()
    
    Returns:
        pd.DataFrame: Formatted display matrix showing top matches with percentages
    """
    result_df = pd.DataFrame()
    for col in weightings.columns:
        col_sorted = weightings[col].sort_values(ascending=False)
        col_filtered = col_sorted[col_sorted >= level].head(LIMIT)
        formatted_series = pd.Series(
            [f"{idx} ({val}%)" for idx, val in col_filtered.items()],
            name=col,
            dtype=str
        )
        formatted_series = formatted_series.reindex(range(5), fill_value="")
        result_df = pd.concat([result_df, formatted_series], axis=1)
    return result_df 
