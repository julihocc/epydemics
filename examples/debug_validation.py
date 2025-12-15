import os
import pandas as pd
from epydemics import DataContainer, Model

print("Testing path logic...")
possible_paths = [
    'examples/data/owid/measles_us_cases.csv',
    'data/owid/measles_us_cases.csv',
    '../examples/data/owid/measles_us_cases.csv'
]
csv_path = None
for p in possible_paths:
    if os.path.exists(p):
        csv_path = p
        print(f"Found at: {p}")
        break

if csv_path:
    df_cases = pd.read_csv(csv_path)
    print("Loaded CSV.")
    df_pop = pd.DataFrame({'Year': range(1980, 2021), 'N': 300e6})
    
    if df_cases is not None:
        if 'Entity' in df_cases.columns:
            df_usa = df_cases[df_cases['Entity'] == 'United States'].copy()
        else:
            df_usa = df_cases.copy()
        
        col_map = {col: 'I' for col in df_usa.columns if 'cases' in col.lower()}
        df_usa = df_usa.rename(columns=col_map)
        df = pd.merge(df_usa, df_pop, on='Year', how='left')
        if 'D' not in df.columns:
            df['D'] = 0
        df = df.sort_values('Year')
        
        print("Creating DataContainer...")
        container = DataContainer(df, mode='incidence')
        model = Model(container)
        model.create_model()
        print("Success!")
else:
    print("CSV not found.")
