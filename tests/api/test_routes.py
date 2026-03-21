"""Tests for the FastAPI routes with mocked Neo4j queries."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


def _patch_query(return_value):
    """Shortcut to patch neo4j_client.query."""
    return patch("src.api.routes.query", new_callable=AsyncMock, return_value=return_value)


def _patch_query_single(return_value):
    """Shortcut to patch neo4j_client.query_single."""
    return patch("src.api.routes.query_single", new_callable=AsyncMock, return_value=return_value)


class TestHealth:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestStats:
    def test_get_stats(self):
        mock_data = [{"diseases": 3, "genes": 15, "proteins": 12, "compounds": 50, "papers": 100, "pathways": 20}]
        with _patch_query(mock_data):
            resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["diseases"] == 3
        assert data["genes"] == 15

    def test_get_stats_empty(self):
        with _patch_query([]):
            resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["diseases"] == 0


class TestDiseases:
    def test_list_diseases(self):
        mock_data = [
            {"efo_id": "EFO_0000337", "name": "Huntington disease", "target_count": 5},
            {"efo_id": "EFO_0002508", "name": "Parkinson disease", "target_count": 8},
        ]
        with _patch_query(mock_data):
            resp = client.get("/api/diseases")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["name"] == "Huntington disease"

    def test_get_disease(self):
        disease = {"efo_id": "EFO_0000337", "name": "Huntington disease"}
        targets = [
            {
                "ensembl_id": "ENSG00000197386",
                "gene_symbol": "HTT",
                "target_name": "Huntingtin",
                "association_score": 0.73,
                "uniprot_accession": "P42858",
                "protein_class": "enzyme",
                "subcellular_locations": ["Cytoplasm"],
                "has_3d_structure": True,
                "compounds": [{"chembl_id": "CHEMBL1234", "pref_name": "DrugA", "max_phase": 4}],
                "pmids": ["12345678"],
                "pathways": [{"reactome_id": "R-HSA-123", "name": "Synaptic signaling"}],
            }
        ]
        with _patch_query_single(disease), _patch_query(targets):
            resp = client.get("/api/diseases/EFO_0000337")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Huntington disease"
        assert len(data["targets"]) == 1
        assert data["targets"][0]["gene_symbol"] == "HTT"

    def test_get_disease_not_found(self):
        with _patch_query_single(None):
            resp = client.get("/api/diseases/EFO_FAKE")
        assert resp.status_code == 404


class TestGraph:
    def test_get_full_graph(self):
        # Mock all the queries that _build_graph_data makes
        call_count = 0
        results = [
            # diseases
            [{"id": "EFO_0000337", "name": "Huntington disease"}],
            # genes
            [{"id": "ENSG00000197386", "symbol": "HTT", "name": "Huntingtin", "disease_id": "EFO_0000337", "score": 0.73}],
            # proteins
            [{"id": "P42858", "protein_class": "enzyme", "has_3d": True, "gene_id": "ENSG00000197386"}],
            # compounds
            [{"id": "CHEMBL1234", "name": "DrugA", "max_phase": 4, "protein_id": "P42858"}],
            # papers
            [{"id": "12345678", "title": "HTT study", "gene_id": "ENSG00000197386", "support_level": "supporting"}],
            # pathways
            [{"id": "R-HSA-123", "name": "Synaptic", "gene_id": "ENSG00000197386"}],
        ]

        async def mock_query(cypher, **params):
            nonlocal call_count
            idx = call_count
            call_count += 1
            return results[idx] if idx < len(results) else []

        with patch("src.api.routes.query", side_effect=mock_query):
            resp = client.get("/api/graph")
        assert resp.status_code == 200
        data = resp.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 6  # 1 disease + 1 gene + 1 protein + 1 compound + 1 paper + 1 pathway
        assert len(data["edges"]) == 5  # ASSOCIATED_WITH, ENCODES, HAS_COMPOUND, MENTIONED_IN, INVOLVED_IN

    def test_get_disease_graph_not_found(self):
        with _patch_query_single(None):
            resp = client.get("/api/graph/EFO_FAKE")
        assert resp.status_code == 404


class TestCompare:
    def test_compare_diseases(self):
        shared = [
            {
                "ensembl_id": "ENSG00000149295",
                "gene_symbol": "DRD2",
                "target_name": "Dopamine receptor D2",
                "score_d1": 0.39,
                "score_d2": 0.45,
                "uniprot_accession": "P14416",
                "protein_class": "GPCR",
                "shared_pathways": [{"reactome_id": "R-HSA-500792", "name": "GPCR ligand binding"}],
            }
        ]
        d1_info = {"name": "Huntington disease"}
        d2_info = {"name": "Parkinson disease"}
        only_d1 = [{"gene_symbol": "HTT", "ensembl_id": "ENSG00000197386"}]
        only_d2 = [{"gene_symbol": "SNCA", "ensembl_id": "ENSG00000145335"}]

        call_count = 0
        query_results = [shared, only_d1, only_d2]
        single_results = [d1_info, d2_info]

        async def mock_query(cypher, **params):
            nonlocal call_count
            idx = call_count
            call_count += 1
            return query_results[idx] if idx < len(query_results) else []

        single_count = 0

        async def mock_single(cypher, **params):
            nonlocal single_count
            idx = single_count
            single_count += 1
            return single_results[idx] if idx < len(single_results) else None

        with patch("src.api.routes.query", side_effect=mock_query), \
             patch("src.api.routes.query_single", side_effect=mock_single):
            resp = client.get("/api/compare?d1=EFO_0000337&d2=EFO_0002508")

        assert resp.status_code == 200
        data = resp.json()
        assert data["disease_1"]["name"] == "Huntington disease"
        assert data["disease_2"]["name"] == "Parkinson disease"
        assert len(data["shared_targets"]) == 1
        assert data["shared_targets"][0]["gene_symbol"] == "DRD2"
        assert len(data["only_in_d1"]) == 1
        assert len(data["only_in_d2"]) == 1


class TestTargets:
    def test_get_target(self):
        gene = {"ensembl_id": "ENSG00000149295", "gene_symbol": "DRD2", "target_name": "Dopamine receptor D2"}
        diseases = [{"efo_id": "EFO_0000337", "name": "Huntington disease", "score": 0.39}]
        protein = {"uniprot_accession": "P14416", "protein_class": "GPCR",
                   "subcellular_locations": ["Cell membrane"], "has_3d_structure": True}
        compounds = [{"chembl_id": "CHEMBL1234", "pref_name": "DrugA", "max_phase": 4}]
        papers = [{"pmid": "12345678", "title": "DRD2 study", "support_level": "supporting"}]
        pathways = [{"reactome_id": "R-HSA-500792", "name": "GPCR ligand binding"}]

        call_count = 0
        query_results = [diseases, compounds, papers, pathways]
        single_results = [gene, protein]

        async def mock_query(cypher, **params):
            nonlocal call_count
            idx = call_count
            call_count += 1
            return query_results[idx] if idx < len(query_results) else []

        single_count = 0

        async def mock_single(cypher, **params):
            nonlocal single_count
            idx = single_count
            single_count += 1
            return single_results[idx] if idx < len(single_results) else None

        with patch("src.api.routes.query", side_effect=mock_query), \
             patch("src.api.routes.query_single", side_effect=mock_single):
            resp = client.get("/api/targets/DRD2")

        assert resp.status_code == 200
        data = resp.json()
        assert data["gene_symbol"] == "DRD2"
        assert len(data["diseases"]) == 1
        assert data["protein"]["protein_class"] == "GPCR"
        assert len(data["compounds"]) == 1
        assert len(data["pathways"]) == 1

    def test_get_target_not_found(self):
        with _patch_query_single(None):
            resp = client.get("/api/targets/FAKEGENE")
        assert resp.status_code == 404
