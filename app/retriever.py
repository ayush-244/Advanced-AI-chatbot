import wikipedia
import re


class WikiRetriever:

    def __init__(self):

        # Use English Wikipedia
        wikipedia.set_lang("en")


    def clean_query(self, query: str) -> str:

        query = query.lower()

        # Expand common abbreviations
        abbreviations = {
            r'\bcm\b': 'chief minister',
            r'\bpm\b': 'prime minister',
            r'\bup\b': 'uttar pradesh',
            r'\bmp\b': 'madhya pradesh',
            r'\bmh\b': 'maharashtra',
            r'\buk\b': 'uttarakhand',
            r'\bus\b': 'united states',
            r'\busa\b': 'united states',
            r'\buk\b(?=.*kingdom)': 'united kingdom',
            r'\bceo\b': 'chief executive officer',
            r'\bcto\b': 'chief technology officer',
            r'\bai\b': 'artificial intelligence',
            r'\bml\b': 'machine learning'
        }

        for abbr, full in abbreviations.items():
            query = re.sub(abbr, full, query)


        # Remove common filler words (DO NOT remove "the")
        remove_words = [
            "what is", "who is", "define", "explain",
            "tell me about", "please", "pls",
            "kaun hai", "kya hai", "batao"
        ]

        for word in remove_words:
            query = query.replace(word, "")


        # Remove symbols and extra spaces
        query = re.sub(r"[^a-zA-Z0-9\s]", "", query)
        query = " ".join(query.split())

        # Format for Wikipedia
        return query.title()


    def try_page(self, title: str):

        try:
            page = wikipedia.page(title, auto_suggest=False)

            # Use more sentences for better facts
            summary = wikipedia.summary(
                page.title,
                sentences=8,
                auto_suggest=False
            )

            return summary

        except:
            return None


    def search(self, query: str):

        try:

            # Clean input
            clean_query = self.clean_query(query)

            # Check if user is asking about a current position
            query_lower = query.lower()

            is_position_query = any(
                word in query_lower for word in [
                    "who is the", "who is current",
                    "current cm", "current pm"
                ]
            )


            # Try direct page first
            summary = self.try_page(clean_query)

            if summary:
                return summary


            # Search Wikipedia
            results = wikipedia.search(clean_query, results=10)

            if not results:
                return None


            # Prefer person pages for position queries
            if is_position_query:

                person_results = [
                    r for r in results
                    if not any(
                        generic in r.lower() for generic in [
                            "list of", "government of",
                            "chief minister of",
                            "prime minister of",
                            "president of",
                            "office of"
                        ]
                    )
                ]

                for title in person_results[:3]:

                    summary = self.try_page(title)

                    if summary:
                        return summary


            # Rank results by relevance
            query_clean = clean_query.lower()

            best_results = sorted(
                results,
                key=lambda t: (
                    0 if t.lower() == query_clean
                    else 1 if t.lower().startswith(query_clean)
                    else 2 if query_clean in t.lower()
                    else 3
                )
            )


            # Try top results
            for title in best_results[:5]:

                summary = self.try_page(title)

                if summary:
                    return summary


            # Fallback to original query
            summary = self.try_page(query)

            if summary:
                return summary


            return None


        except wikipedia.exceptions.DisambiguationError as e:

            try:
                page = wikipedia.page(e.options[0])

                return wikipedia.summary(
                    page.title,
                    sentences=8
                )

            except:
                return None


        except Exception as e:

            print("Wiki error:", e)

            return None
