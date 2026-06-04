"""
Testy pro nginx aplikaci.

Spouštění:
  Lokálně (Docker):   BASE_URL=http://localhost:8080 pytest tests/ -v
  Proti ALB:          BASE_URL=http://<alb-dns> pytest tests/ -v
"""

import os
import pytest
import requests

# URL se předává přes env proměnnou; fallback na localhost (lokální Docker)
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080").rstrip("/")


class TestNginxHomepage:
    """Testy hlavní stránky."""

    @pytest.fixture(scope="class")
    def response(self):
        """Načte stránku jednou pro celou třídu testů."""
        resp = requests.get(f"{BASE_URL}/", timeout=10)
        return resp

    def test_http_status_200(self, response):
        """Stránka musí vracet HTTP 200."""
        assert response.status_code == 200, (
            f"Očekáván HTTP 200, dostal jsem {response.status_code}"
        )

    def test_content_type_html(self, response):
        """Content-Type musí být text/html."""
        assert "text/html" in response.headers.get("Content-Type", ""), (
            f"Neočekávaný Content-Type: {response.headers.get('Content-Type')}"
        )

    def test_page_title(self, response):
        """Stránka musí obsahovat správný titulek."""
        assert "ECS Nginx Demo" in response.text, (
            "Titulek 'ECS Nginx Demo' nenalezen v HTML"
        )

    def test_running_badge(self, response):
        """Stránka musí zobrazovat badge RUNNING."""
        assert "RUNNING" in response.text, (
            "Badge 'RUNNING' nenalezen – stránka nemusí být správná verze"
        )

    def test_tech_stack_docker(self, response):
        """Stránka musí zmiňovat Docker."""
        assert "Docker" in response.text, (
            "'Docker' nenalezen v HTML"
        )

    def test_tech_stack_ecr(self, response):
        """Stránka musí zmiňovat AWS ECR."""
        assert "AWS ECR" in response.text, (
            "'AWS ECR' nenalezen v HTML"
        )

    def test_tech_stack_ecs(self, response):
        """Stránka musí zmiňovat ECS Fargate."""
        assert "ECS Fargate" in response.text, (
            "'ECS Fargate' nenalezen v HTML"
        )

    def test_page_not_empty(self, response):
        """Odpověď musí mít alespoň 200 znaků."""
        assert len(response.text) > 200, (
            f"Stránka je podezřele krátká ({len(response.text)} znaků)"
        )

    def test_no_nginx_default_page(self, response):
        """Nesmí se zobrazit výchozí nginx stránka (Welcome to nginx)."""
        assert "Welcome to nginx" not in response.text, (
            "Zobrazuje se výchozí nginx stránka místo vlastního index.html"
        )


class TestNginxHealthCheck:
    """Health check endpoint."""

    def test_health_check_responds(self):
        """`/` musí odpovídat i jako health check endpoint."""
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        assert resp.status_code == 200
