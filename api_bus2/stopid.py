import os
import pandas as pd
import glob

# Configuration
input_folder = "../data_stops/"
output_dir = "stopid"
os.system(f"mkdir -p '{output_dir}'")
output_file = output_dir+'/'+"stopid.csv"

# Columns to keep
columns = [
    'routeshortname', 'routelongname', 'stopid', 'departuretime', 'stopsequence',
    'boarding', 'landing', 'occupation', 'day', 'stop_lon', 'stop_lat', 'stopname'
]

# Dictionary to store unique stopid -> info
stopid_coords = {}

# Read all CSV files in the folder
csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
csv_files.sort()

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {input_folder}")

for file in csv_files:
    print(f"Processing {file}...")
    try:
        # Read only required columns, but handle missing ones
        df = pd.read_csv(file,)# usecols=[col for col in columns if col in pd.read_csv(file, nrows=0).columns])
    except ValueError as e:
        print(f"⚠️  Missing some expected columns in {file}, skipping: {e}")
        continue

    # Filter out rows where lat or lon is missing, NaN, or empty
    df = df.dropna(subset=['stop_lat', 'stop_lon'], how='any')
    df = df[(df['stop_lat'].astype(str).str.strip() != '') & (df['stop_lon'].astype(str).str.strip() != '')]

    # Convert to float safely
    df['stop_lat'] = pd.to_numeric(df['stop_lat'], errors='coerce')
    df['stop_lon'] = pd.to_numeric(df['stop_lon'], errors='coerce')

    # Remove rows with invalid lat/lon after conversion
    df = df.dropna(subset=['stop_lat', 'stop_lon'])

    # Iterate over rows and fill stopid map (only first occurrence)
    for _, row in df.iterrows():
        stopid = row['stopid']
        if stopid not in stopid_coords:
            stopid_coords[stopid] = {
                'stopname': row['stopname'],
                'lat': row['stop_lat'],
                'lon': row['stop_lon']
            }

# Convert to DataFrame and save
if stopid_coords:
    result_df = pd.DataFrame([
        {'stopid': sid, 'stopname': info['stopname'], 'lat': info['lat'], 'lon': info['lon']}
        for sid, info in stopid_coords.items()
    ])
    result_df.to_csv(output_file, index=False)
    print(f"\n✅ Saved {len(result_df)} unique stops to '{output_file}'")
else:
    print("❌ No valid stop data found.")