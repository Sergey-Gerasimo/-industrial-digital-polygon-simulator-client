"""
Integration tests for service availability and basic API endpoints.
"""

import pytest
import grpc
from simulation_client.proto.simulator_pb2 import PingRequest
from simulation_client.proto.simulator_pb2_grpc import SimulationServiceStub, SimulationDatabaseManagerStub


class TestServiceAvailability:
    """Test basic service availability and ping endpoints."""

    @pytest.mark.asyncio
    async def test_simulation_service_ping(self, unified_client):
        """Test that SimulationService responds to ping."""
        # Connect client first
        ping_result = await unified_client.ping()
        assert ping_result["simulation_service"] is True

    @pytest.mark.asyncio
    async def test_database_service_ping(self, unified_client):
        """Test that DatabaseManager responds to ping."""
        # Connect client first
        ping_result = await unified_client.ping()
        assert ping_result["database_service"] is True

    @pytest.mark.asyncio
    async def test_both_services_ping(self, unified_client):
        """Test that both services respond to ping simultaneously."""
        # Connect client first
        ping_result = await unified_client.ping()
        assert ping_result["simulation_service"] is True
        assert ping_result["database_service"] is True

    def test_grpc_channels_direct(self, simulation_service_port, database_service_port):
        """Test direct gRPC channel connections."""
        # Test simulation service channel
        with grpc.insecure_channel(f"localhost:{simulation_service_port}") as channel:
            stub = SimulationServiceStub(channel)
            request = PingRequest()
            try:
                response = stub.ping(request, timeout=5.0)
                assert response.success is True
                assert len(response.message) > 0
            except grpc.RpcError:
                pytest.fail("SimulationService gRPC channel failed")

        # Test database service channel
        with grpc.insecure_channel(f"localhost:{database_service_port}") as channel:
            stub = SimulationDatabaseManagerStub(channel)
            request = PingRequest()
            try:
                response = stub.ping(request, timeout=5.0)
                assert response.success is True
                assert len(response.message) > 0
            except grpc.RpcError:
                pytest.fail("DatabaseService gRPC channel failed")
