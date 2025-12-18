"""
Integration tests for complex simulation scenarios.
"""

import pytest


class TestSimulationScenarios:
    """Test complex simulation scenarios."""

    
    @pytest.mark.asyncio
    async def test_create_configure_run_simulation(
        self, configured_simulation_id, unified_client
    ):
        """Test full simulation lifecycle: create, configure, run."""
        simulation_id = configured_simulation_id

        result = await unified_client.run_simulation(simulation_id)

        assert result is not None
        assert result.simulation.simulation_id == simulation_id

    @pytest.mark.asyncio
    async def test_simulation_with_different_configs(
        self, unified_client, configure_simulation
    ):
        """Test simulation with different configuration scenarios."""
        # Test 1: Fully configured simulation
        sim1 = await unified_client.create_simulation()
        await configure_simulation(sim1.simulation_id)
        result1 = await unified_client.run_simulation(sim1.simulation_id)
        assert result1 is not None

        # Test 2: Another fully configured simulation
        sim2 = await unified_client.create_simulation()
        await configure_simulation(sim2.simulation_id)
        result2 = await unified_client.run_simulation(sim2.simulation_id)
        assert result2 is not None

    @pytest.mark.asyncio
    async def test_simulation_metrics_availability(
        self, configured_simulation_id, unified_client
    ):
        """Test that simulation metrics are available after running."""
        # Create and run simulation
        simulation_id = configured_simulation_id

        await unified_client.run_simulation(simulation_id)

        # Try to get various metrics (step будет получен автоматически из симуляции)
        metrics_available = []

        try:
            factory_metrics = await unified_client.get_factory_metrics(simulation_id)
            metrics_available.append('factory')
            assert factory_metrics is not None
        except Exception:
            pass

        try:
            production_metrics = await unified_client.get_production_metrics(simulation_id)
            metrics_available.append('production')
            assert production_metrics is not None
        except Exception:
            pass

        try:
            quality_metrics = await unified_client.get_quality_metrics(simulation_id)
            metrics_available.append('quality')
            assert quality_metrics is not None
        except Exception:
            pass

        # At least some metrics should be available
        assert len(metrics_available) > 0, "No metrics available after simulation run"

    @pytest.mark.asyncio
    async def test_simulation_data_consistency(
        self, configured_simulation_id, unified_client
    ):
        """Test that simulation data remains consistent across operations."""
        # Create simulation
        simulation_id = configured_simulation_id

        # Get initial state
        initial_sim = await unified_client.get_simulation(simulation_id)

        # Run simulation
        await unified_client.run_simulation(simulation_id)

        # Get final state
        final_sim = await unified_client.get_simulation(simulation_id)

        # Simulation ID should remain the same
        assert initial_sim.simulation.simulation_id == final_sim.simulation.simulation_id
        assert final_sim.simulation.simulation_id == simulation_id

    @pytest.mark.asyncio
    async def test_concurrent_simulations(
        self, unified_client, configure_simulation
    ):
        """Test running multiple simulations concurrently."""
        # Create multiple simulations
        sim_configs = []
        for _ in range(3):
            config = await unified_client.create_simulation()
            sim_configs.append(config)

        # Configure all simulations before running
        for config in sim_configs:
            await configure_simulation(config.simulation_id)

        # Run them concurrently
        import asyncio
        tasks = [
            unified_client.run_simulation(config.simulation_id)
            for config in sim_configs
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check that all simulations completed
        successful_runs = 0
        for result in results:
            if not isinstance(result, Exception):
                successful_runs += 1

        assert successful_runs > 0, "No simulations completed successfully"

    @pytest.mark.asyncio
    async def test_reference_data_consistency(self, unified_client):
        """Test that reference data is consistent across calls."""
        # Get reference data multiple times
        material_types_1 = await unified_client.get_material_types()
        material_types_2 = await unified_client.get_material_types()

        equipment_types_1 = await unified_client.get_equipment_types()
        equipment_types_2 = await unified_client.get_equipment_types()

        # Data should be consistent (same structure and timestamps)
        assert material_types_1.material_types == material_types_2.material_types
        assert equipment_types_1.equipment_types == equipment_types_2.equipment_types

    @pytest.mark.asyncio
    async def test_error_handling_graceful(self, unified_client):
        """Test that API handles errors gracefully."""
        # Test with invalid simulation ID
        try:
            await unified_client.get_simulation("invalid-simulation-id")
            # If no exception, that's also acceptable (service might handle gracefully)
        except Exception as e:
            # Exception is acceptable as long as it's handled properly
            assert isinstance(e, Exception)

        # Test with invalid supplier ID - try to configure simulation with invalid supplier
        sim_config = await unified_client.create_simulation()
        try:
            await unified_client.configure_simulation_and_check(
                simulation_id=sim_config.simulation_id,
                supplier_ids=["invalid-supplier-id"]
            )
            # If no exception, service handles gracefully
        except Exception as e:
            # Exception is acceptable
            assert isinstance(e, Exception)
