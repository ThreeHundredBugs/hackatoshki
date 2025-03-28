from typing import Any

import structlog

from src.handlers.base import BaseHandler
from src.models.events import OpsgenieEvent
import kubernetes

logger = structlog.get_logger()


class LowDiskSpaceHandler(BaseHandler):
    """Handler to manage low disk space events."""

    async def handle(self, event: OpsgenieEvent) -> dict[str, Any]:
        """Increase PVC disk space by an additional 10Gi based on Opsgenie event."""

        # Extract namespace and PVC name from the event
        namespace = event.alert.namespace  # Assuming these attributes exist
        pvc_name = event.alert.pvc_name

        # Load Kubernetes configuration
        config.load_kube_config()

        # Initialize the Kubernetes API client
        v1 = client.CoreV1Api()

        try:
            # Get the current PVC
            pvc = v1.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=namespace)
            current_size = pvc.spec.resources.requests['storage']

            # Calculate new size by adding 10Gi
            new_size = f"{int(current_size[:-2]) + 10}Gi"

            # Create a patch to update the PVC size
            patch = {
                "spec": {
                    "resources": {
                        "requests": {
                            "storage": new_size
                        }
                    }
                }
            }

            # Patch the PVC to increase its size
            v1.patch_namespaced_persistent_volume_claim(
                name=pvc_name,
                namespace=namespace,
                body=patch
            )
            logger.info("PVC size increased", pvc_name=pvc_name, namespace=namespace, new_size=new_size)
        except client.exceptions.ApiException as e:
            logger.error("Failed to increase PVC size", error=str(e))
            return {
                "status": "failed",
                "handler": "LowDiskSpaceHandler",
                "error": str(e)
            }

        return {
            "status": "processed",
            "handler": "LowDiskSpaceHandler",
            "event_action": event.action,
            "alert_id": event.alert.alert_id,
        }
