import os
import sys
import logging
import requests
from dotenv import load_dotenv
from content_generator import generate_post

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

THREADS_API_BASE = "https://graph.threads.net/v1.0"


def _get_config() -> dict:
    token = os.getenv("THREADS_ACCESS_TOKEN")
    user_id = os.getenv("THREADS_USER_ID")
    if not token or not user_id:
        raise EnvironmentError(
            "THREADS_ACCESS_TOKEN と THREADS_USER_ID を .env に設定してください。"
        )
    return {"token": token, "user_id": user_id}


def create_container(user_id: str, token: str, text: str) -> str:
    """Step 1: Create a media container and return its ID."""
    url = f"{THREADS_API_BASE}/{user_id}/threads"
    resp = requests.post(
        url,
        params={"access_token": token},
        json={"media_type": "TEXT", "text": text},
        timeout=30,
    )
    resp.raise_for_status()
    container_id = resp.json()["id"]
    logger.info("コンテナ作成完了: %s", container_id)
    return container_id


def publish_container(user_id: str, token: str, container_id: str) -> str:
    """Step 2: Publish the container and return the post ID."""
    url = f"{THREADS_API_BASE}/{user_id}/threads_publish"
    resp = requests.post(
        url,
        params={"access_token": token},
        json={"creation_id": container_id},
        timeout=30,
    )
    resp.raise_for_status()
    post_id = resp.json()["id"]
    logger.info("投稿完了! 投稿ID: %s", post_id)
    return post_id


def post_to_threads(text: str) -> str:
    """Create and publish a Threads post. Returns the post ID."""
    cfg = _get_config()
    container_id = create_container(cfg["user_id"], cfg["token"], text)
    post_id = publish_container(cfg["user_id"], cfg["token"], container_id)
    return post_id


def run_once(dry_run: bool = False) -> None:
    """Generate content and post to Threads."""
    topic = os.getenv("POST_TOPIC", "テクノロジー")
    tone = os.getenv("POST_TONE", "カジュアル")

    logger.info("コンテンツ生成中... テーマ: %s / 口調: %s", topic, tone)
    text = generate_post(topic, tone)
    logger.info("生成された投稿 (%d文字):\n%s", len(text), text)

    if dry_run:
        logger.info("[DRY RUN] 実際には投稿しません。")
        return

    post_id = post_to_threads(text)
    logger.info("✅ 投稿成功! ID: %s", post_id)


def test_connection() -> None:
    """Verify the API token without posting."""
    cfg = _get_config()
    url = f"{THREADS_API_BASE}/{cfg['user_id']}"
    resp = requests.get(
        url,
        params={"fields": "id,username", "access_token": cfg["token"]},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    logger.info("✅ 接続OK! ユーザー: @%s (ID: %s)", data.get("username"), data.get("id"))


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--test" in args:
        test_connection()
    elif "--dry-run" in args:
        run_once(dry_run=True)
    else:
        run_once()
