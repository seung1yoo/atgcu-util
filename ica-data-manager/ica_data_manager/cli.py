
import click
from typing import Optional
from .project_manager import ProjectManager
from .data_manager import DataManager


@click.group()
def cli():
    """ICA (Illumina Connected Analytics) 데이터 관리 도구"""
    pass


@cli.group()
def projects():
    """프로젝트 관련 명령어"""
    pass


@projects.command('list')
@click.option('--details', is_flag=True, help='상세 정보 표시')
def list_projects(details: bool):
    """프로젝트 목록 조회"""
    try:
        manager = ProjectManager()
        projects = manager.list_projects()
        manager.display_projects(projects)
    except Exception as e:
        click.echo(f"오류: {str(e)}", err=True)
        raise click.Abort()


@cli.group()
def data():
    """프로젝트 데이터 관련 명령어"""
    pass


@data.command('list')
@click.option('--project-id', required=True, help='프로젝트 ID')
@click.option('--path', default='/', help='조회할 경로')
@click.option('--details', is_flag=True, help='상세 정보 표시')
def list_data(project_id: str, path: str, details: bool):
    """프로젝트 데이터 목록 조회"""
    try:
        manager = DataManager()
        data_list = manager.list_project_data(project_id)
        
        if path != '/':
            data_list = manager.get_data_by_path(data_list, path)
        
        manager.display_project_data(data_list, show_details=details)
    except Exception as e:
        click.echo(f"오류: {str(e)}", err=True)
        raise click.Abort()


@data.command('download-fastq')
@click.option('--project-id', required=True, help='프로젝트 ID')
@click.option('--path', required=True, help='FASTQ 파일이 있는 경로')
@click.option('--output-dir', required=True, help='저장할 디렉토리 경로')
@click.option('--workers', default=4, help='동시 다운로드 수 (기본값: 4)')
def download_fastq(project_id: str, path: str, output_dir: str, workers: int):
    """FASTQ 파일 다운로드"""
    try:
        manager = DataManager()
        data_list = manager.list_project_data(project_id)
        manager.download_fastq_files(
            project_id=project_id,
            data_list=data_list,
            path=path,
            output_dir=output_dir,
            max_workers=workers
        )
    except Exception as e:
        click.echo(f"오류: {str(e)}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli() 
