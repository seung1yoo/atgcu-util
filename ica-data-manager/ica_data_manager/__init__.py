"""
ICA Data Manager
~~~~~~~~~~~~~~~

Illumina Connected Analytics (ICA) 데이터 관리를 위한 Python 패키지
"""

__version__ = "0.1.0"

from .utils import verify_icav2_installation
from .project_manager import ProjectManager, Project
from .data_manager import DataManager, ProjectData

# 패키지 임포트 시 ICAv2 CLI 설치 여부 확인
verify_icav2_installation()

__all__ = [
    "ProjectManager",
    "Project",
    "DataManager",
    "ProjectData",
] 