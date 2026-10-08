# VERCEL DEPLOY — инструкция для владельца

## Проблема
Vercel-токены протухли 9 сентября 2026. Деплой stackpickr.vercel.app невозможен без повторного входа.

## Быстрое решение (2 минуты)

1. Откройте в браузере: https://vercel.com/oauth/device?user_code=SGDP-FNCC
2. Нажмите "Approve" (разрешить доступ)
3. Скажите мне — я продолжу деплой автоматически

## Альтернатива (если не работает)

1. Откройте https://vercel.com/login
2. Войдите через GitHub (аккаунт Alex20Sas12)
3. После входа скажите мне — я задеплою через GitHub Actions

## Что будет задеплоено

47 страниц (было 40):
- ✅ AvitoVIP Transfer review (/transfer/avitovip/) — $3/покупка
- ✅ Гайд "How to book airport transfer in Turkey" (/guides/...)
- ✅ Хаб /transfer/ для трансферного контента
- ✅ 3 новых vs-страницы: Boardmix vs Miro, Boardmix vs Mural, InVideo vs Canva
- ✅ /privacy/ (требование Adsterra)
- ✅ Фикс витринной ссылки (shablonypro.dpdns.org)
- ✅ Обновлённая навигация (Transfers в меню)

## После деплоя

Я автоматически:
1. Проверю все 47 страниц (200 OK)
2. Сабмитну новые URL в IndexNow
3. Обновлю STATE.md
4. Запущу кроны автопилота

## Кроны автопилота (уже созданы)

| Крон | Расписание | Что делает |
|------|-----------|-----------|
| health | 8:00, 20:00 | Проверка сайта + кронов |
| content | 9:00 | Новая страница/улучшение |
| traffic | 12:00 | IndexNow + GSC мониторинг |
| report | 20:00 | Вечерняя сводка |

## Контакты

- GitHub repo: https://github.com/Alex20Sas12/stackpickr
- Сайт: https://stackpickr.vercel.app
- Vercel project: keyt9750-7169s-projects/stackpickr
