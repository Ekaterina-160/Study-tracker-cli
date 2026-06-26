# Подсказки: как сделать графики аналитики осмысленнее

## Цель

Сейчас график "Динамика оценок по датам" выглядит перегруженным: он рисует каждую отдельную оценку как точку линии и раскрашивает линии по всем предметам сразу. Когда в базе много записей, например 3000 оценок за учебный год, такой график превращается в шум.

Нужно научиться не просто выводить все данные на экран, а **агрегировать** их: группировать по неделям, месяцам, предметам или ученикам. Тогда графики начинают отвечать на понятные вопросы:

- как менялся средний балл класса по месяцам;
- по каким предметам есть просадки;
- какие оценки встречаются чаще всего;
- сколько времени ученики тратили на занятия;
- есть ли связь между учебными сессиями и оценками.

## Почему текущий график плохой

В `analytics.py` сейчас функция `build_score_trend_chart()` строит график примерно так:

```python
data = df.sort_values("date")

fig = px.line(
    data,
    x="date",
    y="score",
    color="subject",
    markers=True,
    title="Динамика оценок по датам",
)
```

Проблемы:

1. Одна строка в таблице `grade_record` = одна оценка. Если записей много, точек слишком много.
2. Оценки дискретные: 2, 3, 4, 5. Линии между ними создают ложное ощущение плавного изменения.
3. На одном графике сразу много предметов. Цвета пересекаются, легенда становится большой.
4. График не отвечает на ясный вопрос. Он показывает все сразу, но ничего конкретного.

## Главная идея улучшения

Перед построением графика нужно подготовить данные:

1. Привести дату к типу `datetime`.
2. Создать колонку с месяцем или неделей.
3. Сгруппировать данные.
4. Посчитать средний балл или количество записей.
5. Построить график уже по агрегированным данным.

То есть вместо:

```python
каждая оценка -> точка на графике
```

нужно сделать:

```python
месяц + предмет -> средний балл
```

## Шаг 1. Убедись, что даты подготовлены

В проекте уже есть функция `prepare_grades_dataframe(df)`. Она приводит `date` к формату даты:

```python
df["date"] = pd.to_datetime(df["date"])
```

Но в `app.py` она сейчас не используется перед построением графиков.

В маршруте `/dashboard` лучше сделать так:

```python
records = GradeRecord.query.all()
df = grades_to_dataframe(records)

if df.empty:
    return render_template("dashboard.html", has_data=False)

df = prepare_grades_dataframe(df)
```

Это важно, потому что группировка по месяцам работает надежнее, когда `date` является настоящей датой, а не строкой.

## Шаг 2. Замени график сырых оценок на средний балл по месяцам

Вместо текущей реализации `build_score_trend_chart()` сделай группировку по месяцу.

Пример:

```python
def build_score_trend_chart(df):
    if df.empty:
        return None

    data = df.copy()
    data["month"] = data["date"].dt.to_period("M").dt.to_timestamp()

    monthly = (
        data.groupby("month", as_index=False)
        .agg(
            average_score=("score", "mean"),
            records_count=("score", "count"),
        )
        .sort_values("month")
    )
    monthly["average_score"] = monthly["average_score"].round(2)

    fig = px.line(
        monthly,
        x="month",
        y="average_score",
        markers=True,
        title="Средний балл класса по месяцам",
        labels={
            "month": "Месяц",
            "average_score": "Средний балл",
        },
        hover_data={
            "records_count": True,
        },
    )
    fig.update_yaxes(range=[2, 5])

    return figure_to_html(fig)
```

Что изменится:

- вместо тысяч точек будет 9 точек учебного года;
- график покажет общую динамику класса;
- станет понятно, в какие месяцы средний балл выше или ниже.

## Шаг 3. Добавь график среднего балла по месяцам и предметам

Если хочется видеть предметы, лучше группировать не по каждой оценке, а по паре "месяц + предмет".

Добавь новую функцию в `analytics.py`:

```python
def build_subject_month_trend_chart(df):
    if df.empty:
        return None

    data = df.copy()
    data["month"] = data["date"].dt.to_period("M").dt.to_timestamp()

    monthly_by_subject = (
        data.groupby(["month", "subject"], as_index=False)
        .agg(
            average_score=("score", "mean"),
            records_count=("score", "count"),
        )
        .sort_values(["month", "subject"])
    )
    monthly_by_subject["average_score"] = monthly_by_subject["average_score"].round(2)

    fig = px.line(
        monthly_by_subject,
        x="month",
        y="average_score",
        color="subject",
        markers=True,
        title="Средний балл по предметам и месяцам",
        labels={
            "month": "Месяц",
            "average_score": "Средний балл",
            "subject": "Предмет",
        },
        hover_data={
            "records_count": True,
        },
    )
    fig.update_yaxes(range=[2, 5])

    return figure_to_html(fig)
```

Этот график все еще может быть насыщенным, потому что предметов много. Но он будет намного понятнее, чем график по каждой отдельной оценке.

## Шаг 4. Добавь тепловую карту "предмет × месяц"

Тепловая карта часто лучше линейного графика, если нужно сравнить много предметов сразу.

Она отвечает на вопрос: **в каком месяце и по какому предмету были сильные или слабые результаты?**

Добавь функцию:

```python
def build_subject_month_heatmap(df):
    if df.empty:
        return None

    data = df.copy()
    data["month"] = data["date"].dt.to_period("M").astype(str)

    heatmap_data = (
        data.groupby(["subject", "month"], as_index=False)
        .agg(average_score=("score", "mean"))
    )
    heatmap_data["average_score"] = heatmap_data["average_score"].round(2)

    fig = px.density_heatmap(
        heatmap_data,
        x="month",
        y="subject",
        z="average_score",
        title="Средний балл: предметы по месяцам",
        labels={
            "month": "Месяц",
            "subject": "Предмет",
            "average_score": "Средний балл",
        },
        color_continuous_scale="RdYlGn",
        range_color=[2, 5],
    )

    return figure_to_html(fig)
```

Плюсы:

- видно весь учебный год;
- видно все предметы;
- не нужно читать много пересекающихся линий;
- слабые места выделяются цветом.

## Шаг 5. Подключи новые графики в `app.py`

В начале `app.py` функции из `analytics.py` импортируются через:

```python
from analytics import *
```

Поэтому новые функции будут доступны автоматически.

Внутри `dashboard()` после подготовки `df` создай новые переменные:

```python
df = prepare_grades_dataframe(df)

subject_chart = build_subject_average_chart(df)
distribution_chart = build_score_distribution_chart(df)
trend_chart = build_score_trend_chart(df)
subject_month_trend_chart = build_subject_month_trend_chart(df)
subject_month_heatmap = build_subject_month_heatmap(df)
```

И передай их в шаблон:

```python
return render_template(
    "dashboard.html",
    has_data=True,
    total_records=total_records,
    average_score=average_score,
    metrics=metrics,
    subjects_summary=subjects_summary,
    score_summary=score_summary,
    subject_chart=subject_chart,
    distribution_chart=distribution_chart,
    trend_chart=trend_chart,
    subject_month_trend_chart=subject_month_trend_chart,
    subject_month_heatmap=subject_month_heatmap,
    selected_subject=selected_subject,
    date_from=date_from,
    date_to=date_to,
)
```

Важно: `metrics`, `subjects_summary`, `score_summary`, `total_records` и `average_score` лучше считать уже после `prepare_grades_dataframe(df)`.

## Шаг 6. Покажи графики в `templates/dashboard.html`

В шаблоне сейчас уже есть блоки:

```html
{% if trend_chart %}
    {{ trend_chart|safe }}
{% endif %}
```

Добавь рядом новые блоки:

```html
{% if subject_month_trend_chart %}
    {{ subject_month_trend_chart|safe }}
{% endif %}

{% if subject_month_heatmap %}
    {{ subject_month_heatmap|safe }}
{% endif %}
```

Можно добавить заголовки:

```html
<h3>Динамика среднего балла</h3>
```

Но Plotly уже показывает `title`, поэтому отдельный HTML-заголовок не обязателен.

## Шаг 7. Добавь фильтры по предмету и датам

В `analytics.py` уже есть функция:

```python
def apply_grade_filters(df, subject=None, date_from=None, date_to=None):
```

Но в `app.py` выбранные значения сейчас только читаются:

```python
selected_subject = request.args.get("subject") or None
date_from = request.args.get("date_from") or None
date_to = request.args.get("date_to") or None
```

Нужно применить фильтры:

```python
selected_subject = request.args.get("subject") or None
date_from = request.args.get("date_from") or None
date_to = request.args.get("date_to") or None

available_subjects = get_available_subjects(df)
filtered_df = apply_grade_filters(
    df,
    subject=selected_subject,
    date_from=date_from,
    date_to=date_to,
)
```

После этого графики можно строить по `filtered_df`, а список доступных предметов брать из полного `df`.

Пример:

```python
subject_chart = build_subject_average_chart(filtered_df)
distribution_chart = build_score_distribution_chart(filtered_df)
trend_chart = build_score_trend_chart(filtered_df)
subject_month_trend_chart = build_subject_month_trend_chart(filtered_df)
subject_month_heatmap = build_subject_month_heatmap(filtered_df)
```

В `render_template()` добавь:

```python
available_subjects=available_subjects,
```

## Шаг 8. Добавь форму фильтров в шаблон

В `templates/dashboard.html` добавь перед графиками простую GET-форму:

```html
<form method="get">
    <label for="subject">Предмет:</label>
    <select name="subject" id="subject">
        <option value="">Все предметы</option>
        {% for subject in available_subjects %}
            <option value="{{ subject }}" {% if subject == selected_subject %}selected{% endif %}>
                {{ subject }}
            </option>
        {% endfor %}
    </select>

    <label for="date_from">С:</label>
    <input type="date" name="date_from" id="date_from" value="{{ date_from or '' }}">

    <label for="date_to">По:</label>
    <input type="date" name="date_to" id="date_to" value="{{ date_to or '' }}">

    <button type="submit">Применить</button>
    <a href="{{ url_for('dashboard') }}">Сбросить</a>
</form>
```

После этого можно будет смотреть:

- все предметы за весь год;
- один предмет за весь год;
- один предмет за четверть;
- все предметы за выбранный месяц.

## Шаг 9. Что можно сделать со `study_session`

Сейчас графики используют только таблицу `grade_record`. Но в базе есть еще `study_session`, и это хорошая возможность для более интересной аналитики.

Идеи:

1. **Время занятий по предметам**
   - сгруппировать `StudySession` по `subject`;
   - сложить `duration_min`;
   - построить bar chart.

2. **Время занятий по месяцам**
   - сгруппировать по месяцу;
   - сложить минуты;
   - построить line chart или bar chart.

3. **Сравнение: средний балл и время занятий**
   - по каждому предмету посчитать средний балл;
   - по каждому предмету посчитать сумму минут;
   - объединить таблицы по `subject`;
   - построить scatter plot: `x = total_minutes`, `y = average_score`.

Пример функции преобразования сессий в DataFrame:

```python
def study_sessions_to_dataframe(records):
    rows = []
    for record in records:
        rows.append(
            {
                "id": record.id,
                "student_name": record.student_name,
                "subject": record.subject,
                "topic": record.topic,
                "duration_min": record.duration_min,
                "date": record.date,
                "notes": record.notes,
            }
        )
    return pd.DataFrame(rows)
```

Пример графика времени занятий по предметам:

```python
def build_study_time_by_subject_chart(df):
    if df.empty:
        return None

    data = df.copy()
    grouped = (
        data.groupby("subject", as_index=False)
        .agg(total_minutes=("duration_min", "sum"))
        .sort_values("total_minutes", ascending=False)
    )

    fig = px.bar(
        grouped,
        x="subject",
        y="total_minutes",
        title="Общее время занятий по предметам",
        labels={
            "subject": "Предмет",
            "total_minutes": "Минуты",
        },
    )

    return figure_to_html(fig)
```

## Рекомендуемый итоговый набор графиков

Для учебного проекта достаточно 5 графиков:

1. **Средний балл по предметам** - bar chart.
2. **Распределение оценок** - bar chart.
3. **Средний балл класса по месяцам** - line chart.
4. **Средний балл: предметы по месяцам** - heatmap.
5. **Общее время занятий по предметам** - bar chart по `study_session`.

Такой набор показывает разные стороны данных и не перегружает экран.

## Проверка результата

После изменений запусти приложение и открой:

```text
http://127.0.0.1:5000/dashboard
```

Проверь:

1. Старый шумный график больше не показывает отдельные оценки.
2. На графике динамики видны месяцы учебного года.
3. Значения среднего балла находятся в диапазоне от 2 до 5.
4. Фильтр по предмету меняет графики.
5. При сбросе фильтра снова показываются все данные.

## Важная мысль

Хорошая аналитика начинается не с красивого графика, а с хорошего вопроса.

Плохой вопрос:

```text
Покажи все оценки.
```

Хорошие вопросы:

```text
Как менялся средний балл класса по месяцам?
По каким предметам есть просадка?
Какие оценки встречаются чаще всего?
Сколько времени ученики занимались по каждому предмету?
```

Если график отвечает на конкретный вопрос, он почти всегда выглядит лучше.
