# atgcu-util

atgcu-util is a repository that contains a set of utilities. These utilities make it easy to perform small, repetitive tasks.

## s3-upload
I use AWS S3 and pre-signed URLs to deliver large amounts of data. This has the advantage of eliminating the need for an intermediary such as an external hard drive. However, it does come at a cost. The occasional credit offered by AWS is enough to cover this.

s3-uploader.py has been created to make this small, repetitive task easier. It takes a csv with the path and bucket name of the files you want to upload, then performs an S3 upload to the desired bucket (or creates one if it doesn't exist) and generates a pre-signed URL. The results are displayed in a table.

### usage
```shell
usage: s3-upload.py [-h] [--infn INFN] [--outprefix OUTPREFIX]

options:
  -h, --help            show this help message and exit
  --infn INFN
  --outprefix OUTPREFIX
```

### example
```shell
python s3-upload.py --infn data/atgcu-util.s3-upload.input.csv --outprefix atgcu-util.s3-upload
```


## iCHMS LIS API

### For DTC 
```shell
python dtc.py \
  --plate-barcode 1234567890 \
  --file-path dtc-data/20241128/1234567890.xls \
  --result-dir dtc-data/20241128 \
  --config-file dtc-data/config.json
```

### For IRS
```shell
python irs.py \
  --plate-barcode 1234567890 \
  --source irs-data/20241128/1234567890.xls \
  --action post \
  --limit-n 0 \
  --config-file irs-data/config.json
```
