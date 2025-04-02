import os
import json
import base64
import io
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

class DataVisualizer:
    """Class for generating visualizations of medical data"""
    
    def __init__(self):
        """Initialize the data visualizer"""
        # Set default style for matplotlib
        plt.style.use('seaborn-v0_8-whitegrid')
        self.colors = px.colors.qualitative.Plotly
    
    def create_bar_chart(self, data, title="", x_label="", y_label=""):
        """Create a bar chart using matplotlib"""
        plt.figure(figsize=(10, 6))
        
        # Create the bar chart
        bars = plt.bar(
            data['labels'], 
            data['values'], 
            color=self.colors[:len(data['labels'])]
        )
        
        # Add title and labels
        plt.title(title, fontsize=16)
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.,
                height + 0.1,
                f"{height:.1f}",
                ha='center', va='bottom'
            )
        
        plt.tight_layout()
        
        # Convert the plot to a base64 encoded string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(image_png).decode('utf-8')
    
    def create_line_chart(self, data, title="", x_label="", y_label=""):
        """Create a line chart using plotly"""
        fig = go.Figure()
        
        # Add each line
        for i, series in enumerate(data['series']):
            fig.add_trace(go.Scatter(
                x=data['x_values'],
                y=series['values'],
                mode='lines+markers',
                name=series['name'],
                line=dict(color=self.colors[i % len(self.colors)], width=2),
                marker=dict(size=8)
            ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            template="plotly_white"
        )
        
        # Convert to JSON
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def create_pie_chart(self, data, title=""):
        """Create a pie chart using plotly"""
        fig = go.Figure(data=[go.Pie(
            labels=data['labels'],
            values=data['values'],
            hole=.3,
            marker_colors=self.colors[:len(data['labels'])]
        )])
        
        fig.update_layout(
            title_text=title,
            template="plotly_white"
        )
        
        # Convert to JSON
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def parse_symptoms_data(self, text_data):
        """Parse symptom frequency data from text and prepare for visualization"""
        try:
            # This is a simplified parser - in a real app you'd want more robust parsing
            lines = text_data.strip().split('\n')
            data = {'labels': [], 'values': []}
            
            for line in lines:
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        symptom = parts[0].strip()
                        try:
                            frequency = float(parts[1].strip().rstrip('%'))
                            data['labels'].append(symptom)
                            data['values'].append(frequency)
                        except ValueError:
                            continue
            
            return data
        except Exception as e:
            print(f"Error parsing symptom data: {e}")
            return {'labels': [], 'values': []}
    
    def parse_treatment_efficacy(self, text_data):
        """Parse treatment efficacy data from text and prepare for visualization"""
        try:
            lines = text_data.strip().split('\n')
            data = {'labels': [], 'values': []}
            
            for line in lines:
                if ':' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        treatment = parts[0].strip()
                        try:
                            efficacy = float(parts[1].strip().rstrip('%'))
                            data['labels'].append(treatment)
                            data['values'].append(efficacy)
                        except ValueError:
                            continue
            
            return data
        except Exception as e:
            print(f"Error parsing treatment data: {e}")
            return {'labels': [], 'values': []}
    
    def parse_time_series_data(self, text_data):
        """Parse time series disease progression data and prepare for visualization"""
        try:
            # Sample data format expected:
            # Date: 2020, Metric1: 10, Metric2: 20
            # Date: 2021, Metric1: 15, Metric2: 25
            
            lines = text_data.strip().split('\n')
            dates = []
            metrics = {}
            
            for line in lines:
                parts = line.split(',')
                if len(parts) < 2:
                    continue
                
                date_part = parts[0].strip()
                if not date_part.startswith('Date:'):
                    continue
                    
                date = date_part.replace('Date:', '').strip()
                dates.append(date)
                
                for metric_part in parts[1:]:
                    if ':' not in metric_part:
                        continue
                        
                    metric_name, value_str = metric_part.split(':')
                    metric_name = metric_name.strip()
                    
                    try:
                        value = float(value_str.strip())
                        if metric_name not in metrics:
                            metrics[metric_name] = []
                        metrics[metric_name].append(value)
                    except ValueError:
                        continue
            
            # Prepare the data structure for the chart
            series_data = []
            for name, values in metrics.items():
                if len(values) == len(dates):  # Only include complete series
                    series_data.append({
                        'name': name,
                        'values': values
                    })
            
            return {
                'x_values': dates,
                'series': series_data
            }
            
        except Exception as e:
            print(f"Error parsing time series data: {e}")
            return {'x_values': [], 'series': []} 