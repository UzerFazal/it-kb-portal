TRANSLATIONS = {
    "en": {
        "nav_search_placeholder": "Search articles, keywords...",
        "nav_admin": "Admin",
        "nav_signout": "Sign out",
        "nav_signin": "Sign in",
        "footer_text": "IT Knowledge Base · Internal Use Only · IT Support Portal",

        "hero_title": "IT Support Knowledge Base",
        "hero_subtitle": "Find step-by-step solutions to common IT issues",
        "hero_articles_available": "articles available",
        "hero_search_placeholder": "Search: VPN, password reset, printer, email setup...",
        "search_button": "Search",

        "browse_by_category": "Browse by Category",
        "no_categories": "No categories yet.",
        "add_in_admin": "Add one in admin panel.",
        "most_viewed": "Most Viewed",
        "recently_updated": "Recently Updated",
        "no_articles": "No articles yet.",
        "views": "views",
        "article_singular": "article",
        "article_plural": "articles",

        "filter_by_category": "Filter by Category",
        "all_categories": "All Categories",
        "search_results_for": "Search results for",
        "found_suffix": "found",
        "search_articles_title": "Search Articles",
        "search_placeholder2": "Search by keyword...",
        "no_results_for": 'No results found for',
        "try_different": "Try different keywords or",
        "browse_categories": "browse categories",
        "enter_keyword": "Enter a keyword to search articles",
        "updated_prefix": "Updated",

        "no_articles_in_category": "No articles in this category yet.",

        "home_breadcrumb": "Home",
        "by_author": "by",
        "edit": "Edit",
        "was_helpful": "Was this article helpful?",
        "yes": "Yes",
        "no": "No",
        "thanks_feedback": "Thank you for your feedback!",
        "related_articles": "Related Articles",

        "theme_toggle_title": "Switch theme",
        "lang_toggle_title": "Switch language",
    },
    "cs": {
        "nav_search_placeholder": "Hledat články, klíčová slova...",
        "nav_admin": "Administrace",
        "nav_signout": "Odhlásit se",
        "nav_signin": "Přihlásit se",
        "footer_text": "Znalostní báze IT · Pouze pro interní použití · Portál IT podpory",

        "hero_title": "Znalostní báze IT podpory",
        "hero_subtitle": "Najděte řešení běžných IT problémů krok za krokem",
        "hero_articles_available": "dostupných článků",
        "hero_search_placeholder": "Hledat: VPN, obnovení hesla, tiskárna, nastavení e-mailu...",
        "search_button": "Hledat",

        "browse_by_category": "Procházet dle kategorie",
        "no_categories": "Zatím žádné kategorie.",
        "add_in_admin": "Přidejte kategorii v administraci.",
        "most_viewed": "Nejčtenější",
        "recently_updated": "Naposledy aktualizováno",
        "no_articles": "Zatím žádné články.",
        "views": "zobrazení",
        "article_singular": "článek",
        "article_plural": "články",

        "filter_by_category": "Filtrovat dle kategorie",
        "all_categories": "Všechny kategorie",
        "search_results_for": "Výsledky hledání pro",
        "found_suffix": "nalezeno",
        "search_articles_title": "Hledat články",
        "search_placeholder2": "Hledat podle klíčového slova...",
        "no_results_for": "Nic nenalezeno pro",
        "try_different": "Zkuste jiná klíčová slova nebo",
        "browse_categories": "procházet kategorie",
        "enter_keyword": "Zadejte klíčové slovo pro vyhledávání článků",
        "updated_prefix": "Aktualizováno",

        "no_articles_in_category": "V této kategorii zatím nejsou žádné články.",

        "home_breadcrumb": "Domů",
        "by_author": "od",
        "edit": "Upravit",
        "was_helpful": "Byl tento článek užitečný?",
        "yes": "Ano",
        "no": "Ne",
        "thanks_feedback": "Děkujeme za zpětnou vazbu!",
        "related_articles": "Související články",

        "theme_toggle_title": "Přepnout motiv",
        "lang_toggle_title": "Přepnout jazyk",
    },
}

SUPPORTED_LANGS = ("en", "cs")
LANG_COOKIE = "kb_lang"


def get_lang(request) -> str:
    lang = request.cookies.get(LANG_COOKIE, "en")
    return lang if lang in SUPPORTED_LANGS else "en"


def t(request, key: str) -> str:
    lang = get_lang(request)
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
