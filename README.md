# Annotator Library

This library provides tools for annotating cell types based on gene expression data. It is designed to help researchers and bioinformaticians process and interpret large-scale gene expression datasets.

## Features

- Identify cell types based on reference gene expression data.
- Compute "scores" for each cell type to assist manual annotation.

## Installation

To use this library, you need to have Python installed along with the following packages:

- pandas
- openpyxl

You can install the required package using pip:

```bash
pip install pandas openpyxl
```
## Usage

Here's a quick example of how to use the library to analyze gene expression data:

```python
import pandas as pd
from annotator import create_top_gene_scores

reference = annotator.load_reference("DataSheet.xlsx")
reference = pd.DataFrame(
    {
        "CellType1": ["GeneA", "GeneB", "GeneC"],
        "CellType2": ["GeneD", "GeneE", "GeneF"],
        "CellType3": ["GeneG", "GeneH", "GeneI"]
    }
)
df = annotator.load_sheet("DataSheet.xlsx", 'E_Xenium_0.4')
df = pd.DataFrame(
    {
        "CellType1": ["GeneA", "GeneB", "GeneC"],
        "CellType2": ["GeneD", "GeneE", "GeneF"],
        "CellType3": ["GeneG", "GeneH", "GeneI"]
    },
)

# Create annotations and display matrix
weightings, top_gene_scores = annotator.create_annotations(reference, df)
display_matrix = annotator.create_display_matrix(weightings)

# Create the top gene scores DataFrame
top_gene_scores_df = create_top_gene_scores(weightings, result_matrix)

# Display the results
print(top_gene_scores_df)
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss improvements or report bugs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact James Reynolds at james@groundupwards.com.
