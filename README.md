# Cloud Data Analytics Pipeline

An end-to-end portfolio data pipeline that extracts product and cart data from [DummyJSON](https://dummyjson.com/), transforms it to Parquet, stores it in Amazon S3, analyses it with Athena, and makes it ready for a Power BI dashboard.

## Architecture

```text
DummyJSON API -> Python ingestion -> raw JSON (local / S3)
                                      |
                                      v
                           Python transformation -> partitioned Parquet
                                                        |
                                                        v
                                                    Amazon S3 -> Athena -> Power BI
```

## Run locally (no AWS charges)

The default run **does not call AWS**. It downloads public sample data and writes local files only.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.pipeline
pytest
```

The output is written beneath `data/raw/` and `data/processed/`; both are ignored by Git.

## Upload to S3 (optional)

1. Create an S3 bucket in your preferred region and copy `.env.example` to `.env`.
2. Set `S3_BUCKET` to that bucket. Set `AWS_PROFILE` only if you use a named local AWS profile.
3. Run extraction with upload enabled:

```powershell
python -c "from src.ingestion.dummyjson import main; main(upload=True)"
```

To upload processed Parquet files, use the AWS CLI after transforming:

```powershell
aws s3 sync data/processed "s3://YOUR_BUCKET/processed/" --profile cloud-data-pipeline
```

Do not create an EC2 instance for this project: the pipeline runs on your local computer. Using S3 and Athena can incur small charges, so create a billing budget and delete data when the portfolio exercise is complete.

## Athena and Power BI

1. Replace `YOUR_DATABASE` and `YOUR_BUCKET` in `sql/athena_setup.sql`, then run it in the Athena query editor.
2. Run the queries in `sql/analytics_queries.sql` to validate the datasets.
3. In Power BI Desktop, choose **Get data → Amazon Athena**, select the two tables, and build visuals for category performance, stock, ratings, and top products by sales.

## Project structure

| Path | Purpose |
| --- | --- |
| `src/ingestion` | API extraction and optional raw S3 upload |
| `src/transformation` | JSON cleaning and Parquet generation |
| `sql` | Athena table definitions and analytical queries |
| `tests` | Transformation unit tests |
| `dashboard` | Dashboard documentation and exports |

## Cost safety

The local pipeline creates no AWS resources. If you use AWS, prefer a small S3 dataset, scan only the Parquet columns you need in Athena, set a workgroup data scan limit, and delete the S3 bucket contents and Athena query results when finished. No EC2, public IPv4, NAT Gateway, or load balancer is required.
