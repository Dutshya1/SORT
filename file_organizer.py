import shutil
import logging
from pathlib import Path

class FileOrganizer:
    def __init__(self, directory_path: str):
        self.directory = Path(directory_path)
        if not self.directory.exists():
            raise FileNotFoundError(f"Директория '{directory_path}' не найдена.")
        
        # 1. Словарь с расширениями
        self.extensions_map = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff', '.ico', '.webp'],
            'Documents': ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.csv', '.md', '.odt'],
            'Audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
            'Video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.iso']
        }
        self.others_dir = 'Others'

        # Настройка логирования
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
        self.logger = logging.getLogger(__name__)

    def _get_target_folder(self, file_path: Path) -> str:
        """Определяет целевую папку по расширению файла."""
        extension = file_path.suffix.lower()
        for folder, extensions in self.extensions_map.items():
            if extension in extensions:
                return folder
        return self.others_dir

    def _handle_duplicate(self, target_path: Path) -> Path:
        """Добавляет индекс к имени файла, если такой файл уже существует."""
        if not target_path.exists():
            return target_path

        stem = target_path.stem
        suffix = target_path.suffix
        counter = 1
        
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = target_path.with_name(new_name)
            if not new_path.exists():
                return new_path
            counter += 1

    def organize(self):
        """Сканирует директорию и перемещает файлы."""
        self.logger.info(f"Начинаю сортировку файлов в: {self.directory}")

        # Создаем необходимые папки
        for folder in self.extensions_map.keys():
            (self.directory / folder).mkdir(exist_ok=True)
        (self.directory / self.others_dir).mkdir(exist_ok=True)

        for item in self.directory.iterdir():
            # Пропускаем директории и сам скрипт (если он в той же папке)
            if item.is_dir() or item.name == Path(__file__).name:
                continue

            target_folder_name = self._get_target_folder(item)
            target_dir = self.directory / target_folder_name
            target_path = target_dir / item.name

            # Обработка дубликатов
            final_path = self._handle_duplicate(target_path)

            try:
                shutil.move(str(item), str(final_path))
                self.logger.info(f"Перемещено: '{item.name}' -> '{target_folder_name}/{final_path.name}'")
            except Exception as e:
                self.logger.error(f"Ошибка при перемещении '{item.name}': {e}")

        self.logger.info("Сортировка завершена.")

if __name__ == "__main__":
    # Пример использования
    # Замените путь на нужную директорию или используйте '.' для текущей
    target_dir = input("Введите путь к директории для сортировки (оставьте пустым для текущей): ").strip()
    if not target_dir:
        target_dir = "."
    
    try:
        organizer = FileOrganizer(target_dir)
        organizer.organize()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
