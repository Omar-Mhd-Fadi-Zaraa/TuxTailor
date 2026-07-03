from ddgs import DDGS
from langchain_core.tools import tool, ToolException
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
    query: str = Field(description="The search query to use with the search engine")


@tool(args_schema=SearchInput)
def search_the_internet(query: str) -> str | ToolException:
    """Use when you need more information about the user's question.
    Make sure to use this tool when a user asks about a specific package."""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=10, backend="duckduckgo")

            results = [
                r
                for r in results
                if r.get("href") and "duckduckgo.com" not in r["href"]
            ]
    except Exception as e:
        return f"Could not complete search query: {e}"

    return (
        "\n\n".join(f"{r['title']}\n{r['href']}\n{r['body']}" for r in results)
        or "No results found."
    )
