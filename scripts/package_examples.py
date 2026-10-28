"""Bundle the runnable public examples for the course website."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted((root / "examples").glob("*")):
            if path.suffix not in (".py", ".txt"):
                continue
            info = ZipInfo("examples/" + path.name, date_time=(2026, 10, 22, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())


if __name__ == "__main__":
    main()
