
import re
from collections import Counter


class KeywordManager:

    def __init__(self):
        self.stop_words = {
            "the", "is", "are", "a", "an", "and",
            "or", "in", "on", "of", "to", "for",
            "with", "by", "this", "that", "it"
        }

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return text

    def extract_keywords(self, text, limit=20):
        words = self.clean_text(text).split()

        keywords = [
            word for word in words
            if word not in self.stop_words and len(word) > 2
        ]

        counts = Counter(keywords)

        return [
            {"keyword": word, "frequency": count}
            for word, count in counts.most_common(limit)
        ]

    def suggest_long_tail_keywords(self, keyword):
        keyword = keyword.strip()

        if not keyword:
            return []

        suggestions = [
            f"best {keyword}",
            f"how to use {keyword}",
            f"{keyword} for beginners",
            f"{keyword} tips and tricks",
            f"benefits of {keyword}",
            f"{keyword} complete guide",
            f"how does {keyword} work",
            f"{keyword} online"
        ]

        return suggestions

    def analyze_keyword(self, keyword, content):
        keyword_count = content.lower().count(keyword.lower())
        word_count = len(content.split())

        density = (
            round(keyword_count / word_count * 100, 2)
            if word_count else 0
        )

        return {
            "keyword": keyword,
            "occurrences": keyword_count,
            "word_count": word_count,
            "density_percent": density
        }

    def create_keyword_report(self, text, main_keyword):
        return {
            "main_keyword": main_keyword,
            "keyword_suggestions": self.suggest_long_tail_keywords(
                main_keyword
            ),
            "extracted_keywords": self.extract_keywords(text),
            "main_keyword_analysis": self.analyze_keyword(
                main_keyword, text
            )
        }


if __name__ == "__main__":

    manager = KeywordManager()

    sample_text = """
    Digital marketing helps businesses grow online.
    SEO and content marketing attract website visitors.
    """

    report = manager.create_keyword_report(
        sample_text,
        "digital marketing"
    )

    print("Asfandyar AI Studio - Keyword Manager")
    print(report)
