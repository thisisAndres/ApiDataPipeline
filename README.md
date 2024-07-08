# ApiDataPipeline Sumary:
Utilizing Azure native technologies such as Azure Data Factory, Databricks, Azure Data Lake, Synapse, and Power BI, this project aims to build a robust data pipeline. The pipeline will consume data from an API on a daily basis, transform the data using Databricks, and store it in Azure Synapse for advanced analysis and visualization with Power BI.

# Architecture Used:
<img src='Architecture/API _PIPELINE_ARCHITECTURE.png'>

# Methodology:
1. Azure Data Factory extracts the data on a daily basis and sends it to an Azure Data Lake Gen 2 container.
2. Databricks consumes that data which is in a JSON format and transform it into a parquet.
3. After the data is transformed Databricks send the data (which is now in a .parquet format) back to ADLS,
4. Azure Synapse Analytics consumes that transfomed data (NOT IMPLEMENTED YET).
5. PowerBI is connected to Synapse Analytics to visualize that daily data.

# Data Catalog:
IN PROGRESS
