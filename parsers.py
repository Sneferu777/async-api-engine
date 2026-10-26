from lxml import html
from typing import List, Dict, Any, Optional


def safe_extract(node : html.HtmlElement, xpath_query : str, default : Optional[str] = None) -> Optional[str]:
    result = node.xpath(xpath_query)

    if result:
        return result[0].strip() if results else default
    
    
def parse_html_quotes(html_bytes : bytes) -> List[Dict[str, Any]] :

    tree = html.fromstring(html_bytes)

    cards = tree.xpath("//div[@class='quotes']")

    records = []

    for card in cards :
        text = safe_extract(card, ".//span[@class='text']/text()")
        author = safe_extract(card, ".//small[@class='author']/text()")
        tags = [t.strip() for t in card.xpath(".//div[@class='tags']/a/text()")]
    
        records.append(

            {
                "quote" : text,
                "author" : author,
                "tags" : ", " join(tags)
            }
        )
    return records


    def parse_api_quotes(data : dict) -> List[Dict[str, Any]]:
        records = []

        for item in data.get('quotes', []) :
            records.append(
                {
                    "quote" : item.get("text"),
                    "author" : item.get("author").get("name"),
                    "tags" : ", " join(item.get("tags", []))
                }
            )

        return records



