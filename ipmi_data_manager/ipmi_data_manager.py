
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO)
import subprocess
from tqdm import tqdm
import time

class Data:
    remote_ip = "server_ip"
    remote_id = "userid"
    remote_pw = "*******" # recommand ssh-copy-id
    remote_path = Path("[Path]")
    local_path = Path("[Path]")

    def __init__(self, sample_id):
        self.rsync_cmd_s = list()
        self.remote_dic = {'cram':Path('./'), 'gvcf':Path('./'), 'vcf':Path('./'),
                           'cnv':Path('./'), 'sv':Path('./')}
        self.local_dic = {'cram':Path('./'), 'gvcf':Path('./'), 'vcf':Path('./'),
                          'cnv':Path('./'), 'sv':Path('./')}

        self.sample_id = sample_id
        self.make_remote_path()
        self.make_local_path()

    def make_rsync_cmd(self, formats):
        for _format in formats:
            cmd = ['rsync']
            cmd.append('-Plrvh')
            cmd.append(f'{self.remote_id}@{self.remote_ip}:{str(self.remote_dic[_format])}')
            cmd.append(f'{str(self.local_dic[_format])}')
            self.rsync_cmd_s.append(cmd)



    def make_remote_path(self):
        file_extensions = [".cram", ".hard-filtered.gvcf.gz", ".hard-filtered.vcf.gz",
                           ".cnv.vcf.gz", ".sv.vcf.gz"]
        for ext in file_extensions:
            file_path = self.remote_path / f"Sample_{self.sample_id}" / f"{self.sample_id}"
            file_path = file_path.with_suffix(ext)
            if ext in ['.cram']:
                self.remote_dic['cram'] = file_path
            elif ext in ['.hard-filtered.gvcf.gz']:
                self.remote_dic['gvcf'] = file_path
            elif ext in ['.hard-filtered.vcf.gz']:
                self.remote_dic['vcf'] = file_path
            elif ext in ['.cnv.vcf.gz']:
                self.remote_dic['cnv'] = file_path
            elif ext in ['.sv.vcf.gz']:
                self.remote_dic['sv'] = file_path
        return 1

    def make_local_path(self):
        file_extensions = [".cram", ".hard-filtered.gvcf.gz", ".hard-filtered.vcf.gz",
                           ".cnv.vcf.gz", ".sv.vcf.gz"]
        for ext in file_extensions:
            if ext in ['.cram']:
                file_path = self.local_path / 'cram' / f"{self.sample_id}"
                file_path = file_path.with_suffix(ext)
                self.local_dic['cram'] = file_path
            elif ext in ['.hard-filtered.gvcf.gz']:
                file_path = self.local_path / 'gvcf' / f"{self.sample_id}"
                file_path = file_path.with_suffix(ext)
                self.local_dic['gvcf'] = file_path
            elif ext in ['.hard-filtered.vcf.gz']:
                file_path = self.local_path / 'vcf' / f"{self.sample_id}"
                file_path = file_path.with_suffix(ext)
                self.local_dic['vcf'] = file_path
            elif ext in ['.cnv.vcf.gz']:
                file_path = self.local_path / 'cnv' / f"{self.sample_id}"
                file_path = file_path.with_suffix(ext)
                self.local_dic['cnv'] = file_path
            elif ext in ['.sv.vcf.gz']:
                file_path = self.local_path / 'sv' / f"{self.sample_id}"
                file_path = file_path.with_suffix(ext)
                self.local_dic['sv'] = file_path
        return 1



def main():
    sample_id_s = list()
    for line in open("ipmi_data_manager.sample_id"):
        if line.startswith("#"):
            continue
        sample_id = line.rstrip()
        sample_id_s.append(sample_id)

    for sample_id in sample_id_s:
        data = Data(sample_id)
        #data.make_rsync_cmd(['cram','gvcf','vcf','cnv','sv']) # to Archiving
        data.make_rsync_cmd(['gvcf']) # for DTC marker report
        logfile_path = Path(f"ipmi_data_manager.log/{data.sample_id}.log")

        logging.info(f"target sample id : {data.sample_id}")
        logging.info(f"rsync log file : {str(logfile_path)}")

        with logfile_path.open("a") as logfile_ofh:
            for cmd in data.rsync_cmd_s:
                logging.info(f"Start command line ==> {' '.join(cmd)}")
                process = subprocess.Popen(
                    ' '.join(cmd),
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                while True:
                    output = process.stdout.readline()
                    if output == "" and process.poll() is not None:
                        break
                    if output:
                        logfile_ofh.write(output)
                        logfile_ofh.flush()

                stderr = process.stderr.read()
                if stderr:
                    logfile_ofh.write(stderr)
                    logfile_ofh.flush()


if __name__=="__main__":
    main()


