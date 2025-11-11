"""
Zone Detection Utilities for Simplified Zoning Integration

This module provides functions to automatically detect zoning classifications
for projects based on barangay, project name, and description.
"""

from projeng.models import ZoningZone
from django.db.models import Q
import re


def detect_zone_for_project(project):
    """
    Automatically detect the most likely zone type for a project.
    
    Detection Strategy (in order of priority):
    1. Keyword matching in project name/description against zone keywords
    2. Barangay-based matching (if barangay has a dominant zone)
    3. Return None if no match found
    
    Args:
        project: Project instance with name, description, and barangay fields
        
    Returns:
        tuple: (zone_type, confidence_score, matched_zone) or (None, 0, None)
        - zone_type: The detected zone code (e.g., 'R-1', 'C-1')
        - confidence_score: 0-100 score indicating match confidence
        - matched_zone: The ZoningZone instance that matched (if any)
    """
    if not project:
        return None, 0, None
    
    # Get searchable text from project
    search_text = ""
    if project.name:
        search_text += f" {project.name.lower()}"
    if project.description:
        search_text += f" {project.description.lower()}"
    
    # Normalize barangay name for matching
    barangay = project.barangay.strip() if project.barangay else None
    
    if not search_text and not barangay:
        return None, 0, None
    
    # Step 1: Keyword matching (highest priority)
    # Get all active zones
    active_zones = ZoningZone.objects.filter(is_active=True)
    
    best_match = None
    best_score = 0
    best_zone = None
    
    for zone in active_zones:
        score = 0
        
        # Check if barangay matches
        if barangay:
            # Exact match
            if zone.barangay.lower().strip() == barangay.lower().strip():
                score += 30
            # Partial match (handles variations)
            elif barangay.lower().strip() in zone.barangay.lower() or zone.barangay.lower() in barangay.lower().strip():
                score += 15
        
        # Check keyword matches in project text
        if search_text and zone.keywords:
            keywords = zone.get_keywords_list()
            for keyword in keywords:
                if keyword:
                    keyword_lower = keyword.lower().strip()
                    # Exact keyword match
                    if keyword_lower in search_text:
                        score += 40
                    # Partial keyword match (word boundary)
                    elif re.search(r'\b' + re.escape(keyword_lower) + r'\b', search_text):
                        score += 25
                    # Substring match (less reliable)
                    elif keyword_lower in search_text or search_text in keyword_lower:
                        score += 10
        
        # Check location description for matches
        if search_text and zone.location_description:
            desc_lower = zone.location_description.lower()
            # Check if any words from project text appear in location description
            project_words = set(re.findall(r'\b\w+\b', search_text))
            desc_words = set(re.findall(r'\b\w+\b', desc_lower))
            common_words = project_words.intersection(desc_words)
            if common_words:
                # More common words = higher score
                score += len(common_words) * 5
        
        # Update best match
        if score > best_score:
            best_score = score
            best_zone = zone
            best_match = zone.zone_type
    
    # Step 2: Barangay-based fallback (if no keyword match)
    if best_score < 30 and barangay:
        # Find zones for this barangay
        barangay_zones = ZoningZone.objects.filter(
            is_active=True,
            barangay__iexact=barangay
        )
        
        if barangay_zones.exists():
            # Count zone types for this barangay
            from collections import Counter
            zone_counts = Counter(zone.zone_type for zone in barangay_zones)
            
            # Get the most common zone type
            if zone_counts:
                most_common_zone = zone_counts.most_common(1)[0]
                zone_type = most_common_zone[0]
                count = most_common_zone[1]
                
                # Use this as fallback if we have multiple zones for this barangay
                if count >= 2:  # At least 2 zones of this type in the barangay
                    # Find a representative zone
                    representative_zone = barangay_zones.filter(zone_type=zone_type).first()
                    return zone_type, 20, representative_zone
    
    # Return results
    if best_score >= 30:  # Minimum confidence threshold
        # Normalize score to 0-100
        confidence = min(100, best_score)
        return best_match, confidence, best_zone
    
    return None, 0, None


def get_zones_for_barangay(barangay_name):
    """
    Get all active zones for a specific barangay.
    
    Args:
        barangay_name: Name of the barangay
        
    Returns:
        QuerySet: ZoningZone objects for the barangay
    """
    if not barangay_name:
        return ZoningZone.objects.none()
    
    return ZoningZone.objects.filter(
        is_active=True,
        barangay__iexact=barangay_name.strip()
    ).order_by('zone_type')


def get_zone_statistics():
    """
    Get statistics about zones in the database.
    
    Returns:
        dict: Statistics including total zones, zones by type, etc.
    """
    from django.db.models import Count
    
    total_zones = ZoningZone.objects.filter(is_active=True).count()
    zones_by_type = ZoningZone.objects.filter(is_active=True).values('zone_type').annotate(
        count=Count('id')
    ).order_by('zone_type')
    
    zones_by_barangay = ZoningZone.objects.filter(is_active=True).values('barangay').annotate(
        count=Count('id')
    ).order_by('barangay')
    
    return {
        'total_zones': total_zones,
        'zones_by_type': list(zones_by_type),
        'zones_by_barangay': list(zones_by_barangay),
    }

