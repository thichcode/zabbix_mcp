import pytest
from datetime import datetime
from app.services.analysis import EventAnalysisService
from app.models.event import Event, EventAnalysis
from unittest.mock import Mock, patch

@pytest.fixture
def sample_event():
    return Event(
        event_id="123",
        host="test-host",
        trigger="High CPU Usage",
        severity=4,
        timestamp=datetime.now(),
        description="CPU usage is above 90%"
    )

@pytest.fixture
def analysis_service():
    return EventAnalysisService()

@pytest.mark.asyncio
async def test_analyze_event(analysis_service, sample_event):
    """Test phân tích sự kiện"""
    with patch('app.services.analysis.EventAnalysisService._create_analysis_prompt') as mock_prompt:
        mock_prompt.return_value = "Test prompt"
        
        with patch('app.services.analysis.EventAnalysisService._parse_analysis_response') as mock_parse:
            mock_parse.return_value = {
                "root_cause": "Test root cause",
                "confidence": 0.9,
                "recommendations": ["Test recommendation"],
                "metadata": {"test": "test"}
            }
            
            result = await analysis_service.analyze_event(sample_event)
            
            assert isinstance(result, EventAnalysis)
            assert result.root_cause == "Test root cause"
            assert result.confidence == 0.9
            assert len(result.recommendations) == 1
            assert result.metadata["test"] == "test"

@pytest.mark.asyncio
async def test_analyze_event_with_cache(analysis_service, sample_event):
    """Test phân tích sự kiện với cache"""
    with patch('app.services.cache_service.CacheService.get_cached_analysis') as mock_cache:
        mock_cache.return_value = {
            "root_cause": "Cached root cause",
            "confidence": 0.8,
            "recommendations": ["Cached recommendation"],
            "metadata": {"cached": "true"}
        }
        
        result = await analysis_service.analyze_event(sample_event)
        
        assert isinstance(result, EventAnalysis)
        assert result.root_cause == "Cached root cause"
        assert result.confidence == 0.8
        assert len(result.recommendations) == 1
        assert result.metadata["cached"] == "true"

@pytest.mark.asyncio
async def test_analyze_event_error(analysis_service, sample_event):
    """Test xử lý lỗi khi phân tích sự kiện"""
    with patch('app.services.analysis.EventAnalysisService._create_analysis_prompt') as mock_prompt:
        mock_prompt.side_effect = Exception("Test error")
        
        with pytest.raises(Exception) as exc_info:
            await analysis_service.analyze_event(sample_event)
        
        assert str(exc_info.value) == "Test error"

@pytest.mark.asyncio
async def test_create_analysis_prompt(analysis_service, sample_event):
    """Test tạo prompt phân tích"""
    prompt = await analysis_service._create_analysis_prompt(sample_event, [])
    
    assert isinstance(prompt, str)
    assert sample_event.host in prompt
    assert sample_event.trigger in prompt
    assert str(sample_event.severity) in prompt
    assert sample_event.description in prompt

@pytest.mark.asyncio
async def test_parse_analysis_response(analysis_service):
    """Test parse kết quả phân tích"""
    response = {
        "root_cause": "Test root cause",
        "confidence": 0.9,
        "recommendations": ["Test recommendation"],
        "metadata": {"test": "test"}
    }
    
    result = await analysis_service._parse_analysis_response(response)
    
    assert isinstance(result, dict)
    assert result["root_cause"] == "Test root cause"
    assert result["confidence"] == 0.9
    assert len(result["recommendations"]) == 1
    assert result["metadata"]["test"] == "test"
    assert "timestamp" in result["metadata"] 