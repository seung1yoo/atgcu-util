# ICA Data Manager

Illumina Connected Analytics (ICA) 데이터 관리를 위한 Python 패키지입니다.

## 요구사항

- Python 3.8 이상
- ICAv2 CLI ([설치 방법](https://help.ica.illumina.com/command-line-interface/cli-installation))

## 설치 방법

```bash
# ICAv2 CLI 설치
curl -L https://github.com/illumina/ica-cli/releases/latest/download/icav2 \
    -o /usr/local/bin/icav2 && \
    chmod +x /usr/local/bin/icav2

# 패키지 설치
pip install ica-data-manager
```

## 주요 기능

- ICA 프로젝트 관리 및 조회
- 프로젝트 데이터 목록 조회
- FASTQ 파일 다운로드 (병렬 처리 지원)
  - 이미 다운로드된 파일은 자동으로 건너뜀 (파일 크기 비교)
  - 다운로드 진행 상황 실시간 출력

## 사용 방법

### 명령행 인터페이스 (CLI)

패키지 설치 후 `ica-manager` 명령어를 사용할 수 있습니다.

```bash
# 도움말 보기
ica-manager --help

# 프로젝트 목록 조회
ica-manager projects list
ica-manager projects list --details  # 상세 정보 표시

# 프로젝트 데이터 목록 조회
ica-manager data list --project-id <PROJECT_ID>
ica-manager data list --project-id <PROJECT_ID> --path /sequencing_data/
ica-manager data list --project-id <PROJECT_ID> --path /sequencing_data/ --details

# FASTQ 파일 다운로드
ica-manager data download-fastq \
    --project-id <PROJECT_ID> \
    --path /sequencing_data/ \
    --output-dir ./fastq_files \
    --workers 4
```

### Python API

#### 프로젝트 목록 조회
```python
from ica_data_manager import ProjectManager

# 프로젝트 목록 조회
manager = ProjectManager()
projects = manager.list_projects()

# 프로젝트 목록 출력
manager.display_projects(projects)

# 출력 예시:
# ID                                      NAME                OWNER               TENANT        REGION    ACTIVE    SHARING    BILLING
# ----------------------------------------  ------------------  ------------------  -----------  --------  --------  ---------  ---------
# 550e18c6-3b2e-416b-97c8-d4e71da223d2    IPMI                3a27f11b-1c58...   IPMIbiocore  Seoul     ✓         ✓          PROJECT
# ...
```

#### FASTQ 파일 다운로드
```python
from ica_data_manager import DataManager

# 데이터 매니저 초기화
manager = DataManager()

# 프로젝트의 모든 데이터 조회
project_id = "your-project-id"
data_list = manager.list_project_data(project_id)

# 특정 경로의 데이터 조회 및 출력
path_data = manager.get_data_by_path(data_list, "/sequencing_data/")
manager.display_project_data(path_data)

# 출력 예시:
# TYPE     NAME                PATH                                SIZE     STATUS
# -------  ------------------  ----------------------------------  -------  --------
# FOLDER   Sample_BC2405140001 /TBD240902_21120_20240625/        0B       AVAILABLE
# FILE     BC2405140001_R2.fq.gz /TBD240902_21120_20240625/...   174.4KB  AVAILABLE

# FASTQ 파일 다운로드
output_dir = "./fastq_files"  # 저장할 로컬 디렉토리
manager.download_fastq_files(
    project_id=project_id,
    data_list=data_list,
    path="/sequencing_data/",  # FASTQ 파일이 있는 경로
    output_dir=output_dir,
    max_workers=4  # 동시 다운로드 수
)

# 다운로드 진행 상황이 실시간으로 출력됩니다:
# 다운로드할 FASTQ 파일 수: 10
# 전체 크기: 25.3GB
# 이미 존재: sample1.fq.gz (2.5GB)
# 다운로드 완료: sample2.fq.gz (2.4GB)
# 다운로드 실패: sample3.fq.gz - 네트워크 오류
# ...
# 
# 다운로드 결과:
# - 성공: 8개
# - 건너뜀: 1개
# - 실패: 1개
```

## 개발 환경 설정

1. 저장소 클론
```bash
git clone https://github.com/yourusername/ica-data-manager.git
cd ica-data-manager
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. 개발 의존성 설치
```bash
pip install -e ".[dev]"
```

## 라이선스

MIT License 