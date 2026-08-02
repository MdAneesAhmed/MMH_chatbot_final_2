from services.semantic_search import semantic_search


def get_context(question):
    return semantic_search(question)