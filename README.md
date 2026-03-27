# QoS Network Measurement with Ping and Spruce

## Описание
Проект измеряет сетевые метрики QoS (в первую очередь задержку и потери) с помощью `ping` и заготовок под Spruce.

## Возможности
- периодические измерения RTT до целевого хоста;
- сохранение сырых результатов в CSV;
- расчёт агрегированной статистики по каждому запуску;
- построение гистограммы задержек.

## Структура проекта
- `src/main.py` — CLI и orchestration полного прогона измерений;
- `src/ping_probe.py` — одиночный ping и парсинг RTT;
- `src/stats.py` — расчёт статистик и запись в CSV;
- `src/plots.py` — построение гистограммы задержек;
- `results/` — сырые данные и графики;
- `report/` — отчётные материалы;
- `tests/` — автотесты.

## Установка
```bash
python3 -m venv venv
source venv/bin/activate
pip install pandas numpy matplotlib
```

## Запуск
```bash
python src/main.py --target 8.8.8.8 --duration 60 --interval 1
```

После выполнения появятся файлы:
- `results/raw/ping_results_<run_id>.csv`;
- `results/raw/ping_results.csv`;
- `results/raw/ping_stats.csv`;
- `results/plots/latency_histogram_<run_id>.png`.

## Эксперимент в Mininet
Минимальный поток:
1. поднять топологию из `mininet/topology.py`;
2. задать сценарий нагрузки/деградации канала;
3. выполнять измерения из `src/main.py` между узлами Mininet;
4. собрать артефакты (CSV + графики) для отчёта.

## Результаты
Для анализа использовать:
- `ping_stats.csv` как сводную таблицу по прогонам;
- гистограммы как визуализацию распределения RTT;
- raw-CSV как первичные данные для воспроизводимости.

## Отчёт
См. пошаговый шаблон в `report/REPORT_TESTS_GUIDE.md`.

## Тесты
Запуск автотестов:
```bash
python -m unittest discover -s tests -v
```
