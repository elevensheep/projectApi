from fastapi import APIRouter, Query
from app.services.crowling import Crowling
from app.services.nlp import Nlp
from typing import Optional
from app.services.database import MySQLDatabase

router = APIRouter()

@router.get("/recommend/{category}")
def get_recommendations(
    category: str,
    date: Optional[str] = Query(None, alias="news_date"),
    page: int = Query(1, gt=0),
    limit: int = Query(10, le=100),
):
    offset = (page - 1) * limit
    db = MySQLDatabase()

    print(f"📥 추천 요청: category={category}, date={date}, page={page}, limit={limit}")

    # Count query
    count_query = """
        SELECT COUNT(DISTINCT r.books_isbn)
        FROM tb_recommend r
        JOIN tb_news_keyword n ON r.news_id = n.news_id
        JOIN tb_books b ON r.books_isbn = b.books_isbn
        WHERE n.news_category = %s
    """
    values = [category]

    if date:
        count_query += " AND DATE(n.news_date) = %s"
        values.append(date)


    print("🧮 Count Query:", count_query)
    print("🧮 Count Params:", values)

    total = db.fetch_query(count_query, values)[0][0]
    print("📊 Total count:", total)

    # Data query
    data_query = """
        SELECT DISTINCT
            b.books_isbn, n.news_category, b.books_img,
            b.books_description, b.books_title, b.books_publisher,
            n.news_date
        FROM tb_recommend r
        JOIN tb_news_keyword n ON r.news_id = n.news_id
        JOIN tb_books b ON r.books_isbn = b.books_isbn
        WHERE n.news_category = %s
    """
    data_values = [category]

    if date:
        data_query += " AND DATE(n.news_date) = %s"
        data_values.append(date)

    data_query += " ORDER BY n.news_date DESC LIMIT %s OFFSET %s"
    data_values += [limit, offset]

    print("📦 Data Query:", data_query)
    print("📦 Data Params:", data_values)

    rows = db.fetch_query(data_query, data_values)
    db.close()

    books = [
        {
            "books_isbn": row[0],
            "news_category": row[1],
            "books_img": row[2],
            "books_description": row[3],
            "books_title": row[4],
            "books_publisher": row[5],
        }
        for row in rows
    ]

    print(f"📚 반환된 책 수: {len(books)}권")

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "books": books
    }

@router.get("/visualize")
def visualize_model():
    nlp = Nlp()
    nlp.LoadModel()
    nlp.VisualizeModel()
    return {"message": "✅ 모델 시각화 완료 (로컬에서 실행됨)"}

@router.get("/clusters/elbow")
def find_clusters_with_elbow(
    max_clusters: int = Query(20, ge=2, le=50),
    method: str = Query("kmeans", regex="^(kmeans|dbscan|agglomerative)$"),
    word_count: int = Query(500, ge=10, le=2000)
):
    """엘보우 기법을 사용한 클러스터링"""
    try:
        nlp = Nlp()
        nlp.LoadModel()
        
        if nlp.model is None:
            return {"error": "❌ Word2Vec 모델이 없습니다. 먼저 모델을 학습시켜주세요."}
        
        # 단어 리스트 선택
        word_list = list(nlp.model.wv.key_to_index)[:word_count]
        
        # 엘보우 기법을 사용한 클러스터링
        reduced_vectors, labels, cluster_groups = nlp.find_clusters_with_elbow(
            word_list=word_list,
            max_clusters=max_clusters,
            method=method
        )
        
        if reduced_vectors is None:
            return {"error": "❌ 클러스터링에 실패했습니다."}
        
        # 클러스터 정보 정리
        clusters_info = []
        for cluster_id, words in cluster_groups.items():
            clusters_info.append({
                "cluster_id": int(cluster_id),
                "word_count": len(words),
                "words": words[:20] if len(words) > 20 else words,  # 최대 20개 단어만 반환
                "total_words": len(words)
            })
        
        # 클러스터 ID로 정렬
        clusters_info.sort(key=lambda x: x["cluster_id"])
        
        return {
            "success": True,
            "message": f"✅ {len(cluster_groups)}개의 클러스터가 생성되었습니다.",
            "total_clusters": len(cluster_groups),
            "total_words": len(word_list),
            "method": method,
            "clusters": clusters_info
        }
        
    except Exception as e:
        return {"error": f"❌ 클러스터링 중 오류가 발생했습니다: {str(e)}"}

@router.get("/clusters/elbow/plot")
def plot_elbow_method(
    max_clusters: int = Query(20, ge=2, le=50),
    word_count: int = Query(300, ge=10, le=1000)
):
    """엘보우 그래프 생성"""
    try:
        nlp = Nlp()
        nlp.LoadModel()
        
        if nlp.model is None:
            return {"error": "❌ Word2Vec 모델이 없습니다. 먼저 모델을 학습시켜주세요."}
        
        # 단어 리스트 선택
        word_list = list(nlp.model.wv.key_to_index)[:word_count]
        
        # 벡터 추출 및 차원 축소
        import numpy as np
        from sklearn.decomposition import PCA
        from sklearn.manifold import TSNE
        
        word_vectors = np.array([nlp.model.wv[word] for word in word_list])
        
        pca = PCA(n_components=min(50, len(word_vectors[0])))
        word_vectors_pca = pca.fit_transform(word_vectors)
        
        tsne = TSNE(
            n_components=2,
            perplexity=min(30, len(word_vectors) - 1),
            learning_rate=200,
            n_iter=1000,
            random_state=42,
            init='pca'
        )
        reduced_vectors = tsne.fit_transform(word_vectors_pca)
        
        # 엘보우 그래프 생성
        optimal_clusters, inertias, silhouette_scores, cluster_range = nlp.plot_elbow_method(
            reduced_vectors, 
            max_clusters=max_clusters,
            save_path="elbow_plot.png"
        )
        
        return {
            "success": True,
            "message": "✅ 엘보우 그래프가 생성되었습니다.",
            "optimal_clusters": int(optimal_clusters),
            "inertias": [float(x) for x in inertias],
            "silhouette_scores": [float(x) for x in silhouette_scores],
            "cluster_range": list(cluster_range),
            "plot_saved": "elbow_plot.png"
        }
        
    except Exception as e:
        return {"error": f"❌ 엘보우 그래프 생성 중 오류가 발생했습니다: {str(e)}"}