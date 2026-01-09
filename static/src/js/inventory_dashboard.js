/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, useRef, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

export class InventoryDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        
        this.state = useState({
            period: "all",  // Par défaut: tous les inventaires
            valuationMethod: "standard",
            data: null,
            loading: true,
            lastUpdate: new Date(),
            warehouseIds: null,
            regionIds: null,
        });
        
        // Refs pour les graphiques
        this.evolutionChartRef = useRef("evolutionChart");
        this.warehousePerformanceChartRef = useRef("warehousePerformanceChart");
        this.categoryDistributionChartRef = useRef("categoryDistributionChart");
        this.regionHeatmapChartRef = useRef("regionHeatmapChart");
        this.warehouseDistributionChartRef = useRef("warehouseDistributionChart");
        this.varianceTrendChartRef = useRef("varianceTrendChart");
        
        // Charts instances
        this.charts = {
            evolution: null,
            warehousePerformance: null,
            categoryDistribution: null,
            regionHeatmap: null,
            warehouseDistribution: null,
            varianceTrend: null,
        };
        
        this.refreshInterval = null;
        
        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this.loadDashboardData();
        });
        
        onMounted(() => {
            this.renderCharts();
            // Auto-refresh toutes les 5 minutes
            this.refreshInterval = setInterval(() => {
                this.loadDashboardData();
            }, 5 * 60 * 1000);
        });
        
        onWillUnmount(() => {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
            this.destroyAllCharts();
        });
    }
    
    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
    }
    
    async loadDashboardData() {
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "stockex.inventory.dashboard",
                "get_dashboard_data",
                [],
                {
                    period: this.state.period,
                    valuation_method: this.state.valuationMethod,
                    warehouse_ids: this.state.warehouseIds,
                    region_ids: this.state.regionIds,
                }
            );
            console.log("✅ Dashboard data loaded:", data);
            this.state.data = data;
            this.state.lastUpdate = new Date();
            
            // Re-render charts après mise à jour données
            setTimeout(() => {
                this.renderCharts();
            }, 100);
        } catch (error) {
            console.error("❌ Erreur chargement dashboard:", error);
            this.notification.add("Erreur de chargement des données", {
                type: "danger",
            });
            this.state.data = null;
        } finally {
            this.state.loading = false;
        }
    }
    
    async changePeriod(period) {
        this.state.period = period;
        await this.loadDashboardData();
    }
    
    async toggleValuationMethod() {
        this.state.valuationMethod = this.state.valuationMethod === 'standard' ? 'economic' : 'standard';
        await this.loadDashboardData();
    }
    
    getLastUpdate() {
        return this.state.lastUpdate.toLocaleTimeString('fr-FR');
    }
    
    formatNumber(num) {
        if (!num) return '0';
        if (Math.abs(num) >= 1000000000) {
            return (num / 1000000000).toFixed(1) + 'Md';
        } else if (Math.abs(num) >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (Math.abs(num) >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toFixed(0);
    }
    
    formatCurrency(amount) {
        if (!amount) return '0 FCFA';
        const formatted = new Intl.NumberFormat('fr-FR', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(Math.abs(amount));
        const sign = amount < 0 ? '-' : '';
        return sign + formatted + ' FCFA';
    }
    
    formatPercent(value) {
        if (!value) return '0%';
        const sign = value >= 0 ? '+' : '';
        return sign + value.toFixed(1) + '%';
    }
    
    getStatusClass(variance_rate) {
        if (variance_rate < 5) return 'success';
        if (variance_rate < 15) return 'warning';
        return 'danger';
    }
    
    getStatusBadge(status) {
        const badges = {
            'excellent': 'success',
            'good': 'info',
            'warning': 'warning',
            'critical': 'danger',
        };
        return badges[status] || 'secondary';
    }
    
    renderCharts() {
        if (!this.state.data || !this.state.data.charts) {
            console.warn("⚠️ Pas de données pour les graphiques");
            return;
        }
        
        this.destroyAllCharts();
        
        const charts = this.state.data.charts;
        
        // Graphique 1: Évolution temporelle
        if (this.evolutionChartRef.el && charts.evolution) {
            this.charts.evolution = new Chart(this.evolutionChartRef.el, {
                type: 'line',
                data: charts.evolution,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Évolution de la Valeur Inventoriée'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (value) => this.formatNumber(value) + ' FCFA'
                            }
                        }
                    }
                }
            });
        }
        
        // Graphique 2: Performance par entrepôt
        if (this.warehousePerformanceChartRef.el && charts.warehouse_performance) {
            this.charts.warehousePerformance = new Chart(this.warehousePerformanceChartRef.el, {
                type: 'bar',
                data: charts.warehouse_performance,
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false,
                        },
                        title: {
                            display: true,
                            text: 'Taux d\'Écart par Entrepôt'
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: (value) => value + '%'
                            }
                        }
                    }
                }
            });
        }
        
        // Graphique 3: Répartition par catégorie
        if (this.categoryDistributionChartRef.el && charts.category_distribution) {
            this.charts.categoryDistribution = new Chart(this.categoryDistributionChartRef.el, {
                type: 'doughnut',
                data: charts.category_distribution,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'right',
                        },
                        title: {
                            display: true,
                            text: 'Répartition par Catégorie'
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const label = context.label || '';
                                    const value = this.formatCurrency(context.parsed);
                                    return `${label}: ${value}`;
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Graphique 4: Heatmap régions
        if (this.regionHeatmapChartRef.el && charts.region_heatmap) {
            this.charts.regionHeatmap = new Chart(this.regionHeatmapChartRef.el, {
                type: 'bar',
                data: charts.region_heatmap,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false,
                        },
                        title: {
                            display: true,
                            text: 'Écarts par Région Électrique'
                        },
                        tooltip: {
                            callbacks: {
                                label: (context) => {
                                    const value = this.formatCurrency(context.parsed.y);
                                    const count = charts.region_heatmap.counts[context.dataIndex];
                                    return [`Écart: ${value}`, `Inventaires: ${count}`];
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (value) => this.formatNumber(value) + ' FCFA'
                            }
                        }
                    }
                }
            });
        }
        
        // Graphique 5: Répartition entrepôt (quantité/valeur/écart)
        if (this.warehouseDistributionChartRef.el && charts.warehouse_distribution) {
            this.charts.warehouseDistribution = new Chart(this.warehouseDistributionChartRef.el, {
                type: 'bar',
                data: charts.warehouse_distribution,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Répartition par Entrepôt (Quantité / Valeur / Écart)'
                        }
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Quantité'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Valeur (FCFA)'
                            },
                            grid: {
                                drawOnChartArea: false,
                            },
                            ticks: {
                                callback: (value) => this.formatNumber(value)
                            }
                        }
                    }
                }
            });
        }
        
        // Graphique 6: Tendance des écarts
        if (this.varianceTrendChartRef.el && charts.variance_trend) {
            this.charts.varianceTrend = new Chart(this.varianceTrendChartRef.el, {
                type: 'line',
                data: charts.variance_trend,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Tendance des Écarts dans le Temps'
                        }
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Écart (FCFA)'
                            },
                            ticks: {
                                callback: (value) => this.formatNumber(value)
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Taux d\'écart (%)'
                            },
                            max: 100,
                            grid: {
                                drawOnChartArea: false,
                            },
                            ticks: {
                                callback: (value) => value + '%'
                            }
                        }
                    }
                }
            });
        }
        
        console.log("✅ Tous les graphiques rendus");
    }
    
    async exportWarehouseTable() {
        try {
            const result = await this.orm.call(
                "stockex.inventory.dashboard",
                "export_warehouse_table_excel",
                [],
                {
                    period: this.state.period,
                    valuation_method: this.state.valuationMethod,
                    warehouse_ids: this.state.warehouseIds,
                    region_ids: this.state.regionIds,
                }
            );
            
            if (result.error) {
                this.notification.add(result.error, { type: "danger" });
            } else if (result.type === 'ir.actions.act_url') {
                window.location.href = result.url;
                this.notification.add("Export Excel réussi", { type: "success" });
            }
        } catch (error) {
            console.error("❌ Erreur export Excel:", error);
            this.notification.add("Erreur lors de l'export Excel", { type: "danger" });
        }
    }
}

InventoryDashboard.template = "stockex.InventoryDashboard";

registry.category("actions").add("stockex.inventory_dashboard", InventoryDashboard);
