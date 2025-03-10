import annotator
import sys

def main(file_path):
    # Load the reference and data sheets
    reference = annotator.load_reference(file_path, 'Integ summary')
    df = annotator.load_sheet(file_path, 'E_Xenium_0.4')
    
    # Create annotations and display matrix
    weightings, top_gene_scores = annotator.create_annotations(reference, df, limit=30, level=0)
    display_matrix = annotator.create_display_matrix(weightings)
    
    # Print results
    print("Display Matrix:")
    print(display_matrix)
    print("\nTop Gene Scores by Column:")
    for key, value in top_gene_scores.items():
        print(f"\n{key}")
        print(value)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python basic_usage.py <excel_file>")
        sys.exit(1)
    main(sys.argv[1])
