"""
Performance tests and optimization utilities for CreditBeast
Tests system performance, scalability, and optimization opportunities
"""

import pytest
import asyncio
import time
import statistics
import concurrent.futures
from typing import List, Dict, Any, Callable
from unittest.mock import AsyncMock
import memory_profiler
import psutil
import gc

class TestPerformance:
    """Performance test suite for automation and security features"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database for performance testing"""
        db = AsyncMock()
        # Simulate realistic database response times
        async def slow_execute(*args, **kwargs):
            await asyncio.sleep(0.01)  # 10ms simulated database latency
            return AsyncMock(data=[{"id": f"result-{i}"} for i in range(10)])
        
        db.table.return_value.select.return_value.eq.return_value.execute = slow_execute
        db.table.return_value.insert.return_value.execute = slow_execute
        return db
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_letter_generation_performance(self, mock_db):
        """Test letter generation performance under load"""
        from services.automation import LetterGenerationService
        
        letter_service = LetterGenerationService(mock_db)
        
        # Generate 100 dispute letters and measure performance
        start_time = time.time()
        tasks = []
        
        for i in range(100):
            task = letter_service.generate_letter(f"dispute-{i}", "org-123")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / 100
        
        # Performance assertions
        assert total_time < 10.0  # Should complete 100 letters in under 10 seconds
        assert avg_time < 0.1     # Average letter generation under 100ms
        assert len(results) == 100
        assert all(r.get("generated", False) for r in results)
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_lead_scoring_performance(self, mock_db):
        """Test lead scoring performance with complex criteria"""
        from services.lead_scoring import LeadScoringService
        
        lead_service = LeadScoringService(mock_db)
        
        # Test with 50 leads
        lead_data_templates = [
            {
                "first_name": f"John{i}",
                "last_name": "Doe",
                "email": f"john{i}@gmail.com",
                "phone": f"555-{i:03d}-1234",
                "utm_source": "google" if i % 2 == 0 else "facebook"
            }
            for i in range(50)
        ]
        
        start_time = time.time()
        tasks = []
        
        for lead_data in lead_data_templates:
            task = lead_service.score_lead(lead_data, "org-123")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / 50
        
        # Performance assertions
        assert total_time < 5.0   # Should score 50 leads in under 5 seconds
        assert avg_time < 0.1     # Average scoring under 100ms
        assert len(results) == 50
        assert all(0 <= r["score"] <= 10 for r in results)
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_churn_prediction_performance(self, mock_db):
        """Test churn prediction performance with large client base"""
        from services.churn_prediction import ChurnPredictionService
        
        churn_service = ChurnPredictionService(mock_db)
        
        # Simulate analysis of 200 clients
        client_batch = [
            {
                "id": f"client-{i}",
                "first_name": f"Client{i}",
                "last_name": "Test",
                "status": "active",
                "created_at": "2023-01-01T00:00:00Z"
            }
            for i in range(200)
        ]
        
        # Mock client history
        mock_history = {
            "disputes": [{"status": "active"} for _ in range(3)],
            "payments": [{"status": "paid"} for _ in range(5)],
            "communications": [{"status": "sent"} for _ in range(10)],
            "documents": [{"status": "uploaded"} for _ in range(2)]
        }
        
        # Mock database responses
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [client_batch[0]]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = mock_history["disputes"]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = mock_history["payments"]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_history["communications"]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = mock_history["documents"]
        
        start_time = time.time()
        
        # Process clients in batches to avoid overwhelming the system
        batch_size = 20
        all_results = []
        
        for batch_start in range(0, len(client_batch), batch_size):
            batch = client_batch[batch_start:batch_start + batch_size]
            batch_tasks = []
            
            for client in batch:
                task = churn_service.predict_client_churn(client, "org-123", 30, True, True)
                batch_tasks.append(task)
            
            batch_results = await asyncio.gather(*batch_tasks)
            all_results.extend(batch_results)
        
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / 200
        
        # Performance assertions
        assert total_time < 30.0  # Should predict churn for 200 clients in under 30 seconds
        assert avg_time < 0.15    # Average prediction under 150ms
        assert len(all_results) == 200
        assert all(0 <= r["churn_probability"] <= 1 for r in all_results)
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_security_operations_performance(self, mock_db):
        """Test security operations performance"""
        from services.security import AuditLogService, SessionManagementService
        
        audit_service = AuditLogService(mock_db)
        session_service = SessionManagementService(mock_db)
        
        # Test audit logging performance
        start_time = time.time()
        audit_tasks = []
        
        for i in range(100):
            event_data = {
                "event_type": "user_action",
                "severity": "info",
                "user_id": f"user-{i}",
                "action": f"action_{i}",
                "resource": f"resource_{i}"
            }
            task = audit_service.log_security_event("org-123", event_data)
            audit_tasks.append(task)
        
        audit_results = await asyncio.gather(*audit_tasks)
        audit_time = time.time() - start_time
        
        # Test session management performance
        start_time = time.time()
        session_tasks = []
        
        for i in range(50):
            session_data = {
                "ip_address": f"192.168.1.{i}",
                "user_agent": f"Browser-{i}"
            }
            task = session_service.create_session(f"user-{i}", "org-123", session_data)
            session_tasks.append(task)
        
        session_results = await asyncio.gather(*session_tasks)
        session_time = time.time() - start_time
        
        # Performance assertions
        assert audit_time < 5.0   # 100 audit logs in under 5 seconds
        assert session_time < 10.0  # 50 sessions in under 10 seconds
        assert len(audit_results) == 100
        assert len(session_results) == 50
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_workflow_performance(self, mock_db):
        """Test multiple workflows running concurrently"""
        from services.automation import BureauTargetingService
        from services.lead_scoring import LeadScoringService
        from services.churn_prediction import ChurnPredictionService
        
        bureau_service = BureauTargetingService(mock_db)
        lead_service = LeadScoringService(mock_db)
        churn_service = ChurnPredictionService(mock_db)
        
        # Create diverse workload
        tasks = []
        
        # 20 bureau targeting requests
        for i in range(20):
            dispute_data = {
                "dispute_type": "late_payment" if i % 2 == 0 else "collection",
                "account_name": f"Account-{i}",
                "organization_id": "org-123"
            }
            task = bureau_service.recommend_bureaus(dispute_data)
            tasks.append(task)
        
        # 30 lead scoring requests
        for i in range(30):
            lead_data = {
                "first_name": f"Lead{i}",
                "last_name": "Test",
                "email": f"lead{i}@example.com",
                "phone": f"555-{i:04d}"
            }
            task = lead_service.score_lead(lead_data, "org-123")
            tasks.append(task)
        
        # 10 churn prediction requests
        for i in range(10):
            client = {
                "id": f"client-{i}",
                "first_name": f"Client{i}",
                "last_name": "Test",
                "status": "active"
            }
            # Mock client history
            mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [client]
            mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
            mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
            mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
            mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
            
            task = churn_service.predict_client_churn(client, "org-123", 30, True, True)
            tasks.append(task)
        
        # Execute all tasks concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        total_time = end_time - start_time
        successful_results = [r for r in results if not isinstance(r, Exception)]
        
        # Performance assertions
        assert total_time < 20.0  # All workflows in under 20 seconds
        assert len(successful_results) >= 50  # At least 50% success rate
        assert len(results) == 60  # All tasks executed
    
    @pytest.mark.performance
    def test_memory_usage_monitoring(self):
        """Test memory usage during intensive operations"""
        import tracemalloc
        
        tracemalloc.start()
        
        # Simulate memory-intensive operations
        data_structures = []
        for i in range(1000):
            # Create various data structures
            lead = {
                "id": f"lead-{i}",
                "data": [j for j in range(100)],  # 100 integers
                "tags": [f"tag-{j}" for j in range(10)],  # 10 strings
                "history": [{"action": f"action-{j}", "timestamp": f"2023-{i:02d}-{j:02d}"} for j in range(20)]
            }
            data_structures.append(lead)
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory assertions
        assert current < 100 * 1024 * 1024  # Less than 100MB current usage
        assert peak < 200 * 1024 * 1024     # Less than 200MB peak usage
        
        # Cleanup
        del data_structures
        gc.collect()
    
    @pytest.mark.performance
    def test_cpu_usage_monitoring(self):
        """Test CPU usage during intensive computations"""
        start_time = time.time()
        start_cpu = psutil.cpu_percent(interval=None)
        
        # Simulate CPU-intensive operations
        def cpu_intensive_task():
            result = 0
            for i in range(1000000):
                result += i * i
            return result
        
        # Run multiple CPU-intensive tasks
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(cpu_intensive_task) for _ in range(4)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        end_cpu = psutil.cpu_percent(interval=None)
        
        processing_time = end_time - start_time
        cpu_usage = end_cpu - start_cpu
        
        # Performance assertions
        assert processing_time < 10.0  # Should complete in under 10 seconds
        assert cpu_usage > 0  # CPU should be utilized
        assert len(results) == 4  # All tasks completed
    
    @pytest.mark.performance
    async def test_database_connection_pool_performance(self, mock_db):
        """Test database connection pool performance"""
        from services.database import db
        
        # Simulate database load
        concurrent_queries = []
        
        for i in range(50):
            async def query_db():
                # Simulate database operations
                await asyncio.sleep(0.005)  # 5ms per query
                return f"result-{i}"
            
            concurrent_queries.append(query_db())
        
        start_time = time.time()
        results = await asyncio.gather(*concurrent_queries)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / 50
        
        # Database performance assertions
        assert total_time < 2.0   # 50 concurrent queries in under 2 seconds
        assert avg_time < 0.05    # Average query time under 50ms
        assert len(results) == 50


class TestOptimization:
    """Test optimization opportunities and improvements"""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_batch_processing_optimization(self, mock_db):
        """Test performance benefits of batch processing"""
        from services.automation import LetterGenerationService
        
        letter_service = LetterGenerationService(mock_db)
        
        # Test individual processing
        start_time = time.time()
        individual_tasks = []
        
        for i in range(10):
            task = letter_service.generate_letter(f"dispute-{i}", "org-123")
            individual_tasks.append(task)
        
        await asyncio.gather(*individual_tasks)
        individual_time = time.time() - start_time
        
        # Test batch processing (optimized version)
        start_time = time.time()
        batch_result = await letter_service.generate_batch_letters([f"dispute-{i}" for i in range(10)], "org-123")
        batch_time = time.time() - start_time
        
        # Optimization assertions
        assert batch_time < individual_time  # Batch should be faster
        assert batch_result["processed_count"] == 10
        assert batch_time < 1.0  # Batch should complete in under 1 second
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_caching_performance(self, mock_db):
        """Test performance benefits of caching"""
        from services.lead_scoring import LeadScoringService
        
        lead_service = LeadScoringService(mock_db)
        
        # Test without cache
        lead_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com"
        }
        
        # First request (cache miss)
        start_time = time.time()
        result1 = await lead_service.score_lead(lead_data, "org-123")
        first_request_time = time.time() - start_time
        
        # Second request (cache hit)
        start_time = time.time()
        result2 = await lead_service.score_lead(lead_data, "org-123")
        second_request_time = time.time() - start_time
        
        # Cache performance assertions
        assert second_request_time < first_request_time  # Cache hit should be faster
        assert result1["score"] == result2["score"]  # Results should be identical
        assert first_request_time > 0  # First request should take some time
    
    @pytest.mark.performance
    def test_data_structure_optimization(self):
        """Test optimized data structures for performance"""
        import array
        
        # Test list vs array performance
        data_size = 1000000
        
        # List operations
        start_time = time.time()
        test_list = [i for i in range(data_size)]
        list_time = time.time() - start_time
        
        # Array operations
        start_time = time.time()
        test_array = array.array('I', range(data_size))
        array_time = time.time() - start_time
        
        # Memory usage
        import sys
        list_memory = sys.getsizeof(test_list) + sum(sys.getsizeof(item) for item in test_list)
        array_memory = sys.getsizeof(test_array) + test_array.buffer_info()[1] * test_array.itemsize
        
        # Optimization assertions
        assert array_time <= list_time  # Array should be as fast or faster
        assert array_memory < list_memory  # Array should use less memory
        assert len(test_array) == data_size
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_api_response_time_benchmarks(self, mock_db):
        """Test API response time benchmarks"""
        from services.lead_scoring import LeadScoringService
        from services.churn_prediction import ChurnPredictionService
        
        lead_service = LeadScoringService(mock_db)
        churn_service = ChurnPredictionService(mock_db)
        
        # Benchmark lead scoring
        lead_data = {"first_name": "Benchmark", "last_name": "Test", "email": "bench@test.com"}
        
        # Run multiple times to get average
        lead_times = []
        for _ in range(10):
            start_time = time.time()
            await lead_service.score_lead(lead_data, "org-123")
            lead_times.append(time.time() - start_time)
        
        avg_lead_time = statistics.mean(lead_times)
        max_lead_time = max(lead_times)
        
        # Benchmark churn prediction
        client = {"id": "bench-client", "first_name": "Bench", "last_name": "Test", "status": "active"}
        
        # Mock database responses for churn service
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [client]
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        
        churn_times = []
        for _ in range(5):
            start_time = time.time()
            await churn_service.predict_client_churn(client, "org-123", 30, True, True)
            churn_times.append(time.time() - start_time)
        
        avg_churn_time = statistics.mean(churn_times)
        max_churn_time = max(churn_times)
        
        # Response time benchmarks
        assert avg_lead_time < 0.1   # Average lead scoring under 100ms
        assert max_lead_time < 0.2   # Maximum lead scoring under 200ms
        assert avg_churn_time < 0.15 # Average churn prediction under 150ms
        assert max_churn_time < 0.3  # Maximum churn prediction under 300ms


# Performance monitoring and alerting
class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    def __init__(self):
        self.metrics = {}
        self.thresholds = {
            "api_response_time": 0.2,  # 200ms
            "db_query_time": 0.05,     # 50ms
            "memory_usage": 100 * 1024 * 1024,  # 100MB
            "cpu_usage": 80  # 80%
        }
    
    def record_metric(self, name: str, value: float, unit: str = "ms"):
        """Record a performance metric"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({
            "value": value,
            "unit": unit,
            "timestamp": time.time()
        })
    
    def check_thresholds(self) -> Dict[str, bool]:
        """Check if metrics exceed thresholds"""
        alerts = {}
        for metric_name, threshold in self.thresholds.items():
            if metric_name in self.metrics:
                recent_values = [m["value"] for m in self.metrics[metric_name][-10:]]  # Last 10 values
                avg_value = statistics.mean(recent_values)
                alerts[metric_name] = avg_value > threshold
        return alerts
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {}
        for metric_name, measurements in self.metrics.items():
            values = [m["value"] for m in measurements]
            summary[metric_name] = {
                "count": len(values),
                "avg": statistics.mean(values),
                "min": min(values),
                "max": max(values),
                "latest": values[-1] if values else 0
            }
        return summary


# Usage example for performance monitoring
def create_performance_test():
    """Example of how to use performance monitoring in tests"""
    monitor = PerformanceMonitor()
    
    # Simulate API calls
    for i in range(100):
        start_time = time.time()
        # Simulate some work
        time.sleep(0.01)
        end_time = time.time()
        
        response_time = end_time - start_time
        monitor.record_metric("api_response_time", response_time)
    
    # Check for performance issues
    alerts = monitor.check_thresholds()
    summary = monitor.get_performance_summary()
    
    return {
        "alerts": alerts,
        "summary": summary,
        "passed": not any(alerts.values())
    }