


import csv
import logging
logging.basicConfig(level=logging.INFO)
import boto3
from botocore.exceptions import ClientError
import os
import sys
import threading
from pathlib import Path
from time import time
from time import localtime
from time import strftime

class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


class S3Uploader:
    def __init__(self, infn):
        self.meta_dic = dict()
        self.parse_infn(Path(infn))
        self.all_bucket_names = list()
        self.get_all_bucket_names()

    def get_all_bucket_names(self):
        s3 = boto3.resource('s3')
        for bucket in s3.buckets.all():
            self.all_bucket_names.append(bucket.name)
            logging.info(f"found the bucket in S3 before : {bucket.name}")
        return True

    def parse_infn(self, infn_path):
        if infn_path.exists():
            csvreader = csv.reader(infn_path.open())
        else:
            logging.critical("the file is not exists.")
            sys.exit()
            return False

        for row in csvreader:
            if row[0] in ["file_path"]:
                idx_dic = dict()
                for idx, item in enumerate(row):
                    idx_dic.setdefault(item, idx)
                continue
            file_path = Path(row[idx_dic["file_path"]])
            file_name = str(file_path)
            bucket_name = row[idx_dic["bucket_name"]]

            if file_path.exists():
                self.meta_dic.setdefault(file_name, {}).setdefault("bucket_name", bucket_name)
                self.meta_dic.setdefault(file_name, {}).setdefault("file_path", file_path)
                self.meta_dic.setdefault(file_name, {}).setdefault("object_name", file_path.name)
                self.meta_dic.setdefault(file_name, {}).setdefault("size", os.path.getsize(file_name))
            else:
                logging.warning(f"the file is passed as not existing. : {file_path}")

        return True

    def upload_to_bucket(self, file_name, info_dic, object_name=None):

        sys.stdout.write("\n")
        logging.info(f"Uploading the file is in progress to bucket.")
        logging.info(f" -> source file : {file_name}")
        logging.info(f" -> target bucket : info_dic['bucket_name']")

        s3_client = boto3.client('s3')

        # find legacy buckets in my s3
        bucket_name = info_dic["bucket_name"]
        if not self.is_exists_bucket(bucket_name):
            logging.info(f"create the bucket : {bucket_name}")
            if self.create_bucket(bucket_name):
                self.all_bucket_names.append(bucket_name)

        # find legacy files in the bucket
        object_list = s3_client.list_objects(Bucket=bucket_name)
        try:
            file_list = [content["Key"] for content in object_list["Contents"]]
        except KeyError as e:
            logging.error(f"KeyError : {e}")
            logging.info(f"bucket is empty : {bucket_name}")
            file_list = list()

        # upload files
        if object_name is None:
            object_name = info_dic["file_path"].name

        if object_name not in file_list:
            try:
                logging.info(f"upload the file : {file_name}")
                resposne = s3_client.upload_file(
                    file_name, bucket_name, object_name,
                    Callback=ProgressPercentage(file_name)
                )
                sys.stdout.write("\n")
            except ClientError as e:
                logging.error(f"ClientError : {e}")
        else:
            logging.warning(f"The file has already been uploaded : {file_name}")

    def is_exists_bucket(self, bucket_name):
        if bucket_name in self.all_bucket_names:
            logging.info(f"found the bucket : {bucket_name}")
            return True
        logging.info(f"could not found the bucket : {bucket_name}")
        return False

    def create_bucket(self, bucket_name):
        region_id = "ap-northeast-2"
        s3_client = boto3.client("s3", region_name=region_id)
        location = {'LocationConstraint': region_id}
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)

        return True

    def create_presigned_url(self, file_name, info_dic, expiration=604800):

        logging.info(f"create presigned url for {file_name}")

        # create presigned url
        s3_client = boto3.client('s3')
        try:
            response = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': info_dic["bucket_name"],
                        'Key': info_dic["object_name"]},
                ExpiresIn=expiration
            )
        except ClientError as e:
            logging.error(e)
            return False

        # add presigned url to meta_dic
        self.meta_dic[file_name].setdefault("presigned_url", response)

        # get expiry date & add to meta_dic
        timestamp = time()
        tm = localtime(timestamp)
        somedate = strftime('%Y-%m-%d %I:%M:%S %p', tm)
        self.meta_dic[file_name].setdefault("create_date", somedate)
        tm = localtime(timestamp+expiration)
        somedate = strftime('%Y-%m-%d %I:%M:%S %p', tm)
        self.meta_dic[file_name].setdefault("expiry_date", somedate)

        return True

    def write_result(self, outfn):
        outfh = open(outfn, "w")
        headers = ["File_name"]
        headers.append("File_size(Bytes)")
        headers.append("S3_url")
        headers.append("Presigned_url")
        headers.append("Create_date")
        headers.append("Expiry_date")
        outfh.write("{0}\n".format("\t".join(headers)))
        for file_name, info_dic in self.meta_dic.items():
            items = [info_dic["object_name"]]
            items.append(f"{info_dic['size']:,}")
            items.append(f"s3://{info_dic['bucket_name']}/{info_dic['object_name']}")
            items.append(info_dic["presigned_url"])
            items.append(info_dic["create_date"])
            items.append(info_dic["expiry_date"])
            outfh.write("{0}\n".format("\t".join(items)))
        outfh.close()

def main(args):

    obj = S3Uploader(args.infn)
    for file_name, info_dic in obj.meta_dic.items():
        obj.upload_to_bucket(file_name, info_dic)
        obj.create_presigned_url(file_name, info_dic)
    obj.write_result(f"{args.outprefix}.result.tsv")



if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--infn", default="atgcu-util.s3-upload.input.csv")
    parser.add_argument("--outprefix", default="atgcu-util.s3-upload")
    args = parser.parse_args()
    main(args)

