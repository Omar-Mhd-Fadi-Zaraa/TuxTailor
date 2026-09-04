from ddgs import DDGS
from ddgs.exceptions import DDGSException, RatelimitException, TimeoutException
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(description="The search query to use with the search engine")


@tool(args_schema=SearchInput)
def search_the_internet(query: str) -> str:
    """Use when you need more information about the user's question.
    Make sure to use this tool when a user asks about a specific package."""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=10, backend="duckduckgo") or []

            results = [
                r
                for r in results
                if r.get("href") and "duckduckgo.com" not in r["href"]
            ]
    except RatelimitException as e:
        return f"Rate limit hit: {e}"
    except TimeoutException as e:
        return f"Time out hit: {e}"
    except DDGSException as e:
        return f"Something went wrong while fetching results: {e}"

    return (
        "\n\n".join(f"{r['title']}\n{r['href']}\n{r['body']}" for r in results)
        or "No results found."
    )
