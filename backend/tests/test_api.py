"""API and statistics-engine tests against the seeded in-memory database."""
from __future__ import annotations


async def test_health(client):
    r = await client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


async def test_competitions(client):
    r = await client.get("/api/v1/competitions")
    assert r.status_code == 200
    codes = {c["code"]: c for c in r.json()}
    assert "mens_world_cup" in codes
    assert codes["mens_world_cup"]["edition_count"] == 1


async def test_tournament_overview(client):
    editions = (await client.get("/api/v1/tournaments")).json()["items"]
    eid = editions[0]["id"]
    r = await client.get(f"/api/v1/tournaments/{eid}")
    assert r.status_code == 200
    body = r.json()
    assert body["champion"]["name"] == "Alpha"
    assert body["num_matches"] == 2
    # Star Striker scored twice.
    assert body["top_scorers"][0]["name"] == "Star Striker"
    assert body["top_scorers"][0]["goals"] == 2


async def test_shootout_counts_as_draw(client):
    """Match 2 (1-1, won on penalties) must count as a draw for both teams."""
    teams = (await client.get("/api/v1/teams")).json()["items"]
    by_name = {t["name"]: t["id"] for t in teams}

    alpha = (await client.get(f"/api/v1/teams/{by_name['Alpha']}")).json()["stats"]
    beta = (await client.get(f"/api/v1/teams/{by_name['Beta']}")).json()["stats"]

    assert alpha["matches_played"] == 2
    assert (alpha["wins"], alpha["draws"], alpha["losses"]) == (1, 1, 0)
    assert alpha["titles"] == 1
    assert (beta["wins"], beta["draws"], beta["losses"]) == (0, 1, 1)
    assert beta["titles"] == 0


async def test_records_top_scorers(client):
    r = await client.get("/api/v1/records")
    assert r.status_code == 200
    boards = {b["key"]: b for b in r.json()}
    assert boards["top_scorers"]["rows"][0]["label"] == "Star Striker"
    assert boards["most_titles"]["rows"][0]["label"] == "Alpha"


async def test_search(client):
    r = await client.get("/api/v1/search", params={"q": "Alph"})
    assert r.status_code == 200
    assert any(hit["title"] == "Alpha" for hit in r.json()["teams"])


async def test_head_to_head(client):
    teams = (await client.get("/api/v1/teams")).json()["items"]
    ids = {t["name"]: t["id"] for t in teams}
    r = await client.get("/api/v1/teams/compare", params={"a": ids["Alpha"], "b": ids["Beta"]})
    assert r.status_code == 200
    h2h = r.json()["head_to_head"]
    assert h2h["matches"] == 2
    assert h2h["team_a_wins"] == 1  # the 3-1
    assert h2h["draws"] == 1  # the shootout


async def test_missing_team_404(client):
    r = await client.get("/api/v1/teams/999999")
    assert r.status_code == 404
