"""
Integration tests for SimulationService API endpoints.
"""

import pytest
from simulation_client.models import SimulationConfig


class TestSimulationService:
    """Test SimulationService endpoints."""

    @pytest.mark.asyncio
    async def test_create_simulation(self, unified_client):
        """Test simulation creation."""
        simulation_config = await unified_client.create_simulation()

        assert isinstance(simulation_config, SimulationConfig)
        assert hasattr(simulation_config, 'simulation_id')
        assert isinstance(simulation_config.simulation_id, str)
        assert len(simulation_config.simulation_id) > 0

    @pytest.mark.asyncio
    async def test_get_simulation(self, unified_client):
        """Test getting simulation data."""
        # Create simulation first
        sim_config = await unified_client.create_simulation()
        simulation_id = sim_config.simulation_id

        # Get simulation data
        simulation_response = await unified_client.get_simulation(simulation_id)

        assert simulation_response is not None
        assert hasattr(simulation_response, 'simulation')
        assert simulation_response.simulation.simulation_id == simulation_id

    
    @pytest.mark.asyncio
    async def test_get_simulation_as_dict(self, unified_client):
        """Test getting simulation data as dictionary."""
        # Create simulation first
        sim_config = await unified_client.create_simulation()
        simulation_id = sim_config.simulation_id

        # Get simulation data as dict
        sim_dict = await unified_client.get_simulation_as_dict(simulation_id)

        assert isinstance(sim_dict, dict)
        assert 'simulation_id' in sim_dict
        assert sim_dict['simulation_id'] == simulation_id

    @pytest.mark.asyncio
    async def test_run_simulation(self, unified_client):
        """Test running simulation."""
        # Create simulation first
        sim_config = await unified_client.create_simulation()
        simulation_id = sim_config.simulation_id

        # Run simulation
        result = await unified_client.run_simulation(simulation_id)

        assert result is not None
        assert hasattr(result, 'simulation')
        assert result.simulation.simulation_id == simulation_id

    @pytest.mark.asyncio
    async def test_run_simulation_and_get_results(self, unified_client):
        """Test running simulation and getting results."""
        # Create simulation first
        sim_config = await unified_client.create_simulation()
        simulation_id = sim_config.simulation_id

        # Run simulation and get results
        results = await unified_client.run_simulation_and_get_results(simulation_id)

        assert results is not None
        assert hasattr(results, 'profit')
        assert hasattr(results, 'cost')
        assert hasattr(results, 'profitability')

    @pytest.mark.asyncio
    async def test_get_material_types(self, unified_client):
        """Test getting material types."""
        material_types = await unified_client.get_material_types()

        assert material_types is not None
        assert hasattr(material_types, 'material_types')
        assert isinstance(material_types.material_types, list)

    
    @pytest.mark.asyncio
    async def test_get_equipment_types(self, unified_client):
        # Connect client first
        """Test getting equipment types."""
        equipment_types = await unified_client.get_equipment_types()

        assert equipment_types is not None
        assert hasattr(equipment_types, 'equipment_types')
        assert isinstance(equipment_types.equipment_types, list)

    
    @pytest.mark.asyncio
    async def test_get_workplace_types(self, unified_client):
        # Connect client first
        """Test getting workplace types."""
        workplace_types = await unified_client.get_workplace_types()

        assert workplace_types is not None
        assert hasattr(workplace_types, 'workplace_types')
        assert isinstance(workplace_types.workplace_types, list)

    
    @pytest.mark.asyncio
    async def test_get_available_defect_policies(self, unified_client):
        # Connect client first
        """Test getting available defect policies."""
        policies = await unified_client.get_available_defect_policies()

        assert policies is not None
        assert hasattr(policies, 'policies')
        assert isinstance(policies.policies, list)

    
    @pytest.mark.asyncio
    async def test_get_available_improvements_list(self, unified_client):
        # Connect client first
        """Test getting available improvements list."""
        improvements = await unified_client.get_available_improvements_list()

        assert improvements is not None
        assert hasattr(improvements, 'improvements')
        assert isinstance(improvements.improvements, list)

    
    @pytest.mark.asyncio
    async def test_get_available_certifications(self, unified_client):
        # Connect client first
        """Test getting available certifications."""
        certifications = await unified_client.get_available_certifications()

        assert certifications is not None
        assert hasattr(certifications, 'certifications')
        assert isinstance(certifications.certifications, list)

    
    @pytest.mark.asyncio
    async def test_get_available_sales_strategies(self, unified_client):
        # Connect client first
        """Test getting available sales strategies."""
        strategies = await unified_client.get_available_sales_strategies()

        assert strategies is not None
        assert hasattr(strategies, 'strategies')
        assert isinstance(strategies.strategies, list)
