import re

class BaseNormalizationRules:
    @staticmethod
    def strip_whitespace(local: str):
        pattern = r'\s'
        return re.sub(pattern, '', local)