"""Common selectors for web applications."""

class GoogleSelectors:
    """
    Selectors for Google's web interface.
    
    This class provides reliable selectors for interacting with Google search
    and its results. The selectors are maintained and tested for reliability.
    Always use google_search() for performing searches rather than manual steps.
    """
    
    SEARCH = {
        'search_input': '[name="q"]',  # Main search input field
        'search_button': '[name="btnK"]',  # Search button (prefer using submit)
        'result_links': '.g .yuRUbf > a',  # Main result links
        'result_titles': '.g h3.LC20lb',   # Result title elements
        'result_snippets': '.g .VwiC3b',   # Result description snippets
        'next_page': '#pnnext',            # Next page button
        'search_results': '#search',        # Main results container
        'organic_results': '.g',            # Individual result containers
        'featured_snippet': '.c2xzTb',      # Featured snippet box
        'knowledge_panel': '.kp-wholepage', # Knowledge panel
        'related_searches': '.gGQDvf',      # Related searches section
    }
    
    @staticmethod
    def get_result_by_index(index: int) -> str:
        """
        Get selector for nth search result (1-based index).
        More reliable than trying to click arbitrary elements.
        """
        return f'.g:nth-of-type({index}) .yuRUbf > a'
        
    @staticmethod
    def get_result_by_text(text: str) -> str:
        """
        Get selector for result containing specific text.
        Note: text matching is case-sensitive
        """
        return f'.g h3.LC20lb:contains("{text}")'
    
    @staticmethod
    def get_result_link_by_text(text: str) -> str:
        """
        Get selector for result link based on title text.
        This is the most reliable way to click specific results.
        """
        return f'.g h3.LC20lb:contains("{text}"):first'