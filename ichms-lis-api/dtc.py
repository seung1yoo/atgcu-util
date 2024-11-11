import pandas as pd
import json
import argparse
from pathlib import Path
from datetime import datetime
import requests

def post_json_data(url, data):
    try:
        response = requests.post(url, json=data, verify=False)
        response.raise_for_status()  # HTTPError 발생 시 예외 처리
        print(f"Data successfully posted to {url}. Response: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error posting data: {e}")

def parse_genotype_file(plate_barcode, file_path, result_dir):
    df = pd.read_csv(file_path, sep='\t', dtype=str)

    df = df[['Sample ID', 'Plate Barcode', 'NCBI SNP Reference', 'Allele 1 Call', 'Allele 2 Call']]

    df.columns = ['sampleId', 'plateBarcode', 'itemCd', 'result1', 'result2']

    df['plateBarcode'] = plate_barcode

    result = df.to_dict(orient='records')

    today = datetime.now().strftime('%Y-%m-%d')
    output_file = result_dir / f"{plate_barcode}.{today}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"JSON file saved to {output_file}")

    return result

def main():
    parser = argparse.ArgumentParser(description='Parse genotype TSV file to JSON format.')
    parser.add_argument('--plate-barcode', type=str, help='Plate barcode', default='TESTD4')
    parser.add_argument('--file-path', type=Path, help='Path to the genotype TSV file',
                        default=Path('dtc-data/DTC_API_TEST_4.genotype.xls'))
    parser.add_argument('--result-dir', type=Path, help='Result directory', default=Path('dtc-data'))
    parser.add_argument('--config-file', type=Path, help='Path to the config file',
                        default=Path('dtc-data/config.json'))
    args = parser.parse_args()

    if not args.file_path.exists():
        print(f"Error: The file {args.file_path} does not exist.")
        return

    args.result_dir.mkdir(exist_ok=True)

    result = parse_genotype_file(args.plate_barcode, args.file_path, args.result_dir)

    config_dict = json.load(args.config_file.open())
    post_url = config_dict['post_url']
    post_json_data(post_url, result)


if __name__ == '__main__':
    main()
