"""Basic structural checks for annual World Cup national-summary CSV files.

Usage: python scripts/validate_worldcup.py PATH_TO_DIRECTORY

This validator checks **structure, not official truth**. It does not mutate input.
Expected years: 2002, 2006, 2010, 2014, 2018, 2022.
"""
from pathlib import Path
import re
import sys
import pandas as pd

YEARS = [2002, 2006, 2010, 2014, 2018, 2022]
REQUIRED = {"Team", "Position", "Games Played", "Win", "Draw", "Loss", "Goals For", "Goals Against"}
NUMERIC = REQUIRED - {"Team"}

def validate(directory: Path):
    problems = []
    year_frames = {}
    for path in directory.glob('*.csv'):
        match = re.search(r'(?<!\d)(?:2002|2006|2010|2014|2018|2022)(?!\d)', path.stem)
        if match:
            year = int(match.group())
            if year in year_frames:
                problems.append(f'Duplicate source files for {year}')
                continue
            df = pd.read_csv(path)
            missing = REQUIRED - set(df.columns)
            if missing:
                problems.append(f'{year}: missing columns {sorted(missing)}')
                continue
            df = df.copy()
            for col in NUMERIC:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                if df[col].isna().any(): problems.append(f'{year}: invalid/null {col}')
            if df['Team'].isna().any() or df['Team'].duplicated().any():
                problems.append(f'{year}: null/duplicate Team names')
            if len(df)!=32: problems.append(f'{year}: expected 32 team entries, got {len(df)}')
            if (df[list(NUMERIC)]<0).any().any(): problems.append(f'{year}: negative numeric value')
            if not (df['Win']+df['Draw']+df['Loss']).eq(df['Games Played']).all():
                problems.append(f'{year}: Win + Draw + Loss does not equal Games Played')
            if 'Goal Difference' in df:
                diff = pd.to_numeric(df['Goal Difference'].astype(str).str.replace('−','-',regex=False),errors='coerce')
                if not (df['Goals For']-df['Goals Against']).eq(diff).all():
                    problems.append(f'{year}: goals difference mismatch')
            year_frames[year]=df
    for year in YEARS:
        if year not in year_frames: problems.append(f'Missing source year {year}')
    print('Year files seen:',sorted(year_frames))
    print('Team-edition rows:', sum(len(x) for x in year_frames.values()))
    print('PASS — structural checks' if not problems else 'FAIL — structural checks')
    for p in problems:print(' -',p)
    return 0 if not problems else 1

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print('Usage: python scripts/validate_worldcup.py PATH_TO_DIRECTORY',file=sys.stderr)
        sys.exit(2)
    if not Path(sys.argv[1]).is_dir():
        print('Data directory not found:',sys.argv[1],file=sys.stderr)
        sys.exit(2)
    sys.exit(validate(Path(sys.argv[1])))
