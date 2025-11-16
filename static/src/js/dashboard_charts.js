/** @odoo-module **/

import { Component, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";

export class DashboardCharts extends Component {
    setup() {
        super.setup();
        onMounted(() => {
            this.renderCharts();
        });
    }

    renderCharts() {
        // Attendre que Chart.js soit chargé
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js non chargé, tentative de chargement...');
            this.loadChartJS().then(() => this.initCharts());
        } else {
            this.initCharts();
        }
    }

    loadChartJS() {
        return new Promise((resolve, reject) => {
            if (typeof Chart !== 'undefined') {
                resolve();
                return;
            }
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    initCharts() {
        // Récupérer les données depuis les champs Odoo
        const records = this.props.list.records;
        if (!records || records.length === 0) return;

        const record = records[0];
        
        // Graphique écarts par entrepôt
        this.initWarehouseGapsChart(record);
        
        // Graphique valeur par famille
        this.initCategoryValueChart(record);
    }

    initWarehouseGapsChart(record) {
        const canvasEl = document.getElementById('warehouseGapsChart');
        if (!canvasEl) return;

        const dataField = record.data.warehouse_gaps_chart_data;
        if (!dataField) return;

        let chartData;
        try {
            chartData = JSON.parse(dataField);
        } catch (e) {
            console.error('Erreur parsing warehouse_gaps_chart_data:', e);
            return;
        }

        const ctx = canvasEl.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.labels || [],
                datasets: [{
                    label: 'Écart (FCFA)',
                    data: chartData.values || [],
                    backgroundColor: chartData.colors || [],
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed.y;
                                return `Écart: ${value.toLocaleString('fr-FR')} FCFA`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => value.toLocaleString('fr-FR')
                        }
                    }
                }
            }
        });
    }

    initCategoryValueChart(record) {
        const canvasEl = document.getElementById('categoryValueChart');
        if (!canvasEl) return;

        const dataField = record.data.category_value_chart_data;
        if (!dataField) return;

        let chartData;
        try {
            chartData = JSON.parse(dataField);
        } catch (e) {
            console.error('Erreur parsing category_value_chart_data:', e);
            return;
        }

        const ctx = canvasEl.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: chartData.labels || [],
                datasets: [{
                    data: chartData.values || [],
                    backgroundColor: chartData.colors || [],
                    borderWidth: 2,
                    borderColor: '#fff',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, padding: 10 }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percent = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value.toLocaleString('fr-FR')} FCFA (${percent}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
}

DashboardCharts.template = "stockex.DashboardCharts";

// Enregistrer le composant
registry.category("view_widgets").add("dashboard_charts", DashboardCharts);
