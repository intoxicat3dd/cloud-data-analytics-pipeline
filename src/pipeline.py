"""Run extraction followed by local transformation.

S3 upload is intentionally a separate opt-in step so local development does
not create AWS resources or charges accidentally.
"""

from src.ingestion import dummyjson
from src.transformation import dummyjson as transform


def main() -> None:
    dummyjson.main(upload=False)
    transform.main()


if __name__ == "__main__":
    main()
