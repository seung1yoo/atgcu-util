

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from pathlib import Path
import json
import time
import logging
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)


def iter_parse_source(infile_path, plate_barcode, limit_n=0):

    data = list()
    samples = list()
    for line in open(infile_path):
        items = line.rstrip("\n").split("\t")
        if items[0] in ["DIST_ID"]:
            idx_dic = dict()
            for idx, item in enumerate(items):
                idx_dic.setdefault(item, idx)
            rs_id_s = items[1:]
            continue
        sample_id = items[idx_dic["DIST_ID"]]
        samples.append(sample_id)
        for rs_id in rs_id_s:
            genotype = items[idx_dic[rs_id]]
            if len(genotype) not in [2]:
                logging.warning(f"{sample_id} has not expected genotype ({genotype}) at {rs_id}")
            if genotype in ["."]:
                genotype = ".."
            _dic = {
                "sampleId": sample_id,
                "plateBarcode": plate_barcode,
                "itemCd": rs_id,
                "result1": genotype[0],
                "result2": genotype[1]
            }
            data.append(_dic)

        logging.debug(f"{len(samples)}, {len(rs_id_s)}, {len(data)}, {limit_n}")
        if len(samples) in [limit_n]:
            yield data
            data = list()
            samples = list()

    yield data


def main(args):

    post_rst_dic = dict()
    iter_n = 0
    for data in iter_parse_source(args.source, args.plate_barcode, args.limit_n):
        iter_n += 1
        logging.info(f"# {iter_n} iteration by limit_n of {args.limit_n}")
        logging.info(f"## number of data : {len(data)}")
        if args.action in ["post"]:
            logging.info(f"## POST to {args.config_file['post_url']}")
            response = requests.post(args.config_file['post_url'], json=data, verify=False)
            logging.info(f"## response : {response}")
            post_rst_dic.setdefault(iter_n, response)
            time.sleep(60)
        elif args.action in ["json"]:
            outfh = Path(f"irs-data/data.{args.plate_barcode}.{iter_n}.json").open("w")
            json.dump(data, outfh, indent=4)
            outfh.close()
    logging.info(f"# Process is done. {args.action}")
    for iter_n, response in post_rst_dic.items():
        logging.info(f"## {iter_n} : {response}")



if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("post", "json"), default="post")
    parser.add_argument("--source",
                        default="irs-data/iCHMS_IRS_Result.v2.xls",
                        help="/PATH/OF/ORIGINAL/SOURCE")
    parser.add_argument("--plate-barcode", default="HC0001")
    parser.add_argument("--limit-n", default=0, type=int,
                        help="limit number of samples per a transfer. (0 is all)")
    parser.add_argument('--config-file', type=Path, help='Path to the config file',
                        default=Path('irs-data/config.json'))
    args = parser.parse_args()
    main(args)



