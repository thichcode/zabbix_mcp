from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import json

class VisualizationService:
    def __init__(self):
        self.colors = {
            'critical': '#FF0000',
            'high': '#FFA500',
            'medium': '#FFFF00',
            'low': '#00FF00'
        }

    def create_event_timeline(self, events: List[Dict[str, Any]]) -> str:
        """Create timeline chart for events"""
        df = pd.DataFrame(events)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = go.Figure()
        
        for severity in ['critical', 'high', 'medium', 'low']:
            mask = df['severity'] == severity
            if mask.any():
                fig.add_trace(go.Scatter(
                    x=df[mask]['timestamp'],
                    y=[severity] * len(df[mask]),
                    mode='markers',
                    name=severity.capitalize(),
                    marker=dict(
                        color=self.colors[severity],
                        size=10
                    )
                ))
        
        fig.update_layout(
            title='Event Timeline',
            xaxis_title='Time',
            yaxis_title='Severity',
            showlegend=True
        )
        
        return fig.to_json()

    def create_severity_distribution(self, events: List[Dict[str, Any]]) -> str:
        """Create severity distribution chart"""
        df = pd.DataFrame(events)
        severity_counts = df['severity'].value_counts()
        
        fig = go.Figure(data=[
            go.Pie(
                labels=severity_counts.index,
                values=severity_counts.values,
                hole=.3
            )
        ])
        
        fig.update_layout(
            title='Severity Distribution',
            showlegend=True
        )
        
        return fig.to_json()

    def create_trend_analysis(self, events: List[Dict[str, Any]], window: str = '1d') -> str:
        """Create trend analysis chart"""
        df = pd.DataFrame(events)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Resample by window
        trend = df.resample(window).size()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend.index,
            y=trend.values,
            mode='lines+markers',
            name='Event Count'
        ))
        
        fig.update_layout(
            title=f'Event Trend Analysis ({window})',
            xaxis_title='Time',
            yaxis_title='Number of Events',
            showlegend=True
        )
        
        return fig.to_json()

    def create_host_analysis(self, events: List[Dict[str, Any]]) -> str:
        """Create host analysis chart"""
        df = pd.DataFrame(events)
        host_counts = df['host'].value_counts()
        
        fig = go.Figure(data=[
            go.Bar(
                x=host_counts.index,
                y=host_counts.values
            )
        ])
        
        fig.update_layout(
            title='Events by Host',
            xaxis_title='Host',
            yaxis_title='Number of Events',
            showlegend=False
        )
        
        return fig.to_json()

    def create_analysis_report(self, events: List[Dict[str, Any]], analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create aggregate analysis report"""
        return {
            'timeline': self.create_event_timeline(events),
            'severity_distribution': self.create_severity_distribution(events),
            'trend_analysis': self.create_trend_analysis(events),
            'host_analysis': self.create_host_analysis(events),
            'summary': {
                'total_events': len(events),
                'total_analyses': len(analyses),
                'average_confidence': sum(a.get('confidence', 0) for a in analyses) / len(analyses) if analyses else 0,
                'most_common_host': pd.DataFrame(events)['host'].mode().iloc[0] if events else None,
                'most_common_severity': pd.DataFrame(events)['severity'].mode().iloc[0] if events else None
            }
        } 