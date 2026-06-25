from services.automation.providers import TerraformProvider


def test_terraform_provider_dry_run():
    provider = TerraformProvider()
    result = provider.execute("plan", {"workspace": "prod"}, dry_run=True)
    assert result["provider"] == "terraform"
    assert result["status"] == "plan_only"
