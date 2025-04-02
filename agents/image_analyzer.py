import os
import io
import json
import base64
import uuid
from datetime import datetime
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

class MedicalImageAnalyzer:
    """
    Class for analyzing medical images and extracting relevant metrics.
    """
    
    def __init__(self):
        """Initialize the image analyzer with defaults"""
        self.supported_formats = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
        self.enhancement_types = {
            'contrast': 'Enhance image contrast',
            'brightness': 'Increase image brightness',
            'sharpen': 'Sharpen image details', 
            'edge_detection': 'Detect edges in the image',
            'invert': 'Invert image colors',
            'grayscale': 'Convert to grayscale'
        }
        self.storage_dir = os.path.join('data', 'images')
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def analyze_image(self, image_data, enhancement=None):
        """
        Analyze a medical image and extract relevant metrics.
        
        Args:
            image_data (str): Base64 encoded image data
            enhancement (str, optional): Type of enhancement to apply before analysis
            
        Returns:
            dict: Analysis results including metrics and enhanced image if requested
        """
        try:
            # Decode base64 image
            img_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(img_bytes))
            
            # Check if format is supported
            format_lower = img.format.lower() if img.format else 'unknown'
            if format_lower not in self.supported_formats:
                return {
                    'success': False,
                    'error': f'Unsupported image format: {img.format}. Supported formats: {", ".join(self.supported_formats)}'
                }
            
            # Apply enhancement if requested
            enhanced_img = None
            if enhancement:
                if enhancement not in self.enhancement_types:
                    return {
                        'success': False,
                        'error': f'Unknown enhancement type: {enhancement}. Available types: {", ".join(self.enhancement_types.keys())}'
                    }
                enhanced_img = self._apply_enhancement(img, enhancement)
                # Use enhanced image for analysis
                analyze_img = enhanced_img
            else:
                analyze_img = img
            
            # Extract image metrics
            metrics = self._extract_image_metrics(analyze_img)
            
            # Save the image with a unique name
            image_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"medical_img_{timestamp}_{image_id}.{format_lower}"
            filepath = os.path.join(self.storage_dir, filename)
            
            # Save original image
            img.save(filepath)
            
            # Save enhanced image if it exists
            enhanced_filepath = None
            if enhanced_img:
                enhanced_filename = f"medical_img_{timestamp}_{image_id}_enhanced.{format_lower}"
                enhanced_filepath = os.path.join(self.storage_dir, enhanced_filename)
                enhanced_img.save(enhanced_filepath)
            
            # Convert enhanced image to base64 if it exists
            enhanced_base64 = None
            if enhanced_img:
                buffered = io.BytesIO()
                enhanced_img.save(buffered, format=img.format)
                enhanced_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            return {
                'success': True,
                'image_id': image_id,
                'format': img.format,
                'dimensions': {
                    'width': img.width,
                    'height': img.height
                },
                'file_size': len(img_bytes),
                'image_metrics': metrics,
                'storage_path': filepath,
                'enhancement_applied': enhancement,
                'enhanced_image': enhanced_base64
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error analyzing image: {str(e)}'
            }
    
    def enhance_image(self, image_data, enhancement_type):
        """
        Apply a specific enhancement to an image.
        
        Args:
            image_data (str): Base64 encoded image data
            enhancement_type (str): Type of enhancement to apply
            
        Returns:
            dict: Enhanced image data as base64
        """
        try:
            # Decode base64 image
            img_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(img_bytes))
            
            # Check if enhancement type is supported
            if enhancement_type not in self.enhancement_types:
                return {
                    'success': False,
                    'error': f'Unknown enhancement type: {enhancement_type}. Available types: {", ".join(self.enhancement_types.keys())}'
                }
            
            # Apply enhancement
            enhanced_img = self._apply_enhancement(img, enhancement_type)
            
            # Convert enhanced image to base64
            buffered = io.BytesIO()
            enhanced_img.save(buffered, format=img.format)
            enhanced_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            return {
                'success': True,
                'enhancement_type': enhancement_type,
                'enhanced_image': enhanced_base64
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error enhancing image: {str(e)}'
            }
    
    def _apply_enhancement(self, img, enhancement_type):
        """
        Apply the specified enhancement to an image.
        
        Args:
            img (PIL.Image): Image to enhance
            enhancement_type (str): Type of enhancement to apply
            
        Returns:
            PIL.Image: Enhanced image
        """
        if enhancement_type == 'contrast':
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(1.5)  # Increase contrast by 50%
            
        elif enhancement_type == 'brightness':
            enhancer = ImageEnhance.Brightness(img)
            return enhancer.enhance(1.3)  # Increase brightness by 30%
            
        elif enhancement_type == 'sharpen':
            return img.filter(ImageFilter.SHARPEN)
            
        elif enhancement_type == 'edge_detection':
            return img.filter(ImageFilter.FIND_EDGES)
            
        elif enhancement_type == 'invert':
            if img.mode == 'RGBA':
                # Handle transparency
                r, g, b, a = img.split()
                rgb_image = Image.merge('RGB', (r, g, b))
                inverted_rgb = ImageOps.invert(rgb_image)
                r2, g2, b2 = inverted_rgb.split()
                return Image.merge('RGBA', (r2, g2, b2, a))
            else:
                return ImageOps.invert(img)
                
        elif enhancement_type == 'grayscale':
            if img.mode == 'RGBA':
                # Handle transparency
                r, g, b, a = img.split()
                rgb_image = Image.merge('RGB', (r, g, b))
                gray_rgb = rgb_image.convert('L').convert('RGB')
                r2, g2, b2 = gray_rgb.split()
                return Image.merge('RGBA', (r2, g2, b2, a))
            else:
                return img.convert('L')
        
        # Default: return original image if enhancement type not recognized
        return img
    
    def _extract_image_metrics(self, img):
        """
        Extract various metrics from an image for analysis.
        
        Args:
            img (PIL.Image): Image to analyze
            
        Returns:
            dict: Various image metrics
        """
        # Convert to grayscale for histogram and intensity analysis
        if img.mode == 'RGBA':
            # Remove alpha channel for analysis
            r, g, b, a = img.split()
            gray_img = Image.merge('RGB', (r, g, b)).convert('L')
        else:
            gray_img = img.convert('L')
        
        # Get histogram
        histogram = gray_img.histogram()
        
        # Calculate average intensity
        total_pixels = img.width * img.height
        total_intensity = sum(i * count for i, count in enumerate(histogram))
        avg_intensity = total_intensity / total_pixels if total_pixels > 0 else 0
        
        # Calculate median intensity (approximate)
        half_pixels = total_pixels // 2
        cumulative = 0
        median_intensity = 0
        for i, count in enumerate(histogram):
            cumulative += count
            if cumulative >= half_pixels:
                median_intensity = i
                break
        
        # Calculate standard deviation
        variance = sum(((i - avg_intensity) ** 2) * count for i, count in enumerate(histogram)) / total_pixels
        std_dev = variance ** 0.5
        
        # Analyze edges
        edge_img = gray_img.filter(ImageFilter.FIND_EDGES)
        edge_histogram = edge_img.histogram()
        edge_intensity = sum(i * count for i, count in enumerate(edge_histogram)) / total_pixels
        
        # Calculate contrast
        min_intensity = min(i for i, count in enumerate(histogram) if count > 0)
        max_intensity = max(i for i, count in enumerate(histogram) if count > 0)
        contrast_range = max_intensity - min_intensity
        
        return {
            'average_intensity': round(avg_intensity, 2),
            'median_intensity': median_intensity,
            'standard_deviation': round(std_dev, 2),
            'contrast_range': contrast_range,
            'edge_intensity': round(edge_intensity, 2),
            'intensity_distribution': self._compress_histogram(histogram),
            'bit_depth': img.mode
        }
    
    def _compress_histogram(self, histogram, bins=10):
        """
        Compress a 256-bin histogram to fewer bins for easier analysis.
        
        Args:
            histogram (list): 256-bin histogram
            bins (int): Number of bins to compress to
            
        Returns:
            dict: Compressed histogram
        """
        bin_size = 256 // bins
        compressed = [0] * bins
        
        for i, count in enumerate(histogram):
            bin_index = min(i // bin_size, bins - 1)
            compressed[bin_index] += count
        
        # Convert to dictionary for readability
        result = {}
        for i, count in enumerate(compressed):
            lower = i * bin_size
            upper = min((i + 1) * bin_size - 1, 255)
            result[f"{lower}-{upper}"] = count
        
        return result
    
    def get_available_enhancements(self):
        """
        Get list of available image enhancement options.
        
        Returns:
            dict: Available enhancement types and their descriptions
        """
        return self.enhancement_types 