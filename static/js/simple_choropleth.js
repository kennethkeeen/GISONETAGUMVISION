// Simple Choropleth Map implementation for Tagum City Barangays
class SimpleChoropleth {
    constructor(map, geojsonUrl, projectsData = null) {
        this.map = map;
        this.geojsonUrl = geojsonUrl;
        this.projectsData = projectsData || [];
        this.choroplethLayer = null;
        this.legend = null;
        this.summaryPanel = null;
        this.barangayData = [];
        this.barangayStats = {};
        // Phase 3: Zoning support
        this.zoningData = null;
        this.currentView = 'projects'; // 'projects', 'urban_rural', 'economic', 'elevation'
        this.zoningLayers = {
            urbanRural: null,
            economic: null,
            elevation: null
        };
    }

    calculateBarangayStats() {
        // Calculate statistics for each barangay
        this.barangayStats = {};
        
        this.projectsData.forEach(project => {
            const barangay = project.barangay;
            if (!barangay) return;
            
            if (!this.barangayStats[barangay]) {
                this.barangayStats[barangay] = {
                    totalProjects: 0,
                    totalCost: 0,
                    completedProjects: 0,
                    ongoingProjects: 0,
                    plannedProjects: 0
                };
            }
            
            this.barangayStats[barangay].totalProjects++;
            
            // Parse project cost
            let cost = 0;
            if (project.project_cost) {
                // Remove currency symbols and commas, then parse
                const costStr = project.project_cost.toString().replace(/[₱,]/g, '');
                cost = parseFloat(costStr) || 0;
            }
            this.barangayStats[barangay].totalCost += cost;
            
            // Count by status
            const status = project.status?.toLowerCase();
            if (status === 'completed') {
                this.barangayStats[barangay].completedProjects++;
            } else if (status === 'ongoing' || status === 'in_progress') {
                this.barangayStats[barangay].ongoingProjects++;
            } else if (status === 'planned' || status === 'pending') {
                this.barangayStats[barangay].plannedProjects++;
            }
        });
        
        console.log('Barangay statistics calculated:', this.barangayStats);
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-PH', {
            style: 'currency',
            currency: 'PHP',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    async loadData() {
        try {
            console.log('Loading GeoJSON data from:', this.geojsonUrl);
            const response = await fetch(this.geojsonUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('GeoJSON data loaded:', data);
            
            this.barangayData = data.features || [];
            console.log(`Loaded ${this.barangayData.length} barangay features`);
            
            return data;
        } catch (error) {
            console.error('Error loading GeoJSON data:', error);
            throw error;
        }
    }

    createChoropleth() {
        if (!this.barangayData.length) {
            console.error('No barangay data available');
            return;
        }

        // Calculate barangay statistics
        this.calculateBarangayStats();

        // Clear existing choropleth layer
        if (this.choroplethLayer) {
            this.map.removeLayer(this.choroplethLayer);
        }

        // Create choropleth layer
        this.choroplethLayer = L.geoJSON(this.barangayData, {
            style: (feature) => {
                const color = feature.properties.color || '#FF6B6B';
                return {
                    fillColor: color,
                    weight: 2,
                    opacity: 1,
                    color: '#333',
                    fillOpacity: 0.7
                };
            },
            onEachFeature: (feature, layer) => {
                const name = feature.properties.name || 'Unknown';
                const stats = this.barangayStats[name] || {
                    totalProjects: 0,
                    totalCost: 0,
                    completedProjects: 0,
                    ongoingProjects: 0,
                    plannedProjects: 0
                };
                const barangay = this.zoningData ? this.zoningData[name] : null;
                
                // Use enhanced popup with zoning info
                const popupContent = this.createZoningPopup(name, barangay, stats);
                
                layer.bindPopup(popupContent);
                
                // Add hover effects
                layer.on({
                    mouseover: (e) => {
                        const layer = e.target;
                        layer.setStyle({
                            weight: 3,
                            fillOpacity: 0.9
                        });
                        layer.bringToFront();
                    },
                    mouseout: (e) => {
                        this.choroplethLayer.resetStyle(e.target);
                    }
                });
            }
        });

        // Add to map
        this.choroplethLayer.addTo(this.map);
        console.log('Choropleth layer added to map');

        // Create legend and summary panel
        this.createLegend();
        this.createSummaryPanel();

        // Fit map to choropleth bounds
        if (this.choroplethLayer.getBounds().isValid()) {
            this.map.fitBounds(this.choroplethLayer.getBounds());
        } else {
            // Fallback center for Tagum City
            this.map.setView([7.4475, 125.8096], 12);
        }
    }

    createLegend() {
        // Remove existing legend
        if (this.legend) {
            this.map.removeControl(this.legend);
        }

        // Create legend
        this.legend = L.control({ position: 'bottomright' });

        this.legend.onAdd = (map) => {
            const div = L.DomUtil.create('div', 'info legend');
            div.style.backgroundColor = 'white';
            div.style.padding = '10px';
            div.style.border = '2px solid #ccc';
            div.style.borderRadius = '5px';
            div.style.fontSize = '11px';
            div.style.minWidth = '180px';
            div.style.maxHeight = 'none';
            div.style.overflowY = 'visible';
            
            // Show different legend based on current view
            if (this.currentView === 'urban_rural') {
                div.innerHTML = '<h4 style="margin: 0 0 8px 0; color: #333; font-size: 13px;">Urban / Rural</h4>';
                div.innerHTML += `
                    <div style="margin: 2px 0; display: flex; align-items: center;">
                        <i style="background: #ef4444; width: 16px; height: 16px; margin-right: 6px; border: 1px solid #333; flex-shrink: 0;"></i>
                        <span>Urban</span>
                    </div>
                    <div style="margin: 2px 0; display: flex; align-items: center;">
                        <i style="background: #fbbf24; width: 16px; height: 16px; margin-right: 6px; border: 1px solid #333; flex-shrink: 0;"></i>
                        <span>Rural</span>
                    </div>
                `;
            } else if (this.currentView === 'economic') {
                div.innerHTML = '<h4 style="margin: 0 0 8px 0; color: #333; font-size: 13px;">Economic Classification</h4>';
                div.innerHTML += `
                    <div style="margin: 2px 0; display: flex; align-items: center;">
                        <i style="background: #3b82f6; width: 16px; height: 16px; margin-right: 6px; border: 1px solid #333; flex-shrink: 0;"></i>
                        <span>Growth Center</span>
                    </div>
                    <div style="margin: 2px 0; display: flex; align-items: center;">
                        <i style="background: #10b981; width: 16px; height: 16px; margin-right: 6px; border: 1px solid #333; flex-shrink: 0;"></i>
                        <span>Emerging</span>
                    </div>
                    <div style="margin: 2px 0; display: flex; align-items: center;">
                        <i style="background: #fbbf24; width: 16px; height: 16px; margin-right: 6px; border: 1px solid #333; flex-shrink: 0;"></i>
                        <span>Satellite</span>
                    </div>
                `;
            } else if (this.currentView === 'elevation') {
                div.innerHTML = '<h4 style="margin: 0 0 8px 0; color: #333; font-size: 13px;">Elevation Type</h4>';
                div.innerHTML += `
                    <div style="margin: 2px 0; display: flex; align-items: center;">
                        <i style="background: #8b5cf6; width: 16px; height: 16px; margin-right: 6px; border: 1px solid #333; flex-shrink: 0;"></i>
                        <span>Highland</span>
                    </div>
                    <div style="margin: 2px 0; display: flex; align-items: center;">
                        <i style="background: #84cc16; width: 16px; height: 16px; margin-right: 6px; border: 1px solid #333; flex-shrink: 0;"></i>
                        <span>Plains</span>
                    </div>
                    <div style="margin: 2px 0; display: flex; align-items: center;">
                        <i style="background: #06b6d4; width: 16px; height: 16px; margin-right: 6px; border: 1px solid #333; flex-shrink: 0;"></i>
                        <span>Coastal</span>
                    </div>
                `;
            } else {
                // Default: show barangay list
                div.innerHTML = '<h4 style="margin: 0 0 8px 0; color: #333; font-size: 13px;">Tagum City Barangays</h4>';
                
                // Get unique barangays with their colors
                const uniqueBarangays = new Map();
                this.barangayData.forEach(feature => {
                    const name = feature.properties.name;
                    const color = feature.properties.color || '#FF6B6B';
                    if (!uniqueBarangays.has(name)) {
                        uniqueBarangays.set(name, color);
                    }
                });

                // Sort barangays alphabetically
                const sortedBarangays = Array.from(uniqueBarangays.entries()).sort();

                sortedBarangays.forEach(([name, color]) => {
                    div.innerHTML += `
                        <div style="margin: 2px 0; display: flex; align-items: center;">
                            <i style="background: ${color}; width: 16px; height: 16px; margin-right: 6px; border: 1px solid #333; flex-shrink: 0;"></i>
                            <span>${name}</span>
                        </div>
                    `;
                });
            }

            return div;
        };

        this.legend.addTo(this.map);
        console.log('Legend created for view:', this.currentView);
    }

    createSummaryPanel() {
        // Remove existing summary panel
        if (this.summaryPanel) {
            this.map.removeControl(this.summaryPanel);
        }

        // Filter projects to only those with valid coordinates and a barangay in the geojson
        const validBarangays = new Set(this.barangayData.map(f => f.properties.name));
        const visibleProjects = this.projectsData.filter(p => {
            const hasCoords = p.latitude && !isNaN(parseFloat(p.latitude)) && p.longitude && !isNaN(parseFloat(p.longitude));
            return hasCoords && validBarangays.has(p.barangay);
        });

        // Debug: List delayed projects not shown on the map
        const delayedAll = this.projectsData.filter(p => p.status?.toLowerCase() === 'delayed');
        const delayedVisible = visibleProjects.filter(p => p.status?.toLowerCase() === 'delayed');
        const delayedMissing = delayedAll.filter(p => !delayedVisible.includes(p));
        if (delayedMissing.length > 0) {
            console.warn('Delayed projects not shown on the map (missing coords or invalid barangay):', delayedMissing);
        }

        const totalProjects = visibleProjects.length;
        const completedProjects = visibleProjects.filter(p => p.status?.toLowerCase() === 'completed').length;
        const ongoingProjects = visibleProjects.filter(p => p.status?.toLowerCase() === 'ongoing' || p.status?.toLowerCase() === 'in_progress').length;
        const plannedProjects = visibleProjects.filter(p => p.status?.toLowerCase() === 'planned' || p.status?.toLowerCase() === 'pending').length;
        const delayedProjects = visibleProjects.filter(p => p.status?.toLowerCase() === 'delayed').length;

        // Create summary panel
        this.summaryPanel = L.control({ position: 'topleft' });

        this.summaryPanel.onAdd = (map) => {
            const div = L.DomUtil.create('div', 'info summary-panel');
            div.style.backgroundColor = 'white';
            div.style.padding = '18px 18px 10px 18px';
            div.style.border = '2px solid #ccc';
            div.style.borderRadius = '10px';
            div.style.fontSize = '14px';
            div.style.minWidth = '240px';
            div.style.boxShadow = '0 2px 8px rgba(0,0,0,0.07)';
            div.innerHTML = `
                <div style="font-size:18px;font-weight:bold;margin-bottom:12px;color:#222;">Overall Project Metrics</div>
                <div style="background:#e8f0fe;border-radius:8px;padding:10px 12px;margin-bottom:8px;display:flex;align-items:center;gap:10px;">
                  <span style="color:#3b82f6;font-size:20px;">&#128202;</span>
                  <span style="font-size:20px;font-weight:bold;">${totalProjects}</span>
                  <span style="color:#333;">Total Projects</span>
                </div>
                <div style="background:#d1fae5;border-radius:8px;padding:10px 12px;margin-bottom:8px;display:flex;align-items:center;gap:10px;">
                  <span style="color:#10b981;font-size:20px;">&#10003;</span>
                  <span style="font-size:20px;font-weight:bold;">${completedProjects}</span>
                  <span style="color:#333;">Completed</span>
                </div>
                <div style="background:#fef3c7;border-radius:8px;padding:10px 12px;margin-bottom:8px;display:flex;align-items:center;gap:10px;">
                  <span style="color:#f59e0b;font-size:20px;">&#9201;</span>
                  <span style="font-size:20px;font-weight:bold;">${ongoingProjects}</span>
                  <span style="color:#333;">In Progress</span>
                </div>
                <div style="background:#ede9fe;border-radius:8px;padding:10px 12px;margin-bottom:8px;display:flex;align-items:center;gap:10px;">
                  <span style="color:#8b5cf6;font-size:20px;">&#128197;</span>
                  <span style="font-size:20px;font-weight:bold;">${plannedProjects}</span>
                  <span style="color:#333;">Planned</span>
                </div>
                <div style="background:#fee2e2;border-radius:8px;padding:10px 12px;margin-bottom:0;display:flex;align-items:center;gap:10px;">
                  <span style="color:#ef4444;font-size:20px;">&#128337;</span>
                  <span style="font-size:20px;font-weight:bold;">${delayedProjects}</span>
                  <span style="color:#333;">Delayed</span>
                </div>
            `;
            return div;
        };

        this.summaryPanel.addTo(this.map);
        console.log('Summary panel created');
    }

    cleanup() {
        console.log('Cleaning up choropleth...');
        
        // Remove choropleth layer
        if (this.choroplethLayer) {
            this.map.removeLayer(this.choroplethLayer);
            this.choroplethLayer = null;
        }

        // Remove legend
        if (this.legend) {
            this.map.removeControl(this.legend);
            this.legend = null;
        }

        // Remove summary panel
        if (this.summaryPanel) {
            this.map.removeControl(this.summaryPanel);
            this.summaryPanel = null;
        }

        console.log('Choropleth cleanup completed');
    }

    async initialize() {
        try {
            console.log('Initializing choropleth...');
            await this.loadData();
            // Phase 3: Load zoning data
            await this.loadZoningData();
            this.createChoropleth();
            console.log('Choropleth initialized successfully');
            console.log('Zoning data available:', this.zoningData ? Object.keys(this.zoningData).length + ' barangays' : 'none');
            console.log('switchView method available:', typeof this.switchView === 'function');
            return true; // Return success
        } catch (error) {
            console.error('Failed to initialize choropleth:', error);
            throw error; // Re-throw to allow promise rejection
        }
    }

    // Phase 3: Zoning functionality
    async loadZoningData() {
        try {
            const response = await fetch('/projeng/api/barangay-metadata/', {
                method: 'GET',
                credentials: 'same-origin', // Include cookies for authentication
                headers: {
                    'Accept': 'application/json',
                }
            });
            if (!response.ok) {
                if (response.status === 401) {
                    console.error('Authentication required. Please log in.');
                } else if (response.status === 403) {
                    console.error('Access forbidden. You may not have permission to view this data.');
                } else {
                    console.error(`HTTP error! status: ${response.status}`);
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.zoningData = {};
            if (data.barangays && Array.isArray(data.barangays)) {
                data.barangays.forEach(barangay => {
                    this.zoningData[barangay.name] = barangay;
                });
                console.log('Zoning data loaded:', Object.keys(this.zoningData).length, 'barangays');
            } else {
                console.warn('Unexpected data format:', data);
                this.zoningData = {};
            }
        } catch (error) {
            console.error('Error loading zoning data:', error);
            this.zoningData = {};
        }
    }

    switchView(viewType) {
        console.log('=== switchView called ===');
        console.log('viewType:', viewType);
        console.log('currentView:', this.currentView);
        console.log('zoningData available:', this.zoningData ? Object.keys(this.zoningData).length + ' barangays' : 'none');
        console.log('barangayData available:', this.barangayData.length + ' features');
        
        this.currentView = viewType;
        
        // Check if zoning data is loaded
        if (viewType !== 'projects' && (!this.zoningData || Object.keys(this.zoningData).length === 0)) {
            console.warn('Zoning data not loaded yet. Loading...');
            this.loadZoningData().then(() => {
                console.log('Zoning data loaded, retrying switchView');
                this.switchView(viewType); // Retry after loading
            }).catch((error) => {
                console.error('Failed to load zoning data:', error);
            });
            return;
        }
        
        // Remove current layer
        if (this.choroplethLayer) {
            try {
                console.log('Removing existing choropleth layer');
                this.map.removeLayer(this.choroplethLayer);
            } catch (e) {
                console.log('Error removing layer:', e);
            }
            this.choroplethLayer = null;
        }

        // Create and add new layer based on view
        if (viewType === 'projects') {
            console.log('Creating projects choropleth');
            this.createChoropleth();
        } else {
            console.log('Creating zoning layer for:', viewType);
            this.createZoningLayer(viewType);
        }
        
        // Update legend
        console.log('Updating legend');
        this.createLegend();
        console.log('=== View switched successfully to:', viewType, '===');
    }

    createZoningLayer(viewType) {
        console.log('=== createZoningLayer called ===');
        console.log('viewType:', viewType);
        console.log('barangayData length:', this.barangayData.length);
        console.log('zoningData keys:', this.zoningData ? Object.keys(this.zoningData).length : 0);
        
        if (!this.barangayData.length) {
            console.error('No barangay data available');
            return;
        }

        if (!this.zoningData || Object.keys(this.zoningData).length === 0) {
            console.error('No zoning data available');
            return;
        }

        // Clear existing layer
        if (this.choroplethLayer) {
            try {
                this.map.removeLayer(this.choroplethLayer);
            } catch (e) {
                console.log('Error removing existing layer:', e);
            }
        }

        // Create zoning layer based on view type
        console.log('Creating GeoJSON layer with zoning colors...');
        let coloredCount = 0;
        let defaultCount = 0;
        
        this.choroplethLayer = L.geoJSON(this.barangayData, {
            style: (feature) => {
                const barangayName = feature.properties.name;
                const barangay = this.zoningData[barangayName];
                let color = '#cccccc'; // Default gray
                
                if (barangay) {
                    switch(viewType) {
                        case 'urban_rural':
                            if (barangay.barangay_class === 'urban') {
                                color = '#ef4444'; // Red for urban
                                coloredCount++;
                            } else if (barangay.barangay_class === 'rural') {
                                color = '#fbbf24'; // Yellow for rural
                                coloredCount++;
                            } else {
                                defaultCount++;
                            }
                            break;
                        case 'economic':
                            if (barangay.economic_class === 'growth_center') {
                                color = '#3b82f6'; // Blue
                                coloredCount++;
                            } else if (barangay.economic_class === 'emerging') {
                                color = '#10b981'; // Green
                                coloredCount++;
                            } else if (barangay.economic_class === 'satellite') {
                                color = '#fbbf24'; // Yellow
                                coloredCount++;
                            } else {
                                defaultCount++;
                            }
                            break;
                        case 'elevation':
                            if (barangay.elevation_type === 'highland') {
                                color = '#8b5cf6'; // Purple
                                coloredCount++;
                            } else if (barangay.elevation_type === 'plains') {
                                color = '#84cc16'; // Green
                                coloredCount++;
                            } else if (barangay.elevation_type === 'coastal') {
                                color = '#06b6d4'; // Cyan
                                coloredCount++;
                            } else {
                                defaultCount++;
                            }
                            break;
                        default:
                            defaultCount++;
                    }
                } else {
                    defaultCount++;
                    console.log('No zoning data for barangay:', barangayName);
                }
                
                return {
                    fillColor: color,
                    weight: 2,
                    opacity: 1,
                    color: '#333',
                    fillOpacity: 0.7 // Slightly more opaque for better visibility
                };
            },
            onEachFeature: (feature, layer) => {
                const name = feature.properties.name || 'Unknown';
                const barangay = this.zoningData[name];
                const stats = this.barangayStats[name] || {
                    totalProjects: 0,
                    totalCost: 0,
                    completedProjects: 0,
                    ongoingProjects: 0,
                    plannedProjects: 0
                };
                
                // Create popup with both project stats and zoning info
                const popupContent = this.createZoningPopup(name, barangay, stats);
                layer.bindPopup(popupContent);
                
                // Add hover effects
                layer.on({
                    mouseover: (e) => {
                        const layer = e.target;
                        layer.setStyle({
                            weight: 3,
                            fillOpacity: 0.9
                        });
                        layer.bringToFront();
                    },
                    mouseout: (e) => {
                        this.choroplethLayer.resetStyle(e.target);
                    }
                });
            }
        });

        // Add to map
        this.choroplethLayer.addTo(this.map);
        console.log('Zoning layer created and added to map');
        console.log('Colored barangays:', coloredCount, 'Default (gray):', defaultCount);
        console.log('=== createZoningLayer completed ===');
    }

    createZoningPopup(name, barangay, stats) {
        let content = `
            <div style="min-width: 250px;">
                <h3 style="margin: 0 0 10px 0; color: #333; font-size: 16px;">${name}</h3>
        `;
        
        // Add zoning information if available
        if (barangay) {
            content += `
                <div style="border-bottom: 1px solid #eee; padding-bottom: 8px; margin-bottom: 8px;">
                    <div style="font-weight: bold; margin-bottom: 5px; color: #555;">Zoning Information</div>
                    <div style="margin: 3px 0; font-size: 12px;">
                        <strong>Classification:</strong> ${barangay.barangay_class ? barangay.barangay_class.charAt(0).toUpperCase() + barangay.barangay_class.slice(1) : 'N/A'}
                    </div>
                    <div style="margin: 3px 0; font-size: 12px;">
                        <strong>Economic Type:</strong> ${barangay.economic_class ? barangay.economic_class.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'N/A'}
                    </div>
                    <div style="margin: 3px 0; font-size: 12px;">
                        <strong>Elevation:</strong> ${barangay.elevation_type ? barangay.elevation_type.charAt(0).toUpperCase() + barangay.elevation_type.slice(1) : 'N/A'}
                    </div>
                    ${barangay.population ? `<div style="margin: 3px 0; font-size: 12px;"><strong>Population:</strong> ${barangay.population.toLocaleString()}</div>` : ''}
                    ${barangay.density ? `<div style="margin: 3px 0; font-size: 12px;"><strong>Density:</strong> ${barangay.density.toLocaleString()} /km²</div>` : ''}
                    ${barangay.growth_rate ? `<div style="margin: 3px 0; font-size: 12px;"><strong>Growth Rate:</strong> ${barangay.growth_rate}%</div>` : ''}
                </div>
            `;
        }
        
        // Add project statistics
        content += `
                <div style="margin-top: 8px;">
                    <div style="font-weight: bold; margin-bottom: 5px; color: #555;">Project Statistics</div>
                    <div style="margin: 3px 0; font-size: 12px;">
                        <strong>Total Projects:</strong> ${stats.totalProjects}
                    </div>
                    <div style="margin: 3px 0; font-size: 12px;">
                        <strong>Total Cost:</strong> ${this.formatCurrency(stats.totalCost)}
                    </div>
                    <div style="margin: 3px 0; font-size: 12px;">
                        <strong>Completed:</strong> ${stats.completedProjects}
                    </div>
                    <div style="margin: 3px 0; font-size: 12px;">
                        <strong>Ongoing:</strong> ${stats.ongoingProjects}
                    </div>
                    <div style="margin: 3px 0; font-size: 12px;">
                        <strong>Planned:</strong> ${stats.plannedProjects}
                    </div>
                </div>
            </div>
        `;
        
        return content;
    }
}

// Export for use in other files
window.SimpleChoropleth = SimpleChoropleth; 