"""
Repository for Kubernetes Clusters, Nodes, Pods, Deployments, and Events.
"""

import uuid
from typing import List, Optional, Any
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.kubernetes import K8sCluster, K8sNode, K8sPod, K8sDeployment, K8sEvent


class CRUDK8sCluster(CRUDBase[K8sCluster, Any, Any]):
    async def get_multi_by_user(
        self, db: AsyncSession, user_id: uuid.UUID, provider: Optional[str] = None
    ) -> List[K8sCluster]:
        stmt = select(K8sCluster).where(K8sCluster.user_id == user_id)
        if provider and provider != "all":
            stmt = stmt.where(K8sCluster.provider == provider)
        res = await db.execute(stmt.order_by(K8sCluster.created_at.desc()))
        return list(res.scalars().all())


class CRUDK8sNode(CRUDBase[K8sNode, Any, Any]):
    async def get_by_cluster(self, db: AsyncSession, cluster_id: uuid.UUID) -> List[K8sNode]:
        stmt = select(K8sNode).where(K8sNode.cluster_id == cluster_id).order_by(K8sNode.name.asc())
        res = await db.execute(stmt)
        return list(res.scalars().all())


class CRUDK8sPod(CRUDBase[K8sPod, Any, Any]):
    async def get_multi_filtered(
        self,
        db: AsyncSession,
        cluster_id: Optional[uuid.UUID] = None,
        namespace: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
    ) -> List[K8sPod]:
        stmt = select(K8sPod)
        if cluster_id:
            stmt = stmt.where(K8sPod.cluster_id == cluster_id)
        if namespace and namespace != "all":
            stmt = stmt.where(K8sPod.namespace == namespace)
        if status and status != "all":
            stmt = stmt.where(K8sPod.status == status)
        if search:
            stmt = stmt.where(
                or_(
                    K8sPod.name.ilike(f"%{search}%"),
                    K8sPod.deployment_name.ilike(f"%{search}%"),
                )
            )
        stmt = stmt.order_by(K8sPod.created_at.desc()).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_by_name(self, db: AsyncSession, pod_name: str) -> Optional[K8sPod]:
        stmt = select(K8sPod).where(K8sPod.name == pod_name)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()


class CRUDK8sDeployment(CRUDBase[K8sDeployment, Any, Any]):
    async def get_multi_filtered(
        self, db: AsyncSession, cluster_id: Optional[uuid.UUID] = None, namespace: Optional[str] = None
    ) -> List[K8sDeployment]:
        stmt = select(K8sDeployment)
        if cluster_id:
            stmt = stmt.where(K8sDeployment.cluster_id == cluster_id)
        if namespace and namespace != "all":
            stmt = stmt.where(K8sDeployment.namespace == namespace)
        res = await db.execute(stmt.order_by(K8sDeployment.name.asc()))
        return list(res.scalars().all())


class CRUDK8sEvent(CRUDBase[K8sEvent, Any, Any]):
    async def get_multi_filtered(
        self, db: AsyncSession, event_type: Optional[str] = None, limit: int = 50
    ) -> List[K8sEvent]:
        stmt = select(K8sEvent)
        if event_type and event_type != "all":
            stmt = stmt.where(K8sEvent.event_type == event_type)
        res = await db.execute(stmt.order_by(K8sEvent.timestamp.desc()).limit(limit))
        return list(res.scalars().all())


crud_k8s_cluster = CRUDK8sCluster(K8sCluster)
crud_k8s_node = CRUDK8sNode(K8sNode)
crud_k8s_pod = CRUDK8sPod(K8sPod)
crud_k8s_deployment = CRUDK8sDeployment(K8sDeployment)
crud_k8s_event = CRUDK8sEvent(K8sEvent)
