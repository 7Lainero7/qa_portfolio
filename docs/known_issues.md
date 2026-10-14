# Known Issues

## BUG-001: PATCH принимает `null` для `category`

**Severity:** Medium  
**Priority:** P2  
**Status:** Open

### Шаги воспроизведения

1. Создать расход: `POST /api/expenses` с `{"title": "Test", "amount_cents": 1000}`
2. Обновить: `PATCH /api/expenses/{id}` с `{"category": null}`

### Ожидаемый результат

`422 Unprocessable Entity` — поле `category` не может быть `null` (в БД `NOT NULL`).

### Фактический результат

`200 OK` с `category = "other"`.

### Комментарий

`exclude_unset=True` в `repository.py` не различает "поле не передано" и "передано как `null`".

---

## BUG-002: `category` с только пробелами принимается как `"other"`

**Severity:** Low  
**Priority:** P3  
**Status:** Open

### Шаги воспроизведения

1. Создать расход: `POST /api/expenses` с `{"title": "Test", "amount_cents": 1000, "category": "   "}`

### Ожидаемый результат

`422 Unprocessable Entity` — значение состоит только из пробелов.

### Фактический результат

`201 Created` с `category = "other"`.

### Комментарий

Валидатор делает `strip()` и при пустом результате возвращает дефолт `"other"` вместо ошибки.

---

## BUG-003: `category` с только пробелами принимается как `"other"`

**Severity:** Low  
**Priority:** P3  
**Status:** Open

### Шаги воспроизведения

1. Создать расход: `POST /api/expenses` с `{"title": "Test", "amount_cents": 1000, "category": "   "}`

### Ожидаемый результат

`422 Unprocessable Entity` — значение состоит только из пробелов.

### Фактический результат

`201 Created` с `category = "other"`.

### Комментарий

Валидатор делает `strip()` и при пустом результате возвращает дефолт `"other"` вместо ошибки.

---

## Примечание

Все баги обнаружены при тестировании и задокументированы.  
Статус `Open` означает, что баг подтверждён, но не исправлен.