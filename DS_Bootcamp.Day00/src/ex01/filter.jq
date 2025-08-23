# Извлекает только нужные поля из JSON и преобразуем в CSV
.items[] | [.id, .created_at, .name, .has_test, .alternate_url] | @csv