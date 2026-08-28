from it_ticket_priority.copilot.retrieval import RunbookRetriever


def test_network_query_retrieves_network_runbook() -> None:
    retriever = RunbookRetriever()
    results = retriever.search(
        "warehouse site WAN DNS outage all scanning blocked network telephely hálózati kiesés"
    )
    assert results
    assert results[0].document_id == "network_outage"
    assert results[0].score > 0
