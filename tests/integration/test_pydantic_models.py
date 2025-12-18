"""
Интеграционные тесты для проверки возврата Pydantic моделей из клиентов.

Эти тесты проверяют, что клиенты возвращают именно Pydantic модели из models.py,
а не protobuf объекты или словари.
"""

import pytest
from pydantic import BaseModel
from simulation_client import AsyncSimulationClient, AsyncDatabaseClient


# Helper function to check if object is a Pydantic model of a specific type
def assert_is_pydantic_model(obj, expected_class_name: str):
    """Проверяет, что объект является Pydantic моделью указанного типа."""
    assert isinstance(
        obj, BaseModel
    ), f"Expected {expected_class_name} (BaseModel), got {type(obj)}"
    assert (
        obj.__class__.__name__ == expected_class_name
    ), f"Expected {expected_class_name}, got {obj.__class__.__name__}"


from simulation_client.models import (
    # Response models
    SimulationResponse,
    SimulationConfig,
    SimulationResults,
    FactoryMetricsResponse,
    ProductionMetricsResponse,
    QualityMetricsResponse,
    EngineeringMetricsResponse,
    CommercialMetricsResponse,
    ProcurementMetricsResponse,
    AllMetricsResponse,
    ProductionScheduleResponse,
    WorkshopPlanResponse,
    RequiredMaterialsResponse,
    AvailableImprovementsResponse,
    DefectPoliciesResponse,
    ValidationResponse,
    # Database response models
    GetAllSuppliersResponse,
    GetAllWorkersResponse,
    GetAllLogistsResponse,
    GetAllEquipmentResponse,
    GetAllTendersResponse,
    GetAllConsumersResponse,
    GetAllWorkplacesResponse,
    GetAllLeanImprovementsResponse,
    GetAvailableLeanImprovementsResponse,
    # Entity models
    Supplier,
    Worker,
    Logist,
    Equipment,
    Tender,
    Consumer,
    Workplace,
    LeanImprovement,
    SuccessResponse,
)


class TestPydanticModelsReturn:
    """Тесты для проверки возврата Pydantic моделей."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_simulation_client_returns_pydantic_models(
        self, unified_client, configured_simulation
    ):
        """Проверка, что SimulationClient возвращает Pydantic модели."""
        # Тест create_simulation
        config = configured_simulation
        # Проверяем, что это Pydantic модель
        assert isinstance(config, BaseModel)
        assert hasattr(config, "__class__")
        assert config.__class__.__name__ == "SimulationConfig"
        assert hasattr(config, "simulation_id")
        assert isinstance(config.simulation_id, str)

        simulation_id = config.simulation_id

        # Тест get_simulation
        sim_response = await unified_client.get_simulation(simulation_id)
        assert_is_pydantic_model(sim_response, "SimulationResponse")
        assert isinstance(sim_response.simulation, BaseModel)
        assert hasattr(sim_response, "timestamp")

        # Делаем хотя бы один шаг симуляции: на сервере step фактически обязателен
        # (встречается проверка вида `if request.step`, и step=0 считается "не передан")
        await unified_client.run_simulation(simulation_id)

        # Тест get_factory_metrics (step будет получен автоматически из симуляции, если не передан)
        factory_metrics = await unified_client.get_factory_metrics(
            simulation_id, step=1
        )
        assert_is_pydantic_model(factory_metrics, "FactoryMetricsResponse")
        assert isinstance(factory_metrics.metrics, BaseModel)
        assert hasattr(factory_metrics, "timestamp")

        # Тест get_production_metrics
        production_metrics = await unified_client.get_production_metrics(
            simulation_id, step=1
        )
        assert_is_pydantic_model(production_metrics, "ProductionMetricsResponse")
        assert isinstance(production_metrics.metrics, BaseModel)

        # Тест get_quality_metrics
        quality_metrics = await unified_client.get_quality_metrics(
            simulation_id, step=1
        )
        assert_is_pydantic_model(quality_metrics, "QualityMetricsResponse")
        assert isinstance(quality_metrics.metrics, BaseModel)

        # Тест get_engineering_metrics
        engineering_metrics = await unified_client.get_engineering_metrics(
            simulation_id, step=1
        )
        assert_is_pydantic_model(engineering_metrics, "EngineeringMetricsResponse")
        assert isinstance(engineering_metrics.metrics, BaseModel)

        # Тест get_commercial_metrics
        commercial_metrics = await unified_client.get_commercial_metrics(
            simulation_id, step=1
        )
        assert_is_pydantic_model(commercial_metrics, "CommercialMetricsResponse")
        assert isinstance(commercial_metrics.metrics, BaseModel)

        # Тест get_procurement_metrics
        procurement_metrics = await unified_client.get_procurement_metrics(
            simulation_id, step=1
        )
        assert_is_pydantic_model(procurement_metrics, "ProcurementMetricsResponse")
        assert isinstance(procurement_metrics.metrics, BaseModel)

        # Тест get_all_metrics
        all_metrics = await unified_client.get_all_metrics(simulation_id, step=1)
        assert_is_pydantic_model(all_metrics, "AllMetricsResponse")
        assert isinstance(all_metrics.factory, BaseModel)
        assert isinstance(all_metrics.production, BaseModel)

        # Тест get_production_schedule
        schedule = await unified_client.get_production_schedule(simulation_id)
        assert_is_pydantic_model(schedule, "ProductionScheduleResponse")
        assert isinstance(schedule.schedule, BaseModel)

        # Тест get_workshop_plan
        workshop_plan = await unified_client.get_workshop_plan(simulation_id)
        assert_is_pydantic_model(workshop_plan, "WorkshopPlanResponse")
        assert isinstance(workshop_plan.workshop_plan, BaseModel)

        # Тест get_required_materials
        required_materials = await unified_client.get_required_materials(simulation_id)
        assert_is_pydantic_model(required_materials, "RequiredMaterialsResponse")
        assert isinstance(required_materials.materials, list)

        # Тест get_available_improvements
        improvements = await unified_client.get_available_improvements(simulation_id)
        assert_is_pydantic_model(improvements, "AvailableImprovementsResponse")
        assert isinstance(improvements.improvements, list)

        # Тест get_defect_policies
        defect_policies = await unified_client.get_defect_policies(simulation_id)
        assert_is_pydantic_model(defect_policies, "DefectPoliciesResponse")
        assert isinstance(defect_policies.available_policies, list)

        # Тест validate_configuration
        validation = await unified_client.validate_configuration(simulation_id)
        assert_is_pydantic_model(validation, "ValidationResponse")
        assert isinstance(validation.is_valid, bool)
        assert isinstance(validation.errors, list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_database_client_returns_pydantic_models(self, unified_client):
        """Проверка, что DatabaseClient возвращает Pydantic модели."""
        # Тест get_all_suppliers
        suppliers_response = await unified_client.get_all_suppliers()
        # Проверяем, что это Pydantic модель
        assert isinstance(suppliers_response, BaseModel)
        assert suppliers_response.__class__.__name__ == "GetAllSuppliersResponse"
        assert isinstance(suppliers_response.suppliers, list)
        assert isinstance(suppliers_response.total_count, int)
        if suppliers_response.suppliers:
            assert_is_pydantic_model(suppliers_response.suppliers[0], "Supplier")
            assert isinstance(suppliers_response.suppliers[0], BaseModel)

        # Тест get_all_workers
        workers_response = await unified_client.get_all_workers()
        assert_is_pydantic_model(workers_response, "GetAllWorkersResponse")
        assert isinstance(workers_response.workers, list)
        assert isinstance(workers_response.total_count, int)
        if workers_response.workers:
            assert isinstance(workers_response.workers[0], Worker)
            assert isinstance(workers_response.workers[0], BaseModel)

        # Тест get_all_logists
        logists_response = await unified_client.get_all_logists()
        assert_is_pydantic_model(logists_response, "GetAllLogistsResponse")
        assert isinstance(logists_response.logists, list)
        assert isinstance(logists_response.total_count, int)
        if logists_response.logists:
            assert_is_pydantic_model(logists_response.logists[0], "Logist")

        # Тест get_all_equipment
        equipment_response = await unified_client.get_all_equipment()
        assert_is_pydantic_model(equipment_response, "GetAllEquipmentResponse")
        assert isinstance(equipment_response.equipments, list)
        assert isinstance(equipment_response.total_count, int)
        if equipment_response.equipments:
            assert_is_pydantic_model(equipment_response.equipments[0], "Equipment")

        # Тест get_all_tenders
        tenders_response = await unified_client.get_all_tenders()
        assert_is_pydantic_model(tenders_response, "GetAllTendersResponse")
        assert isinstance(tenders_response.tenders, list)
        assert isinstance(tenders_response.total_count, int)
        if tenders_response.tenders:
            assert_is_pydantic_model(tenders_response.tenders[0], "Tender")

        # Тест get_all_consumers
        consumers_response = await unified_client.get_all_consumers()
        assert_is_pydantic_model(consumers_response, "GetAllConsumersResponse")
        assert isinstance(consumers_response.consumers, list)
        assert isinstance(consumers_response.total_count, int)
        if consumers_response.consumers:
            assert_is_pydantic_model(consumers_response.consumers[0], "Consumer")

        # Тест get_all_workplaces
        workplaces_response = await unified_client.get_all_workplaces()
        assert_is_pydantic_model(workplaces_response, "GetAllWorkplacesResponse")
        assert isinstance(workplaces_response.workplaces, list)
        assert isinstance(workplaces_response.total_count, int)
        if workplaces_response.workplaces:
            assert isinstance(workplaces_response.workplaces[0], Workplace)
            assert isinstance(workplaces_response.workplaces[0], BaseModel)

        # Тест get_all_lean_improvements
        lean_improvements_response = await unified_client.get_all_lean_improvements()
        assert_is_pydantic_model(
            lean_improvements_response, "GetAllLeanImprovementsResponse"
        )
        assert isinstance(lean_improvements_response.improvements, list)
        if lean_improvements_response.improvements:
            assert isinstance(
                lean_improvements_response.improvements[0], LeanImprovement
            )
            assert isinstance(lean_improvements_response.improvements[0], BaseModel)

        # Тест get_available_lean_improvements
        available_improvements = await unified_client.get_available_lean_improvements()
        assert_is_pydantic_model(
            available_improvements, "GetAvailableLeanImprovementsResponse"
        )
        assert isinstance(available_improvements.improvements, list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_operations_return_pydantic_models(self, unified_client):
        """Проверка, что операции создания возвращают Pydantic модели."""
        from simulation_client.models import (
            CreateSupplierRequest,
            CreateWorkerRequest,
            CreateLogistRequest,
            CreateEquipmentRequest,
            CreateConsumerRequest,
            CreateTenderRequest,
            CreateWorkplaceRequest,
        )

        # Тест create_supplier
        supplier_req = CreateSupplierRequest(
            name="Test Supplier",
            product_name="Test Product",
            material_type="steel",
            delivery_period=10,
            special_delivery_period=5,
            reliability=0.95,
            product_quality=0.9,
            cost=1000,
            special_delivery_cost=1500,
        )
        supplier = await unified_client.create_supplier(supplier_req)
        # Проверяем, что это Pydantic модель
        assert_is_pydantic_model(supplier, "Supplier")
        assert supplier.name == "Test Supplier"

        # Тест create_worker
        worker_req = CreateWorkerRequest(
            name="Test Worker",
            qualification=3,
            specialty="welder",
            salary=50000,
        )
        worker = await unified_client.create_worker(worker_req)
        assert_is_pydantic_model(worker, "Worker")
        assert worker.name == "Test Worker"

        # Тест create_logist
        logist_req = CreateLogistRequest(
            name="Test Logist",
            qualification=2,
            specialty="logistics",
            salary=60000,
            speed=50,
            vehicle_type="truck",
        )
        logist = await unified_client.create_logist(logist_req)
        assert_is_pydantic_model(logist, "Logist")
        assert logist.name == "Test Logist"

        # Тест create_equipment
        equipment_req = CreateEquipmentRequest(
            name="Test Equipment",
            equipment_type="machine",
            reliability=0.9,
            maintenance_period=30,
            maintenance_cost=5000,
            cost=100000,
            repair_cost=20000,
            repair_time=5,
        )
        equipment = await unified_client.create_equipment(equipment_req)
        assert_is_pydantic_model(equipment, "Equipment")
        assert equipment.name == "Test Equipment"

        # Тест create_consumer
        consumer_req = CreateConsumerRequest(name="Test Consumer", type="COMMERCIAL")
        consumer = await unified_client.create_consumer(consumer_req)
        assert_is_pydantic_model(consumer, "Consumer")
        assert consumer.name == "Test Consumer"

        # Тест create_tender
        tender_req = CreateTenderRequest(
            consumer_id=consumer.consumer_id,
            cost=100000,
            quantity_of_products=10,
            penalty_per_day=1000,
            warranty_years=2,
            payment_form="cash",
        )
        tender = await unified_client.create_tender(tender_req)
        assert_is_pydantic_model(tender, "Tender")
        assert tender.cost == 100000

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_delete_operations_return_pydantic_models(self, unified_client):
        """Проверка, что операции удаления возвращают Pydantic модели."""
        from simulation_client.models import (
            CreateSupplierRequest,
            DeleteSupplierRequest,
            CreateWorkerRequest,
            DeleteWorkerRequest,
        )

        # Создаем тестовые данные
        supplier_req = CreateSupplierRequest(
            name="Test Supplier Delete",
            product_name="Test Product",
            material_type="steel",
            delivery_period=10,
            special_delivery_period=5,
            reliability=0.95,
            product_quality=0.9,
            cost=1000,
            special_delivery_cost=1500,
        )
        supplier = await unified_client.create_supplier(supplier_req)

        # Тест delete_supplier - создаем симуляцию для получения simulation_id
        sim_config = await unified_client.create_simulation()
        delete_req = DeleteSupplierRequest(
            simulation_id=sim_config.simulation_id, supplier_id=supplier.supplier_id
        )
        delete_response = await unified_client.delete_supplier(delete_req)
        assert_is_pydantic_model(delete_response, "SuccessResponse")
        assert isinstance(delete_response, BaseModel)
        assert delete_response.success is True

        # Тест delete_worker
        worker_req = CreateWorkerRequest(
            name="Test Worker Delete",
            qualification=3,
            specialty="welder",
            salary=50000,
        )
        worker = await unified_client.create_worker(worker_req)

        delete_worker_req = DeleteWorkerRequest(worker_id=worker.worker_id)
        delete_worker_response = await unified_client.delete_worker(delete_worker_req)
        assert_is_pydantic_model(delete_worker_response, "SuccessResponse")
        assert isinstance(delete_worker_response, BaseModel)
        assert delete_worker_response.success is True

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_pydantic_models_have_validation(self, unified_client):
        """Проверка, что Pydantic модели имеют валидацию."""
        from simulation_client.models import CreateSupplierRequest

        # Проверяем, что можно создать валидный запрос
        supplier_req = CreateSupplierRequest(
            name="Test Supplier",
            product_name="Test Product",
            material_type="steel",
            delivery_period=10,
            special_delivery_period=5,
            reliability=0.95,
            product_quality=0.9,
            cost=1000,
            special_delivery_cost=1500,
        )
        assert supplier_req.name == "Test Supplier"

        # Проверяем, что модель можно сериализовать в dict
        supplier_dict = supplier_req.model_dump()
        assert isinstance(supplier_dict, dict)
        assert supplier_dict["name"] == "Test Supplier"

        # Проверяем, что модель можно сериализовать в JSON
        supplier_json = supplier_req.model_dump_json()
        assert isinstance(supplier_json, str)
        assert "Test Supplier" in supplier_json

        # Создаем поставщика и проверяем, что ответ тоже валидируется
        supplier = await unified_client.create_supplier(supplier_req)
        # Проверяем, что это Pydantic модель
        assert isinstance(supplier, BaseModel)
        assert supplier.__class__.__name__ == "Supplier"

        # Проверяем, что можно получить dict из ответа
        supplier_dict = supplier.model_dump()
        assert isinstance(supplier_dict, dict)
        assert "supplier_id" in supplier_dict

        # Проверяем, что можно получить JSON из ответа
        supplier_json = supplier.model_dump_json()
        assert isinstance(supplier_json, str)
        assert "supplier_id" in supplier_json

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_simulation_results_is_pydantic_model(self, unified_client):
        """Проверка, что результаты симуляции возвращаются как Pydantic модель."""
        # Создаем симуляцию
        config = await unified_client.create_simulation()
        simulation_id = config.simulation_id

        # Получаем симуляцию
        sim_response = await unified_client.get_simulation(simulation_id)
        assert_is_pydantic_model(sim_response, "SimulationResponse")

        # Проверяем, что results - это Pydantic модель
        if sim_response.simulation.results:
            results_list = sim_response.simulation.results
            assert isinstance(results_list, list)
            last_result = results_list[-1]
            assert_is_pydantic_model(last_result, "SimulationResults")
            assert hasattr(last_result, "profit")
            assert hasattr(last_result, "cost")
            assert hasattr(last_result, "profitability")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_nested_pydantic_models(
        self, unified_client, configured_simulation_id
    ):
        """Проверка, что вложенные модели тоже являются Pydantic моделями."""
        # Создаем симуляцию
        simulation_id = configured_simulation_id

        # Запускаем симуляцию, чтобы получить метрики
        await unified_client.run_simulation(simulation_id)

        # Получаем метрики завода (step будет получен автоматически из симуляции)
        factory_metrics = await unified_client.get_factory_metrics(
            simulation_id, step=1
        )
        assert_is_pydantic_model(factory_metrics, "FactoryMetricsResponse")

        # Проверяем вложенные модели
        if factory_metrics.metrics.warehouse_metrics:
            for (
                warehouse_id,
                warehouse_metrics,
            ) in factory_metrics.metrics.warehouse_metrics.items():
                assert isinstance(warehouse_metrics, BaseModel)
                assert hasattr(warehouse_metrics, "fill_level")
                assert hasattr(warehouse_metrics, "current_load")

        # Получаем метрики производства
        production_metrics = await unified_client.get_production_metrics(simulation_id)
        assert_is_pydantic_model(production_metrics, "ProductionMetricsResponse")

        # Проверяем вложенные модели
        if production_metrics.metrics.monthly_productivity:
            for monthly_prod in production_metrics.metrics.monthly_productivity:
                assert isinstance(monthly_prod, BaseModel)
                assert hasattr(monthly_prod, "month")
                assert hasattr(monthly_prod, "units_produced")
