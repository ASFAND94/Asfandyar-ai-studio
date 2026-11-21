class SEOManager:

    def analyze_content(self, title, content, keyword):
        words = content.split()
        word_count = len(words)

        return {
            "title": title,
            "keyword": keyword,
            "word_count": word_count,
            "title_length": len(title),
            "keyword_in_title": keyword.lower() in title.lower(),
            "keyword_in_content": keyword.lower() in content.lower(),
            "has_content": word_count > 0
        }

    def generate_meta_description(self, content, limit=155):
        description = " ".join(content.split())
        return description[:limit].rsplit(" ", 1)[0] if len(description) > limit else description

    def generate_seo_title(self, keyword):
        return f"{keyword} - Complete Guide"

    def get_seo_checklist(self):
        return [
            "Use a clear SEO title",
            "Write a useful meta description",
            "Use relevant keywords naturally",
            "Add descriptive image alt text",
            "Use internal links",
            "Use descriptive headings",
            "Create original content",
            "Ensure mobile-friendly design"
        ]
