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
