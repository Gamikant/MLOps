from module_1 import scrape_google_news

def extract_top_stories_link():
    soup = scrape_google_news()
    if not soup:
        return None
    top_stories_section = soup.select_one("div.n3GXRc")
    if top_stories_section:
        a_tag = top_stories_section.select_one("h3 a")
        if a_tag and "href" in a_tag.attrs:
            return "https://news.google.com" + a_tag["href"][1:]
    print("Top stories section not found")
    return None
