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
from datetime import datetime

class DataVisualizer:
    """Class for generating visualizations of medical data"""
    
    def __init__(self):
        """Initialize the data visualizer"""
        # Set default style for matplotlib
        plt.style.use('seaborn-v0_8-whitegrid')
        self.colors = px.colors.qualitative.Plotly
        
        # Create output directory
        self.output_dir = os.path.join(os.getcwd(), "data", "visualizations")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_bar_chart(self, data, title="", x_label="", y_label="", description=""):
        """
        Create a bar chart for data visualization
        
        Args:
            data (dict): Dictionary with keys for data points
            title (str): Chart title
            x_label (str): X-axis label
            y_label (str): Y-axis label
            description (str): Chart description
            
        Returns:
            str: Path to the saved image
        """
        plt.figure(figsize=(10, 6))
        
        # Handle different data formats
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # List of dictionaries format
            df = pd.DataFrame(data)
            x_key = list(df.columns)[0]  # First column as x-axis
            y_key = list(df.columns)[1]  # Second column as y-axis
            
            # Create the bar chart
            bars = plt.bar(
                df[x_key],
                df[y_key],
                color=self.colors[:len(df)]
            )
        else:
            # Direct key-value format
            keys = list(data.keys())
            values = list(data.values())
            
            # Create the bar chart
            bars = plt.bar(
                keys,
                values,
                color=self.colors[:len(keys)]
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
        
        # Save the plot to a file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"bar_chart_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, format='png', dpi=300)
        plt.close()
        
        return filepath
    
    def create_line_chart(self, data, title="", x_label="", y_label="", description=""):
        """
        Create a line chart for time series data
        
        Args:
            data (dict/list): Data to visualize (dict with x/y values or list of points)
            title (str): Chart title
            x_label (str): X-axis label
            y_label (str): Y-axis label
            description (str): Chart description
            
        Returns:
            str: Path to the saved image
        """
        plt.figure(figsize=(10, 6))
        
        # Handle different data formats
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # List of dictionaries format
            df = pd.DataFrame(data)
            x_key = list(df.columns)[0]  # First column as x-axis
            
            # For each numerical column (except x), plot a line
            for col in df.columns:
                if col != x_key and pd.api.types.is_numeric_dtype(df[col]):
                    plt.plot(df[x_key], df[col], marker='o', linewidth=2, label=col)
        
        elif isinstance(data, dict):
            # Check if it's the old format with 'x_values' and 'series'
            if 'x_values' in data and 'series' in data:
                x_values = data['x_values']
                for series in data['series']:
                    plt.plot(x_values, series['values'], marker='o', linewidth=2, label=series['name'])
            else:
                # Simple x-y dict format
                keys = sorted(list(data.keys()))
                values = [data[k] for k in keys]
                plt.plot(keys, values, marker='o', linewidth=2)
        
        # Add title and labels
        plt.title(title, fontsize=16)
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend if we have multiple lines
        if 'label' in plt.gca().get_lines()[0].properties():
            plt.legend()
        
        plt.tight_layout()
        
        # Save the plot to a file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"line_chart_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, format='png', dpi=300)
        plt.close()
        
        return filepath
    
    def create_comparison_chart(self, data, title="", description=""):
        """
        Create a visualization for comparing different values
        
        Args:
            data (dict/list): Data to visualize
            title (str): Chart title
            description (str): Chart description
            
        Returns:
            str: Path to the saved image
        """
        plt.figure(figsize=(10, 6))
        
        # Handle different data formats
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # List of dictionaries format
            df = pd.DataFrame(data)
            labels = df[df.columns[0]]  # First column as labels
            values = df[df.columns[1]]  # Second column as values
        elif isinstance(data, dict):
            # Dictionary format
            labels = list(data.keys())
            values = list(data.values())
        else:
            # Unsupported format
            return None
        
        # Create the pie chart
        plt.pie(
            values, 
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=self.colors[:len(labels)],
            wedgeprops={'edgecolor': 'w'}
        )
        
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title(title, fontsize=16)
        
        # Save the plot to a file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"comparison_chart_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, format='png', dpi=300)
        plt.close()
        
        return filepath
    
    def create_schedule_chart(self, data, title="", description=""):
        """
        Create a chart showing medication schedule
        
        Args:
            data (list): List of schedule entries with Day, Medication, Scheduled columns
            title (str): Chart title
            description (str): Chart description
            
        Returns:
            str: Path to the saved image
        """
        # Convert to DataFrame if not already
        if not isinstance(data, pd.DataFrame):
            df = pd.DataFrame(data)
        else:
            df = data
            
        # Group by Day and Medication, with Scheduled as values
        pivot_df = pd.pivot_table(
            df, 
            values='Scheduled', 
            index='Medication',
            columns='Day',
            fill_value=0
        )
        
        # Create a heatmap
        plt.figure(figsize=(max(10, len(pivot_df.columns) * 0.8), max(6, len(pivot_df) * 0.5)))
        
        # Create the heatmap
        plt.pcolormesh(
            np.arange(len(pivot_df.columns) + 1),
            np.arange(len(pivot_df) + 1),
            pivot_df.values,
            cmap='Greens',
            alpha=0.8,
            edgecolors='white',
            linewidth=1
        )
        
        # Add labels
        plt.title(title, fontsize=16)
        plt.yticks(np.arange(len(pivot_df)) + 0.5, pivot_df.index, fontsize=10)
        plt.xticks(np.arange(len(pivot_df.columns)) + 0.5, pivot_df.columns, fontsize=10, rotation=45, ha='right')
        
        # Add colorbar
        cbar = plt.colorbar(pad=0.01)
        cbar.set_label('Scheduled')
        
        plt.tight_layout()
        
        # Save the plot to a file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"schedule_chart_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, format='png', dpi=300)
        plt.close()
        
        return filepath
    
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
    
    def create_medication_schedule_chart(self, data):
        """
        Create a heatmap-style chart for medication schedules
        
        Args:
            data (dict): Medication schedule data with dates and medication names
            
        Returns:
            dict: Chart data or image reference
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            import numpy as np
            from datetime import datetime
            import base64
            from io import BytesIO
            
            # Extract data
            dates = data["dates"]
            medications = data["medications"]
            
            # Convert dates to datetime objects for better formatting
            date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
            
            # Create a matrix for the heatmap
            med_names = [med["name"] for med in medications]
            schedule_matrix = np.array([med["schedule"] for med in medications])
            
            # Create the figure
            fig, ax = plt.subplots(figsize=(10, max(5, len(medications) * 0.5)))
            
            # Create the heatmap
            heatmap = ax.pcolormesh(
                np.arange(len(dates) + 1), 
                np.arange(len(medications) + 1), 
                schedule_matrix, 
                cmap='Greens', 
                vmin=0, 
                vmax=1
            )
            
            # Set the ticks and labels
            ax.set_xticks(np.arange(len(dates)) + 0.5)
            ax.set_xticklabels([date.strftime('%a\n%m/%d') for date in date_objects], 
                              ha='center', minor=False)
            
            ax.set_yticks(np.arange(len(medications)) + 0.5)
            ax.set_yticklabels(med_names, va='center', minor=False)
            
            # Set labels and title
            ax.set_xlabel('Date')
            ax.set_ylabel('Medication')
            ax.set_title('7-Day Medication Schedule')
            
            # Add grid lines
            ax.set_xticks(np.arange(len(dates) + 1), minor=True)
            ax.set_yticks(np.arange(len(medications) + 1), minor=True)
            ax.grid(which='minor', color='w', linestyle='-', linewidth=2)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save figure to a BytesIO object
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            
            # Convert to base64 string
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            
            return {
                "type": "heatmap",
                "image": f"data:image/png;base64,{image_base64}"
            }
            
        except Exception as e:
            print(f"Error creating medication schedule chart: {e}")
            return None
        
    def _extract_values(self, data_string, pattern=r'[\w\s]+:\s*(\d+)%'):
        """Extract values from a string using regex pattern"""
        # ... existing code ... 