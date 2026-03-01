#!/usr/bin/env python3
import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(prog="rde", description="Receipts Data Extractor")
    parser.add_argument("input", help="Path to receipt image or PDF")
    parser.add_argument("--output-format", choices=["json","csv"], default="json")
    args = parser.parse_args()

    # Placeholder result
    result = {"vendor": None, "date": None, "total": None, "line_items": []}
    if args.output_format == "json":
        json.dump(result, sys.stdout, indent=2)
    else:
        # Minimal CSV fallback
        print("vendor,date,total")
        print("{},{},{}".format(result["vendor"], result["date"], result["total"]))

if __name__ == "__main__":
    main()
