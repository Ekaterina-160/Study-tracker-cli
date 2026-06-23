import pandas as pd

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
