## Вспомогательные компоненты
- `config_generator.py` - реализует структуру для работы с конфигурационным файлом блокчейн системы. Позволяет считывать и изменять значения параметров. Изменения по умолчанию сохраняются в новом конфигурационном файле.
- `parse_bench_output.py` - позволяет спарсить значения TPS и Droprate из логов бенмарка.
- `serializer.py` - сериализует и десериализует основные структуры в байты и обратно (для передачи данных в matlab-сервер).
- `images_cleaner.py` - удаляет неименованные Docker-котейнеры и образы из хоста.
