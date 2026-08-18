# 🤖 Этап 4: AI-советник по успеваемости (интеграция LLM)

**🎯 Цель этапа:** Безопасно подключить языковую модель (LLM) и научиться главному навыку работы с ней: собирать контекст из своих данных, формировать промпт, парсить и валидировать ответ, кэшировать результат и не падать, когда модель недоступна.
**⏱️ Время:** 4 часа (self-paced).
**🛠️ Стек:** `Flask`, `Flask-SQLAlchemy`, `requests` (или `openai`), `python-dotenv`, уже готовый `analytics.py` с этапа 3.
**📌 Предварительные условия:** Завершён Этап 3: есть `/dashboard`, функции метрик (`calculate_summary_metrics`, `average_score_by_subject`, `score_distribution`) и `DataFrame` из `GradeRecord`.

---

## 🧭 Что должно получиться к концу этапа

На дашборде появляется кнопка **«Совет от AI»**. По нажатию приложение:

1. берёт уже посчитанные метрики (не сырые строки БД);
2. собирает из них короткий текстовый контекст;
3. отправляет его в LLM с чётким промптом;
4. получает и валидирует ответ;
5. сохраняет ответ в БД (чтобы не запрашивать одно и то же дважды);
6. показывает совет пользователю с индикацией загрузки и ошибки;
7. если модель недоступна — показывает совет по простым локальным правилам (fallback).

> ⚠️ Главная идея этапа: **LLM не считает — LLM формулирует.**
> Все числа даёт `pandas` (этап 3). LLM только превращает их в понятный текст.
> Так мы избегаем «галлюцинаций» с цифрами и тратим минимум токенов.

Это НЕ этап про «чат с искусственным интеллектом ради чата». Это этап про умение пройти путь **БД → метрики → контекст → промпт → ответ → валидация → БД → UI**.

---

## 🔌 Выбор модели: облако или локально

Для учебного проекта подойдут два варианта. Выбери один и не переключайся посреди этапа.

| | Вариант A: Ollama (локально) | Вариант B: OpenAI API (облако) |
|---|---|---|
| Стоимость | Бесплатно | Платно, нужна карта и ключ |
| Установка | Скачать [ollama.com](https://ollama.com), `ollama pull llama3.2` | `pip install openai`, получить API-ключ |
| Интернет | Не нужен после загрузки модели | Нужен всегда |
| Клиент | `requests` к `http://localhost:11434` | библиотека `openai` |

**Рекомендация для экспресс-курса — вариант A (Ollama):** бесплатно, работает офлайн, не нужно вводить платёжные данные и ключи. В пособии основной код показан для Ollama, а в конце Часа 2 приведён эквивалент для OpenAI — переключение занимает несколько строк.

> 🔐 Правило безопасности с самого начала: ключи и адреса моделей живут **только в `.env`**, никогда в коде и никогда в Git.

---

## ⏱️ Час 1: Настройка, `.env` и первый запрос к модели

### 🧠 Концепции для понимания

1. **LLM — это внешний сервис, который может упасть.**
   Любой запрос к модели надо оборачивать в `try/except` и ставить `timeout`. Приложение не должно «зависать» или падать из-за модели.

2. **Структура промпта = роль + контекст + задача + формат вывода.**
   - *роль:* «Ты доброжелательный школьный тьютор.»
   - *контекст:* факты об ученике (наши метрики).
   - *задача:* «Дай 3 совета, что подтянуть.»
   - *формат вывода:* «Ответь простым языком, без Markdown» или «Верни JSON вида ...».

3. **Секреты — в `.env`.**
   В коде мы читаем их через `os.getenv(...)`, а сам `.env` уже в `.gitignore`.

### 💻 Практика

1. Создай ветку этапа:

   ```powershell
   git checkout -b feat/ai-integration
   ```

2. (Вариант A) Установи Ollama, скачай лёгкую модель и убедись, что сервер отвечает:

   ```powershell
   ollama pull llama3.2
   ollama run llama3.2 "Привет! Ответь одним словом: работаешь?"
   ```

3. Установи HTTP-клиент и зафиксируй зависимости:

   ```powershell
   pip install requests
   pip freeze > requirements.txt
   ```

4. Добавь настройки модели в `.env` (НЕ в код):

   ```env
   AI_PROVIDER=ollama
   AI_BASE_URL=http://localhost:11434
   AI_MODEL=llama3.2
   AI_TIMEOUT=30
   # Для варианта B (OpenAI) вместо этого:
   # AI_PROVIDER=openai
   # OPENAI_API_KEY=sk-...
   # AI_MODEL=gpt-4o-mini
   ```

5. Проверь, что `.env` не попадёт в Git (в `.gitignore` должна быть строка `.env`):

   ```powershell
   git check-ignore .env
   ```

   Команда должна вывести `.env`. Если вывод пустой — добавь `.env` в `.gitignore` **до первого коммита**.

6. Создай файл `ai_service.py` и напиши самый простой запрос — «hello world» для LLM:

   ```python
   import os
   import requests

   AI_BASE_URL = os.getenv("AI_BASE_URL", "http://localhost:11434")
   AI_MODEL = os.getenv("AI_MODEL", "llama3.2")
   AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "30"))


   def ask_model(prompt):
       """Отправляет промпт в Ollama и возвращает текст ответа."""
       response = requests.post(
           f"{AI_BASE_URL}/api/generate",
           json={
               "model": AI_MODEL,
               "prompt": prompt,
               "stream": False,
           },
           timeout=AI_TIMEOUT,
       )
       response.raise_for_status()
       data = response.json()
       return data["response"].strip()
   ```

7. Проверь функцию отдельным скриптом (не трогая Flask). Создай `instruments/test_ai.py`:

   ```python
   from dotenv import load_dotenv
   load_dotenv()

   from ai_service import ask_model

   print(ask_model("Ответь одним предложением: чем полезен трекер оценок?"))
   ```

   Запусти:

   ```powershell
   python instruments/test_ai.py
   ```

✅ **Чек-поинт:** Скрипт выводит осмысленный ответ модели. Ключи/адреса читаются из `.env`, в коде их нет.

Коммит:

```powershell
git add ai_service.py instruments/test_ai.py requirements.txt .env.example
git commit -m "feat: add basic LLM client (ai_service)"
```

> 💡 Хорошая привычка: рядом с `.env` держать `.env.example` с теми же ключами, но без значений — чтобы другой человек понял, что нужно заполнить. `.env.example` коммитить можно, `.env` — нельзя.

---

## ⏱️ Час 2: Контекст из данных и обработка ошибок

### 🧠 Концепции для понимания

1. **Контекст — это НЕ вся база.**
   Мы не отправляем в модель сотни строк. Мы отправляем сжатую сводку: средний балл, слабые предметы, распределение. Это дёшево по токенам и безопасно.

2. **Отделяем «сбор фактов» от «запроса к модели».**
   Одна функция строит текст-контекст из метрик, другая шлёт промпт. Так проще тестировать и переключать провайдеров.

3. **Ошибка сети — это нормальная ветка логики, а не крах.**
   `timeout`, «сервер недоступен», «пустой ответ» — всё это должно приводить к аккуратному fallback, а не к 500-й ошибке.

### 💻 Практика

1. В `ai_service.py` добавь сбор контекста из **уже готовых** функций аналитики (переиспользуем этап 3):

   ```python
   from analytics import (
       calculate_summary_metrics,
       average_score_by_subject,
       score_distribution,
   )


   def build_student_context(df):
       """Собирает короткий текстовый контекст из посчитанных метрик."""
       metrics = calculate_summary_metrics(df)
       by_subject = average_score_by_subject(df)

       weak = [s for s in by_subject if s["average_score"] < 4]
       weak_text = ", ".join(
           f"{s['subject']} ({s['average_score']})" for s in weak
       ) or "нет явно слабых предметов"

       lines = [
           f"Всего оценок: {metrics['total_records']}",
           f"Средний балл: {metrics['average_score']}",
           f"Лучший балл: {metrics['best_score']}, худший: {metrics['worst_score']}",
           f"Предметов: {metrics['subjects_count']}",
           f"Проседают: {weak_text}",
       ]
       return "\n".join(lines)
   ```

2. Собери полноценный промпт (роль + контекст + задача + формат):

   ```python
   def build_advice_prompt(context):
       return (
           "Ты доброжелательный школьный тьютор.\n"
           "Вот данные об успеваемости ученика:\n"
           f"{context}\n\n"
           "Задача: дай 3 коротких конкретных совета, что подтянуть в первую очередь.\n"
           "Отвечай простым языком, по-русски, без Markdown и без вступлений.\n"
           "Не придумывай новых цифр — используй только данные выше."
       )
   ```

3. Оберни запрос в надёжную функцию с обработкой ошибок:

   ```python
   def get_ai_advice(df):
       """Возвращает (текст, источник). Источник: 'ai' или 'fallback'."""
       if df.empty:
           return "Пока нет данных для совета. Добавьте несколько оценок.", "fallback"

       context = build_student_context(df)
       prompt = build_advice_prompt(context)

       try:
           answer = ask_model(prompt)
           if not answer:
               raise ValueError("Модель вернула пустой ответ")
           return answer, "ai"
       except (requests.RequestException, ValueError) as error:
           print(f"[ai_service] Ошибка запроса к модели: {error}")
           return local_fallback_advice(df), "fallback"
   ```

4. Реализуй **fallback по простым правилам** — он работает без интернета и без модели:

   ```python
   def local_fallback_advice(df):
       by_subject = average_score_by_subject(df)
       weak = [s for s in by_subject if s["average_score"] < 4]

       if not weak:
           return "Успеваемость ровная. Продолжай в том же темпе."

       weak_sorted = sorted(weak, key=lambda s: s["average_score"])
       names = ", ".join(s["subject"] for s in weak_sorted[:3])
       return f"Стоит уделить внимание предметам: {names}."
   ```

5. *(Только для варианта B — OpenAI.)* Переключение провайдера — это одна функция. Замени `ask_model` на:

   ```python
   from openai import OpenAI

   client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


   def ask_model(prompt):
       completion = client.chat.completions.create(
           model=AI_MODEL,
           messages=[{"role": "user", "content": prompt}],
           timeout=AI_TIMEOUT,
       )
       return completion.choices[0].message.content.strip()
   ```

   Остальной код (`build_student_context`, `get_ai_advice`, fallback) не меняется — в этом и смысл изоляции AI-логики.

✅ **Чек-поинт:** `get_ai_advice(df)` возвращает совет, когда модель работает, и осмысленный fallback, когда ты выключил Ollama / интернет. Приложение не падает ни в одном из случаев.

Коммит:

```powershell
git add ai_service.py
git commit -m "feat: build context from metrics + fallback advice"
```

---

## ⏱️ Час 3: Кэширование ответов в БД

### 🧠 Концепции для понимания

1. **Запрос к LLM — дорогой (по времени и деньгам).**
   Если данные не изменились, повторно спрашивать модель бессмысленно. Ответ надо запомнить.

2. **Ключ кэша — это «отпечаток» контекста.**
   Считаем хэш от текста-контекста. Одинаковый контекст → одинаковый хэш → берём ответ из БД, а не из модели.

3. **Кэш переиспользует то, что уже есть.**
   У нас уже есть SQLAlchemy и БД. Не тянем новую библиотеку — заводим одну маленькую таблицу.

### 💻 Практика

1. В `db_models.py` добавь модель для хранения ответов:

   ```python
   class AiInsight(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       context_hash = db.Column(db.String(64), unique=True, nullable=False)
       advice_text = db.Column(db.Text, nullable=False)
       source = db.Column(db.String(20), nullable=False)  # 'ai' или 'fallback'
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
   ```

   > Таблица создастся сама при следующем запуске: `db.create_all()` уже есть в `app.py`.

2. В `ai_service.py` добавь вычисление хэша контекста:

   ```python
   import hashlib


   def context_fingerprint(context):
       return hashlib.sha256(context.encode("utf-8")).hexdigest()
   ```

3. Сделай функцию с кэшем, которая работает поверх `get_ai_advice`:

   ```python
   from db_models import AiInsight
   from extensions import db


   def get_cached_advice(df):
       """Возвращает совет, используя кэш в БД. Отдаёт (текст, источник, cached)."""
       if df.empty:
           return "Пока нет данных для совета. Добавьте несколько оценок.", "fallback", False

       context = build_student_context(df)
       key = context_fingerprint(context)

       cached = AiInsight.query.filter_by(context_hash=key).first()
       if cached:
           return cached.advice_text, cached.source, True

       text, source = get_ai_advice(df)

       # Кэшируем только успешные ответы модели, fallback — нет смысла запоминать.
       if source == "ai":
           insight = AiInsight(context_hash=key, advice_text=text, source=source)
           db.session.add(insight)
           db.session.commit()

       return text, source, False
   ```

✅ **Чек-поинт:** Первый запрос идёт в модель (медленно), повторный при тех же данных отдаётся мгновенно из БД (`cached=True`). После добавления новой оценки контекст меняется → хэш другой → модель спрашивается заново.

Коммит:

```powershell
git add db_models.py ai_service.py
git commit -m "feat: cache AI advice in database by context hash"
```

---

## ⏱️ Час 4: Route, UI и устойчивость

### 🧠 Концепции для понимания

1. **Route тонкий — логика в `ai_service.py`.**
   Как и с аналитикой на этапе 3: route берёт данные, вызывает сервис, отдаёт шаблон.

2. **Пользователь должен видеть три состояния:** идёт загрузка → пришёл ответ → произошла ошибка / это fallback.

3. **Сырой промпт и ключи никогда не попадают в UI.**
   Показываем только финальный текст совета.

### 💻 Практика

1. В `app.py` добавь маршрут (переиспользуем подготовку `DataFrame` как в `/dashboard`):

   ```python
   from ai_service import get_cached_advice

   @app.route("/ai-advice")
   @login_required
   def ai_advice():
       records = GradeRecord.query.all()
       df = grades_to_dataframe(records)
       df = prepare_grades_dataframe(df)

       advice_text, source, cached = get_cached_advice(df)

       return render_template(
           "ai_advice.html",
           advice_text=advice_text,
           source=source,
           cached=cached,
       )
   ```

2. Создай `templates/ai_advice.html`:

   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>Совет от AI</title>
   </head>
   <body>
       <h2>🤖 Совет по успеваемости</h2>

       {% if source == 'fallback' %}
           <p><em>Модель недоступна, показан совет по локальным правилам.</em></p>
       {% elif cached %}
           <p><em>Ответ взят из кэша (данные не менялись).</em></p>
       {% endif %}

       <p>{{ advice_text }}</p>

       <a href="{{ url_for('dashboard') }}">← Назад к аналитике</a>
   </body>
   </html>
   ```

3. Добавь на `dashboard.html` кнопку-переход с индикацией загрузки (LLM думает несколько секунд, пользователя надо предупредить):

   ```html
   <p>
       <a href="{{ url_for('ai_advice') }}"
          onclick="this.textContent='⏳ AI думает...'">
          🤖 Получить совет от AI
       </a>
   </p>
   ```

4. Проверь устойчивость руками:
   - модель включена → приходит совет от AI;
   - выключи Ollama (или интернет) → приходит fallback, страница не падает;
   - обнови страницу с теми же данными → ответ из кэша, мгновенно.

✅ **Чек-поинт:** `/ai-advice` защищён логином, показывает совет, честно отмечает fallback/кэш и не падает при выключенной модели.

Коммит:

```powershell
git add app.py templates/ai_advice.html templates/dashboard.html
git commit -m "feat: add AI advice page with loading and fallback UI"
```

---

## 📄 Документация промптов

Создай `docs/prompts.md` и запиши туда финальные промпты, которые сработали, и те, что не сработали. Это требование чек-листа этапа и полезная привычка: промпт — это тоже код.

```markdown
# Промпты проекта

## Совет по успеваемости (рабочий)
Роль: доброжелательный школьный тьютор.
Задача: 3 коротких совета, что подтянуть.
Формат: простой текст, без Markdown.
Что улучшило ответ: явный запрет придумывать цифры.

## Что не сработало
- Без указания формата модель отвечала длинными абзацами с Markdown.
- Без запрета «не придумывай цифры» модель иногда выдумывала оценки.
```

---

## 🛡️ Финальный чек-лист перед Pull Request

- [ ] Выбран и настроен провайдер (Ollama или OpenAI).
- [ ] Ключи/адреса только в `.env`, есть `.env.example`, `.env` в `.gitignore`.
- [ ] Вся AI-логика изолирована в `ai_service.py`.
- [ ] Контекст строится из **метрик**, а не из сырых строк БД.
- [ ] Запрос к модели обёрнут в `try/except` и имеет `timeout`.
- [ ] Реализован fallback по локальным правилам.
- [ ] Ответы кэшируются в БД по хэшу контекста.
- [ ] Есть route `/ai-advice`, защищённый `@login_required`.
- [ ] UI показывает загрузку, ответ и метку fallback/кэш.
- [ ] Промпт и ключи не попадают в UI и логи.
- [ ] Приложение не падает при выключенной модели / без интернета.
- [ ] Промпты записаны в `docs/prompts.md`.
- [ ] В `DEVLOG.md` записаны удачные и неудачные промпты.

Финальный коммит этапа:

```powershell
git add .
git commit -m "feat: complete AI study assistant"
```

---

## 💡 Вопросы для рефлексии

1. Почему мы отправляем в модель метрики, а не все строки из БД? (токены, деньги, приватность)
2. Почему нельзя доверять LLM вычисление среднего балла?
3. Зачем нужен fallback, если модель обычно работает?
4. Что именно мы кладём в хэш кэша и почему?
5. Чем плоха идея дать LLM выполнять SQL-запросы к нашей базе?
6. Как изменится код, если завтра захотим сменить Ollama на OpenAI?
7. Где в промпте «роль», «контекст», «задача» и «формат вывода»?

---

## 📝 DEVLOG-шаблон для этапа 4

```markdown
# 📘 DEVLOG: Этап 4

**Дата:** ____
**Время:** ____
**Тема:** Интеграция LLM — AI-советник по успеваемости

## ✅ Сделано

- Подключён провайдер: ____ (Ollama / OpenAI).
- Создан `ai_service.py` с изолированной AI-логикой.
- Контекст собирается из метрик этапа 3.
- Реализованы обработка ошибок и fallback.
- Ответы кэшируются в таблице `AiInsight`.
- Добавлен route `/ai-advice` и страница с загрузкой/ошибкой.

## 💡 Инсайты

- Удачный промпт: ...
- Неудачный промпт: ...

## 🧱 Сложности

- ...

## ❓ Вопросы

- ...

## 🎯 Следующий шаг

- Подготовиться к Этапу 5: финализация, деплой и портфолио.
```

---

🎉 **Этап завершён, когда приложение даёт полезный совет по реальным данным ученика, честно отмечает fallback/кэш и не падает при выключенной модели.**
