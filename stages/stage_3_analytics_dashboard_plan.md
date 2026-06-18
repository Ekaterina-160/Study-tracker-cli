# 📚 Этап 3: Данные, Аналитика и Визуализация во Flask

**🎯 Цель этапа:** Научиться превращать сохранённые в базе оценки в понятную аналитику: агрегировать данные, считать метрики, строить графики и показывать интерактивный dashboard внутри Flask-приложения.  
**⏱️ Время:** 4 часа (self-paced).  
**🛠️ Стек:** `Flask`, `Flask-SQLAlchemy`, `pandas`, `plotly`, `Jinja2`, `SQLite`.  
**📌 Предварительные условия:** Завершён Этап 2: есть Flask-приложение, модель `User`, модель `GradeRecord`, регистрация, логин и защищённый маршрут `/add_grade`.

---

## 🧭 Что должно получиться к концу этапа

После этапа в приложении должна появиться страница `/dashboard`, доступная только авторизованному пользователю. На ней должны быть:

- общие метрики по оценкам;
- распределение оценок;
- средний балл по предметам;
- динамика оценок по датам;
- фильтры по предмету и диапазону дат;
- понятное сообщение, если данных пока нет.

Этот этап не про "красивый дизайн", а про умение пройти полный путь: **БД → Python-данные → pandas → plotly → HTML-шаблон**.

---

## ⏱️ Час 1: Подготовка аналитического слоя

### 🧠 Концепции для понимания

1. **Аналитика не должна жить прямо в route.**  
   Route должен принимать запрос, вызывать функции и отдавать шаблон. Расчёты лучше вынести в отдельный модуль, например `analytics.py`.

2. **ORM-объект и аналитическая строка данных — разные вещи.**  
   `GradeRecord` удобен для сохранения записи в БД, но для группировок и графиков удобнее список словарей или `DataFrame`.

3. **Dashboard должен быть устойчив к пустым данным.**  
   Если пользователь ещё не добавил оценки, страница не должна падать. Она должна показать текст: "Пока нет данных для аналитики".

### 💻 Практика

1. Создай ветку для этапа:

   ```powershell
   git checkout -b feat/analytics-dashboard
   ```

2. Установи зависимости:

   ```powershell
   pip install pandas plotly
   pip freeze > requirements.txt
   ```

3. Создай файл `analytics.py`.

4. Добавь функцию, которая превращает записи из БД в `DataFrame`:

   ```python
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
   ```

5. Добавь функцию проверки пустого набора:

   ```python
   def has_grade_data(df):
       return df is not None and not df.empty
   ```

6. Временно проверь идею через простой route `/dashboard`, пока без графиков:

   ```python
   @app.route("/dashboard")
   @login_required
   def dashboard():
       records = GradeRecord.query.all()
       df = grades_to_dataframe(records)

       if df.empty:
           return render_template("dashboard.html", has_data=False)

       total_records = len(df)
       average_score = round(df["score"].mean(), 2)

       return render_template(
           "dashboard.html",
           has_data=True,
           total_records=total_records,
           average_score=average_score,
       )
   ```

7. Создай `templates/dashboard.html` с минимальным выводом:

   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>Аналитика</title>
   </head>
   <body>
       <h2>Аналитика оценок</h2>

       {% if not has_data %}
           <p>Пока нет данных для аналитики. Добавьте первую оценку.</p>
       {% else %}
           <p>Всего записей: {{ total_records }}</p>
           <p>Средний балл: {{ average_score }}</p>
       {% endif %}
   </body>
   </html>
   ```

✅ **Чек-поинт:** `/dashboard` открывается только после логина и показывает базовые метрики или сообщение об отсутствии данных.

Коммит:

```powershell
git add app.py analytics.py templates/dashboard.html requirements.txt
git commit -m "feat: add basic analytics dashboard"
```

---

## ⏱️ Час 2: Метрики и агрегации через pandas

### 🧠 Концепции для понимания

1. **Агрегация** — это сводка по группе данных: среднее, минимум, максимум, количество.

2. **`groupby`** отвечает на вопросы вида:  
   "Какой средний балл по каждому предмету?"  
   "Сколько оценок каждого типа работы?"  
   "Какая динамика оценок по дням?"

3. **Дата должна быть датой, а не строкой.**  
   Для графиков по времени важно привести колонку `date` к `datetime`.

### 💻 Практика

1. В `analytics.py` добавь функцию подготовки типов:

   ```python
   def prepare_grades_dataframe(df):
       if df.empty:
           return df

       df = df.copy()
       df["date"] = pd.to_datetime(df["date"])
       df["subject"] = df["subject"].fillna("Без предмета")
       df["work_type"] = df["work_type"].fillna("Без типа")
       return df
   ```

2. Добавь функцию общих метрик:

   ```python
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
   ```

3. Добавь агрегацию по предметам:

   ```python
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
   ```

4. Добавь распределение оценок:

   ```python
   def score_distribution(df):
       if df.empty:
           return []

       grouped = (
           df.groupby("score", as_index=False)
           .agg(records_count=("score", "count"))
           .sort_values("score")
       )

       return grouped.to_dict(orient="records")
   ```

5. Обнови route `/dashboard`, чтобы он передавал:

   - `metrics`;
   - `subjects_summary`;
   - `score_summary`.

6. В шаблоне временно выведи таблицы списками:

   ```html
   <h3>Средний балл по предметам</h3>
   {% for item in subjects_summary %}
       <p>{{ item.subject }}: {{ item.average_score }} ({{ item.records_count }} записей)</p>
   {% endfor %}

   <h3>Распределение оценок</h3>
   {% for item in score_summary %}
       <p>Оценка {{ item.score }}: {{ item.records_count }}</p>
   {% endfor %}
   ```

✅ **Чек-поинт:** Метрики считаются из реальных записей в БД. При добавлении новой оценки `/dashboard` меняется после обновления страницы.

Коммит:

```powershell
git add app.py analytics.py templates/dashboard.html
git commit -m "feat: calculate grade analytics metrics"
```

---

## ⏱️ Час 3: Интерактивные графики Plotly

### 🧠 Концепции для понимания

1. **Plotly строит HTML/JavaScript-график на стороне Python.**  
   Мы создаём объект графика в Python, превращаем его в HTML-фрагмент и вставляем в Jinja-шаблон.

2. **`|safe` нужен осознанно.**  
   Jinja по умолчанию экранирует HTML. Для графика Plotly нужно разрешить вставку HTML через `{{ chart_html|safe }}`. Используй `|safe` только для HTML, который создал твой код, а не пользовательский ввод.

3. **График должен отвечать на конкретный вопрос.**  
   Плохой график: "просто что-то нарисовать". Хороший график: "какие предметы проседают?", "улучшаются ли оценки со временем?"

### 💻 Практика

1. В `analytics.py` импортируй Plotly:

   ```python
   import plotly.express as px
   ```

2. Добавь helper для конвертации графика:

   ```python
   def figure_to_html(fig):
       return fig.to_html(full_html=False, include_plotlyjs="cdn")
   ```

3. Добавь график среднего балла по предметам:

   ```python
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
   ```

4. Добавь график распределения оценок:

   ```python
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
   ```

5. Добавь график динамики оценок:

   ```python
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
   ```

6. В route `/dashboard` передай графики:

   ```python
   subject_chart = build_subject_average_chart(df)
   distribution_chart = build_score_distribution_chart(df)
   trend_chart = build_score_trend_chart(df)
   ```

7. В `dashboard.html` выведи графики:

   ```html
   {% if subject_chart %}
       {{ subject_chart|safe }}
   {% endif %}

   {% if distribution_chart %}
       {{ distribution_chart|safe }}
   {% endif %}

   {% if trend_chart %}
       {{ trend_chart|safe }}
   {% endif %}
   ```

✅ **Чек-поинт:** На `/dashboard` отображаются минимум 3 интерактивных графика. При наведении мышкой видны значения.

Коммит:

```powershell
git add app.py analytics.py templates/dashboard.html
git commit -m "feat: add interactive plotly charts"
```

---

## ⏱️ Час 4: Фильтры, UX и устойчивость

### 🧠 Концепции для понимания

1. **Фильтры в dashboard обычно передаются через query parameters.**  
   Например: `/dashboard?subject=math&date_from=2026-06-01&date_to=2026-06-30`.

2. **Фильтры должны применяться до агрегации.**  
   Сначала отбираем нужные записи, потом считаем метрики и строим графики.

3. **Dashboard должен быть полезен даже на маленьком наборе данных.**  
   Если записей мало, графики всё равно должны работать, а пустые состояния должны быть понятными.

### 💻 Практика

1. В `analytics.py` добавь функцию получения предметов для фильтра:

   ```python
   def get_available_subjects(df):
       if df.empty:
           return []

       return sorted(df["subject"].dropna().unique().tolist())
   ```

2. Добавь функцию фильтрации:

   ```python
   def apply_grade_filters(df, subject=None, date_from=None, date_to=None):
       if df.empty:
           return df

       filtered = df.copy()

       if subject:
           filtered = filtered[filtered["subject"] == subject]

       if date_from:
           filtered = filtered[filtered["date"] >= pd.to_datetime(date_from)]

       if date_to:
           filtered = filtered[filtered["date"] <= pd.to_datetime(date_to)]

       return filtered
   ```

3. В `app.py` импортируй `request`:

   ```python
   from flask import request
   ```

4. В route `/dashboard` прочитай фильтры:

   ```python
   selected_subject = request.args.get("subject") or None
   date_from = request.args.get("date_from") or None
   date_to = request.args.get("date_to") or None
   ```

5. Построй два DataFrame:

   - `df` — все данные пользователя;
   - `filtered_df` — данные после фильтров.

6. Передай в шаблон:

   - `available_subjects`;
   - `selected_subject`;
   - `date_from`;
   - `date_to`;
   - `has_data`;
   - `has_filtered_data`.

7. Добавь форму фильтров в `dashboard.html`:

   ```html
   <form method="GET">
       <label for="subject">Предмет</label>
       <select name="subject" id="subject">
           <option value="">Все предметы</option>
           {% for subject in available_subjects %}
               <option value="{{ subject }}" {% if subject == selected_subject %}selected{% endif %}>
                   {{ subject }}
               </option>
           {% endfor %}
       </select>

       <label for="date_from">С даты</label>
       <input type="date" name="date_from" id="date_from" value="{{ date_from or '' }}">

       <label for="date_to">По дату</label>
       <input type="date" name="date_to" id="date_to" value="{{ date_to or '' }}">

       <button type="submit">Применить</button>
       <a href="{{ url_for('dashboard') }}">Сбросить</a>
   </form>
   ```

8. Добавь пустое состояние для случая, когда данные есть, но фильтры ничего не нашли:

   ```html
   {% if has_data and not has_filtered_data %}
       <p>По выбранным фильтрам нет оценок. Измените фильтры или сбросьте их.</p>
   {% endif %}
   ```

✅ **Чек-поинт:** Фильтр по предмету и датам меняет метрики и графики без ошибок.

Коммит:

```powershell
git add app.py analytics.py templates/dashboard.html
git commit -m "feat: add dashboard filters"
```

---

## 🔐 Важная доработка: изоляция данных пользователя

Если на Этапе 2 уже реализована изоляция данных по пользователям, dashboard должен показывать только записи текущего пользователя.

Идеальный вариант:

```python
records = GradeRecord.query.filter_by(user_id=current_user.id).all()
```

Если `GradeRecord` пока не связан с `User`, нужно добавить это до серьёзной аналитики:

```python
user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
```

И при создании оценки сохранять:

```python
user_id=current_user.id
```

Без этой связи dashboard будет показывать общую аналитику по всем пользователям. Для учебного проекта это допустимо только временно, но для правильной архитектуры данные должны быть изолированы.

---

## 🧪 Минимальные проверки

### Проверка вручную

1. Зарегистрируй нового пользователя.
2. Войди в аккаунт.
3. Добавь 5-10 оценок по разным предметам и датам.
4. Открой `/dashboard`.
5. Проверь, что:
   - метрики не пустые;
   - графики отображаются;
   - фильтр по предмету работает;
   - фильтр по датам работает;
   - после добавления новой оценки dashboard обновляется.

### Проверка пустых данных

1. Создай нового пользователя без оценок.
2. Открой `/dashboard`.
3. Убедись, что страница не падает и показывает понятное сообщение.

### Проверка авторизации

1. Выйди из аккаунта.
2. Попробуй открыть `/dashboard`.
3. Убедись, что Flask-Login перенаправляет на `/login`.

---

## 🧹 Качество кода

Перед завершением этапа проверь:

- route `/dashboard` не содержит длинной аналитической логики;
- расчёты лежат в `analytics.py`;
- в шаблоне нет сложных вычислений;
- `|safe` используется только для Plotly-графиков;
- `.env`, `instance/`, `*.db`, `venv/` не попадают в Git;
- в `requirements.txt` есть `pandas` и `plotly`;
- README обновлён: добавлен маршрут `/dashboard` и описание аналитики.

---

## 🛡️ Финальный чек-лист перед Pull Request

- [ ] Установлены `pandas` и `plotly`.
- [ ] Создан `analytics.py`.
- [ ] Создан route `/dashboard`.
- [ ] `/dashboard` защищён через `@login_required`.
- [ ] Данные из `GradeRecord` превращаются в `DataFrame`.
- [ ] Считаются общие метрики: количество записей, средний балл, лучший/худший балл.
- [ ] Есть агрегация по предметам.
- [ ] Есть распределение оценок.
- [ ] Есть минимум 2-3 интерактивных Plotly-графика.
- [ ] Есть фильтры по предмету и датам.
- [ ] Пустые состояния обработаны без ошибок.
- [ ] Если есть несколько пользователей, dashboard не показывает чужие данные.
- [ ] README дополнен описанием dashboard.
- [ ] В `DEVLOG.md` записаны сложности с `pandas`, `plotly`, фильтрами и выводами в Jinja2.

Финальный коммит этапа:

```powershell
git add .
git commit -m "feat: complete analytics dashboard"
```

---

## 💡 Вопросы для рефлексии

1. Почему аналитику лучше вынести из `app.py` в отдельный модуль?
2. Чем отличается список ORM-объектов от `DataFrame`?
3. Почему фильтры нужно применять до группировки?
4. В каких случаях `|safe` в Jinja2 может быть опасен?
5. Почему dashboard должен корректно работать без данных?
6. Какие графики реально помогают понять успеваемость, а какие просто занимают место?
7. Что произойдёт с производительностью, если в таблице будет 10 000 оценок?

---

## 📝 DEVLOG-шаблон для этапа 3

```markdown
# 📘 DEVLOG: Этап 3

**Дата:** ____  
**Время:** ____  
**Тема:** Данные, аналитика и визуализация во Flask

## ✅ Сделано

- Добавлен route `/dashboard`.
- Данные из БД преобразуются в `pandas.DataFrame`.
- Реализованы метрики и агрегации.
- Добавлены графики Plotly.
- Добавлены фильтры по предмету и датам.

## 💡 Инсайты

- ...

## 🧱 Сложности

- ...

## ❓ Вопросы

- ...

## 🎯 Следующий шаг

- Подготовиться к Этапу 4: AI/ML-интеграция.
```

---

🎉 **Этап завершён, когда `/dashboard` помогает пользователю быстро понять состояние оценок, а не просто показывает сырые записи из базы.**
