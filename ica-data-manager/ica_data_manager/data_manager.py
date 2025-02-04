"""ICA 프로젝트 데이터 관리 모듈"""

import subprocess
from typing import List, Dict, Any, Optional, Tuple
import json
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tabulate import tabulate


@dataclass
class ProjectData:
    """ICA 프로젝트 데이터 정보를 담는 클래스"""
    id: str
    name: str
    data_type: str  # FILE or FOLDER
    path: str
    file_size: int
    format: Optional[str]
    status: str
    creator_id: str
    time_created: str
    time_modified: str
    project_id: str
    project_name: str
    tags: Dict[str, List[str]]

    @property
    def file_size_readable(self) -> str:
        """파일 크기를 읽기 쉬운 형태로 변환"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}PB"

    @property
    def is_file(self) -> bool:
        """파일 여부 확인"""
        return self.data_type == "FILE"

    @property
    def is_folder(self) -> bool:
        """폴더 여부 확인"""
        return self.data_type == "FOLDER"


class DataManager:
    """ICA 프로젝트 데이터 관리 클래스"""

    @staticmethod
    def list_project_data(project_id: str) -> List[ProjectData]:
        """
        프로젝트 내 데이터 목록 조회
        
        Args:
            project_id: 프로젝트 ID
            
        Returns:
            List[ProjectData]: 데이터 목록
            
        Raises:
            subprocess.CalledProcessError: icav2 명령어 실행 실패시
            json.JSONDecodeError: JSON 파싱 실패시
        """
        try:
            # icav2 명령어로 프로젝트 데이터 목록 조회
            result = subprocess.run(
                ['icav2', 'projectdata', 'list', 
                 '--project-id', project_id,
                 '--output-format', 'json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # JSON 파싱
            response_data = json.loads(result.stdout)
            items_data = response_data.get('items', [])
            
            # ProjectData 객체 리스트로 변환
            return [
                ProjectData(
                    id=item['id'],
                    name=item['details'].get('name', ''),
                    data_type=item['details'].get('dataType', 'UNKNOWN'),
                    path=item['details'].get('path', ''),
                    file_size=item['details'].get('fileSizeInBytes', 0),
                    format=item['details'].get('format', {}).get('code'),
                    status=item['details'].get('status', 'UNKNOWN'),
                    creator_id=item['details'].get('creatorId', ''),
                    time_created=item['details'].get('timeCreated', ''),
                    time_modified=item['details'].get('timeModified', ''),
                    project_id=item['details'].get('owningProjectId', ''),
                    project_name=item['details'].get('owningProjectName', ''),
                    tags=item['details'].get('tags', {'technicalTags': [], 'userTags': []})
                )
                for item in items_data
            ]
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"프로젝트 데이터 목록 조회 실패: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"프로젝트 데이터 파싱 실패: {str(e)}")
        except KeyError as e:
            raise RuntimeError(f"프로젝트 데이터 형식 오류: {str(e)}")

    @staticmethod
    def display_project_data(data_list: List[ProjectData], show_details: bool = False) -> None:
        """
        프로젝트 데이터 목록을 테이블 형식으로 출력
        
        Args:
            data_list: 출력할 데이터 목록
            show_details: 상세 정보 표시 여부
        """
        if show_details:
            headers = ['TYPE', 'NAME', 'PATH', 'SIZE', 'FORMAT', 'STATUS', 'CREATED', 'MODIFIED']
            data = [
                [
                    d.data_type,
                    d.name,
                    d.path,
                    d.file_size_readable,
                    d.format or '-',
                    d.status,
                    d.time_created,
                    d.time_modified
                ]
                for d in data_list
            ]
        else:
            headers = ['TYPE', 'NAME', 'PATH', 'SIZE', 'STATUS']
            data = [
                [
                    d.data_type,
                    d.name,
                    d.path,
                    d.file_size_readable,
                    d.status
                ]
                for d in data_list
            ]
        
        print(tabulate(data, headers=headers, tablefmt='simple'))
        print(f"\nNo of items : {len(data_list)}")

    @staticmethod
    def get_files_by_extension(data_list: List[ProjectData], extension: str) -> List[ProjectData]:
        """
        특정 확장자를 가진 파일들만 필터링
        
        Args:
            data_list: 데이터 목록
            extension: 확장자 (예: '.fastq', '.bam')
            
        Returns:
            List[ProjectData]: 필터링된 파일 목록
        """
        return [
            data for data in data_list 
            if data.is_file and data.name.lower().endswith(extension.lower())
        ]

    @staticmethod
    def get_folders(data_list: List[ProjectData]) -> List[ProjectData]:
        """
        폴더 목록만 필터링
        
        Args:
            data_list: 데이터 목록
            
        Returns:
            List[ProjectData]: 폴더 목록
        """
        return [data for data in data_list if data.is_folder]

    @staticmethod
    def get_data_by_path(data_list: List[ProjectData], path: str) -> List[ProjectData]:
        """
        특정 경로에 있는 데이터 필터링
        
        Args:
            data_list: 데이터 목록
            path: 필터링할 경로
            
        Returns:
            List[ProjectData]: 필터링된 데이터 목록
        """
        return [data for data in data_list if data.path.startswith(path)]

    @staticmethod
    def download_file(project_id: str, file_data: ProjectData, output_dir: str) -> Tuple[bool, str]:
        """
        단일 파일 다운로드
        
        Args:
            project_id: 프로젝트 ID
            file_data: 다운로드할 파일 정보
            output_dir: 저장할 디렉토리 경로
            
        Returns:
            Tuple[bool, str]: (성공 여부, 메시지)
        """
        try:
            # 출력 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)
            
            # 파일 저장 경로
            output_path = os.path.join(output_dir, file_data.name)
            
            # 파일이 이미 존재하는지 확인
            if os.path.exists(output_path):
                # 파일 크기 비교
                local_size = os.path.getsize(output_path)
                if local_size == file_data.file_size:
                    return True, f"이미 존재: {file_data.name} ({file_data.file_size_readable})"
            
            # icav2 명령어로 파일 다운로드
            result = subprocess.run(
                ['icav2', 'projectdata', 'download', 
                 '--project-id', project_id,
                 file_data.id, output_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            return True, f"다운로드 완료: {file_data.name} ({file_data.file_size_readable})"
            
        except subprocess.CalledProcessError as e:
            return False, f"다운로드 실패: {file_data.name} - {str(e)}"
        except Exception as e:
            return False, f"예상치 못한 오류: {file_data.name} - {str(e)}"

    def download_fastq_files(self, project_id: str, data_list: List[ProjectData], 
                           path: str, output_dir: str, max_workers: int = 4) -> None:
        """
        특정 경로의 FASTQ 파일들을 병렬로 다운로드
        
        Args:
            project_id: 프로젝트 ID
            data_list: 데이터 목록
            path: 대상 경로
            output_dir: 저장할 디렉토리 경로
            max_workers: 최대 동시 다운로드 수
        """
        # 경로 내의 FASTQ 파일 필터링
        path_data = self.get_data_by_path(data_list, path)
        fastq_files = [
            data for data in path_data 
            if data.is_file and (data.name.endswith('.fq.gz') or data.name.endswith('.fastq.gz'))
        ]
        
        if not fastq_files:
            print(f"지정된 경로에 FASTQ 파일이 없습니다: {path}")
            return
        
        print(f"다운로드할 FASTQ 파일 수: {len(fastq_files)}")
        total_size = sum(f.file_size for f in fastq_files)
        print(f"전체 크기: {ProjectData(id='', name='', data_type='', path='', file_size=total_size, format=None, status='', creator_id='', time_created='', time_modified='', project_id='', project_name='', tags={}).file_size_readable}")
        
        # 병렬 다운로드 실행
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.download_file, project_id, file_data, output_dir)
                for file_data in fastq_files
            ]
            
            # 결과 집계
            success = 0
            skipped = 0
            for future in as_completed(futures):
                result, message = future.result()
                print(message)
                if result:
                    if "이미 존재" in message:
                        skipped += 1
                    else:
                        success += 1
            
            print(f"\n다운로드 결과:")
            print(f"- 성공: {success}개")
            print(f"- 건너뜀: {skipped}개")
            print(f"- 실패: {len(fastq_files) - success - skipped}개") 