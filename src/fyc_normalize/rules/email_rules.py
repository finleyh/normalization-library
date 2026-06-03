import re

class EmailNormalizingRules:
    @staticmethod
    def make_lowercase(local:str) -> str:
        return local.lower()
    
    @staticmethod
    def strip_nonlegals(local:str) -> str:
        pattern = r'[\`\;\:\\\/\(\)\[\]\<\>]'
        return re.sub(pattern, '', local)

    @staticmethod
    def strip_extra_at(local:str) -> str:
        if '@' in local:
            user,domain = local.rsplit('@',1) 
            return user.replace('@','')+'@'+domain
        else:
            return local

    @staticmethod
    def strip_plus_as_tag(local: str) -> str:
        pattern = r'(\+.*?)\@'
        return re.sub(pattern,'@',local)

    @staticmethod
    def strip_dots(local: str) -> str:
        user,domain = local.rsplit('@',1) if '@' in local else ''
        return user.replace('.','').lower()+'@'+domain.lower()
    
    @staticmethod
    def strip_hyphen_as_tag(local: str) -> str:
        pattern = r'\-.*?\@'
        return re.sub(pattern, '@', local)
    
    @staticmethod
    def strip_hyphens(local: str) -> str:
        user,domain = local.rsplit('@',1) if '@' in local else ''
        return user.replace('-', '').lower() + '@' + domain.lower()
    
    @staticmethod
    def strip_whitespace(local: str) -> str:
        pattern = r'\s'
        return re.sub(pattern, '', local)
    
    @staticmethod
    def strip_underscore(local: str) -> str:
        return local.replace('_','')

    @staticmethod
    def strip_fastmail_subdomain(local: str) -> str:
        pattern = r'\@.*?\.([^\.]+?)\.(co\.uk|org|com|us|net|cc|fm|biz|info|ms|st|as|at|uk|ca|cn|au|de|es|fr|im|in|jp|mx|nl|se|to|tw)'
        return re.sub(pattern, r'@\g<1>.\g<2>', local)