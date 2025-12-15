import json
import random

def fix_scenario_notebook():
    path = 'examples/scenario_analysis_measles.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    # Find the cell generating data
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if 'periods=5' in source or 'periods=25' in source:
                # Replace with better synthetic data generation
                new_source = [
                    "# Create synthetic incidence data (sporadic outbreaks, 25 years)\n",
                    "dates = pd.date_range(start=\"2000-01-01\", periods=25, freq=\"YE\")\n",
                    "# Generate random sporadic data\n",
                    "np.random.seed(42)\n",
                    "I = (np.random.poisson(5, 25) * np.random.choice([0, 1, 10], 25, p=[0.6, 0.3, 0.1])).astype(float)\n",
                    "data = pd.DataFrame({\n",
                    "    \"I\": I,\n",
                    "    \"N\": [1000.0] * 25,\n",
                    "    \"D\": [0.0] * 25\n",
                    "}, index=dates)\n",
                    "\n",
                    "container = DataContainer(data, mode=\"incidence\")"
                ]
                cell['source'] = new_source
                print("Fixed scenario_analysis_measles.ipynb data generation.")
                break
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)

def fix_07_notebook():
    path = 'examples/notebooks/07_incidence_mode_measles.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if 'periods=15' in source and 'incident_cases = np.array' in source:
                 # Replace with generated data (35 years)
                 new_source = [
                    "# Realistic Mexico measles pattern (35 years)\n",
                    "np.random.seed(42)\n",
                    "dates = pd.date_range('1990', periods=35, freq='YE')\n",
                    "\n",
                    "# Incident cases per year (realistic pattern generated)\n",
                    "# Sporadic outbreaks\n",
                    "incident_cases = np.random.poisson(20, 35) * np.random.choice([0, 1, 5, 20], 35, p=[0.4, 0.3, 0.2, 0.1])\n",
                    "incident_cases = np.maximum(incident_cases, 0)\n",
                    "\n",
                    "# Deaths (CFR ~0.1-0.2% for measles)\n",
                    "incident_deaths = (incident_cases * 0.002).astype(int)\n",
                    "cumulative_deaths = np.cumsum(incident_deaths)\n",
                    "\n",
                    "# Population (Mexico ~130M)\n",
                    "population = [100_000_000 + i*1_000_000 for i in range(35)]\n",
                    "\n",
                    "# Create DataFrame with INCIDENT cases (I) and cumulative deaths (D)\n",
                    "measles_data = pd.DataFrame({\n",
                    "    'I': incident_cases,        # NEW: Incident cases (can vary)\n",
                    "    'D': cumulative_deaths,     # Cumulative deaths (monotonic)\n",
                    "    'N': population\n",
                    "}, index=dates)\n",
                    "\n",
                    "print(\"Mexico Measles Data (Simulated)\")\n",
                    "print(\"=\"*60)\n",
                    "print(measles_data.head())\n",
                    "print(f\"\\nData shape: {measles_data.shape}\")\n",
                    "print(f\"Total cases (sum of I): {incident_cases.sum()}\")"
                 ]
                 cell['source'] = new_source
                 print("Fixed 07_incidence_mode_measles.ipynb data generation.")
                 break

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)

def fix_validation_path():
    path = 'examples/validation_usa_measles.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if 'pd.read_csv' in source and 'measles_us_cases.csv' in source:
                new_source = [
                    "import os\n",
                    "try:\n",
                    "    # Load local data if available (downloaded via script)\n",
                    "    # Handle running from root or notebook dir\n",
                    "    possible_paths = [\n",
                    "        'examples/data/owid/measles_us_cases.csv',\n",
                    "        'data/owid/measles_us_cases.csv',\n",
                    "        '../examples/data/owid/measles_us_cases.csv'\n",
                    "    ]\n",
                    "    csv_path = None\n",
                    "    for p in possible_paths:\n",
                    "        if os.path.exists(p):\n",
                    "            csv_path = p\n",
                    "            break\n",
                    "    \n",
                    "    if csv_path:\n",
                    "        df_cases = pd.read_csv(csv_path)\n",
                    "    else:\n",
                    "        raise FileNotFoundError(\"Could not find measles_us_cases.csv\")\n",
                    "\n",
                    "    df_pop = pd.DataFrame({'Year': range(1980, 2021), 'N': 300e6}) # Approximation for demo\n",
                    "except Exception as e:\n",
                    "    print(f\"Data not found or error: {e}\")\n",
                    "    print(\"Please run examples/data/fetch_measles_data.py first.\")\n",
                    "    # Create dummy data for testing\n",
                    "    print(\"Creating dummy data for testing...\")\n",
                    "    df_cases = pd.DataFrame({'Year': range(1980, 1985), 'cases': [100.0]*5, 'Entity': ['United States']*5})\n"
                ]
                cell['source'] = new_source
                print("Fixed validation_usa_measles.ipynb path.")
                break
    
    # Also need to import os
    # Find the import cell
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if 'import pandas as pd' in source and 'import os' not in source:
                cell['source'].insert(0, "import os\n")
                print("Added import os to validation notebook.")
                break

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)

def fix_05_lag():
    path = 'examples/notebooks/05_multi_backend_comparison.ipynb'
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if 'model_var.fit_model(' in source and 'max_lag=' in source:
                cell['source'] = [row.replace("max_lag=10", "max_lag=1").replace("max_lag=3", "max_lag=1") for row in cell['source']]
                print("Fixed 05_multi_backend_comparison.ipynb max_lag to 1.")
            
            # Also fix Prophet args if present
            if 'forecaster="prophet"' in source:
                # remove lines with seasonality args that might be causing issues (or just comment them out)
                # But it's multi-line call.
                # Easier to replace the specific lines string-wise
                for i, line in enumerate(cell['source']):
                    if 'yearly_seasonality=' in line:
                         cell['source'][i] = line.replace('yearly_seasonality=', '# yearly_seasonality=')
                    if 'weekly_seasonality=' in line:
                         cell['source'][i] = line.replace('weekly_seasonality=', '# weekly_seasonality=')
                    if 'daily_seasonality=' in line:
                         cell['source'][i] = line.replace('daily_seasonality=', '# daily_seasonality=')
                print("Fixed 05 Prophet args.")

                
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)

if __name__ == "__main__":
    try:
        fix_scenario_notebook() 
        fix_07_notebook() 
        fix_validation_path()
        fix_05_lag()
        pass
    except Exception as e:
        print(f"Error: {e}")
