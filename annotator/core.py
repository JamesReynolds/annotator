import pandas as pd
from collections import Counter

def load_sheet(file_path, sheet_name):
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
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
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

def load_reference(file_path):
    """
    Load the reference sheet from the Excel file

    The reference sheet must be named 'Integ summary' and is
    of the form:

    | Cell type 1       | Cell type 1    | Cell type 2       | Cell type 2    | ...
    | Wilcoxon Ordering | Other ordering | Wilcoxon Ordering | Other ordering | ...
    ...

    The first column contains the cell type labels, and the remaining
    columns contain the number of integrations for each cell type.
    """
    reference = pd.read_excel(file_path, sheet_name='Integ summary')
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

def _create_top_gene_scores(weightings, result_matrix, match_matrix, limit=4):
    """
    Create a dictionary of dataframes with top matching cell types and their top 10 gene scores.
    """
    results = {}
    for col in weightings.columns:
        col_sorted = weightings[col].sort_values(ascending=False)
        col_filtered = col_sorted[col_sorted >= 0.1].head(5)
        top_gene_scores_df = pd.DataFrame()
        for match in col_filtered.index:
            scores = match_matrix[col] * result_matrix[match] * 100
            top_genes = scores.sort_values(ascending=False)
            top_genes = top_genes[top_genes > 0.01].head(limit)
            formatted_genes = [f"{gene} ({score:.2f})" for gene, score in top_genes.items()]
            match_series = pd.Series(formatted_genes, name=match)
            match_series = match_series.reindex(range(limit), fill_value="")
            top_gene_scores_df = pd.concat([top_gene_scores_df, match_series], axis=1)
        results[col] = top_gene_scores_df
    return results

def create_annotations(reference, df):
    """
    Create an annotation weighting matrix from the reference and the dataframe
    
    Parameters:
        reference (pd.DataFrame): Reference data loaded using load_reference()
        df (pd.DataFrame): Sheet data loaded using load_sheet()
    
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
    return weightings, _create_top_gene_scores(weightings, result_matrix, match_matrix)

def create_display_matrix(weightings):
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
        col_filtered = col_sorted[col_sorted >= 0.1].head(5)
        formatted_series = pd.Series(
            [f"{idx} ({val}%)" for idx, val in col_filtered.items()],
            name=col,
            dtype=str
        )
        formatted_series = formatted_series.reindex(range(5), fill_value="")
        result_df = pd.concat([result_df, formatted_series], axis=1)
    return result_df 