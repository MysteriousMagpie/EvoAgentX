"""
Multi-Modal Intelligence System for VaultPilot

Advanced multi-modal AI capabilities leveraging EvoAgentX's
intelligence systems for processing text, images, audio, and
structured data within Obsidian vaults.
"""

import asyncio
import json
import base64
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import mimetypes
import os

from .api_models import APIResponse


class ModalityType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CODE = "code"
    TABLE = "table"
    DIAGRAM = "diagram"
    MATHEMATICAL = "mathematical"
    STRUCTURED_DATA = "structured_data"


class ProcessingCapability(Enum):
    EXTRACTION = "extraction"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    TRANSFORMATION = "transformation"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CLASSIFICATION = "classification"
    COMPARISON = "comparison"


@dataclass
class MediaAsset:
    """Multi-modal media asset"""
    asset_id: str
    file_path: str
    modality: ModalityType
    mime_type: str
    size_bytes: int
    created_date: datetime
    metadata: Dict[str, Any]
    processing_status: str = "pending"
    extracted_content: Optional[Dict[str, Any]] = None
    analysis_results: Optional[Dict[str, Any]] = None


@dataclass
class MultiModalRequest:
    """Multi-modal processing request"""
    request_id: str
    assets: List[MediaAsset]
    capabilities: List[ProcessingCapability]
    context: str
    output_format: str
    user_id: str
    timestamp: datetime
    priority: int = 5  # 1-10 scale


@dataclass
class MultiModalResponse:
    """Multi-modal processing response"""
    request_id: str
    results: Dict[str, Any]
    processing_time: float
    capabilities_used: List[ProcessingCapability]
    confidence_scores: Dict[str, float]
    generated_artifacts: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]


class MultiModalIntelligenceEngine:
    """
    Advanced multi-modal intelligence system for VaultPilot.
    
    Processes and analyzes various media types within Obsidian vaults,
    extracting insights and generating structured knowledge.
    """
    
    def __init__(self):
        self.supported_modalities = {
            ModalityType.TEXT: [".md", ".txt", ".pdf", ".docx"],
            ModalityType.IMAGE: [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"],
            ModalityType.AUDIO: [".mp3", ".wav", ".m4a", ".flac"],
            ModalityType.VIDEO: [".mp4", ".avi", ".mov", ".mkv"],
            ModalityType.CODE: [".py", ".js", ".ts", ".html", ".css", ".json"],
            ModalityType.TABLE: [".csv", ".xlsx", ".tsv"],
            ModalityType.STRUCTURED_DATA: [".json", ".yaml", ".xml", ".toml"]
        }
        
        self.processing_pipeline = {
            ModalityType.TEXT: self._process_text,
            ModalityType.IMAGE: self._process_image,
            ModalityType.AUDIO: self._process_audio,
            ModalityType.VIDEO: self._process_video,
            ModalityType.CODE: self._process_code,
            ModalityType.TABLE: self._process_table,
            ModalityType.STRUCTURED_DATA: self._process_structured_data
        }
        
        self.processed_assets: Dict[str, MediaAsset] = {}
        self.processing_history: List[MultiModalRequest] = []
    
    async def process_vault_media(self, 
                                vault_path: str, 
                                capabilities: List[ProcessingCapability],
                                user_id: str,
                                context: str = "") -> MultiModalResponse:
        """
        Process all media assets in a vault
        
        Args:
            vault_path: Path to the Obsidian vault
            capabilities: Desired processing capabilities
            user_id: ID of the requesting user
            context: Additional context for processing
            
        Returns:
            Comprehensive multi-modal analysis results
        """
        # Discover media assets
        assets = await self._discover_media_assets(vault_path)
        
        # Create processing request
        request = MultiModalRequest(
            request_id=f"vault_process_{datetime.now().timestamp()}",
            assets=assets,
            capabilities=capabilities,
            context=context,
            output_format="comprehensive",
            user_id=user_id,
            timestamp=datetime.now()
        )
        
        # Process assets
        response = await self._process_multi_modal_request(request)
        
        # Store processing history
        self.processing_history.append(request)
        
        return response
    
    async def analyze_specific_assets(self, 
                                    asset_paths: List[str],
                                    capabilities: List[ProcessingCapability],
                                    user_id: str,
                                    context: str = "") -> MultiModalResponse:
        """
        Analyze specific media assets
        
        Args:
            asset_paths: Paths to specific assets to analyze
            capabilities: Desired processing capabilities
            user_id: ID of the requesting user
            context: Additional context for processing
            
        Returns:
            Analysis results for the specified assets
        """
        # Convert paths to MediaAsset objects
        assets = []
        for path in asset_paths:
            asset = await self._create_media_asset(path)
            if asset:
                assets.append(asset)
        
        if not assets:
            return MultiModalResponse(
                request_id="empty_request",
                results={"error": "No valid assets found"},
                processing_time=0.0,
                capabilities_used=[],
                confidence_scores={},
                generated_artifacts=[],
                recommendations=[],
                metadata={}
            )
        
        # Create and process request
        request = MultiModalRequest(
            request_id=f"specific_analysis_{datetime.now().timestamp()}",
            assets=assets,
            capabilities=capabilities,
            context=context,
            output_format="detailed",
            user_id=user_id,
            timestamp=datetime.now()
        )
        
        return await self._process_multi_modal_request(request)
    
    async def generate_multimedia_summary(self, 
                                        vault_path: str,
                                        focus_areas: List[str],
                                        user_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive multimedia summary of the vault
        
        Args:
            vault_path: Path to the Obsidian vault
            focus_areas: Areas to focus the summary on
            user_id: ID of the requesting user
            
        Returns:
            Multimedia vault summary with insights and recommendations
        """
        # Process vault with all capabilities
        all_capabilities = list(ProcessingCapability)
        context = f"Focus areas: {', '.join(focus_areas)}"
        
        response = await self.process_vault_media(vault_path, all_capabilities, user_id, context)
        
        # Generate summary insights
        summary = await self._generate_comprehensive_summary(response, focus_areas)
        
        return summary
    
    async def extract_cross_modal_insights(self, 
                                         assets: List[MediaAsset],
                                         user_id: str) -> Dict[str, Any]:
        """
        Extract insights that span multiple modalities
        
        Args:
            assets: List of media assets to analyze together
            user_id: ID of the requesting user
            
        Returns:
            Cross-modal insights and connections
        """
        # Group assets by modality
        modality_groups = {}
        for asset in assets:
            if asset.modality not in modality_groups:
                modality_groups[asset.modality] = []
            modality_groups[asset.modality].append(asset)
        
        # Process each modality group
        modality_results = {}
        for modality, group_assets in modality_groups.items():
            if modality in self.processing_pipeline:
                results = []
                for asset in group_assets:
                    result = await self.processing_pipeline[modality](asset)
                    results.append(result)
                modality_results[modality.value] = results
        
        # Find cross-modal connections
        connections = await self._find_cross_modal_connections(modality_results)
        
        # Generate insights
        insights = await self._generate_cross_modal_insights(connections, modality_results)
        
        return {
            "cross_modal_connections": connections,
            "insights": insights,
            "modality_breakdown": {k: len(v) for k, v in modality_groups.items()},
            "processing_summary": modality_results
        }
    
    async def _discover_media_assets(self, vault_path: str) -> List[MediaAsset]:
        """Discover all media assets in a vault"""
        assets = []
        
        for root, dirs, files in os.walk(vault_path):
            for file in files:
                file_path = os.path.join(root, file)
                asset = await self._create_media_asset(file_path)
                if asset:
                    assets.append(asset)
        
        return assets
    
    async def _create_media_asset(self, file_path: str) -> Optional[MediaAsset]:
        """Create a MediaAsset from a file path"""
        if not os.path.exists(file_path):
            return None
        
        # Determine modality from file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        modality = None
        for mod_type, extensions in self.supported_modalities.items():
            if ext in extensions:
                modality = mod_type
                break
        
        if not modality:
            return None
        
        # Get file info
        stat = os.stat(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        asset = MediaAsset(
            asset_id=hashlib.md5(file_path.encode()).hexdigest(),
            file_path=file_path,
            modality=modality,
            mime_type=mime_type or "application/octet-stream",
            size_bytes=stat.st_size,
            created_date=datetime.fromtimestamp(stat.st_ctime),
            metadata={
                "filename": os.path.basename(file_path),
                "directory": os.path.dirname(file_path),
                "relative_path": file_path,
                "extension": ext
            }
        )
        
        return asset
    
    async def _process_multi_modal_request(self, request: MultiModalRequest) -> MultiModalResponse:
        """Process a multi-modal request"""
        start_time = datetime.now()
        results = {}
        capabilities_used = []
        confidence_scores = {}
        generated_artifacts = []
        
        # Process each asset
        for asset in request.assets:
            if asset.modality in self.processing_pipeline:
                asset_results = await self.processing_pipeline[asset.modality](asset)
                results[asset.asset_id] = asset_results
                
                # Extract confidence scores
                if "confidence" in asset_results:
                    confidence_scores[asset.asset_id] = asset_results["confidence"]
        
        # Apply requested capabilities
        for capability in request.capabilities:
            capability_results = await self._apply_capability(capability, results, request.context)
            results[f"capability_{capability.value}"] = capability_results
            capabilities_used.append(capability)
        
        # Generate artifacts if requested
        if ProcessingCapability.GENERATION in request.capabilities:
            artifacts = await self._generate_artifacts(results, request)
            generated_artifacts.extend(artifacts)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(results, request)
        
        return MultiModalResponse(
            request_id=request.request_id,
            results=results,
            processing_time=processing_time,
            capabilities_used=capabilities_used,
            confidence_scores=confidence_scores,
            generated_artifacts=generated_artifacts,
            recommendations=recommendations,
            metadata={
                "total_assets": len(request.assets),
                "modalities_processed": list(set(asset.modality.value for asset in request.assets)),
                "processing_timestamp": datetime.now().isoformat()
            }
        )
    
    async def _process_text(self, asset: MediaAsset) -> Dict[str, Any]:
        """Process text-based assets"""
        try:
            with open(asset.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract text features
            word_count = len(content.split())
            char_count = len(content)
            line_count = len(content.splitlines())
            
            # Simple sentiment analysis (placeholder)
            sentiment = "neutral"
            if any(word in content.lower() for word in ["excellent", "great", "amazing", "wonderful"]):
                sentiment = "positive"
            elif any(word in content.lower() for word in ["terrible", "awful", "bad", "horrible"]):
                sentiment = "negative"
            
            # Extract potential topics (simplified)
            topics = await self._extract_topics(content)
            
            return {
                "content_preview": content[:500] + "..." if len(content) > 500 else content,
                "statistics": {
                    "word_count": word_count,
                    "character_count": char_count,
                    "line_count": line_count
                },
                "analysis": {
                    "sentiment": sentiment,
                    "topics": topics,
                    "language": "english",  # Simplified
                    "readability": "medium"  # Simplified
                },
                "confidence": 0.85
            }
        except Exception as e:
            return {"error": str(e), "confidence": 0.0}
    
    async def _process_image(self, asset: MediaAsset) -> Dict[str, Any]:
        """Process image assets"""
        try:
            # Get image metadata
            metadata = {
                "format": asset.metadata.get("extension", "unknown"),
                "size_mb": round(asset.size_bytes / (1024 * 1024), 2)
            }
            
            # Placeholder for image analysis
            # In a real implementation, this would use computer vision APIs
            analysis = {
                "has_text": False,  # OCR placeholder
                "dominant_colors": ["blue", "white"],  # Color analysis placeholder
                "detected_objects": [],  # Object detection placeholder
                "scene_description": "Image analysis not yet implemented",
                "technical_quality": "good"
            }
            
            return {
                "metadata": metadata,
                "analysis": analysis,
                "suggestions": [
                    "Consider adding alt text for accessibility",
                    "Image could be optimized for web if size > 1MB"
                ],
                "confidence": 0.6  # Lower confidence for placeholder implementation
            }
        except Exception as e:
            return {"error": str(e), "confidence": 0.0}
    
    async def _process_audio(self, asset: MediaAsset) -> Dict[str, Any]:
        """Process audio assets"""
        # Placeholder implementation
        return {
            "metadata": {
                "duration": "unknown",  # Would need audio library
                "format": asset.metadata.get("extension", "unknown"),
                "size_mb": round(asset.size_bytes / (1024 * 1024), 2)
            },
            "analysis": {
                "transcription": "Audio transcription not yet implemented",
                "speaker_count": "unknown",
                "sentiment": "neutral",
                "key_topics": []
            },
            "confidence": 0.3  # Low confidence for placeholder
        }
    
    async def _process_video(self, asset: MediaAsset) -> Dict[str, Any]:
        """Process video assets"""
        # Placeholder implementation
        return {
            "metadata": {
                "duration": "unknown",
                "resolution": "unknown",
                "format": asset.metadata.get("extension", "unknown"),
                "size_mb": round(asset.size_bytes / (1024 * 1024), 2)
            },
            "analysis": {
                "scene_changes": [],
                "dominant_topics": [],
                "audio_transcription": "Video analysis not yet implemented"
            },
            "confidence": 0.3
        }
    
    async def _process_code(self, asset: MediaAsset) -> Dict[str, Any]:
        """Process code files"""
        try:
            with open(asset.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic code analysis
            lines = content.splitlines()
            non_empty_lines = [line for line in lines if line.strip()]
            comment_lines = [line for line in lines if line.strip().startswith(('#', '//', '/*', '*', '"""', "'''"))]
            
            # Detect language (simplified)
            ext = asset.metadata.get("extension", "")
            language_map = {
                ".py": "Python",
                ".js": "JavaScript", 
                ".ts": "TypeScript",
                ".html": "HTML",
                ".css": "CSS",
                ".json": "JSON"
            }
            language = language_map.get(ext, "Unknown")
            
            return {
                "metadata": {
                    "language": language,
                    "total_lines": len(lines),
                    "code_lines": len(non_empty_lines),
                    "comment_lines": len(comment_lines)
                },
                "analysis": {
                    "complexity": "medium",  # Simplified
                    "documentation_ratio": len(comment_lines) / max(len(non_empty_lines), 1),
                    "potential_issues": [],
                    "suggestions": [
                        "Consider adding more comments if ratio < 0.1",
                        "Code appears well-structured" if len(non_empty_lines) < 100 else "Large file - consider breaking into smaller modules"
                    ]
                },
                "confidence": 0.8
            }
        except Exception as e:
            return {"error": str(e), "confidence": 0.0}
    
    async def _process_table(self, asset: MediaAsset) -> Dict[str, Any]:
        """Process tabular data"""
        # Placeholder for CSV/Excel processing
        return {
            "metadata": {
                "format": asset.metadata.get("extension", "unknown"),
                "size_mb": round(asset.size_bytes / (1024 * 1024), 2)
            },
            "analysis": {
                "estimated_rows": "unknown",
                "estimated_columns": "unknown",
                "data_types": [],
                "summary_statistics": "Table analysis not yet implemented"
            },
            "confidence": 0.4
        }
    
    async def _process_structured_data(self, asset: MediaAsset) -> Dict[str, Any]:
        """Process structured data files (JSON, YAML, etc.)"""
        try:
            with open(asset.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse as JSON
            try:
                if asset.metadata.get("extension") == ".json":
                    data = json.loads(content)
                    return {
                        "metadata": {
                            "format": "JSON",
                            "valid": True,
                            "size_mb": round(asset.size_bytes / (1024 * 1024), 2)
                        },
                        "analysis": {
                            "structure": type(data).__name__,
                            "top_level_keys": list(data.keys()) if isinstance(data, dict) else [],
                            "depth": await self._calculate_json_depth(data),
                            "complexity": "simple" if len(str(data)) < 1000 else "complex"
                        },
                        "confidence": 0.9
                    }
            except json.JSONDecodeError:
                pass
            
            # Fallback for other structured formats
            return {
                "metadata": {
                    "format": asset.metadata.get("extension", "unknown"),
                    "valid": "unknown"
                },
                "analysis": {
                    "structure": "Structured data analysis not fully implemented",
                    "suggestions": ["Consider validating format", "May contain useful structured information"]
                },
                "confidence": 0.5
            }
        except Exception as e:
            return {"error": str(e), "confidence": 0.0}
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text (simplified implementation)"""
        # Very basic topic extraction
        common_topics = {
            "project": ["project", "task", "goal", "objective"],
            "research": ["research", "study", "analysis", "investigation"],
            "technology": ["technology", "software", "programming", "development"],
            "meeting": ["meeting", "discussion", "call", "conference"],
            "planning": ["plan", "strategy", "roadmap", "timeline"]
        }
        
        text_lower = text.lower()
        detected_topics = []
        
        for topic, keywords in common_topics.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics[:5]  # Return up to 5 topics
    
    async def _calculate_json_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate the depth of a JSON object"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            depths = []
            for value in obj.values():
                depth = await self._calculate_json_depth(value, current_depth + 1)
                depths.append(depth)
            return max(depths) if depths else current_depth
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            depths = []
            for item in obj:
                depth = await self._calculate_json_depth(item, current_depth + 1)
                depths.append(depth)
            return max(depths) if depths else current_depth
        else:
            return current_depth
    
    async def _apply_capability(self, capability: ProcessingCapability, results: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Apply a specific processing capability"""
        if capability == ProcessingCapability.SUMMARIZATION:
            return await self._summarize_results(results, context)
        elif capability == ProcessingCapability.CLASSIFICATION:
            return await self._classify_content(results)
        elif capability == ProcessingCapability.COMPARISON:
            return await self._compare_assets(results)
        else:
            return {"capability": capability.value, "status": "not_implemented"}
    
    async def _summarize_results(self, results: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Summarize processing results"""
        summary = {
            "total_assets": len([k for k in results.keys() if not k.startswith("capability_")]),
            "modalities_found": [],
            "key_insights": [],
            "recommendations": []
        }
        
        # Extract modalities
        for asset_id, asset_result in results.items():
            if not asset_id.startswith("capability_") and "metadata" in asset_result:
                # Determine modality from file extension or format
                format_info = asset_result.get("metadata", {})
                if "format" in format_info:
                    summary["modalities_found"].append(format_info["format"])
        
        summary["modalities_found"] = list(set(summary["modalities_found"]))
        
        # Generate insights based on context
        if context:
            summary["key_insights"].append(f"Analysis focused on: {context}")
        
        return summary
    
    async def _classify_content(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Classify content by type and characteristics"""
        classifications = {
            "content_types": {},
            "complexity_levels": {},
            "quality_assessments": {}
        }
        
        for asset_id, asset_result in results.items():
            if not asset_id.startswith("capability_"):
                # Basic classification based on available analysis
                if "analysis" in asset_result:
                    analysis = asset_result["analysis"]
                    if "topics" in analysis:
                        for topic in analysis["topics"]:
                            classifications["content_types"][topic] = classifications["content_types"].get(topic, 0) + 1
        
        return classifications
    
    async def _compare_assets(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare assets and find similarities/differences"""
        comparisons = {
            "similar_content": [],
            "size_distribution": {},
            "quality_comparison": {}
        }
        
        # Compare file sizes
        sizes = []
        for asset_id, asset_result in results.items():
            if not asset_id.startswith("capability_") and "metadata" in asset_result:
                size_mb = asset_result["metadata"].get("size_mb", 0)
                sizes.append(size_mb)
        
        if sizes:
            comparisons["size_distribution"] = {
                "average_mb": sum(sizes) / len(sizes),
                "largest_mb": max(sizes),
                "smallest_mb": min(sizes)
            }
        
        return comparisons
    
    async def _generate_artifacts(self, results: Dict[str, Any], request: MultiModalRequest) -> List[str]:
        """Generate artifacts from processing results"""
        artifacts = []
        
        # Generate summary report
        summary_artifact = f"multimodal_summary_{request.request_id}.md"
        artifacts.append(summary_artifact)
        
        # Generate detailed analysis report if many assets
        if len(request.assets) > 5:
            detailed_artifact = f"detailed_analysis_{request.request_id}.json"
            artifacts.append(detailed_artifact)
        
        return artifacts
    
    async def _generate_recommendations(self, results: Dict[str, Any], request: MultiModalRequest) -> List[str]:
        """Generate recommendations based on processing results"""
        recommendations = []
        
        # Analyze results for recommendations
        asset_count = len(request.assets)
        
        if asset_count > 20:
            recommendations.append("Consider organizing large media collections into themed folders")
        
        if any("error" in result for result in results.values() if isinstance(result, dict)):
            recommendations.append("Some files could not be processed - check file permissions and formats")
        
        # Check for large files
        large_files = []
        for asset_id, asset_result in results.items():
            if not asset_id.startswith("capability_") and "metadata" in asset_result:
                size_mb = asset_result["metadata"].get("size_mb", 0)
                if size_mb > 10:  # Files larger than 10MB
                    large_files.append(asset_id)
        
        if large_files:
            recommendations.append(f"Consider optimizing {len(large_files)} large files for better performance")
        
        recommendations.append("Regular multi-modal analysis can help maintain vault organization")
        
        return recommendations
    
    async def _find_cross_modal_connections(self, modality_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Find connections between different modalities"""
        connections = []
        
        # Look for shared topics between text and other modalities
        text_topics = []
        if "text" in modality_results:
            for result in modality_results["text"]:
                if "analysis" in result and "topics" in result["analysis"]:
                    text_topics.extend(result["analysis"]["topics"])
        
        # Check if image filenames relate to text topics
        if "image" in modality_results and text_topics:
            for result in modality_results["image"]:
                if "metadata" in result:
                    filename = result["metadata"].get("filename", "").lower()
                    for topic in text_topics:
                        if topic.lower() in filename:
                            connections.append({
                                "type": "topic_filename_match",
                                "topic": topic,
                                "filename": filename,
                                "modalities": ["text", "image"]
                            })
        
        return connections
    
    async def _generate_cross_modal_insights(self, connections: List[Dict[str, Any]], modality_results: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Generate insights from cross-modal analysis"""
        insights = []
        
        if connections:
            insights.append(f"Found {len(connections)} cross-modal connections in your vault")
        
        # Analyze modality distribution
        modality_counts = {modality: len(results) for modality, results in modality_results.items()}
        dominant_modality = max(modality_counts.keys(), key=lambda k: modality_counts[k]) if modality_counts else None
        
        if dominant_modality:
            insights.append(f"Your vault is primarily {dominant_modality}-based with {modality_counts[dominant_modality]} assets")
        
        # Suggest improvements
        if len(modality_results) == 1:
            insights.append("Consider adding diverse media types to enrich your knowledge base")
        elif len(modality_results) > 3:
            insights.append("Great diversity in media types - this enhances knowledge retention and understanding")
        
        return insights
    
    async def _generate_comprehensive_summary(self, response: MultiModalResponse, focus_areas: List[str]) -> Dict[str, Any]:
        """Generate a comprehensive summary of the vault"""
        return {
            "executive_summary": {
                "total_assets": len([k for k in response.results.keys() if not k.startswith("capability_")]),
                "processing_time": response.processing_time,
                "overall_confidence": sum(response.confidence_scores.values()) / len(response.confidence_scores) if response.confidence_scores else 0.0,
                "focus_areas_addressed": focus_areas
            },
            "modality_breakdown": response.metadata.get("modalities_processed", []),
            "key_insights": response.results.get("capability_analysis", {}).get("key_insights", []),
            "recommendations": response.recommendations,
            "generated_artifacts": response.generated_artifacts,
            "actionable_items": [
                "Review generated artifacts for detailed analysis",
                "Consider implementing recommendations for vault improvement",
                "Schedule regular multi-modal analysis for optimal organization"
            ]
        }
