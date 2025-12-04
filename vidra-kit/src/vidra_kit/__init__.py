import logging
from dataclasses import dataclass, field
from pathlib import Path
import uuid

get_logger = False

if get_logger:

    from rich.logging import RichHandler

    logging.basicConfig(
        level=logging.INFO,
        format="(%(name)s:%(lineno)d)  %(message)s ",
        handlers=[
            RichHandler(
                log_time_format="[%Y-%m-%d %H:%M:%S]",
                rich_tracebacks=True,
                show_time=True,
                show_level=True,
                show_path=False,
            )
        ],
    )

logger = logging.getLogger("vidra_kit")
logger.propagate = True  # keep default behavior

logging.getLogger("kombu").setLevel(logging.WARNING)
logging.getLogger("celery").setLevel(logging.INFO)


@dataclass
class TestSample:
    input_path: Path  # Path to input file or data
    output_dir: Path  # Unique path to output folder

    def __post_init__(self):
        # Ensure output_dir is a simple unique path by appending a UUID if not already unique
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
        else:
            unique_suffix = str(uuid.uuid4())[:8]  # Short UUID for simplicity
            self.output_dir = (
                self.output_dir.parent / f"{self.output_dir.name}_{unique_suffix}"
            )
            self.output_dir.mkdir(parents=True, exist_ok=True)


input_sample = "/home/kamba/neo/vidra_kit/media/src/samples/TearsOfSteel.mp4"


@dataclass
class IOConfig:
    input: str = input_sample  # Default input path
    output: Path = field(default_factory=lambda: IOConfig.generate_unique_output_path())

    @staticmethod
    def generate_unique_output_path(root: Path = Path("./media/outputs")) -> Path:
        unique_id = uuid.uuid4().hex[:8]  # short unique id
        path = root / f"run_{unique_id}"
        path.mkdir(parents=True, exist_ok=True)
        return path


__all__ = ["logger", "IOConfig"]
