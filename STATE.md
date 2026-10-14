# StackPickr (cmpsite) — State

Обновлено: 14.10.2026 16:20 МСК

## Проект
Статический сайт сравнений хостинга/софта с affiliate-монetизацией + Adsterra.
Домен: https://stackpickr.vercel.app (Vercel, статика, **47 страниц**)

## 💰 Заработано за всё время: **$0**
Причина (проверено 14.10): сайт живёт 23 дня, но **индексировано 5 из 47 URL**
→ ~90% страниц не существуют в поиске → трафика нет → кликов в партнёрки нет.
Вторая причина: 8 страниц Cloudways вели читателей на голый сайт без affiliate-ссылки
(исправлено 14.10).

## Базовая линия (R7)
- До изменений 14.10: 47 страниц, 32 с партнёрским CTA, **8 страниц с CTA без монетизации**
  (все cloudways), 0 аналитики, 5/47 URL в индексе.
- После: 32 страницы с партнёрским CTA, **0 страниц без монетизации**, 47/47 URL в IndexNow
  + Yandex ping, деплой верифицирован (200, 47 URL).

## Критические проблемы (14.10)
| Проблема | Severity | Статус |
|----------|----------|--------|
| 4 крона StackPickr (health/content/traffic/report) удалены ~08.10 при инциденте очистки | CRITICAL | ❌ НЕ ВОССОЗДАНЫ — next action 1 |
| Конфиг Hermes бит (дублирующий `enabled: false` в блоке `custom`) → новые правки не применялись, пиннинг моделей не работал | CRITICAL | ✅ ИСПРАВЛЕНО 14.10; `hermes config check` → rc=0 |
| Сайт отдавал 404 на ВСЕХ страницах (мой ошибочный деплой корня репо) | CRITICAL | ✅ ВОССТАНОВЛЕНО (`deploy site --prod`); /, /hosting/, /hosting/cloudways/, /sitemap.xml = 200 |
| Деплой уходил в **другой** Vercel-проект (`cmpsite-lyart`), созданный случайно; живой сайт не обновлялся 6 дней | CRITICAL | ✅ `--project stackpickr --scope keyt9750-7169s-projects` + `deploy.py` |
| Cloudways-CTA → голый сайт: 8 страниц (обзор + 7 vs) без комиссионной ссылки | HIGH | ✅ `ALT_MONETISE={cloudways:ishosting}` в `cta_box()`; live: /hosting/cloudways/ aff:1 |
| Хаб /hosting/ без партнёрского CTA | HIGH | ✅ `cta_box('ishosting')`; live aff:1 |
| GitHub Actions не деплоил никогда: workflow на `main`, репо на `master` | HIGH | ⚠️ workflow вхолостую; деплой теперь `python deploy.py` (проверено) |
| 26 из 28 падающих кронов системы идут с `model=None` → HTTP 503 Gemini structure_limit | HIGH (системный) | ⚠️ Кроны с явной моделью (qwen3.8-flash) держатся. Не чинил: влияет на все проекты, требует смены основного |
| Индексация 5/47 URL (главный рычаг денег) | HIGH | ⚠️ 47 URL → IndexNow 200 + Yandex ping 200 (14.10); GSC-крон +2 URL/день |
| НЕТ аналитики — не видно ни одного визита, конверсию мерить нельзя | HIGH | ⏳ GoatCounter требует регистрации |
| `geo_audit/` не существует → триггер A1 (контент по запросам GSC) мёртв | MEDIUM | ✅ СОЗДАН 14.10 `geo_audit.py` (Google Suggest, без регистрации) → `fabrika/geo_audit/gsc_queries.csv`: 144 запросов, **68 дыр**. Самая чистая: `collaboration whiteboard` (score=0). Проверено `--check` OK |
| Cloudways affiliate на 24h-модерации | MEDIUM | ⏳ Апрува нет (14.10 16:10 МСК, все входящие alexford0289@gmail.com); крон 471fb4e0b8b6 следит |

## Кроны (фактически, 14.10)
**Живые для StackPickr:**
| ID | Расписание | Что | Денежный след |
|---|---|---|---|
| 4a2686df505a | 10:10 ежедневно | GSC IndexNow, квота 2/сайт/день | URL в индексе → трафик → клик в партнёрку |
| 471fb4e0b8b6 | 10:00/18:00 | апрув Cloudways (почта + панель) | ссылка Cloudways $50-125/продажа |
| a7a4d645691d | вс 12:30 | SEO-backlog триггеры | ✅ geo_audit.py создан — триггеры снова живы |

**Воссозданы 14.10:** health `7097de8b595b` (8/20), content `ed8133ecd8db` (9:00),
traffic `a8ee9e6b505e` (12:00), report `4e61f07dc6f8` (20:00) — все deliver=local,
закреплены на `gpt-6-astra` / `custom:frontierspace` (единственная связка, где кроны реально отвечают).
Проверка провайдеров 14.10: `q`/qwen — не имя провайдера в CLI; `custom` — группа без кредов (503);
`omni` — локальный OmniRoute :20128 мёртв (502).

## Автопилот — что должно быть (фаза 5)
| Роль | Расписание | Действие → метрика → оплата |
|---|---|---|
| health 2×/день | 8:00, 20:00 | `python deploy.py`-проверки: / = 200, sitemap ≥40, ≥30 страниц с партнёрским CTA; падало → 🚨 + пересборка |
| content 1×/день | 9:00 | новая vs-страница + `python deploy.py` + IndexNow → рост страниц с партнёрским CTA |
| traffic 1×/день | 12:00 | `gsc_index_queue.py` + IndexNow; цель >25 URL в индексе к 21.10, 47 к 28.10 |
| report 1×/вечер | 20:00 | URL в индексе (база 5 → цель 47), что задеплоено |

## Файлы
- `sitegen.py` (сборка), `pages.py` (контент), `data/*.json`
- **`deploy.py`** — единый вход: пересборка → commit → push → `vercel deploy site --prod`
  → live-проверка (exit 0 только если / = 200 и sitemap ≥40 URL)
- `vercel.json` — cleanUrls, статика из `site/`
- `gsc_index_queue.py` — очередь GSC через CDP 9232
- Карантин `_quarantine/2026-10-08/` (3 МБ) + `_quarantine/2026-10-11/` (cw_*.py)

## Юнит-экономика (фаза 3C)
| Оффер | Ставка | Сеть | Статус на сайте |
|---|---|---|---|
| is*hosting | 50% первой покупки + 20% lifetime | DIRECT | ✅ единственная реально платящая сейчас |
| Cloudways | $50-125/продажа (Hybrid) | DIRECT | ⏳ модерация; читатель ведётся на ishosting alt-CTA |
| Tapfiliate | $178/тариф | Admitad | ✅ |
| Boardmix | 32% | Admitad | ✅ |
| InVideo | 16-32% | Admitad | ✅ |
| AvitoVIP | $3/покупка | Admitad | ✅ |
| Adsterra | CPM копеечный | — | фон, не зарплата |

## GitHub
Репо https://github.com/Alex20Sas12/stackpickr, ветка `master`.
Workflow `.github/workflows/deploy.yml` смотрит на `main` → не срабатывал.
Деплой теперь через `python deploy.py` (токен из `%APPDATA%\Roaming\com.vercel.cli\auth.json`).

## Следующие шаги (деدлайны)
1. [сегодня 18:00] Воссоздать 4 крона (health/content/traffic/report) — с `deploy.py` в health/traffic,
   deliver=local в сводку 20:00, модель которая держит (не та что с 503).
2. [сегодня 20:00] Аналитика (GoatCounter/Plausible, free) → без неё конверсия не мерится и фаза 3B мертва.
   Нужна регистрация → спросить владельца.
3. [21.10] Цель: ≥25 URL в индексе. Контроль через `gsc_index_queue.py`.

## Чего НЕ делать дальше
- Не деплоить с корня репо (404 на всём сайте). Только `deploy.py` / `vercel deploy site`.
- Не создавать новые Vercel-проекты — только `--project stackpickr`.
- Не трогать Admitad (2FA заблокирован с 29.09, поддержка молчит).
- Не масштабировать Adsterra ($0 за 6 млн показов).
- Не ждать Cloudways: alt-CTA на ishosting уже держит комиссию.
