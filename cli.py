"""Analyze Python files from the terminal; export JSON without executing source."""
import argparse
import json
from pathlib import Path
from analyzer import analyze

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--output',type=Path,help='Write the full JSON report')
    args=parser.parse_args()
    try: report=analyze(args.source.read_text(encoding='utf-8-sig'))
    except (OSError,SyntaxError,ValueError) as e: parser.exit(2,f'Analysis failed: {e}\n')
    if args.output: args.output.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(f'{args.source}: {report["summary"]["findings"]} findings')
    for f in report['findings']: print(f'  {f["line"]:>4}  {f["severity"]:<6} {f["type"]}: {f["evidence"]}')
if __name__=='__main__': main()
