from services.crowling import Crowling
from services.database import MySQLDatabase
from services.nlp import Nlp
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

def recommend_books_by_keywords_enhanced(news_data: dict):
    """향상된 키워드 기반 도서 추천"""
    db = MySQLDatabase()
    nlp = Nlp()
    today = datetime.now().strftime("%Y-%m-%d")

    # 모델 로드
    nlp.LoadModel()
    
    print("🔍 향상된 추천 시스템 시작...")

    for category, keywords in news_data.items():
        print(f"📰 카테고리 '{category}' 처리 중...")
        
        for keyword in keywords:
            # 뉴스 키워드 저장
            insert_news_sql = """
                INSERT INTO tb_news_keyword (news_category, news_date, news_keyword)
                VALUES (%s, %s, %s)
            """
            db.execute_query(insert_news_sql, (category, today, keyword))

            # 1. 직접 매칭 (기존 방식)
            direct_matches = find_direct_matches(db, keyword)
            
            # 2. 유사도 기반 매칭 (새로운 방식)
            similarity_matches = find_similarity_matches(nlp, db, keyword)
            
            # 3. 클러스터 기반 매칭
            cluster_matches = find_cluster_matches(nlp, db, keyword, category)
            
            # 결과 통합 및 가중치 적용
            all_matches = combine_matches(direct_matches, similarity_matches, cluster_matches)
            
            # 최신 news_id 가져오기
            news_id_sql = """
                SELECT news_id FROM tb_news_keyword 
                WHERE news_category = %s AND news_date = %s AND news_keyword = %s
                ORDER BY news_id DESC LIMIT 1
            """
            news_id = db.fetch_query(news_id_sql, (category, today, keyword))[0][0]

            # 추천 저장 (가중치 순으로 정렬)
            for isbn, score in all_matches:
                insert_recommend_sql = """
                    INSERT IGNORE INTO tb_recommend (news_id, books_isbn, similarity_score) 
                    VALUES (%s, %s, %s)
                """
                db.execute_query(insert_recommend_sql, (news_id, isbn, score))
                
    db.close()
    print("✅ 향상된 추천 완료 및 DB 저장 완료")

def find_direct_matches(db, keyword):
    """직접 매칭 (기존 방식)"""
    book_sql = """
        SELECT books_isbn FROM tb_books 
        WHERE books_title LIKE %s OR books_description LIKE %s
    """
    matched_books = db.fetch_query(book_sql, (f'%{keyword}%', f'%{keyword}%'))
    return [(isbn[0], 1.0) for isbn in matched_books]  # 직접 매칭은 최고 점수

def find_similarity_matches(nlp, db, keyword, top_k=10):
    """유사도 기반 매칭"""
    if nlp.model is None:
        return []
    
    # 모든 책의 설명에서 키워드 추출
    query = """
        SELECT books_isbn, books_description 
        FROM tb_books 
        WHERE books_description IS NOT NULL AND books_description != ''
    """
    books = db.fetch_query(query)
    
    similarities = []
    for isbn, description in books:
        if not description:
            continue
            
        # 책 설명에서 키워드 추출
        book_keywords = nlp.extract_nouns_enhanced([description])
        
        if not book_keywords:
            continue
        
        # 키워드와 책 키워드 간의 최대 유사도 계산
        max_similarity = 0
        for book_keyword in book_keywords:
            try:
                if keyword in nlp.model.wv and book_keyword in nlp.model.wv:
                    similarity = nlp.model.wv.similarity(keyword, book_keyword)
                    max_similarity = max(max_similarity, similarity)
            except:
                continue
        
        if max_similarity > 0.3:  # 임계값 설정
            similarities.append((isbn, max_similarity))
    
    # 유사도 순으로 정렬하고 상위 k개 반환
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]

def find_cluster_matches(nlp, db, keyword, category, top_k=5):
    """클러스터 기반 매칭"""
    if nlp.model is None:
        return []
    
    # 카테고리별 클러스터 정보 (미리 정의된 클러스터)
    category_clusters = {
        'economy': ['경제', '금융', '투자', '주식', '은행', '기업', '시장'],
        'politics': ['정치', '정부', '국회', '대통령', '정책', '법안', '선거'],
        'society': ['사회', '교육', '복지', '환경', '교통', '안전', '건강'],
        'sports': ['스포츠', '축구', '야구', '농구', '올림픽', '선수', '경기'],
        'world': ['국제', '외교', '무역', '전쟁', '평화', '협력', '갈등']
    }
    
    # 카테고리에 해당하는 클러스터 키워드들
    cluster_keywords = category_clusters.get(category.lower(), [])
    
    if not cluster_keywords:
        return []
    
    # 키워드와 클러스터 키워드들 간의 유사도 계산
    cluster_similarities = []
    for cluster_keyword in cluster_keywords:
        try:
            if keyword in nlp.model.wv and cluster_keyword in nlp.model.wv:
                similarity = nlp.model.wv.similarity(keyword, cluster_keyword)
                cluster_similarities.append(similarity)
        except:
            continue
    
    if not cluster_similarities:
        return []
    
    # 클러스터 유사도의 평균
    avg_cluster_similarity = np.mean(cluster_similarities)
    
    # 클러스터와 유사한 책들 찾기
    query = """
        SELECT books_isbn, books_description 
        FROM tb_books 
        WHERE books_description IS NOT NULL AND books_description != ''
    """
    books = db.fetch_query(query)
    
    cluster_matches = []
    for isbn, description in books:
        if not description:
            continue
            
        book_keywords = nlp.extract_nouns_enhanced([description])
        
        if not book_keywords:
            continue
        
        # 책 키워드와 클러스터 키워드 간의 유사도
        book_cluster_similarities = []
        for book_keyword in book_keywords:
            for cluster_keyword in cluster_keywords:
                try:
                    if book_keyword in nlp.model.wv and cluster_keyword in nlp.model.wv:
                        similarity = nlp.model.wv.similarity(book_keyword, cluster_keyword)
                        book_cluster_similarities.append(similarity)
                except:
                    continue
        
        if book_cluster_similarities:
            avg_book_cluster_similarity = np.mean(book_cluster_similarities)
            # 클러스터 매칭 점수 = 키워드-클러스터 유사도 * 책-클러스터 유사도
            cluster_score = avg_cluster_similarity * avg_book_cluster_similarity
            if cluster_score > 0.1:  # 임계값
                cluster_matches.append((isbn, cluster_score))
    
    cluster_matches.sort(key=lambda x: x[1], reverse=True)
    return cluster_matches[:top_k]

def combine_matches(direct_matches, similarity_matches, cluster_matches):
    """매칭 결과 통합 및 가중치 적용"""
    combined = defaultdict(float)
    
    # 직접 매칭: 가중치 1.0
    for isbn, score in direct_matches:
        combined[isbn] += score * 1.0
    
    # 유사도 매칭: 가중치 0.8
    for isbn, score in similarity_matches:
        combined[isbn] += score * 0.8
    
    # 클러스터 매칭: 가중치 0.6
    for isbn, score in cluster_matches:
        combined[isbn] += score * 0.6
    
    # 점수 정규화 (0-1 범위)
    if combined:
        max_score = max(combined.values())
        if max_score > 0:
            combined = {isbn: score/max_score for isbn, score in combined.items()}
    
    # 점수 순으로 정렬
    sorted_matches = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    return sorted_matches

def evaluate_recommendation_quality():
    """추천 품질 평가"""
    db = MySQLDatabase()
    
    # 최근 추천 결과 분석
    query = """
        SELECT r.books_isbn, r.similarity_score, b.books_title, n.news_keyword, n.news_category
        FROM tb_recommend r
        JOIN tb_books b ON r.books_isbn = b.books_isbn
        JOIN tb_news_keyword n ON r.news_id = n.news_id
        WHERE r.similarity_score IS NOT NULL
        ORDER BY r.similarity_score DESC
        LIMIT 100
    """
    
    results = db.fetch_query(query)
    
    if not results:
        print("📊 평가할 추천 데이터가 없습니다.")
        return
    
    # 통계 계산
    scores = [float(row[1]) for row in results if row[1] is not None]
    
    print("📊 추천 품질 평가 결과:")
    print(f"   - 총 추천 수: {len(results)}")
    print(f"   - 평균 유사도 점수: {np.mean(scores):.4f}")
    print(f"   - 최고 유사도 점수: {np.max(scores):.4f}")
    print(f"   - 최저 유사도 점수: {np.min(scores):.4f}")
    print(f"   - 표준편차: {np.std(scores):.4f}")
    
    # 카테고리별 분석
    category_scores = defaultdict(list)
    for row in results:
        category = row[4]
        score = float(row[1]) if row[1] is not None else 0
        category_scores[category].append(score)
    
    print("\n📈 카테고리별 평균 점수:")
    for category, scores_list in category_scores.items():
        avg_score = np.mean(scores_list)
        print(f"   - {category}: {avg_score:.4f} ({len(scores_list)}개)")
    
    db.close()

if __name__ == "__main__":
    # 기존 추천 시스템 (호환성 유지)
    def recommend_books_by_keywords(news_data: dict):
        recommend_books_by_keywords_enhanced(news_data)
    
    crawler = Crowling()
    print("📡 중앙일보 뉴스 키워드 크롤링 중...")
    news_data = crawler.wordExtraction()
    print("✅ 키워드 추출 완료:", news_data)

    print("📘 향상된 추천 도서 추출 및 저장 중...")
    recommend_books_by_keywords_enhanced(news_data)
    print("✅ 향상된 추천 완료 및 DB 저장 완료")
    
    # 추천 품질 평가
    print("\n🔍 추천 품질 평가 중...")
    evaluate_recommendation_quality()
