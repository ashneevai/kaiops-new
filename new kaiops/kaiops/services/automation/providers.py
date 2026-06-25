from __future__ import annotations

from abc import ABC, abstractmethod
from base64 import b64encode

import httpx
from kubernetes import client as k8s_client
from kubernetes import config as k8s_config

from app.core.config import settings


class AutomationProvider(ABC):
    @abstractmethod
    def execute(self, action: str, payload: dict, dry_run: bool = False) -> dict:
        raise NotImplementedError


class KubernetesProvider(AutomationProvider):
    def __init__(self) -> None:
        if settings.kubeconfig_path:
            k8s_config.load_kube_config(config_file=settings.kubeconfig_path)
        else:
            k8s_config.load_kube_config()
        self.apps_api = k8s_client.AppsV1Api()

    def execute(self, action: str, payload: dict, dry_run: bool = False) -> dict:
        namespace = payload.get("namespace", "default")
        deployment = payload.get("deployment")
        replicas = payload.get("replicas")

        if action == "scale_deployment":
            if dry_run:
                return {
                    "provider": "kubernetes",
                    "status": "dry_run",
                    "namespace": namespace,
                    "deployment": deployment,
                    "replicas": replicas,
                }
            patch = {"spec": {"replicas": replicas}}
            response = self.apps_api.patch_namespaced_deployment_scale(deployment, namespace, patch)
            return {
                "provider": "kubernetes",
                "status": "applied",
                "deployment": response.metadata.name,
                "replicas": response.spec.replicas,
            }

        raise ValueError(f"Unsupported Kubernetes action: {action}")


class TerraformProvider(AutomationProvider):
    def execute(self, action: str, payload: dict, dry_run: bool = False) -> dict:
        workspace = payload.get("workspace", "default")
        run_id = payload.get("run_id", "manual")
        status = "plan_only" if dry_run else "apply_requested"
        return {
            "provider": "terraform",
            "workspace": workspace,
            "run_id": run_id,
            "status": status,
            "auth": "token" if settings.terraform_token else "none",
        }


class AnsibleProvider(AutomationProvider):
    def execute(self, action: str, payload: dict, dry_run: bool = False) -> dict:
        if not settings.ansible_runner_endpoint:
            raise ValueError("ansible_runner_endpoint is not configured")

        endpoint = settings.ansible_runner_endpoint.rstrip("/")
        headers = {"Authorization": f"Bearer {settings.ansible_runner_token}"} if settings.ansible_runner_token else {}
        body = {
            "action": action,
            "payload": payload,
            "check": dry_run,
        }
        response = httpx.post(f"{endpoint}/api/v1/jobs", json=body, headers=headers, timeout=30)
        response.raise_for_status()
        return {"provider": "ansible", "status": "submitted", "job": response.json()}


class JenkinsProvider(AutomationProvider):
    def execute(self, action: str, payload: dict, dry_run: bool = False) -> dict:
        if action != "trigger_pipeline":
            raise ValueError(f"Unsupported Jenkins action: {action}")
        if not settings.jenkins_url or not settings.jenkins_user or not settings.jenkins_api_token:
            raise ValueError("jenkins_url, jenkins_user, and jenkins_api_token must be configured")

        job_name = payload.get("job_name")
        parameters = payload.get("parameters", {})
        if dry_run:
            return {"provider": "jenkins", "status": "dry_run", "job_name": job_name, "parameters": parameters}

        auth_token = b64encode(f"{settings.jenkins_user}:{settings.jenkins_api_token}".encode("utf-8")).decode("utf-8")
        headers = {"Authorization": f"Basic {auth_token}"}
        response = httpx.post(
            f"{settings.jenkins_url.rstrip('/')}/job/{job_name}/buildWithParameters",
            params=parameters,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return {"provider": "jenkins", "status": "triggered", "job_name": job_name}


class ArgoCDProvider(AutomationProvider):
    def execute(self, action: str, payload: dict, dry_run: bool = False) -> dict:
        if not settings.argocd_url or not settings.argocd_token:
            raise ValueError("argocd_url and argocd_token must be configured")

        app_name = payload.get("application")
        if action != "sync_application":
            raise ValueError(f"Unsupported ArgoCD action: {action}")

        if dry_run:
            return {"provider": "argocd", "status": "dry_run", "application": app_name}

        headers = {"Authorization": f"Bearer {settings.argocd_token}"}
        response = httpx.post(
            f"{settings.argocd_url.rstrip('/')}/api/v1/applications/{app_name}/sync",
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return {"provider": "argocd", "status": "sync_requested", "application": app_name}


PROVIDER_REGISTRY: dict[str, type[AutomationProvider]] = {
    "kubernetes": KubernetesProvider,
    "terraform": TerraformProvider,
    "ansible": AnsibleProvider,
    "jenkins": JenkinsProvider,
    "argocd": ArgoCDProvider,
}


def get_provider(provider_name: str) -> AutomationProvider:
    factory = PROVIDER_REGISTRY.get(provider_name.lower())
    if not factory:
        raise ValueError(f"Unsupported automation provider: {provider_name}")
    return factory()
