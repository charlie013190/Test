import os
import time
import logging
import schedule
from dotenv import load_dotenv
from threads_bot import run_once

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("threads_bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def job() -> None:
    try:
        logger.info("⏰ 定期投稿を開始します...")
        run_once()
    except Exception as exc:
        logger.error("投稿中にエラーが発生しました: %s", exc, exc_info=True)


def main() -> None:
    interval_hours = int(os.getenv("POST_INTERVAL_HOURS", "6"))
    logger.info("スケジューラー起動: %d時間ごとに投稿します。", interval_hours)

    # 起動直後に1回投稿する
    job()

    schedule.every(interval_hours).hours.do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
