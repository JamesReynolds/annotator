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
import annotator

# Load reference from file
reference = annotator.load_reference("DataSheet.xlsx", "Integ Summary")

# ...results in a dataframe like this:
reference = pd.DataFrame(
    {
        "CellType1": ["GeneA", "GeneB", "GeneC"],
        "CellType2": ["GeneD", "GeneE", "GeneF"],
        "CellType3": ["GeneG", "GeneH", "GeneI"]
    }
)

# Load file for annotation
df = annotator.load_sheet("DataSheet.xlsx", 'E_Xenium_0.4')

# ...results in a dataframe of the same form as the annotator
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

# Display the results
print(display_matrix)
print(top_gene_scores)
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss improvements or report bugs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact James Reynolds at james@groundupwards.com.
