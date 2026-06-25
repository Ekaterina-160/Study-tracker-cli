import pandas as pd
import plotly.express as px

def grades_to_dataframe(records):
    rows = []
    for record in records:
       rows.append(
           {
               "id": record.id,
               "student_name": record.student_name,
               "subject": record.subject,
               "score": record.score,
               "date": record.date,
               "work_type": record.work_type,
               "comment": record.comment,
           }
       )
    return pd.DataFrame(rows)
def has_grade_data(df):
       return df is not None and not df.empty

def prepare_grades_dataframe(df):
    if df.empty:
        return df

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["subject"] = df["subject"].fillna("Без предмета")
    df["work_type"] = df["work_type"].fillna("Без типа")
    return df

def calculate_summary_metrics(df):
    if df.empty:
        return {
           "total_records": 0,
           "average_score": None,
           "best_score": None,
           "worst_score": None,
           "subjects_count": 0,
        }

    return {
        "total_records": int(len(df)),
        "average_score": round(float(df["score"].mean()), 2),
        "best_score": int(df["score"].max()),
        "worst_score": int(df["score"].min()),
        "subjects_count": int(df["subject"].nunique()),
    }

def average_score_by_subject(df):
    if df.empty:
        return []
    grouped = (
        df.groupby("subject", as_index=False)
        .agg(
            average_score=("score", "mean"),
            records_count=("score", "count"),
        )
        .sort_values("average_score", ascending=False)
    )
    grouped["average_score"] = grouped["average_score"].round(2)
    return grouped.to_dict(orient="records")

def score_distribution(df):
    if df.empty:
       return []
    grouped = (
       df.groupby("score", as_index=False)
       .agg(records_count=("score", "count"))
       .sort_values("score")
    )

    return grouped.to_dict(orient="records")

def figure_to_html(fig):
    return fig.to_html(full_html=False, include_plotlyjs="cdn")

def build_subject_average_chart(df):
    if df.empty:
        return None

    data = (
        df.groupby("subject", as_index=False)
        .agg(average_score=("score", "mean"))
        .sort_values("average_score", ascending=False)
    )
    data["average_score"] = data["average_score"].round(2)

    fig = px.bar(
        data,
        x="subject",
        y="average_score",
        title="Средний балл по предметам",
        labels={
            "subject": "Предмет",
            "average_score": "Средний балл",
        },
    )

    return figure_to_html(fig)

def build_score_distribution_chart(df):
    if df.empty:
        return None

    data = (
        df.groupby("score", as_index=False)
        .agg(records_count=("score", "count"))
        .sort_values("score")
    )

    fig = px.bar(
        data,
        x="score",
        y="records_count",
        title="Распределение оценок",
        labels={
            "score": "Оценка",
            "records_count": "Количество",
        },
    )

    return figure_to_html(fig)

def build_score_trend_chart(df):
    if df.empty:
        return None

    data = df.sort_values("date")

    fig = px.line(
        data,
        x="date",
        y="score",
        color="subject",
        markers=True,
        title="Динамика оценок по датам",
        labels={
            "date": "Дата",
            "score": "Оценка",
            "subject": "Предмет",
        },
    )

    return figure_to_html(fig)