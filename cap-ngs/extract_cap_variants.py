#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import pandas as pd
from pathlib import Path
import sys
import re

def setup_logging():
    """로깅 설정을 초기화합니다."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def parse_arguments():
    """명령행 인자를 파싱합니다."""
    parser = argparse.ArgumentParser(description='CAP NGS 변이 정보 추출 스크립트')
    parser.add_argument('--variants', required=True, type=str,
                      help='전체 변이 정보가 담긴 TSV 파일 경로')
    parser.add_argument('--targets', required=True, type=str,
                      help='평가 대상 정보가 담긴 TSV 파일 경로 (CAP 리스트와 동일)')
    parser.add_argument('--output', required=True, type=str,
                      help='결과를 저장할 TSV 파일 경로')
    parser.add_argument('--strict-trid', action='store_true',
                      help='TRID가 정확히 일치하는 변이만 추출 (기본값: False)')
    return parser.parse_args()

def clean_gene_symbol(gene_symbol):
    """Gene Symbol에서 HGNC 번호를 제거합니다."""
    return gene_symbol.split()[0]

def parse_chromosomal_interval(interval):
    """Chromosomal interval을 파싱하여 염색체, 시작 위치, 종료 위치를 반환합니다."""
    # 'chr' 접두사 제거
    interval = interval.replace('chr', '')
    
    # 정규식으로 파싱
    pattern = r'^(\d+|[XY]):(\d+)-(\d+)$'
    match = re.match(pattern, interval)
    
    if not match:
        raise ValueError(f"잘못된 chromosomal interval 형식: {interval}")
    
    chrom, start, end = match.groups()
    return chrom, int(start), int(end)

def extract_variants(variants_file, targets_file, output_file, strict_trid, logger):
    """주어진 조건에 맞는 변이를 추출합니다."""
    try:
        # 변이 파일 로드
        logger.info(f"변경 파일 로드 중: {variants_file}")
        variants_df = pd.read_csv(variants_file, sep='\t', low_memory=False)
        
        # 평가 대상 정보 로드 (CAP 리스트와 동일)
        logger.info(f"평가 대상 정보 로드 중: {targets_file}")
        targets_df = pd.read_csv(targets_file, sep='\t')
        
        # 결과를 저장할 리스트
        all_results = []
        
        # 각 평가 대상에 대해 처리
        for _, target in targets_df.iterrows():
            gene_symbol = clean_gene_symbol(target['Gene_Symbol'])
            chrom, start_pos, end_pos = parse_chromosomal_interval(target['Chromosomal_interval'])
            transcript = target['Transcript']
            
            # 기본 필터링 조건 (염색체, 유전자, 위치 범위)
            base_filter = (
                (variants_df['GENE'] == gene_symbol) &
                (variants_df['CHROM'] == chrom) &
                (variants_df['POS'] >= start_pos) &
                (variants_df['POS'] <= end_pos)
            )
            
            # TRID 필터링 조건 (strict_trid 옵션에 따라 다름)
            if strict_trid:
                trid_filter = (variants_df['TRID'] == transcript)
                matched = variants_df[base_filter & trid_filter]
                logger.info(f"TRID 정확히 일치하는 변이만 검색: {transcript}")
            else:
                # TRID 필터링 없이 기본 조건만 적용
                matched = variants_df[base_filter]
                logger.info(f"TRID 일치 여부와 관계없이 검색: {transcript}")
            
            if not matched.empty:
                logger.info(f"매칭된 변이 발견: {gene_symbol} - {len(matched)}개")
                # 각 매칭된 변이의 상세 정보 로깅
                for _, row in matched.iterrows():
                    logger.info(f"  - CHROM: {row['CHROM']}, POS: {row['POS']}, TRID: {row['TRID']}, GENE: {row['GENE']}")
                
                # 필요한 컬럼만 선택
                variant_info = matched[['CHROM', 'POS', 'TRID', 'GENE', 'ID', '2025_CAP_A_GT', 'HGVS_C', 'HGVS_P']]
                
                # 각 변이에 대해 원본 target 정보와 결합
                for _, variant_row in variant_info.iterrows():
                    result_row = target.copy()
                    # 변이 정보를 직접 할당
                    result_row['CHROM'] = variant_row['CHROM']
                    result_row['POS'] = variant_row['POS']
                    result_row['TRID'] = variant_row['TRID']
                    result_row['GENE'] = variant_row['GENE']
                    result_row['ID'] = variant_row['ID']
                    result_row['2025_CAP_A_GT'] = variant_row['2025_CAP_A_GT']
                    result_row['HGVS_C'] = variant_row['HGVS_C']
                    result_row['HGVS_P'] = variant_row['HGVS_P']
                    all_results.append(result_row)
            else:
                logger.warning(f"매칭된 변이 없음: {gene_symbol}")
                # 변이가 없는 경우에도 원본 target 정보 추가
                all_results.append(target)
        
        # 모든 결과를 DataFrame으로 변환
        result_df = pd.DataFrame(all_results)
        
        # 결과 저장
        result_df.to_csv(output_file, sep='\t', index=False)
        logger.info(f"결과 저장 완료: {output_file}")
        
        # 변이가 있는 행 수 계산
        variant_count = sum(1 for _, row in result_df.iterrows() if pd.notna(row.get('CHROM')))
        logger.info(f"총 {variant_count}개의 변이 추출됨")
        
        # 결과 요약 출력
        logger.info("추출된 변이 요약:")
        for _, row in result_df.iterrows():
            if pd.notna(row.get('CHROM')):
                logger.info(f"  - CHROM: {row['CHROM']}, POS: {row['POS']}, TRID: {row['TRID']}, GENE: {row['GENE']}, ID: {row['ID']}, GT: {row['2025_CAP_A_GT']}, HGVS_C: {row['HGVS_C']}, HGVS_P: {row['HGVS_P']}")
            
    except Exception as e:
        logger.error(f"오류 발생: {str(e)}")
        raise

def main():
    """메인 함수"""
    logger = setup_logging()
    args = parse_arguments()
    
    # 입력 파일 존재 확인
    variants_path = Path(args.variants)
    targets_path = Path(args.targets)
    
    if not variants_path.exists():
        logger.error(f"변경 파일을 찾을 수 없습니다: {variants_path}")
        sys.exit(1)
    
    if not targets_path.exists():
        logger.error(f"평가 대상 파일을 찾을 수 없습니다: {targets_path}")
        sys.exit(1)
    
    # 변이 추출 실행
    extract_variants(args.variants, args.targets, args.output, args.strict_trid, logger)

if __name__ == "__main__":
    main() 