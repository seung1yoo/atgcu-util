"""ICA 프로젝트 관리 모듈"""

import subprocess
from typing import List, Dict, Any
import json
from dataclasses import dataclass
from tabulate import tabulate


@dataclass
class Project:
    """ICA 프로젝트 정보를 담는 클래스"""
    id: str
    name: str
    owner: str
    tenant: str
    region: str
    active: bool
    data_sharing_enabled: bool
    billing_mode: str
    time_created: str
    time_modified: str
    tags: Dict[str, List[str]]


class ProjectManager:
    """ICA 프로젝트 관리 클래스"""

    @staticmethod
    def list_projects() -> List[Project]:
        """
        ICA 프로젝트 목록 조회
        
        Returns:
            List[Project]: 프로젝트 목록
        
        Raises:
            subprocess.CalledProcessError: icav2 명령어 실행 실패시
            json.JSONDecodeError: JSON 파싱 실패시
        """
        try:
            # icav2 명령어로 프로젝트 목록 조회 (JSON 형식)
            result = subprocess.run(
                ['icav2', 'projects', 'list', '--output-format', 'json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # JSON 파싱
            response_data = json.loads(result.stdout)
            projects_data = response_data.get('items', [])
            
            # Project 객체 리스트로 변환
            return [
                Project(
                    id=project['id'],
                    name=project['name'],
                    owner=project['ownerId'],
                    tenant=project['tenantName'],
                    region=project['region']['cityName'],
                    active=project['active'],
                    data_sharing_enabled=project['dataSharingEnabled'],
                    billing_mode=project['billingMode'],
                    time_created=project['timeCreated'],
                    time_modified=project['timeModified'],
                    tags=project['tags']
                )
                for project in projects_data
            ]
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"프로젝트 목록 조회 실패: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"프로젝트 데이터 파싱 실패: {str(e)}")
        except KeyError as e:
            raise RuntimeError(f"프로젝트 데이터 형식 오류: {str(e)}")

    @staticmethod
    def display_projects(projects: List[Project]) -> None:
        """
        프로젝트 목록을 테이블 형식으로 출력
        
        Args:
            projects: 출력할 프로젝트 목록
        """
        # 테이블 헤더와 데이터 준비
        headers = ['ID', 'NAME', 'OWNER', 'TENANT', 'REGION', 'ACTIVE', 'SHARING', 'BILLING']
        data = [
            [
                p.id,
                p.name,
                p.owner,
                p.tenant,
                p.region,
                '✓' if p.active else '✗',
                '✓' if p.data_sharing_enabled else '✗',
                p.billing_mode
            ]
            for p in projects
        ]
        
        # 테이블 출력
        print(tabulate(data, headers=headers, tablefmt='simple'))
        print(f"\nNo of items : {len(projects)}")

    @staticmethod
    def get_project_details(project: Project) -> Dict[str, Any]:
        """
        프로젝트 상세 정보를 딕셔너리로 반환
        
        Args:
            project: 상세 정보를 조회할 프로젝트
            
        Returns:
            프로젝트 상세 정보를 담은 딕셔너리
        """
        return {
            'id': project.id,
            'name': project.name,
            'owner': project.owner,
            'tenant': project.tenant,
            'region': project.region,
            'active': project.active,
            'data_sharing_enabled': project.data_sharing_enabled,
            'billing_mode': project.billing_mode,
            'time_created': project.time_created,
            'time_modified': project.time_modified,
            'technical_tags': project.tags['technicalTags'],
            'user_tags': project.tags['userTags']
        } 