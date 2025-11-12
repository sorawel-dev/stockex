/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

// Chargement de Chart.js depuis CDN
function loadChartJS() {
    return new Promise((resolve, reject) => {
        if (window.Chart) {
            resolve();
            return;
        }
        
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
        script.onload = () => resolve();
        script.onerror = () => reject(new Error('Failed to load Chart.js'));
        document.head.appendChild(script);
    });
}

class AnalyticsDashboardRenderer extends Component {
    setup() {
        this.orm = useService("orm");
        this.chartInstances = {};
        
        onMounted(() => {
            this.renderCharts();
        });
    }
    
    async renderCharts() {
        try {
            await loadChartJS();
            
            // Récupérer les données des champs
            const trendData = this.getTrendChartData();
            const valueData = this.getValueChartData();
            const varianceData = this.getVarianceChartData();
            
            // Rendre les graphiques
            if (trendData) this.renderTrendChart(trendData);
            if (valueData) this.renderValueChart(valueData);
            if (varianceData) this.renderVarianceChart(varianceData);
        } catch (error) {
            console.error('Error rendering charts:', error);
        }
    }
    
    getTrendChartData() {
        // Récupérer depuis le champ chart_inventory_trend_data
        const field = document.querySelector('[name="chart_inventory_trend_data"]');
        if (!field || !field.value) return null;
        
        try {
            return JSON.parse(field.value);
        } catch (e) {
            console.error('Error parsing trend data:', e);
            return null;
        }
    }
    
    getValueChartData() {
        const field = document.querySelector('[name="chart_stock_value_evolution_data"]');
        if (!field || !field.value) return null;
        
        try {
            return JSON.parse(field.value);
        } catch (e) {
            console.error('Error parsing value data:', e);
            return null;
        }
    }
    
    getVarianceChartData() {
        const field = document.querySelector('[name="chart_variance_by_category_data"]');
        if (!field || !field.value) return null;
        
        try {
            return JSON.parse(field.value);
        } catch (e) {
            console.error('Error parsing variance data:', e);
            return null;
        }
    }
    
    renderTrendChart(data) {
        const canvas = document.getElementById('chart-inventory-trend');
        if (!canvas) return;
        
        // Créer un canvas si besoin
        let ctx = canvas.querySelector('canvas');
        if (!ctx) {
            ctx = document.createElement('canvas');
            canvas.innerHTML = '';
            canvas.appendChild(ctx);
        }
        
        if (this.chartInstances.trend) {
            this.chartInstances.trend.destroy();
        }
        
        this.chartInstances.trend = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    renderValueChart(data) {
        const canvas = document.getElementById('chart-stock-value');
        if (!canvas) return;
        
        let ctx = canvas.querySelector('canvas');
        if (!ctx) {
            ctx = document.createElement('canvas');
            canvas.innerHTML = '';
            canvas.appendChild(ctx);
        }
        
        if (this.chartInstances.value) {
            this.chartInstances.value.destroy();
        }
        
        this.chartInstances.value = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    renderVarianceChart(data) {
        const canvas = document.getElementById('chart-variance');
        if (!canvas) return;
        
        let ctx = canvas.querySelector('canvas');
        if (!ctx) {
            ctx = document.createElement('canvas');
            canvas.innerHTML = '';
            canvas.appendChild(ctx);
        }
        
        if (this.chartInstances.variance) {
            this.chartInstances.variance.destroy();
        }
        
        this.chartInstances.variance = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

AnalyticsDashboardRenderer.template = "stockex.AnalyticsDashboardRenderer";

registry.category("view_widgets").add("analytics_dashboard_renderer", { component: AnalyticsDashboardRenderer });

// Script simple pour les vues legacy (non-OWL)
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        // Vérifier si Chart.js est chargé
        if (typeof Chart === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
            script.onload = function() {
                renderAllCharts();
            };
            document.head.appendChild(script);
        } else {
            renderAllCharts();
        }
    }, 1000);
});

function renderAllCharts() {
    try {
        // Trend Chart
        renderChart('chart_inventory_trend_data', 'chart-inventory-trend', 'line');
        
        // Value Chart
        renderChart('chart_stock_value_evolution_data', 'chart-stock-value', 'bar', true);
        
        // Variance Chart
        renderChart('chart_variance_by_category_data', 'chart-variance', 'bar', true);
    } catch (error) {
        console.error('Error in renderAllCharts:', error);
    }
}

function renderChart(fieldName, canvasId, chartType, horizontal = false) {
    const field = document.querySelector(`[name="${fieldName}"]`);
    const container = document.getElementById(canvasId);
    
    if (!field || !container || !field.value) {
        // Silencieux: pas d'erreur si le graphique n'est pas présent
        return;
    }
    
    try {
        const data = JSON.parse(field.value);
        
        // Créer canvas
        let canvas = container.querySelector('canvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            container.innerHTML = '';
            container.appendChild(canvas);
        }
        
        const ctx = canvas.getContext('2d');
        
        const config = {
            type: chartType,
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: chartType === 'line',
                        position: 'top',
                    }
                },
                scales: {}
            }
        };
        
        if (horizontal) {
            config.options.indexAxis = 'y';
        }
        
        if (chartType === 'line' || chartType === 'bar') {
            config.options.scales.y = {
                beginAtZero: true,
                ticks: {
                    precision: 0
                }
            };
        }
        
        new Chart(ctx, config);
        console.log(`Chart ${canvasId} rendered successfully`);
    } catch (error) {
        console.error(`Error rendering chart ${canvasId}:`, error);
        container.innerHTML = `<div class="alert alert-danger">Erreur de rendu du graphique: ${error.message}</div>`;
    }
}
