from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ..services.database import DatabaseService

class TrendAnalysisService:
    def __init__(self, db: DatabaseService):
        self.db = db

    async def analyze_trends(self, host: str, trigger: str, time_range: int = 24) -> Dict[str, Any]:
        """
        Analyze trigger trends within a time range
        time_range: số giờ để phân tích
        """
        # Get events within the time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_range)
        
        events = await self.db.get_events_by_host_and_trigger(
            host=host,
            trigger=trigger,
            start_time=start_time,
            end_time=end_time
        )

        if not events:
            return {
                "has_trend": False,
                "message": "Không đủ dữ liệu để phân tích xu hướng"
            }

        # Convert to DataFrame for analysis
        df = pd.DataFrame(events)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        # Analyze frequency
        frequency = self._analyze_frequency(df)
        
        # Analyze severity
        severity = self._analyze_severity(df)
        
        # Analyze recovery time
        recovery = self._analyze_recovery_time(df)

        return {
            "has_trend": True,
            "frequency_analysis": frequency,
            "severity_analysis": severity,
            "recovery_analysis": recovery,
            "time_range": time_range,
            "total_events": len(events)
        }

    def _analyze_frequency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trigger occurrence frequency"""
        # Calculate hourly event count
        hourly_counts = df.resample('H').size()
        
        return {
            "total_events": len(df),
            "average_per_hour": hourly_counts.mean(),
            "max_per_hour": hourly_counts.max(),
            "min_per_hour": hourly_counts.min(),
            "trend": "increasing" if hourly_counts.diff().mean() > 0 else "decreasing"
        }

    def _analyze_severity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze severity"""
        severity_counts = df['severity'].value_counts()
        
        return {
            "average_severity": df['severity'].mean(),
            "max_severity": df['severity'].max(),
            "severity_distribution": severity_counts.to_dict(),
            "trend": "increasing" if df['severity'].diff().mean() > 0 else "decreasing"
        }

    def _analyze_recovery_time(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze recovery time"""
        recovery_times = []
        
        # Find PROBLEM -> OK pairs
        problem_events = df[df['status'] == 'PROBLEM']
        ok_events = df[df['status'] == 'OK']
        
        for idx, problem in problem_events.iterrows():
            # Find the next OK event
            next_ok = ok_events[ok_events.index > idx]
            if not next_ok.empty:
                recovery_time = (next_ok.index[0] - idx).total_seconds() / 60  # Convert to minutes
                recovery_times.append(recovery_time)

        if not recovery_times:
            return {
                "has_recovery_data": False,
                "message": "Không có dữ liệu về thời gian phục hồi"
            }

        return {
            "has_recovery_data": True,
            "average_recovery_time": np.mean(recovery_times),
            "min_recovery_time": np.min(recovery_times),
            "max_recovery_time": np.max(recovery_times),
            "recovery_times": recovery_times
        } 