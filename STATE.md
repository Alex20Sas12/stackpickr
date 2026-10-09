# StackPickr (cmpsite) — State

## Проект
Статический сайт сравнений софта/хостинга с affiliate-монетизацией (Admitad) + Adsterra-реклама.
Домен: https://stackpickr.vercel.app (Vercel, статика, 40 страниц)

## Деньги (воронка)
- **Admitad affiliate**: Cloudways ($108), is*hosting (9-30%), Tapfiliate ($178), Boardmix (32%), InVideo (16-32%), AvitoVIP ($3)
- **Adsterra**: zone 6030096, NativeBanner_1 (1x4) — показы есть, $0 на балансе (низкий CPM RU-трафика)
- **AvitoVIP**: ДОБАВЛЕН 08.10.2026 — review + guide + hub /transfer/

## Критические проблемы (найдены 08.10)
| Проблема | Severity | Статус |
|----------|----------|--------|
| ~~Vercel-токены протухли (09.09)~~ | CRITICAL | ✅ ИСПРАВЛЕНО 08.10 21:50 — вход через email-код (keyt9750@gmail.com), деплой OK |
| ~~Cloudways/is*hosting CTA → голые сайты без affiliate-ссылок~~ | HIGH | ✅ is*hosting ПОДКЛЮЧЁН НАПРЯМУЮ 08.10 (программа is*hosting internal: 50% first purchase + 20% lifetime, вывод $20+ на PayPal/крипту/карту). Ссылка https://ishosting.com/affiliate/Nzk5NiM2 вшита на ВСЕ 7 is*hosting-страниц + dual-CTA на vs-страницах. Cloudways ждёт Admitad 2FA (support@mitgo.com молчит с 29.09). |
| ~~Навигация /tools/ → 404 на boardmix-vs-miro/mural, invideo-vs-canva~~ | HIGH | ✅ ЗАДЕПЛОЕНО 08.10 (3 новые страницы, 200 OK) |
| ~~AvitoVIP $3 не монетизировался (0 страниц)~~ | HIGH | ✅ ЗАДЕПЛОЕНО 08.10: /transfer/avitovip/ с kjuzv.com CTA + гайд + хаб |
| ~~Нет /privacy/~~ | MEDIUM | ✅ ЗАДЕПЛОЕНО |
| ~~Витринная ссылка → мёртвый shablony-pro.vercel.app~~ | MEDIUM | ✅ ЗАДЕПЛОЕНО (shablonypro.dpdns.org) |
| ~~SEO-backlog крон a7a4d645691d сломан (DSML-баг)~~ | MEDIUM | ✅ Пересоздан как content-крон cc9acb7a2028 |
| GSC-квота исчерпывается (общая ~10/день на все сайты) | LOW | Лимит 2/сайт/день соблюдается |

## Кроны
- GSC-крон 4a2686df505a: работает, ежедневно 10:10, сабмитит URL (квота ~2/сайт/день)
- SEO-backlog-крон a7a4d645691d: сломан (DSML), не выполняет backlog
- Дайджест ea6bf4fdb6cb: не работает (кронов нет в системе — потеряны при миграции)

## Файлы
- Код: cmpsite/sitegen.py + pages.py
- Данные: cmpsite/data/*.json
- Деплой: cmpsite/site/ → vercel --prod (требует auth)

## Следующие шаги (дедлайны)
1. [до 09.10 22:00] Cloudways: дождаться апрува на alexford0289@gmail.com (himalaya envelope list --account alex | grep -i cloudways) → забрать affiliate-ссылку из панели unified.cloudways.com/account/referral → вписать в data/config.json links.cloudways → sitegen.py → деплой.
2. [10.10] Проверить GSC: появились ли новые URL (/transfer/*, /tools/*) в индексе после IndexNow-сабмита 08.10.
3. [ежедневно, content-крон] Триггер A1: новый запрос в geo_audit/gsc_queries.csv с impressions>=8 без страницы → создать страницу, пересборка, деплой, IndexNow.

## Автопилот (СОЗДАН 08.10)
| Крон | ID | Расписание | Что делает |
|------|----|-----------|-----------|
| health | 56d9c3299a42 | 8:00, 20:00 | сайт 200? sitemap >40? CTA не пустые? кроны не молчат? |
| content | cc9acb7a2028 | 9:00 | триггеры SEO-BACKLOG (A1: новый запрос impressions>=8 → страница) |
| traffic | d4bcf1a69171 | 12:00 | IndexNow новых URL + проверка GSC-крона |
| report | f22749669341 | 20:00 | вечерняя сводка (в сводку 20:00) |
- GSC-крон 4a2686df505a: работает, ежедневно 10:10 (квота 2/сайт/день)
- SEO-backlog a7a4d645691d: сломан DSML-багом 04.10 — пересоздан как content-крон выше

## Уборка (фаза 2B, 08.10)
- Карантин `_quarantine/2026-10-08/` (3 МБ, ~120 файлов): gsc_*.py, adsterra_*.py, make_shots*.py, старые .png/.jpg скриншоты, deploy_*.log — одноразовые скрипты отладки GSC/Adsterra, ни на что не влияют (проверено: sitegen + сайт 200 OK после уборки). Удаление навсегда: 15.10, если ничего не сломается.

## Юнит-экономика (фаза 3C, 08.10)
| Оффер | Ставка | Сеть | Статус |
|---|---|---|---|
| is*hosting | 50% первой покупки + 20% lifetime | DIRECT | ✅ ЖИВАЯ на сайте |
| Cloudways | $50-125/продажа (Hybrid) | DIRECT | ⏳ заявка на модерации (ответ ≤24ч на alexford0289@gmail.com, крон проверяет) |
| Tapfiliate | $178/тариф | Admitad | ✅ |
| Boardmix | 32% | Admitad | ✅ |
| InVideo | 16-32% | Admitad | ✅ |
| AvitoVIP | $3/покупка | Admitad | ✅ |
| Adsterra | CPM копеечный | — | фон, не зарплата |

## GitHub
Репо: https://github.com/Alex20Sas12/stackpickr (создан 08.10, workflow .github/workflows/deploy.yml готов — нужен VERCEL_TOKEN secret после перелогина)
