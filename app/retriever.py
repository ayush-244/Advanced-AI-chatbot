import wikipedia
import re


class WikiRetriever:

    def __init__(self):
        # Always use English Wikipedia
        wikipedia.set_lang("en")


    def clean_query(self, query: str) -> str:
        """
        Clean and normalize user query
        """

        query = query.lower()

        # Expand common abbreviations BEFORE removing words
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

        # Remove common useless words
        remove_words = [
            "what is", "who is", "define", "explain",
            "tell me about", "please", "pls",
            "kaun hai", "kya hai", "batao", "the"
        ]

        for word in remove_words:
            query = query.replace(word, "")

        # Remove symbols
        query = re.sub(r"[^a-zA-Z0-9\s]", "", query)

        # Remove extra spaces
        query = " ".join(query.split())

        # Capitalize for Wikipedia
        return query.title()


    def try_page(self, title: str):
        """
        Try loading a Wikipedia page safely
        """

        try:
            page = wikipedia.page(title, auto_suggest=False)
            summary = wikipedia.summary(
                page.title,
                sentences=5,
                auto_suggest=False
            )
            return summary
        except:
            return None


    def search(self, query: str):

        try:
            # Step 1: Clean query
            clean_query = self.clean_query(query)
            
            # Check if query is asking for current officeholder
            query_lower = query.lower()
            is_current_position_query = any(word in query_lower for word in [
                'who is the', 'who is current', 'current cm', 'current pm'
            ])

            # Step 2: Try direct page
            summary = self.try_page(clean_query)
            if summary:
                return summary

            # Step 3: Search Wikipedia
            results = wikipedia.search(clean_query, results=10)

            if not results:
                return None

            # Step 4: For position queries, try alternate searches
            if is_current_position_query and results:
                # Try to find person pages by looking for common patterns
                person_results = [
                    r for r in results 
                    if not any(generic in r.lower() for generic in [
                        'list of', 'government of', 'chief minister of',
                        'prime minister of', 'president of', 'office of'
                    ])
                ]
                
                # If we found person pages, try them first
                if person_results:
                    for title in person_results[:3]:
                        summary = self.try_page(title)
                        if summary:
                            return summary
            
            # Step 5: Try results with standard sorting
            query_lower_clean = clean_query.lower()
            best_results = sorted(
                results,
                key=lambda t: (
                    0 if t.lower() == query_lower_clean
                    else 1 if t.lower().startswith(query_lower_clean)
                    else 2 if query_lower_clean in t.lower()
                    else 3
                )
            )

            for title in best_results[:5]:

                summary = self.try_page(title)

                if summary:
                    return summary

            # Step 5: Fallback: try original query
            summary = self.try_page(query)

            if summary:
                return summary

            return None


        except wikipedia.exceptions.DisambiguationError as e:

            # Try first option if disambiguation
            try:
                page = wikipedia.page(e.options[0])
                return wikipedia.summary(page.title, sentences=5)
            except:
                return None


        except Exception as e:

            print("Wiki error:", e)
            return None
