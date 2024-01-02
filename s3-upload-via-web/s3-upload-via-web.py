
import csv
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO)
import boto3
from botocore.exceptions import ClientError
import requests # pip install requests

class S3UploaderViaWeb:
    def __init__(self, infn):
        self.meta_dic = dict()
        self.parse_infn(Path(infn))

    def parse_infn(self, infn_path):
        if infn_path.exists():
            csvreader = csv.reader(infn_path.open())
        else:
            logging.critical("the file is not exists.")
            sys.exit()
            return False

        for row in csvreader:
            if row[0] in ["object_name"]:
                idx_dic = dict()
                for idx, item in enumerate(row):
                    idx_dic.setdefault(item, idx)
                continue
            object_name = row[idx_dic["object_name"]]
            bucket_name = row[idx_dic["bucket_name"]]

            self.meta_dic.setdefault(object_name, {}).setdefault("bucket_name", bucket_name)
            self.meta_dic.setdefault(object_name, {}).setdefault("object_name", object_name)

        return True

    def create_presigned_post(self, bucket_name, object_name, region_id = "ap-northeast-2",
                              fields=None, conditions=None, expiration=3600):

        s3_client = boto3.client('s3', region_name=region_id)
        try:
            response = s3_client.generate_presigned_post(bucket_name,
                                                         object_name,
                                                         Fields=fields,
                                                         Conditions=conditions,
                                                         ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)
            return None

        return response

    def response_to_meta(self, response, object_name):
        self.meta_dic[object_name].setdefault("url", response["url"])
        self.meta_dic[object_name].setdefault("key", response["fields"]["key"])
        self.meta_dic[object_name].setdefault("awsaccesskeyid", response["fields"]["x-amz-credential"])
        self.meta_dic[object_name].setdefault("policy", response["fields"]["policy"])
        self.meta_dic[object_name].setdefault("signature", response["fields"]["x-amz-signature"])

    def write_html(self, outfn):
        outfh = open(outfn, "w")
        outfh.write(f"<html>\n")
        outfh.write(f"  <head>\n")
        outfh.write(f"    <meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />\n")
        outfh.write(f"  </head>\n")
        outfh.write(f"  <body>\n")
        for object_name, info_dic in self.meta_dic.items():
            _url = info_dic["url"]
            _key = info_dic["key"]
            _awsaccesskeyid = info_dic["awsaccesskeyid"].split('/')[0]
            _policy = info_dic["policy"]
            _signature = info_dic["signature"]
            outfh.write(f"      <form action='{_url}' method='post' enctype='multipart/form-data'>\n")
            outfh.write(f"        <input type='hidden' name='key' value='{_key}' />\n")
            outfh.write(f"        <input type='hidden' name='AWSAccessKeyId' value='{_awsaccesskeyid}' />\n")
            outfh.write(f"        <input type='hidden' name='policy' value='{_policy}' />\n")
            outfh.write(f"        <input type='hidden' name='signature' value='{_signature}' />\n")
            outfh.write(f"      File:\n")
            outfh.write(f"        <input type='file' name='file' /> <br />\n")
            outfh.write(f"        <input type='submit' name='submit' value='Upload to Amazon S3' />\n")
            outfh.write(f"      </form>\n")
            break
        outfh.write(f"  </body>\n")
        outfh.write(f"</html>\n")
        outfh.close()

def main(args):

    obj = S3UploaderViaWeb(args.infn)
    for object_name, info_dic in obj.meta_dic.items():
        bucket_name = info_dic["bucket_name"]
        response = obj.create_presigned_post(bucket_name, object_name)
        if response is None:
            logging.error(f"create_presigned_post retured None.")
            exit(1)
        obj.response_to_meta(response, object_name)
    obj.write_html(f"{args.outprefix}.html")







if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--infn", default="data/atgcu-util.s3-upload-via-web.input.csv")
    parser.add_argument("--outprefix", default="data/atgcu-util.s3-upload-via-web")
    args = parser.parse_args()
    main(args)

