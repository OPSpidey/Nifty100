import pandas as pd
from pathlib import Path


def load_excel(path):
    """
    Reads Bluestock Excel files.

    Row 1 = metadata
    Row 2 = headers
    Row 3+ = data
    """

    df = pd.read_excel(path, header=1)

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


if __name__ == "__main__":

    data_dir = Path("data")

    for file in data_dir.rglob("*.xlsx"):

        try:
            df = load_excel(file)

            print(
                f"{file.name}: "
                f"{df.shape[0]} rows "
                f"{df.shape[1]} columns"
            )

        except Exception as e:

            print(f"ERROR: {file.name}")
            print(e)



audit = []

for file in data_dir.rglob("*.xlsx"):

    df = load_excel(file)

    audit.append({
        "file_name": file.name,
        "rows": len(df),
        "columns": len(df.columns)
    })

    print(
        f"{file.name}: "
        f"{len(df)} rows "
        f"{len(df.columns)} columns"
    )

audit_df = pd.DataFrame(audit)

audit_df.to_csv(
    "output/load_audit.csv",
    index=False
)

print("\nAudit file created.")