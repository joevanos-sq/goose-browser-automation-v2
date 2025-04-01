"""Common selectors for web applications."""

class GoogleSelectors:
    """
    Selectors for Google's web interface.
    
    This class provides reliable selectors for interacting with Google search
    and its results. The selectors are maintained and tested for reliability.
    Always use google_search() for performing searches rather than manual steps.
    """
    
    # Result type identifiers
    RESULT_TYPES = {
        'organic': 'g',                    # Standard organic result class
        'featured': 'g featured-snippet',  # Featured snippet results
        'knowledge': 'kp-wholepage',       # Knowledge panel
        'advertisement': 'ads-ad',         # Advertisement results
    }
    
    SEARCH = {
        'search_input': '[name="q"]',      # Main search input field
        'search_button': '[name="btnK"]',  # Search button (prefer using submit)
        
        # Updated result selectors with type distinction
        'result_links': {
            'organic': 'a.zReHs:not(.Ww4FFb)',     # Organic result links (excluding ads)
            'featured': 'a.zReHs.ruhjFe',          # Featured snippet links
            'knowledge': 'a.zReHs.kpgb',           # Knowledge panel links
            'advertisement': 'a.zReHs.Ww4FFb',     # Advertisement links
        },
        
        # Container selectors
        'search_results': '#search',               # Main results container
        'organic_results': '.g:not(.Ww4FFb)',      # Organic result containers
        'featured_snippet': '.c2xzTb',             # Featured snippet box
        'knowledge_panel': '.kp-wholepage',        # Knowledge panel
        'related_searches': '.gGQDvf',            # Related searches section
        
        # Navigation
        'next_page': '#pnnext',                   # Next page button
    }
    
    @staticmethod
    def get_result_by_index(index: int, result_type: str = 'organic') -> str:
        """
        Get selector for nth search result (1-based index).
        
        Args:
            index: Position of result (1-based)
            result_type: Type of result ('organic', 'featured', 'knowledge', 'advertisement')
            
        Returns:
            str: Selector for the specified result
        """
        base_selector = GoogleSelectors.SEARCH['result_links'].get(result_type, GoogleSelectors.SEARCH['result_links']['organic'])
        return f'({base_selector}):nth-of-type({index})'
        
    @staticmethod
    def get_result_by_text(text: str, result_type: str = 'organic') -> str:
        """
        Get selector for result containing specific text.
        
        Args:
            text: Text to match in result
            result_type: Type of result ('organic', 'featured', 'knowledge', 'advertisement')
            
        Returns:
            str: Selector for the result containing the specified text
        """
        base_selector = GoogleSelectors.SEARCH['result_links'].get(result_type, GoogleSelectors.SEARCH['result_links']['organic'])
        return f'{base_selector}:has-text("{text}")'
    
    @staticmethod
    def get_result_link_by_text(text: str, result_type: str = 'organic') -> str:
        """
        Get selector for result link based on title text.
        This is the most reliable way to click specific results.
        
        Args:
            text: Text to match in result title
            result_type: Type of result ('organic', 'featured', 'knowledge', 'advertisement')
            
        Returns:
            str: Selector for the first result link containing the specified text
        """
        base_selector = GoogleSelectors.SEARCH['result_links'].get(result_type, GoogleSelectors.SEARCH['result_links']['organic'])
        return f'{base_selector}:has-text("{text}"):first'
        
    @staticmethod
    def get_result_type(element_classes: str) -> str:
        """
        Determine result type from element classes.
        
        Args:
            element_classes: Space-separated class string from element
            
        Returns:
            str: Result type ('organic', 'featured', 'knowledge', 'advertisement')
        """
        if 'Ww4FFb' in element_classes:
            return 'advertisement'
        elif 'ruhjFe' in element_classes:
            return 'featured'
        elif 'kpgb' in element_classes:
            return 'knowledge'
        return 'organic'