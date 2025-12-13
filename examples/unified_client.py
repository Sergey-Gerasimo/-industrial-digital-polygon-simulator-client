#!/usr/bin/env python3
"""
Пример использования обновленного клиента с новыми возможностями.
"""

import asyncio
import logging
from simulation_client import AsyncUnifiedClient
from simulation_client.models import CreateSupplierRequest, CreateLeanImprovementRequest


logging.basicConfig(level=logging.INFO)


async def main():
    print("=== Использование обновленного unified клиента ===")

    # Используем unified клиент для работы с обоими сервисами
    async with AsyncUnifiedClient(
        sim_host="localhost",
        sim_port=50051,  # SimulationService
        db_host="localhost",
        db_port=50052,  # DatabaseManager
    ) as client:
        print("Connected to both services")

        # Проверяем доступность сервисов
        ping_results = await client.ping()
        print(f"Service status: Simulation={ping_results['simulation_service']}, Database={ping_results['database_service']}")

        # Получаем доступные ресурсы
        resources = await client.get_available_resources_simple()
        print(f"Available resources: {len(resources['suppliers'])} suppliers, {len(resources['workers'])} workers, {len(resources['equipment'])} equipment")

        # Создаем нового поставщика с material_type
        supplier_request = CreateSupplierRequest(
            name="Новый поставщик",
            product_name="Сталь",
            material_type="Металл",  # Новое поле
            delivery_period=10,
            special_delivery_period=5,
            reliability=0.95,
            product_quality=0.9,
            cost=10000,
            special_delivery_cost=15000,
        )
        new_supplier = await client.create_supplier(supplier_request)
        print(f"Created supplier: {new_supplier.name} ({new_supplier.material_type})")

        # Создаем Lean улучшение
        improvement_request = CreateLeanImprovementRequest(
            name="Just-in-Time Production",
            is_implemented=False,
            implementation_cost=50000,
            efficiency_gain=0.15,
        )
        new_improvement = await client.create_lean_improvement(improvement_request)
        print(f"Created improvement: {new_improvement.name}")

        # Создаем и настраиваем симуляцию
        print("\n--- Simulation Setup ---")
        simulation_config = await client.create_and_configure_simulation(
            supplier_ids=[new_supplier.supplier_id],
            production_improvements=[new_improvement.improvement_id],
        )
        print(f"Created and configured simulation: {simulation_config.simulation_id}")

        # Запускаем симуляцию
        results = await client.run_simulation(simulation_config.simulation_id)
        print(f"Simulation results: profit={results.profit:,} ₽")

        # Получаем метрики
        try:
            metrics = await client.get_all_metrics(simulation_config.simulation_id)
            print(f"Factory metrics: profitability={metrics.factory.profitability:.1%}, OEE={metrics.factory.oee:.1%}")
            print(f"Production metrics: equipment utilization={metrics.production.average_equipment_utilization:.1%}")
            print(f"Quality metrics: defect rate={metrics.quality.defect_percentage:.1%}")
        except Exception as e:
            print(f"Could not get metrics: {e}")

        # Получаем производственный план
        try:
            schedule = await client.get_production_schedule(simulation_config.simulation_id)
            print(f"Production schedule has {len(schedule.schedule.rows)} rows")
        except Exception as e:
            print(f"Could not get production schedule: {e}")

        # Получаем справочные данные
        try:
            material_types = await client.get_material_types()
            equipment_types = await client.get_equipment_types()
            print(f"Reference data: {len(material_types.material_types)} material types, {len(equipment_types.equipment_types)} equipment types")
        except Exception as e:
            print(f"Could not get reference data: {e}")

        print("\n=== Demo completed successfully ===")


if __name__ == "__main__":
    asyncio.run(main())
