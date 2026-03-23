import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def generate_post(topic: str, tone: str = "カジュアル", max_chars: int = 500) -> str:
    """Generate a Threads post using Claude."""
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=1024,
        thinking={"type": "adaptive"},
        system=(
            "あなたはThreads（Meta社のSNS）向けの投稿コンテンツを作成するライターです。"
            "自然で読みやすく、エンゲージメントを得やすい文章を書いてください。"
            "ハッシュタグは3〜5個程度付けてください。"
            "必ず指定された文字数以内に収めてください。"
        ),
        messages=[{
            "role": "user",
            "content": (
                f"テーマ: {topic}\n"
                f"口調: {tone}\n"
                f"最大文字数: {max_chars}文字\n\n"
                "上記の条件でThreadsに投稿する文章を1つ作成してください。"
                "本文のみ出力し、前置きや説明は不要です。"
            ),
        }],
    ) as stream:
        text = stream.get_final_message()

    content = next(
        (block.text for block in text.content if block.type == "text"), ""
    ).strip()

    if len(content) > max_chars:
        content = content[:max_chars]

    return content


if __name__ == "__main__":
    topic = os.getenv("POST_TOPIC", "テクノロジー")
    tone = os.getenv("POST_TONE", "カジュアル")
    post = generate_post(topic, tone)
    print("生成された投稿:\n")
    print(post)
    print(f"\n文字数: {len(post)}")
