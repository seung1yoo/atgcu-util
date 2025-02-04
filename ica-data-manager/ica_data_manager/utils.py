"""ICA 유틸리티 모듈"""

import subprocess
import sys
from typing import Tuple
import shutil


def check_icav2_cli() -> Tuple[bool, str]:
    """
    ICAv2 CLI가 설치되어 있는지 확인
    
    Returns:
        Tuple[bool, str]: (설치 여부, 메시지)
    """
    # icav2 명령어 존재 여부 확인
    icav2_path = shutil.which('icav2')
    
    if not icav2_path:
        return False, "ICAv2 CLI가 설치되어 있지 않습니다. https://help.ica.illumina.com/command-line-interface/cli-installation 에서 설치 방법을 확인하세요."
    
    try:
        # icav2 버전 확인
        result = subprocess.run(['icav2', 'version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        return True, f"ICAv2 CLI가 설치되어 있습니다. 버전: {result.stdout.strip()}"
    except subprocess.CalledProcessError as e:
        return False, f"ICAv2 CLI 실행 중 오류가 발생했습니다: {str(e)}"
    except Exception as e:
        return False, f"예상치 못한 오류가 발생했습니다: {str(e)}"


def verify_icav2_installation():
    """
    ICAv2 CLI 설치 확인 및 미설치시 에러 발생
    
    Raises:
        RuntimeError: ICAv2 CLI가 설치되어 있지 않은 경우
    """
    is_installed, message = check_icav2_cli()
    if not is_installed:
        raise RuntimeError(message)
    print(message, file=sys.stderr) 